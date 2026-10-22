---
title: Code Search Index
difficulty: Medium
source: Loosely based on a Windsurf (now part of Cognition) 2025 Glassdoor report of a 45-minute "building a search engine" round. The exact question wasn't published, so this spec is reconstructed.
order: 2
minutes: 45
tags: design, inverted index, strings, tokenization
---
A coding agent (or an IDE) needs to find the files relevant to a query like `"parse json"` fast. Build an in-memory
code search index.

> A 2025 Glassdoor review of Windsurf (Codeium, acquired by Cognition in 2025) describes a 45-minute round on
> "building a search engine". The details weren't shared. This version is reconstructed for a code base.

```
CodeSearch()
add_file(path: str, content: str) -> None
search(query: str, k: int) -> list[str]
remove_file(path: str) -> bool         # Follow-up
```

### Tokenization (used for both files and queries)
1. Split the text into **words**: maximal runs of ASCII letters and digits. Everything else is a separator,
   **including `_`**.
2. Split each word into **sub-tokens** at case and digit boundaries, using this regex:
   `[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+`. Read left to right, each sub-token is one of:
   - a run of capitals **not** followed by a lowercase letter (`HTTP` in `HTTPServer`)
   - an optional capital followed by lowercase letters (`Server`, `get`)
   - a run of digits
3. Lowercase every sub-token.

```
"getUserID2"        -> get, user, id, 2
"HTTPServer"        -> http, server
"parse_json(raw)"   -> parse, json, raw
"MAX_RETRIES = 10"  -> max, retries, 10
```

### Part 1
- `add_file(path, content)`: index a new file. In Part 1, every `path` is new.
- `search(query, k)`: tokenize the query and drop duplicate terms.
  - A file **matches** only if it contains **every** query term.
  - Its **score** is the total number of occurrences of the query terms in the file. Each distinct term counts
    once in the sum.
  - Return the paths of the top `k` matches, by score descending. Break ties by path ascending (plain string
    comparison).
  - Return `[]` if the query has no tokens, if nothing matches, or if `k <= 0`. Return fewer than `k` paths if
    fewer match.

### Example
```
add_file("src/json_util.py", "def parseJSON(raw):\n    return json.loads(raw)")
add_file("src/http.py",      "class HTTPServer:\n    def parse_request(self, raw): return raw")
add_file("README.md",        "Parse JSON quickly. JSON json JSON!")
search("parse json", 5)   -> ["README.md", "src/json_util.py"]
    # README: parse 1 + json 4 = 5.   json_util: parse 1 + json 2 = 3.   http.py has no "json".
search("raw", 1)          -> ["src/http.py"]    # both .py files score 2; the tie goes to "src/http.py"
search("__", 3)           -> []                 # no tokens
```

### Follow-up: files change
Files are edited and deleted while the agent works.
- `add_file` on an **existing** path **replaces** that file's content. Its old tokens must no longer match.
- `remove_file(path)` removes the file and returns `True`. It returns `False` if the path isn't indexed.
- Searches must stay fast. The hidden tests run thousands of searches over thousands of files, so re-scanning every
  file on every query will time out.

### Constraints
- Up to `5000` files, each up to a few hundred tokens. Up to `2 * 10^4` total calls.
- Paths are non-empty strings and are not tokenized.

### What the interviewer cares about
- An **inverted index** (term → {path: count}), with the query intersected starting from the rarest term.
- Getting tokenization exactly right. It's a small parser, and code search lives or dies by it.
- Keeping the index consistent on update and delete: remove a file's old postings before adding new ones.
