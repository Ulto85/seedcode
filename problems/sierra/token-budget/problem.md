---
title: Fetch All Pages, Then Compact to a Token Budget
difficulty: Medium
source: Sierra SWE technical screen, "Fetch every page from a data API, then compact records to a token budget" (reported on PracHub, 2026; retry, cycle and tie rules are ours)
order: 1
minutes: 60
tags: pagination, retries, sliding window, two pointers
---
An AI agent pulls a customer's records (orders, tickets, past messages) from a paginated API and then has to fit
them into a model's context window. Build both halves.

### Part 1: fetch every page
You're given a JSON description of an API. The `MockAPI` class in the starter wraps it (don't edit it); create one
with `api = MockAPI(api_spec)` and call `api.fetch(cursor)`.

```
fetch_all(api_spec) -> {"records": [...], "status": str, "calls": int}
api.fetch(cursor) -> (records, next_cursor)        # may raise TransientError
```

- Start with `cursor = None`. Each successful call returns a batch of records (dicts with at least an `"id"`) and
  the cursor of the next page (a non-empty string, or `None`).
- **Transient failures:** a call can raise `TransientError`. Retry the **same** cursor, up to `MAX_RETRIES = 3`
  retries (so at most 4 attempts per page). If all 4 attempts fail, stop with status `"failed"` and return
  what you've collected so far.
- **End of data:** stop with status `"complete"` when a batch is **empty** (even if it carries a next cursor), or
  after processing a batch whose next cursor is `None`.
- **Cursor loops:** if the next cursor is one you've already fetched, stop with status `"cycle"` (the current
  batch's records are still kept).
- **No duplicates:** keep records in the order received, but skip any record whose `"id"` was already collected.
- `"calls"` is the total number of `fetch` calls made, failed ones included (`api.calls`).

### Part 2: compact to a token budget
Every record has a non-negative integer `"tokens"`.

```
compact(records, trigger, target) -> list
```
- If the total tokens is **`<= trigger`**, return `records` unchanged.
- Otherwise return the **longest contiguous run** of records (original order) whose total is **`<= target`**.
  Ties go to the run that starts **earliest**. If no single record fits, return `[]`. Empty input returns `[]`.

### Follow-up: keep the most tokens
`compact(records, trigger, target, mode="tokens")`: same rules, but pick the contiguous run with the **largest
total tokens** that is `<= target`. Ties: more records wins, then the earliest start. (`mode` defaults to `"count"`.)

### Example
```
tokens:  [4000, 3000, 5000, 2000, 1000, 6000, 3000]      total 24000 > trigger 20000
compact(records, 20000, 10000)
  no run of 4 fits; runs of 3 that fit: idx 1-3 (10000), 2-4 (8000), 3-5 (9000), 4-6 (10000)
  -> earliest: records[1:4]  (tokens 3000, 5000, 2000)
compact(records, 20000, 10000, mode="tokens")
  best total is 10000: idx 1-3 and 4-6 tie on total and length -> records[1:4]
compact(records, 30000, 10000)  -> all 7 records, unchanged (24000 <= 30000)
```
```
api_spec = {"pages": {"":   {"records": [{"id": "a"}, {"id": "b"}], "next": "p2"},
                      "p2": {"records": [{"id": "b"}, {"id": "c"}], "next": "p3"},
                      "p3": {"records": [], "next": None}},
            "failures": {"p2": 2}}
fetch_all(api_spec) -> {"records": [{"id": "a"}, {"id": "b"}, {"id": "c"}], "status": "complete", "calls": 5}
#   "" ok, p2 fails twice then ok, p3 empty -> done
```
In `api_spec`, the first page is keyed `""` (that's what `cursor=None` maps to), `failures[cursor]` is how many
times that cursor fails before it works, and a cursor with no entry in `pages` returns an empty batch.

### Constraints
- Up to `2 * 10^5` records and `5 * 10^4` pages; `0 <= tokens <= 10^4`; `1 <= target <= trigger`.

### What the interviewer cares about
- A loop that always terminates: empty pages, repeated cursors, and retries that give up
- Not losing or duplicating records when a call fails mid-way
- A linear sliding window for compaction (tokens are non-negative), not checking every pair of endpoints
- Why there are two thresholds (compact well below the trigger so you don't re-compact on every new record)
