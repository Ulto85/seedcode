---
title: Time-Versioned KV Store with Restore
difficulty: Medium
source: Perplexity SWE online assessment, "time-versioned KV store with restore" (reported 2026). Method names and the exact change-point and tie rules are reconstructed.
order: 2
minutes: 45
tags: design, binary search, stack, versioning
---
An answer engine caches facts it has looked up, and every fact changes over time. You need a key-value store that
remembers **every version** of every key, can answer "what was the value at time `t`?", and can roll the whole
store back to an earlier moment.

```
VersionedKV()
set(key, value, ts) -> None
delete(key, ts) -> None
get(key, ts) -> value | None
get_range(key, start, end) -> list[[ts, value | None]]     # Part 2
restore(ts) -> None                                         # Follow-up
```

Keys are strings. Values are strings or integers (never `None`). Only `set` and `delete` are **mutations**;
`get` and `get_range` never change anything.

**Timestamps.** Each mutation's `ts` is `>=` the `ts` of every mutation currently stored. Several mutations can
share a timestamp; among those, the one that came **later in the call order wins**. Query timestamps can be
anything (before, between or after the mutations).

### Part 1
- `set(key, value, ts)`: from time `ts` on, `key` holds `value`.
- `delete(key, ts)`: from time `ts` on, `key` doesn't exist. Deleting a key that doesn't exist is allowed.
- `get(key, ts)`: the value of `key` at time `ts`, i.e. the result of the last mutation of `key` with timestamp
  `<= ts`. Returns `None` if there is no such mutation or it was a delete.

### Part 2: history
`get_range(key, start, end)` returns the **visible history** of `key` over `[start, end]` as change points:
1. If `key` exists at time `start`, the first entry is `[start, get(key, start)]`.
2. Then, for each timestamp `t` with `start < t <= end` at which the value visible at `t` is **different** from the
   value just before `t`, append `[t, value at t]`. A deletion shows up as `[t, None]`.

So rewriting a key with the same value, deleting a missing key, or a set-then-delete at the same timestamp
(when the key didn't exist before) are **not** changes. If `start > end`, return `[]`.

### Follow-up: restore
`restore(ts)` rolls the whole store back to its state after exactly the mutations with timestamp `<= ts`. Every
mutation with a larger timestamp is **discarded forever**. Later mutations may then use any timestamp `>=` the
mutations still stored (even one smaller than a discarded one). If nothing is newer than `ts`, it's a no-op.

### Example
```
set("a", "x", 1)
set("a", "y", 4)
get("a", 3)             -> "x"
get("a", 0)             -> None
get_range("a", 1, 5)    -> [[1, "x"], [4, "y"]]
get_range("a", 2, 3)    -> [[2, "x"]]
delete("a", 6)
get("a", 6)             -> None
set("b", 20, 6)
get_range("a", 0, 10)   -> [[1, "x"], [4, "y"], [6, None]]
restore(4)              # discards delete("a", 6) and set("b", 20, 6)
get("a", 100)           -> "y"
get("b", 100)           -> None
set("a", "z", 5)        # 5 >= 4 (the newest kept mutation), so it's allowed
get_range("a", 3, 9)    -> [[3, "x"], [4, "y"], [5, "z"]]
```

### Constraints
- Up to `2 * 10^5` calls; timestamps are integers in `[0, 10^9]`.
- A single key can have tens of thousands of versions, so a linear scan per `get` is too slow.

### What the interviewer cares about
- A per-key, timestamp-sorted history with binary search, not a scan or a full snapshot per version
- Getting ties right (the last write at a timestamp wins) and stating your assumptions before coding
- `restore` without rebuilding the store: a global stack of mutations you can pop
