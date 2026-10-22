#!/usr/bin/env python3
"""SeedCode — local LeetCode-style practice server.

    python3 server.py            # then open http://localhost:8765
    PORT=9000 python3 server.py

No dependencies beyond the Python 3.9+ standard library.
"""
import json
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from engine import core

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8765))
PROBES = os.path.join(ROOT, "probes")
WORK = os.path.join(ROOT, "work")
os.makedirs(PROBES, exist_ok=True)
os.makedirs(WORK, exist_ok=True)
probe_lock = threading.Lock()

LEVELS = {
    "nudge": "One-line nudge. No spoilers, no code.",
    "hint": "A concrete hint: point at the idea or the line, don't write the fix.",
    "debug": "Find why the code fails. Point to the smallest bug first; explain, but don't rewrite the solution.",
    "complexity": "Explain the time and space complexity of the candidate's code and whether it can be improved.",
    "review": "Act like the interviewer: give feedback on correctness, edge cases, clarity, complexity and what they'd ask next.",
    "approach": "Outline the algorithm in steps. Short pseudo-code is fine; no full solution.",
    "solution": "Show a full clean solution with explanation and complexity.",
}


def short(x, n=300):
    s = json.dumps(x, default=repr)
    return s if len(s) <= n else s[:n] + f"... ({len(s)} chars)"


def write_probe(body):
    p = core.load_problem(body["company"], body["slug"])
    level = body.get("level", "hint")
    res = body.get("last_run") or {}
    lines = [f"# Probe: {p['title']} ({body['company']})", "",
             f"- problem: problems/{body['company']}/{body['slug']}/problem.md",
             f"- time on clock: {body.get('elapsed', '?')}",
             f"- help level: **{level}** — {LEVELS.get(level, '')}", "",
             "## Candidate's note", body.get("note") or "(none)", "",
             "## Candidate's code", "```python", body.get("code", ""), "```", "", "## Last run"]
    if not res:
        lines.append("(not run yet)")
    elif res.get("compile_error"):
        lines += ["compile error:", "```", res["compile_error"].strip(), "```"]
    else:
        lines.append(f"mode: {res.get('mode')}, {sum(r.get('status') == 'pass' for r in res.get('results', []))}/{len(res.get('results', []))} passed")
        for r in res.get("results", []):
            line = f"- [{str(r.get('status')).upper()}] {r.get('name')} ({r.get('tag')})"
            if r.get("status") != "pass":
                if r.get("kind") == "function":
                    line += f"\n    input: {r.get('call')}({short(r.get('args'), 200)[1:-1] if isinstance(r.get('args'), list) else r.get('args')})"
                if r.get("first_bad") is not None:
                    line += f"\n    first wrong op index: {r['first_bad']}"
                line += f"\n    expected: {short(r.get('expected'))}\n    got: {short(r.get('got'))}"
                if r.get("error"):
                    line += "\n    error: " + r["error"].strip().splitlines()[-1]
            lines.append(line)
    cx = body.get("complexity")
    if cx and cx.get("mine"):
        lines += ["", "## Measured complexity",
                  f"- candidate: time {((cx['mine'].get('time') or {}).get('label'))}, space {((cx['mine'].get('space') or {}).get('label'))}",
                  f"- reference: time {((cx['ref'].get('time') or {}).get('label'))}, space {((cx['ref'].get('space') or {}).get('label'))}"]
    text = "\n".join(lines) + "\n"
    with probe_lock:
        n = len([f for f in os.listdir(PROBES) if f.endswith(".md")]) + 1
        path = os.path.join(PROBES, f"probe_{n:03d}.md")
        open(path, "w").write(text)
        with open(os.path.join(PROBES, "probe.log"), "a") as f:
            f.write(f"PROBE {n} [{body['company']}/{body['slug']}] level={level} -> {os.path.relpath(path, ROOT)}\n")
    prompt = ("I'm practicing a coding interview problem. Please help at this level: "
              f"{level} — {LEVELS.get(level, '')}\n\n## Problem\n{p['description']}\n\n" + text)
    return n, prompt


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=repr).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def guard(self, fn):
        try:
            return fn()
        except KeyError as e:
            return self.send(404, {"error": str(e)})
        except Exception as e:
            traceback.print_exc()
            return self.send(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        if path in ("/", "/index.html"):
            return self.send(200, open(os.path.join(ROOT, "app", "index.html"), "rb").read(), "text/html; charset=utf-8")
        if path == "/api/companies":
            return self.guard(lambda: self.send(200, core.list_companies()))
        if path.startswith("/api/problem/"):
            parts = path.split("/")[3:]
            if len(parts) == 2:
                return self.guard(lambda: self.send(200, core.public_problem(core.load_problem(*parts))))
        self.send(404, {"error": "not found"})

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self.send(400, {"error": "bad json"})
        company, slug = body.get("company", ""), body.get("slug", "")

        def save():
            d = os.path.join(WORK, company)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, slug + ".py"), "w").write(body.get("code", ""))

        if self.path == "/api/run":
            def go():
                core.problem_dir(company, slug)
                save()
                return self.send(200, core.run_user(company, slug, body.get("code", ""), body.get("mode", "run")))
            return self.guard(go)
        if self.path == "/api/complexity":
            def go():
                core.problem_dir(company, slug)
                save()
                return self.send(200, core.complexity(company, slug, body.get("code", "")))
            return self.guard(go)
        if self.path == "/api/probe":
            def go():
                core.problem_dir(company, slug)
                save()
                n, prompt = write_probe(body)
                return self.send(200, {"probe": n, "prompt": prompt})
            return self.guard(go)
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9+ required")
    open(os.path.join(PROBES, "probe.log"), "a").close()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"SeedCode running at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
