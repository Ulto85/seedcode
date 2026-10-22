---
title: Department-Scoped Typeahead
difficulty: Medium
source: Glean SWE onsite / technical screen, "top-k prefix suggestions filtered by department" (reported 2026 on PracHub; tie and duplicate rules are ours)
order: 2
minutes: 45
tags: design, prefix search, binary search, top-k, segment tree
---
Glean's search box suggests completions as you type, but people should only see suggestions from **their own
department**. You're given a static list of suggestions, and the service has to answer a lot of queries against it.

```
Typeahead(suggestions: list)          # each suggestion is [ngram: str, department: int, score: int]
top(query: str, dept: int, k: int) -> list[str]
```

`top` returns up to `k` ngrams that are **valid** for this query:
- `query` is a prefix of the ngram (plain string prefix, case-sensitive; the empty query matches everything), and
- the suggestion's department equals `dept`.

**Order:** highest score first; equal scores by ngram ascending (plain string comparison).

**Rules to pin down:**
- If the same `(ngram, department)` pair appears more than once, it counts as one suggestion with the **highest** of
  its scores. The same ngram in two departments is two independent suggestions.
- Fewer than `k` valid suggestions: return all of them. `k == 0`, an unknown department, or no prefix match: `[]`.
- The list is never modified after construction.

### Example
```
t = Typeahead([
    ["sales deck", 1, 50], ["salesforce", 1, 90], ["salary bands", 2, 70],
    ["sales kickoff", 1, 50], ["security", 1, 99], ["salesforce", 2, 10],
])
t.top("sal", 1, 2)    -> ["salesforce", "sales deck"]     # 90, then 50 (ties: "sales deck" < "sales kickoff")
t.top("sal", 1, 10)   -> ["salesforce", "sales deck", "sales kickoff"]
t.top("sal", 2, 10)   -> ["salary bands", "salesforce"]
t.top("", 1, 1)       -> ["security"]
t.top("sal", 3, 5)    -> []                                # unknown department
```

### Part 1: correct baseline
Get the filtering, ordering, duplicate and empty-case rules right. A scan over every suggestion per query is fine
here.

### Part 2: fast queries, small memory
The suggestion list already takes about half the server's memory, and `top` is called constantly. Preprocess once
so each query avoids touching every match:
- Hidden Part 2 tests have up to `60,000` suggestions and `20,000` queries, many with short prefixes that match
  thousands of suggestions, and small `k`. A full scan or a sort of all matches per query will time out.
- Keep extra memory roughly **linear** in the number of suggestions (no "copy of the top-k list at every trie node"
  for every possible prefix).

*Hint:* within one department, the ngrams sharing a prefix form a **contiguous range** of the sorted ngram list.
How do you pull the best `k` out of a range without visiting all of it?

### Constraints
- `0 <= len(suggestions) <= 6 * 10^4`, ngrams are 1-30 lowercase letters / spaces, `0 <= score <= 10^9`
- `0 <= k <= 50`, up to `2 * 10^4` calls to `top`

### What the interviewer cares about
- Settling ties, duplicates and the empty query before coding, and a correct baseline first
- An index that resolves both filters without a scan (per-department sorted ngrams + binary search for the prefix
  range), then top-k from a range in about `O(k log n)` (range-max structure + heap)
- Memory accounting: store indexes into the list, not copies of strings
