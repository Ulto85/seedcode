# SEARCH.md: finding and adding a company's interview questions

This is the playbook Claude Code follows when you ask something like:

> add Notion
> find questions for Figma and Vercel
> what does Replit ask? add it

It turns a company name into a validated problem set in `problems/<company>/`, written the same way as every other
company in this repo.

---

## 1. Research (what they actually ask)

Search the last ~2 years of reports. Good sources, in rough order of usefulness:

| Source | What you get | Notes |
|---|---|---|
| prachub.com/companies/`<slug>` | Question titles, previews, round type, dates | Many pages are locked; titles and previews are still public. Some question pages are fully readable. |
| 1point3acres.com/interview/company/`<slug>` | Candidate threads, round structure | Details often behind login; titles and summaries are public. |
| leetcode.com/discuss (search "`<company>` interview") | Full write-ups | Often returns 403 to fetchers; use search-result summaries. |
| glassdoor.com interview reviews | Round format, question gist | Usually 403; search snippets are fine. |
| reddit (r/cscareerquestions, r/leetcode, r/csMajors), Blind | Format, difficulty, vibe | |
| jointaro.com, hellointerview.com, interviewing.io, Exponent | Experiences and guides | Guides that don't cite candidates are unverified. |
| The company's own blog / careers page / founder podcasts | How they say they interview | Often the only source for very small startups. |

Useful queries:
```
"<company>" software engineer interview coding question
"<company>" phone screen OR onsite "implement"
site:prachub.com <company>
site:1point3acres.com <company> interview
"<company>" interview experience 2025 OR 2026
```

Prefer questions that are **reported by multiple people**, **recent**, and **practical** (build a small system, parse
or process data, multi-part with follow-ups). Skip anything that's just a LeetCode problem with a new name. Mention
those in `company.json` notes instead.

## 2. Honesty rules (non-negotiable)

- **Write every problem in your own words.** Never paste paywalled text.
- **Only call a question "reported" if you found a report.** Put where it came from in `source:`.
- If you only found the format or themes, you may write a problem in that style, but `source:` **must start with
  "In the style of"** (or "Loosely based on") and end with "Not a reported question." The app labels these
  automatically.
- When details are locked or vague, invent precise rules and say so in the description ("exact rules are
  reconstructed").
- If you can't find anything credible, add **fewer** problems (2 is fine) and tell the user, rather than inventing.
- Don't add questions the user personally got in an interview they're under NDA for.
- `company.json` `sources` list only pages you actually used.

## 3. Build

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the exact file format. Aim for:

- **3–4 problems** per company, mixed difficulty, at least one multi-part (`### Part 1` / `### Follow-up`, tests tagged
  to match).
- **Unambiguous statements:** signatures in a code block, a worked example, constraints, tie-breaks, empty cases,
  error return values.
- **8+ tests per problem:** visible edge cases, seeded random hidden tests, and one **large hidden test** that a naive
  solution fails on time.
- A **`scale(n)` benchmark** whenever input size matters (6–7 doubling sizes; reference ≤ ~0.5s at the largest).
- A **correct reference solution.** Cross-check tricky ones against a brute-force version on a few hundred random
  inputs, and hand-check every worked example.

Several companies at once? Use one subagent per company in parallel, each limited to its own
`problems/<company>/` folder, and give it this file plus CONTRIBUTING.md.

## 4. Validate and publish

```bash
python3 tools/validate.py <company>        # iterate until every problem prints "ok"
python3 tools/readme.py                    # regenerate the README company table
```

The running server picks up new folders automatically. Refresh the page. Then summarize for the user: each problem,
whether it's reported or in-the-style-of, and the sources.

## 5. Removing a company

```bash
git rm -r problems/<company> && rm -f .cache/<company>__*
python3 tools/readme.py
```
Also replace any examples in the docs that mention it.
