---
title: KV Store Load Monitor
difficulty: Easy
source: Databricks SWE technical phone screen, "KV store that measures GET/PUT load" (reported 2024–2026)
order: 0
minutes: 40
tags: design, sliding window, binary search
---
Build an in-memory key-value store that also reports how busy it is. Every call carries the current time in whole
seconds. **Timestamps never decrease** across calls (several calls can share the same second).

### Part 1
```
KVStore()
put(key: str, value: str, timestamp: int) -> None
get(key: str, timestamp: int) -> str | None     # latest value for key, or None if it was never put
measure_put_load(timestamp: int) -> float
measure_get_load(timestamp: int) -> float
```
`measure_put_load(t)` returns the average number of `put` calls **per second over the last 300 seconds**: the number
of `put` calls with timestamp in `(t - 300, t]` (i.e. `t - 299 … t`), divided by `300`. Same for `get`.

- Every `put` and `get` counts, including a `get` for a missing key and a `put` that overwrites a key.
- The `measure_*` calls themselves don't count as load.
- Always divide by 300, even if the store has been running for less than 300 seconds.

### Follow-up: arbitrary windows
```
average_qps(op: str, timestamp: int, window: int) -> float    # op is "put" or "get"
```
Number of `op` calls with timestamp in `(timestamp - window, timestamp]`, divided by `window` (`window ≥ 1`, can be
far larger than 300). Must be fast even with lots of history: an O(history) scan per query is too slow.

### Example
```
put("a", "1", 1)
put("b", "2", 1)
get("a", 2)              -> "1"
get("z", 5)              -> None
measure_put_load(5)      -> 0.006667   # 2 puts / 300
measure_get_load(300)    -> 0.006667   # gets at t=2 and t=5 are inside (0, 300]
measure_get_load(302)    -> 0.003333   # window is (2, 302]: only t=5 left
average_qps("put", 302, 1000) -> 0.002  # 2 puts / 1000
```

### What the interviewer cares about
- Part 1 with bounded memory: a deque of timestamps, or better a ring buffer of 300 one-second buckets
  (each bucket remembers which second it holds, so stale counts aren't reused).
- Discussion: thread safety, many calls in the same second, why the follow-up needs to keep history
  (sorted timestamps + binary search, or prefix sums per second).

### Constraints
- Up to 2·10⁵ calls, 0 ≤ timestamp ≤ 10⁹. Answers are checked with 1e-6 tolerance.
- The follow-up is reconstructed from a reported variant that asks for QPS over a per-query window.
