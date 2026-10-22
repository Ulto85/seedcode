---
title: Leftmost-Fit Memory Allocator
difficulty: Hard
source: OpenAI SWE onsite coding, "malloc/free over fixed memory, then make both logarithmic" (reported Sep–Oct 2026)
order: 3
minutes: 60
tags: design, intervals, segment tree
---
You manage a fixed block of memory with `n` units, addressed `0` to `n - 1`. All units start free. Programs
(identified by an integer `owner`) ask for runs of **consecutive** free units and later release everything they
hold.

```
Allocator(n: int)
malloc(owner: int, size: int) -> int
free(owner: int) -> int
```

- `malloc(owner, size)` finds the **leftmost** run of `size` consecutive free units, i.e. the smallest address `a`
  such that units `a .. a + size - 1` are all free, marks them as owned by `owner`, and returns `a`. If no such run
  exists (including `size > n`), it changes nothing and returns `-1`.
- `free(owner)` releases **every** unit currently held by `owner` (an owner can hold many separate blocks) and
  returns how many units were released. It returns `0` if the owner holds nothing. The owner id can be reused
  afterwards.
- Freed units merge with neighbouring free units: a run is "consecutive free units", no matter which `free` calls
  produced them.

### Example
```
a = Allocator(10)
a.malloc(1, 3)  -> 0     # [1 1 1 . . . . . . .]
a.malloc(2, 2)  -> 3     # [1 1 1 2 2 . . . . .]
a.malloc(1, 4)  -> 5     # [1 1 1 2 2 1 1 1 1 .]
a.free(2)       -> 2     # [1 1 1 . . 1 1 1 1 .]
a.malloc(3, 3)  -> -1    # free runs are 3..4 (2 units) and 9 (1 unit)
a.malloc(3, 2)  -> 3     # [1 1 1 3 3 1 1 1 1 .]
a.free(1)       -> 7     # both of owner 1's blocks: [. . . 3 3 . . . . .]
a.malloc(4, 6)  -> -1    # free runs are 0..2 and 5..9; 3 and 5 units aren't merged across owner 3's block
a.malloc(4, 5)  -> 5     # [. . . 3 3 4 4 4 4 4]
a.free(7)       -> 0     # owner 7 holds nothing
```

### Part 1
Make it correct. Keeping a sorted list of allocated blocks, or even scanning the memory array, is fine here.

### Follow-up: make both logarithmic
`n` and the number of calls are both up to `10^5`. Make `malloc` run in `O(log n)` and `free` in `O(k log n)` for
an owner holding `k` blocks. A linear scan per call is too slow for the hidden tests.

Hint, if you're stuck: a segment tree where each node stores the longest free run inside its range, plus the free
run touching its left edge and the one touching its right edge, can both answer "leftmost run of length `size`" by
walking down from the root and mark a range used/free with lazy propagation.

### Constraints
- `1 <= n <= 10^5`, `1 <= size <= 10^5`, `1 <= owner <= 10^9`
- Up to `10^5` calls

### What the interviewer cares about
- Precise semantics first: leftmost fit, all-or-nothing, free returns a count, multiple blocks per owner
- Tracking each owner's blocks so `free` never scans the whole memory
- Knowing *why* the naive version is O(n) per call and what structure fixes it
