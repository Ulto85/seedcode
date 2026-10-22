"""Problem discovery, test generation, running code, and complexity fitting."""
import hashlib
import json
import math
import os
import re
import runpy
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBLEMS_DIR = os.path.join(ROOT, "problems")
CACHE_DIR = os.path.join(ROOT, ".cache")
HARNESS = os.path.join(ROOT, "engine", "harness.py")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_lock = threading.Lock()
_problem_cache = {}


# ----------------------------------------------------------------------------- discovery

def parse_frontmatter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = text[end + 4:].lstrip("\n")
    return meta, body


STYLE_RE = re.compile(r"^\s*(in the style of|loosely)", re.I)


def is_style(source):
    """Problems whose source line starts with "In the style of" / "Loosely" are practice problems, not reported questions."""
    return bool(STYLE_RE.match(source or ""))


def list_companies():
    out = []
    for slug in sorted(os.listdir(PROBLEMS_DIR)):
        cdir = os.path.join(PROBLEMS_DIR, slug)
        cfile = os.path.join(cdir, "company.json")
        if not os.path.isfile(cfile):
            continue
        info = json.load(open(cfile))
        probs = []
        for p in sorted(os.listdir(cdir)):
            pdir = os.path.join(cdir, p)
            if os.path.isfile(os.path.join(pdir, "problem.md")):
                meta, _ = parse_frontmatter(open(os.path.join(pdir, "problem.md")).read())
                probs.append({"slug": p, "title": meta.get("title", p), "difficulty": meta.get("difficulty", "Medium"),
                              "order": int(meta.get("order", 99)), "style": is_style(meta.get("source")), "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]})
        probs.sort(key=lambda x: (x["order"], x["title"]))
        out.append({"slug": slug, "name": info.get("name", slug), "tagline": info.get("tagline", ""),
                    "sources": info.get("sources", []), "notes": info.get("notes", ""), "problems": probs})
    out.sort(key=lambda c: c["name"].lower())
    return out


def problem_dir(company, slug):
    d = os.path.realpath(os.path.join(PROBLEMS_DIR, company, slug))
    if not d.startswith(os.path.realpath(PROBLEMS_DIR) + os.sep) or not os.path.isfile(os.path.join(d, "problem.md")):
        raise KeyError(f"no problem {company}/{slug}")
    return d


def _file_hash(*paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(p.encode())
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:16]


def load_tests_module(pdir):
    return runpy.run_path(os.path.join(pdir, "tests.py"), run_name="tests")


def load_problem(company, slug, force=False):
    """Returns the full problem dict, including tests with expected values (generated + cached)."""
    pdir = problem_dir(company, slug)
    files = [os.path.join(pdir, f) for f in ("problem.md", "starter.py", "solution.py", "tests.py")] + [HARNESS, os.path.join(ROOT, "engine", "spec.py")]
    key = _file_hash(*files)
    ck = f"{company}/{slug}"
    with _lock:
        if not force and ck in _problem_cache and _problem_cache[ck]["_key"] == key:
            return _problem_cache[ck]
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{company}__{slug}.json")
    if not force and os.path.exists(cache_file):
        data = json.load(open(cache_file))
        if data.get("_key") == key:
            with _lock:
                _problem_cache[ck] = data
            return data

    meta, body = parse_frontmatter(open(os.path.join(pdir, "problem.md")).read())
    mod = load_tests_module(pdir)
    tests = mod["tests"]()
    timeout = float(meta.get("timeout", 20))
    need = [i for i, t in enumerate(tests) if "expected" not in t]
    if need:
        solution = open(os.path.join(pdir, "solution.py")).read()
        r = execute(solution, [tests[i] for i in need], "record", timeout=max(timeout * 3, 60))
        if r.get("compile_error"):
            raise RuntimeError(f"{ck}: reference solution failed to import:\n{r['compile_error']}")
        for i, res in zip(need, r["results"]):
            if res["status"] != "recorded":
                raise RuntimeError(f"{ck}: reference solution failed on test '{tests[i]['name']}':\n{res.get('error')}")
            tests[i]["expected"] = res["got"]
    for i, t in enumerate(tests):
        t["i"] = i
    data = {
        "_key": key, "company": company, "slug": slug,
        "title": meta.get("title", slug), "difficulty": meta.get("difficulty", "Medium"),
        "source": meta.get("source", ""), "style": is_style(meta.get("source")), "minutes": int(meta.get("minutes", 45)), "timeout": timeout,
        "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "description": body, "starter": open(os.path.join(pdir, "starter.py")).read(),
        "tests": tests, "has_scale": "scale" in mod,
        "scale_label": (mod.get("SCALE") or {}).get("label", "n"),
    }
    json.dump(data, open(cache_file, "w"))
    with _lock:
        _problem_cache[ck] = data
    return data


def public_problem(p):
    tests = []
    for t in p["tests"]:
        d = {k: t[k] for k in ("i", "name", "tag", "hidden", "kind")}
        if not t["hidden"]:
            d.update({k: t[k] for k in ("call", "args", "cls", "init", "ops", "expected") if k in t})
        tests.append(d)
    return {k: v for k, v in p.items() if k not in ("tests", "_key")} | {"tests": tests}


# ----------------------------------------------------------------------------- running

def execute(code, tests, mode, timeout=20, extra=None):
    job = {"mode": mode, "tests": tests} | (extra or {})
    with tempfile.TemporaryDirectory() as d:
        sol, jp, out = (os.path.join(d, x) for x in ("solution.py", "job.json", "out.jsonl"))
        open(sol, "w").write(code)
        json.dump(job, open(jp, "w"))
        t0 = time.time()
        timed_out, stderr = False, ""
        try:
            proc = subprocess.run([sys.executable, "-I", HARNESS, sol, jp, out], cwd=d,
                                  capture_output=True, text=True, timeout=timeout)
            stderr = proc.stderr[-3000:]
        except subprocess.TimeoutExpired:
            timed_out = True
        lines = []
        if os.path.exists(out):
            for l in open(out):
                try:
                    lines.append(json.loads(l))
                except ValueError:
                    pass
    if lines and "compile_error" in lines[0]:
        return {"compile_error": lines[0]["compile_error"], "stdout": lines[0].get("stdout", "")}
    if mode == "bench":
        return {"points": lines, "timed_out": timed_out, "elapsed": round(time.time() - t0, 2)}
    results = []
    for k in range(len(tests)):
        if k < len(lines):
            results.append(lines[k])
        else:
            results.append({"status": "tle" if timed_out else "error",
                            "error": f"Time limit exceeded ({timeout:g}s for the whole run)" if timed_out
                            else (stderr or "Process crashed (out of memory?)")})
    return {"results": results, "timed_out": timed_out, "elapsed": round(time.time() - t0, 2)}


def _trim(r, t):
    """Shape a result for the UI (truncate huge op lists around the first mismatch)."""
    r = dict(r)
    r.update(i=t["i"], name=t["name"], tag=t["tag"], hidden=t["hidden"], kind=t["kind"], expected=t["expected"])
    if t["kind"] == "class":
        r.update(cls=t["cls"], init=t["init"], ops=t["ops"])
        if len(t["ops"]) > 60:
            fb = r.get("first_bad") or 0
            lo = max(0, fb - 5)
            r["ops"], r["expected"] = t["ops"][lo:lo + 25], t["expected"][lo:lo + 25]
            if isinstance(r.get("got"), list):
                r["got"] = r["got"][lo:lo + 25]
            r["window"] = [lo, len(t["ops"])]
        if len(json.dumps(r["init"])) > 3000:
            r["init"] = "(large input)"
    else:
        r["call"] = t["call"]
        if len(json.dumps(t["args"])) > 3000:
            r["args"] = "(large input)"
        else:
            r["args"] = t["args"]
        for k in ("expected", "got"):
            if k in r and len(json.dumps(r[k], default=repr)) > 3000:
                r[k] = json.dumps(r[k], default=repr)[:3000] + " …(truncated)"
    return r


def run_user(company, slug, code, mode):
    p = load_problem(company, slug)
    tests = [t for t in p["tests"] if mode == "submit" or (not t["hidden"] and t["tag"] != "Stretch")]
    r = execute(code, tests, "test", timeout=p["timeout"])
    if "results" in r:
        r["results"] = [_trim(res, t) for res, t in zip(r["results"], tests)]
    r["mode"] = mode
    return r


# ----------------------------------------------------------------------------- complexity

CLASSES = [
    ("O(1)", lambda n: 1.0),
    ("O(log n)", lambda n: math.log2(max(n, 2))),
    ("O(n)", lambda n: float(n)),
    ("O(n log n)", lambda n: n * math.log2(max(n, 2))),
    ("O(n²)", lambda n: float(n) ** 2),
    ("O(n³)", lambda n: float(n) ** 3),
    ("O(2ⁿ)", lambda n: 2.0 ** n),
]


SPACE_CLASSES = {"O(1)", "O(log n)", "O(n)", "O(n²)"}  # memory is too noisy to tell n from n log n


def fit(points, key, floor):
    """Pick the complexity class whose shape best matches the measurements (least squares in log space)."""
    pts = [(p["n"], p[key]) for p in points if p.get("status") == "ok" and p.get(key) is not None]
    if len(pts) < 3:
        return None
    if all(v <= floor for _, v in pts):
        return {"label": "O(1)", "note": "too small to measure"}
    pts = [(n, max(v, floor)) for n, v in pts]
    scored = []
    for label, f in CLASSES:
        if label == "O(2ⁿ)" and max(n for n, _ in pts) > 40:
            continue
        if key == "mem" and label not in SPACE_CLASSES:
            continue
        logs = [math.log(v) - math.log(f(n)) for n, v in pts]
        c = sum(logs) / len(logs)
        err = sum((x - c) ** 2 for x in logs) / len(logs)
        scored.append((label, err, math.exp(c)))
    # measurements are noisy: prefer the simplest class that fits almost as well as the best one
    min_err = min(e for _, e, _ in scored)
    best = next(s for s in scored if s[1] <= min_err * 1.6 + 0.004)
    # growth exponent between first and last point, as a sanity number
    (n0, v0), (n1, v1) = pts[0], pts[-1]
    slope = math.log(v1 / v0) / math.log(n1 / n0) if n1 != n0 and v0 > 0 else None
    return {"label": best[0], "err": round(best[1], 4), "c": best[2], "slope": round(slope, 2) if slope is not None else None}


def complexity(company, slug, code):
    pdir = problem_dir(company, slug)
    mod = load_tests_module(pdir)
    if "scale" not in mod:
        return {"error": "This problem has no scaling benchmark yet."}
    cfg = mod.get("SCALE") or {}
    sizes = cfg.get("sizes", [500, 1000, 2000, 4000, 8000, 16000, 32000])
    specs = []
    for n in sizes:
        s = mod["scale"](n)
        s["n"] = n
        specs.append(s)
    extra = {"budget": cfg.get("budget", 20), "max_single": cfg.get("max_single", 1.5)}

    ref_key = _file_hash(os.path.join(pdir, "solution.py"), os.path.join(pdir, "tests.py"), HARNESS)
    ref_file = os.path.join(CACHE_DIR, f"{company}__{slug}__bench.json")
    ref = None
    if os.path.exists(ref_file):
        d = json.load(open(ref_file))
        if d.get("_key") == ref_key:
            ref = d
    if ref is None:
        ref = execute(open(os.path.join(pdir, "solution.py")).read(), specs, "bench", timeout=60, extra=extra)
        ref["_key"] = ref_key
        os.makedirs(CACHE_DIR, exist_ok=True)
        json.dump(ref, open(ref_file, "w"))

    mine = execute(code, specs, "bench", timeout=extra["budget"] + 15, extra=extra)
    if mine.get("compile_error"):
        return {"compile_error": mine["compile_error"]}
    out = {"label": cfg.get("label", "n"), "per_op": cfg.get("per_op", False), "sizes": sizes}
    for name, r in (("mine", mine), ("ref", ref)):
        pts = r.get("points", [])
        errors = [p.get("error") for p in pts if p.get("status") == "error"]
        out[name] = {"points": [p for p in pts if p.get("status") == "ok"],
                     "time": fit(pts, "time", 2e-6), "space": fit(pts, "mem", 256),
                     "error": errors[0] if errors else None, "timed_out": r.get("timed_out")}
    return out
