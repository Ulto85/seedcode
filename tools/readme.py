#!/usr/bin/env python3
"""Regenerate the "## Companies" table in README.md from problems/."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import core

cs = core.list_companies()
total = sum(len(c["problems"]) for c in cs)
style = sum(p["style"] for c in cs for p in c["problems"])
rows = ["| Company | Problems |", "|---|---|"]
for c in cs:
    rows.append(f"| **{c['name']}** | " + ", ".join(p["title"] + (" *" if p["style"] else "") for p in c["problems"]) + " |")
body = (f"{total} problems across {len(cs)} companies. {total - style} are based on questions candidates reported; "
        f"the {style} marked * are practice problems written in a company's reported style, for companies with little "
        "public data (labeled \"Practice · in their style\" in the app).\n\n"
        "Want another company? In Claude Code, just say **\"add <company>\"** (see [SEARCH.md](SEARCH.md)).\n\n"
        + "\n".join(rows) + "\n")
path = os.path.join(ROOT, "README.md")
s = open(path).read()
s, n = re.subn(r"## Companies\n.*?\n## How it works", lambda m: "## Companies\n" + body + "\n## How it works", s, flags=re.S)
if not n:
    sys.exit("README.md has no '## Companies' ... '## How it works' section")
open(path, "w").write(s)
print(f"README updated: {total} problems, {len(cs)} companies")
