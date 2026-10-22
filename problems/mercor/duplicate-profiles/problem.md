---
title: Merge Duplicate Candidate Profiles
difficulty: Medium
source: In the style of Mercor's reported SWE technical round ("finding duplicates using hash sets", Exponent/Aced candidate report) and practical data-processing coding. Not a reported question.
order: 3
minutes: 40
tags: hashing, union-find, strings, data cleaning
---
A hiring marketplace ends up with the same expert signed up several times: once from a referral link, once from a
job board, once with a work email. Before ranking candidates for a client, you need to collapse duplicates.

```
merge_profiles(profiles: list[dict], normalize_gmail: bool = False) -> list[dict]
```
Each profile is `{"id": str, "emails": [str, ...], "phones": [str, ...]}`. Ids are unique; either list may be empty.

### Part 1
**Normalising identifiers**
- **Email:** strip surrounding whitespace and lowercase it. It is valid only if it then contains exactly one `@`
  with a non-empty part on both sides. Invalid emails are ignored completely.
- **Phone:** keep only the digits (`"+1 (415) 555-0101"` becomes `"14155550101"`). If that leaves 11 digits starting
  with `1`, drop the leading `1`. It is valid only if exactly 10 digits remain. Invalid phones are ignored completely.

**Matching.** Two profiles belong to the same person if they share at least one valid normalised email or phone.
This is transitive: if A shares an email with B and B shares a phone with C, then A, B and C are one person even if
A and C have nothing in common.

**Output.** One dict per person: `{"ids": [...], "emails": [...], "phones": [...]}` where
- `ids` are that person's profile ids, sorted ascending (plain string order);
- `emails` / `phones` are the distinct valid **normalised** identifiers across their profiles, sorted ascending;
- people are ordered by their smallest id. A profile matching no one is its own person. No profiles: `[]`.

### Example
```
profiles = [
  {"id": "p1", "emails": ["Ana@Mail.com"],  "phones": []},
  {"id": "p2", "emails": [" ana@mail.com"], "phones": ["(415) 555-0101"]},
  {"id": "p3", "emails": ["not-an-email"],  "phones": ["+1 415 555 0101"]},
  {"id": "p4", "emails": ["bo@x.io"],       "phones": ["555-0101"]},
]
merge_profiles(profiles) -> [
  {"ids": ["p1", "p2", "p3"], "emails": ["ana@mail.com"], "phones": ["4155550101"]},
  {"ids": ["p4"],             "emails": ["bo@x.io"],       "phones": []},
]
```
p1 and p2 share an email; p2 and p3 share a phone (the `+1` is dropped). `"not-an-email"` and the 7-digit phone are
ignored, so p4 matches nobody.

### Follow-up: Gmail aliases
With `normalize_gmail=True`, apply extra rules to emails whose domain (after lowercasing) is `gmail.com` or
`googlemail.com`, before matching:
1. In the local part, drop the first `+` and everything after it (`ana+jobs` becomes `ana`).
2. Then remove every `.` from the local part (`a.n.a` becomes `ana`).
3. The domain becomes `gmail.com`.

If the local part ends up empty (e.g. `"+x@gmail.com"`), the email is invalid. Other domains are untouched. The
output lists the fully normalised form.
```
merge_profiles([{"id": "a", "emails": ["A.na+jobs@googlemail.com"], "phones": []},
                {"id": "b", "emails": ["ana@gmail.com"], "phones": []}], True)
  -> [{"ids": ["a", "b"], "emails": ["ana@gmail.com"], "phones": []}]
```

### Constraints
- Up to `5 * 10^4` profiles and `2 * 10^5` identifiers in total. Comparing every pair of profiles is too slow.

### What the interviewer cares about
- Writing normalisation as small, separately testable functions, and asking about the rules instead of guessing
- Handling transitivity (union-find or graph traversal) rather than one pass of pairwise checks
- Not letting invalid or junk identifiers glue unrelated people together
