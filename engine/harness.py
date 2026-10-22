"""Runs a solution file against test specs in an isolated subprocess.

usage: python3 -I harness.py <solution.py> <job.json> <out.jsonl>

job.json = {"mode": "test" | "record" | "bench", "tests": [spec, ...], "budget": seconds}

Writes one JSON line per test, so partial results survive a timeout.
  test   -> compares with spec["expected"]
  record -> just records outputs (used to generate expected values from reference solutions)
  bench  -> measures time and peak memory per spec (used by the complexity view)
"""
import contextlib
import gc
import importlib.util
import io
import json
import math
import sys
import time
import tracemalloc
import traceback

sol_path, job_path, out_path = sys.argv[1:4]
job = json.load(open(job_path))
mode = job["mode"]
out = open(out_path, "w", buffering=1)
sys.setrecursionlimit(100000)


def emit(d):
    out.write(json.dumps(d, default=repr) + "\n")
    out.flush()


def clean_tb():
    return traceback.format_exc().replace(sol_path, "solution.py")


buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        spec = importlib.util.spec_from_file_location("solution", sol_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
except BaseException:
    emit({"compile_error": clean_tb(), "stdout": buf.getvalue()[-4000:]})
    sys.exit(0)


def norm(x):
    """Make outputs JSON-comparable: tuples -> lists, sets -> sorted lists, dict keys -> str."""
    if isinstance(x, (list, tuple)):
        return [norm(v) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted((norm(v) for v in x), key=lambda v: json.dumps(v, sort_keys=True, default=repr))
    if isinstance(x, dict):
        return {str(k): norm(v) for k, v in x.items()}
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return repr(x)
    return x


def canon(x, how):
    if how == "unordered" and isinstance(x, list):
        return sorted(x, key=lambda v: json.dumps(v, sort_keys=True, default=repr))
    if how == "unordered_deep" and isinstance(x, list):
        return sorted((canon(v, how) for v in x), key=lambda v: json.dumps(v, sort_keys=True, default=repr))
    return x


def same(a, b, fl):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b if isinstance(a, bool) and isinstance(b, bool) else False
    if fl and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, fl) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], fl) for k in a)
    return a == b


def fresh(x):
    return json.loads(json.dumps(x))


def build(t):
    """Returns a zero-arg callable that executes the spec and returns the outputs."""
    if t["kind"] == "function":
        fn = getattr(mod, t["call"], None)
        if fn is None:
            raise NameError(f"function '{t['call']}' is not defined")
        args = fresh(t["args"])
        return lambda: fn(*args)
    cls = getattr(mod, t["cls"], None)
    if cls is None:
        raise NameError(f"class '{t['cls']}' is not defined")
    init, ops = fresh(t["init"]), fresh(t["ops"])

    def go():
        obj = cls(*init)
        return [getattr(obj, m)(*a) for m, a in ops]
    return go


def run_test(i, t):
    res = {"i": i}
    buf = io.StringIO()
    t0 = time.perf_counter()
    try:
        with contextlib.redirect_stdout(buf):
            how = t.get("compare")
            if t["kind"] == "function":
                got = norm(build(t)())
                res["got"] = got
                if mode == "test":
                    ok = same(canon(got, how), canon(t["expected"], how), t.get("float"))
            else:
                cls = getattr(mod, t["cls"], None)
                if cls is None:
                    raise NameError(f"class '{t['cls']}' is not defined")
                obj = cls(*fresh(t["init"]))
                got = []
                res["got"] = got
                ok, first_bad = True, None
                for j, (m, a) in enumerate(fresh(t["ops"])):
                    if not hasattr(obj, m):
                        raise AttributeError(f"'{t['cls']}' has no method '{m}'")
                    r = norm(getattr(obj, m)(*a))
                    got.append(r)
                    if mode == "test" and ok and not same(canon(r, how), canon(t["expected"][j], how), t.get("float")):
                        ok, first_bad = False, j
                res["first_bad"] = first_bad
        res["status"] = "recorded" if mode == "record" else ("pass" if ok else "fail")
    except RecursionError:
        res.update(status="error", error="RecursionError: maximum recursion depth exceeded\n" + clean_tb()[-1500:])
    except BaseException:
        res.update(status="error", error=clean_tb()[-3000:])
    res["ms"] = round((time.perf_counter() - t0) * 1000, 2)
    res["stdout"] = buf.getvalue()[-2000:]
    emit(res)


def bench(i, t, deadline):
    res = {"i": i, "n": t.get("n")}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            # time: GC off (its pauses dominate noise), best of several runs.
            # Small inputs repeat until ~0.1s per sample; big ones run up to 3 times.
            gc.collect()
            gc.disable()
            try:
                go = build(t)
                t0 = time.perf_counter(); go(); first = time.perf_counter() - t0
                best = first
                reps = max(1, int(0.1 / max(first, 1e-6))) if first < 0.05 else 1
                rounds = 3 if first < 0.6 else 1
                for _ in range(rounds):
                    go = build(t)
                    t0 = time.perf_counter()
                    for _ in range(reps):
                        go()
                    best = min(best, (time.perf_counter() - t0) / reps)
            finally:
                gc.enable()
            res["time"] = best
            # space: peak bytes allocated during the call (input is built before tracing starts)
            go = build(t)
            tracemalloc.start()
            tracemalloc.reset_peak()
            base = tracemalloc.get_traced_memory()[0]
            go()
            res["mem"] = max(0, tracemalloc.get_traced_memory()[1] - base)
            tracemalloc.stop()
        res["status"] = "ok"
    except BaseException:
        res.update(status="error", error=clean_tb()[-1500:])
    emit(res)
    return res


if mode == "bench":
    deadline = time.time() + job.get("budget", 20)
    for i, t in enumerate(job["tests"]):
        if time.time() > deadline:
            break
        r = bench(i, t, deadline)
        # stop growing once a single run gets slow; bigger sizes would only time out
        if r["status"] != "ok" or r["time"] > job.get("max_single", 1.5):
            break
else:
    for i, t in enumerate(job["tests"]):
        run_test(i, t)
