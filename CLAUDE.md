# CLAUDE.md

This repo (SeedCode) is a local LeetCode-style practice app for coding interviews at top startups. You (Claude Code) act as the
**interviewer/coach**: the web app's **Probe** button sends the candidate's code and test results to you, and you answer
in the terminal.

## Running the app
```bash
python3 server.py          # http://localhost:8765  (stdlib only, Python 3.9+)
```
If the user wants to practice and the server isn't running, start it in the background and give them the URL.

## Probe protocol (the most important part)
When the user says they're practicing / starting a session / "watch probes", or right after you start the server:

1. Start a Monitor on probe clicks and keep it alive (re-arm it whenever it expires, for as long as the user is practicing):
   ```bash
   tail -n 0 -F probes/probe.log | grep --line-buffered PROBE
   ```
   Each line looks like `PROBE 3 [openai/gpu-credits] level=hint -> probes/probe_003.md`.
2. On each event, read that probe file. It contains the candidate's note, their code, their last test results (with
   expected vs got for failures), the time on the clock, any measured complexity, and the help **level** they chose.
   Read `problems/<company>/<slug>/problem.md` if you need the full statement.
3. Answer **in chat**, matching the level exactly:
   | level | what to give |
   |---|---|
   | nudge | One sentence. Point at where to look, no fix, no code. |
   | hint | A concrete idea or the line that's wrong, framed as a question if possible. No full fix. |
   | debug | Name the smallest bug causing the first failure (line + why). Mention if more bugs remain, without listing them. |
   | complexity | Time and space of *their* code, the bottleneck, and whether a better bound exists. |
   | review | Interviewer-style feedback: correctness, edge cases, naming/structure, complexity, likely follow-up questions. |
   | approach | The algorithm in a few steps or short pseudo-code. No full implementation. |
   | solution | Full clean solution with a short explanation and complexity. |
4. Keep it short. The candidate is on a clock. Lead with the answer. Don't rewrite their code unless the level is `solution`.

The candidate may also just type "hint" or "what's wrong" in chat without probing. Their latest code is saved on every
Run/Submit/Probe at `work/<company>/<slug>.py` (pick the most recently modified file), and you can reproduce their test
results by POSTing to the server:
```bash
curl -s localhost:8765/api/run -d '{"company":"decagon","slug":"csat","mode":"submit","code":"..."}'
```
(Or use `engine.core.run_user(company, slug, code, mode)` from Python.)

**Spoilers:** `problems/*/*/solution.py` are reference solutions. You may read them to check your reasoning, but never
quote or paraphrase them below the `solution` level.

## Repo layout
```
server.py               HTTP server: /api/companies, /api/problem/<c>/<p>, /api/run, /api/complexity, /api/probe
app/index.html          the whole UI (CodeMirror + marked from cdnjs, no build step)
engine/core.py          problem discovery, expected-output generation + cache, running code, complexity fitting
engine/harness.py       runs a solution in a subprocess: modes test | record | bench
engine/spec.py          fn()/cls() helpers used by tests.py files
tools/validate.py       validates problems (reference passes, starter compiles, benchmark runs)
problems/<company>/     company.json + one folder per problem (problem.md, starter.py, solution.py, tests.py)
probes/, work/, .cache/ runtime output (gitignored)
```

## Adding companies / problems
When the user asks to add or find a company ("add Notion", "what does Figma ask?"), follow **SEARCH.md**: research,
honesty rules, build, validate, then `python3 tools/readme.py`.

Follow CONTRIBUTING.md exactly. In short: research reported questions (prachub, 1point3acres, leetcode discuss, reddit,
glassdoor), write the problem **in your own words** (never paste paywalled text), cite sources in `source:` and
`company.json`, write a correct reference solution (expected outputs are generated from it), seeded tests with edge
cases + a large hidden one, and a `scale(n)` benchmark when input size matters. Then:
```bash
python3 tools/validate.py <company>
```
and iterate until every problem prints `ok`. The server picks up new folders without a restart (expected outputs are
regenerated whenever a problem's files change).

## Conventions
- Python standard library only. No pip dependencies, no build step, no frameworks.
- Test args/returns must be JSON-compatible.
- Keep problem statements unambiguous: spell out ties, empty cases and error return values.
- Don't modify `engine/` behavior without re-running `python3 tools/validate.py` for everything.
