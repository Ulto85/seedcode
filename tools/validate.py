#!/usr/bin/env python3
"""Validate problems: generates expected outputs from each reference solution, then checks
that the reference passes its own tests, the starter compiles, and the scaling benchmark runs.

    python3 tools/validate.py                 # everything
    python3 tools/validate.py openai          # one company
    python3 tools/validate.py openai/gpu-credits
    python3 tools/validate.py --no-bench      # skip complexity benchmarks
"""
import os, sys, json, ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import core

args = [a for a in sys.argv[1:] if not a.startswith("--")]
bench = "--no-bench" not in sys.argv
targets = []
for c in core.list_companies():
    for p in c["problems"]:
        key = f"{c['slug']}/{p['slug']}"
        if not args or any(key == a or c["slug"] == a for a in args):
            targets.append((c["slug"], p["slug"]))
if not targets:
    sys.exit(f"nothing matched {args}")

bad = 0
for company, slug in targets:
    key = f"{company}/{slug}"
    issues, notes = [], []
    try:
        p = core.load_problem(company, slug, force=True)
    except Exception as e:
        print(f"FAIL {key}\n     {e}"); bad += 1; continue
    pdir = core.problem_dir(company, slug)
    for f in ("title", "difficulty", "source"):
        if not p.get(f) or p.get(f) == slug:
            issues.append(f"problem.md frontmatter missing '{f}'")
    if p["difficulty"] not in ("Easy", "Medium", "Hard"):
        issues.append("difficulty must be Easy, Medium or Hard")
    try:
        ast.parse(p["starter"])
    except SyntaxError as e:
        issues.append(f"starter.py does not parse: {e}")
    tests = p["tests"]
    names = [t["name"] for t in tests]
    if len(set(names)) != len(names):
        issues.append("duplicate test names")
    if sum(1 for t in tests if not t["hidden"] and t["tag"] != "Stretch") < 2:
        issues.append("need at least 2 visible tests")
    if not any(t["hidden"] for t in tests):
        notes.append("no hidden tests")
    entries = {t.get("call") or t.get("cls") for t in tests}
    for e in entries:
        if e and e not in p["starter"]:
            issues.append(f"starter.py doesn't define '{e}'")
    sol = open(os.path.join(pdir, "solution.py")).read()
    r = core.execute(sol, tests, "test", timeout=max(p["timeout"] * 3, 60))
    failed = [t["name"] for t, res in zip(tests, r.get("results", [])) if res.get("status") != "pass"]
    if r.get("compile_error") or failed:
        issues.append(f"reference fails its own tests: {failed or r.get('compile_error')}")
    slow = [(t["name"], res.get("ms")) for t, res in zip(tests, r.get("results", [])) if (res.get("ms") or 0) > p["timeout"] * 1000 / 3]
    if slow:
        notes.append(f"slow reference tests (vs {p['timeout']:g}s limit): {slow}")
    starter = core.execute(p["starter"], tests[:1], "test", timeout=20)
    if starter.get("compile_error"):
        issues.append("starter.py raises on import:\n" + starter["compile_error"])
    cx = ""
    if bench and p["has_scale"]:
        c = core.complexity(company, slug, sol)
        if c.get("error") or c.get("compile_error") or c["ref"].get("error"):
            issues.append(f"benchmark failed: {c.get('error') or c.get('compile_error') or c['ref'].get('error')}")
        else:
            pts = c["ref"]["points"]
            t, s = c["ref"]["time"] or {}, c["ref"]["space"] or {}
            cx = f"  ref time {t.get('label')} space {s.get('label')} ({len(pts)} sizes)"
            if len(pts) < 4:
                notes.append(f"benchmark only measured {len(pts)} sizes; use smaller/more sizes")
    elif bench:
        notes.append("no scale() benchmark")
    status = "FAIL" if issues else "ok  "
    bad += bool(issues)
    print(f"{status} {key}: {len(tests)} tests ({sum(t['hidden'] for t in tests)} hidden){cx}")
    for i in issues: print(f"     ✗ {i}")
    for n in notes: print(f"     · {n}")
print(f"\n{len(targets) - bad}/{len(targets)} problems valid")
sys.exit(1 if bad else 0)
