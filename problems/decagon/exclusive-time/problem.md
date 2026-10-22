---
title: Exclusive CPU Time From Nested Logs
difficulty: Medium
source: Decagon coding round (same as LeetCode 636)
order: 6
minutes: 30
tags: stack, simulation
---
A single-threaded CPU runs functions with IDs `0` to `n-1`. Calls can nest (and recurse). Each log is
`"{id}:start:{t}"` (starts at the **beginning** of time `t`) or `"{id}:end:{t}"` (ends at the **end** of time `t`).

A function's **exclusive time** is the time it spent running, not counting time spent in functions it called.
Return a list where index `i` is the exclusive time of function `i`.

```
exclusive_time(n: int, logs: list[str]) -> list[int]
```

### Example
```
n = 2, logs = ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]
-> [3, 4]
```

### Constraints
- Logs are sorted by time and always valid (every start has a matching end).
- A function can call itself (recursion), and a function can call several children one after another.
