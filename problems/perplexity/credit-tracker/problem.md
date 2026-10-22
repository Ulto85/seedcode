---
title: Credit Tracker with Expirations
difficulty: Hard
source: Perplexity SWE technical screen, "CreditTracker with expirations" (reported 2025). The rules follow the report; the function signature and Follow-up framing are this site's.
order: 4
minutes: 60
tags: heap, segment tree, Fenwick tree, coordinate compression
---
Perplexity gives users credits (promos, API credits, Pro query credits) that are each valid only during a window
of time. Write a tracker that processes a log of operations and answers balance checks.

```
track_credits(operations: list[list]) -> list[int]
```
Each operation is one of:
```
["add", start, end, credit]    # a grant of `credit`, live at every time t with start <= t <= end (inclusive)
["subtract", time, credit]     # spend `credit` at `time`
["check", time]                # how much credit is live at `time`?
```
Return the result of every `check`, in order.

### Rules
- Operations are applied **in the order given**, but their times can go **backwards**: an operation sees the
  effect of every earlier operation in the list, whatever their times. (This is not a replay in time order: a
  later `add` with an early start never changes what an earlier `subtract` did.)
- `subtract(time, credit)` takes from the grants **live at `time`** that still have credit, in order of the
  **earliest `end`** first. Ties on `end` go to the grant that was **added first**.
- If the live grants don't have `credit` in total, take everything they have and drop the rest (no debt, no
  error).
- `check(time)` returns the total credit remaining in grants live at `time` (`0` if none).

### Example
```
["add", 0, 10, 30]       # A
["add", 5, 8, 20]        # B
["subtract", 6, 25]      # live: A, B. B ends first: take 20 from B, then 5 from A
["check", 6]   -> 25
["check", 3]   -> 25     # only A is live at 3
["check", 9]   -> 25     # B is not live at 9 (and is empty anyway)
["add", 0, 8, 10]        # C
["subtract", 2, 30]      # live at 2: A (25) and C (10); B starts at 5. C ends first: 10 from C, 20 from A
["check", 2]   -> 5
["check", 6]   -> 5
["check", 11]  -> 0      # every grant has ended
["subtract", 4, 50]      # only 5 is live at 4: take it, drop the other 45
["check", 4]   -> 0
```
Output: `[25, 25, 25, 5, 5, 0, 0]`.

### Part 1
Get the rules right. Tests are small: scanning every grant on each operation is fine.

### Follow-up: make it fast
Up to `2 * 10^5` operations with long, heavily overlapping windows. Scanning and sorting the live grants on every
`subtract` is quadratic and will time out. Hint: you see all the operations up front.

### Constraints
- `0 <= start <= end <= 10^9`, `0 <= time <= 10^9`, `1 <= credit <= 10^9`

### What the interviewer cares about
- Pinning down the semantics first: inclusive windows, partial subtraction, tie-breaking, and what "times go
  backwards" means
- A correct brute force quickly, then a real data-structure answer: compress the times, keep balances in a
  Fenwick tree (range add, point query), and find the earliest-ending live grant with a segment tree of heaps
- Stating the time and space complexity of each version
