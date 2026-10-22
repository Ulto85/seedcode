---
title: Source Highlighting with Citations
difficulty: Medium
source: Harvey SWE technical screen / onsite, "highlight exact source matches" + "multi-source string matching and tagging" (reported 2025–2026; exact I/O reconstructed)
order: 1
minutes: 45
tags: strings, intervals, merging, citations
---
Harvey's assistant answers legal questions and must show which parts of its answer are copied **verbatim** from
the source documents. You get the LLM's answer `text` and a list of `sources` (quoted passages). Highlight every
place in the answer that a source appears, then report which sources back each highlight.

```
highlight(text: str, sources: list[str]) -> str
count_matches(text: str, sources: list[str]) -> list[int]
highlight_with_citations(text: str, sources: list[str]) -> str
```

**Matching rules (all parts)**
- Matching is **exact and case-sensitive** (`"A"` does not match `"a"`). No word-boundary rule: `"cat"` matches
  inside `"concatenate"`.
- Every occurrence counts, including **overlapping** ones: `"aa"` occurs at indices 0, 1, 2 and 3 of `"aaaaa"`.
- An occurrence of `s` starting at index `i` covers the half-open span `[i, i + len(s))`.
- An **empty** source never matches anything.
- `sources` may contain the same string more than once.

### Part 1: highlight
Wrap every maximal covered region in `<yellow>` and `</yellow>`. Spans that **overlap or touch** (one ends exactly
where the next starts) merge into a single region with a single tag pair. Characters not covered by any match are
copied unchanged. With no matches, return `text` as is.

```
highlight("abcxyz123", ["abc", "xyz", "z12"])
  spans [0,3) [3,6) [5,8)  -> touch/overlap -> one region [0,8)
  -> "<yellow>abcxyz12</yellow>3"

highlight("foobarbaz", ["foo", "baz"])   -> "<yellow>foo</yellow>bar<yellow>baz</yellow>"
```

### Part 2: count
Return a list where entry `i` is the number of (possibly overlapping) occurrences of `sources[i]` in `text`.
An empty source counts `0`.
```
count_matches("aaaaa", ["aa", "aaa", "b", ""])   -> [4, 3, 0, 0]
```

### Follow-up: citations
Produce the same output as Part 1, but immediately after each `</yellow>` append the citation markers
`[i]` for every **distinct source index** `i` that has at least one occurrence inside that region, in ascending
order. Duplicate source strings are separate indices, so both are cited.
```
highlight_with_citations("abcxyz123", ["abc", "xyz", "z12"])
  -> "<yellow>abcxyz12</yellow>[0][1][2]3"

highlight_with_citations("aaXXbbYYaa", ["aa", "bb", "YY", "q"])
  regions: [0,2) from "aa";  [4,10) from "bb" [4,6), "YY" [6,8), "aa" [8,10)
  -> "<yellow>aa</yellow>[0]XX<yellow>bbYYaa</yellow>[0][1][2]"
```

### Constraints
- `0 <= len(text) <= 2 * 10^5`, `0 <= len(sources) <= 200`, each source at most 50 characters
- `text` and sources never contain `<`, `>`, `[` or `]`
- Total number of occurrences across all sources is at most `~2 * 10^6`

### What the interviewer cares about
- Collect spans against the **original** text first, then build the output once (inserting tags while searching
  shifts every later index)
- Sort-and-merge intervals (or a difference array over positions) instead of comparing every pair of matches
- Getting overlap vs. touch, empty sources and duplicates right without being told twice
