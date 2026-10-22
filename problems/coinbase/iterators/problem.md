---
title: Range & Interleaving Iterators
difficulty: Medium
source: Coinbase SWE onsite / phone screen, "implement iterators from scratch" (reported 2022-2025, most recently Jul 2025)
order: 0
minutes: 50
tags: design, iterator, queue, laziness
---
Coinbase's best-known coding round: build iterators **from scratch** (no built-in generators or
`itertools`), then compose them. Every iterator here has the same two-method interface:

```
has_next() -> bool    # is there another element? never advances
next()     -> int | None   # return the next element and advance; None if exhausted (no exception)
```

### Part 1: RangeIterator
```
RangeIterator(start: int, end: int, step: int)
```
Yields `start, start + step, start + 2·step, …` while the value hasn't passed `end`. **`end` is inclusive.**
- `step > 0`: yield while value ≤ `end`. `step < 0`: yield while value ≥ `end`.
- `step == 0`, or `start` already past `end` in the step's direction: the iterator is **empty**.
- Ranges can be astronomically long (`RangeIterator(0, 10**15, 1)`): it must be **O(1) space**.

```
it = RangeIterator(0, 10, 4)
it.next() -> 0    it.next() -> 4    it.has_next() -> True    it.next() -> 8
it.has_next() -> False    it.next() -> None
```

### Part 2: InterleavingIterator
```
InterleavingIterator(sources: list)
```
Each source is either a **list of ints** (iterate it in order) or a dict `{"range": [start, end, step]}` (behaves
like a `RangeIterator`). Yield elements **round-robin**: one from source 0, one from source 1, …, then wrap
around. Exhausted sources (including ones that are empty from the start) are **skipped**, and the round-robin
continues among the rest.

```
sources = [[1, 2, 3], [], {"range": [10, 30, 10]}, [7]]
next() calls -> 1, 10, 7, 2, 20, 3, 30, None
```

Requirements: construction is O(number of sources), **don't copy ranges into lists**, and `next()` must be
**O(1)** amortized even when thousands of sources are exhausted (don't scan past dead sources every call).

### Follow-up: peek
Add `peek() -> int | None` to `InterleavingIterator`: return what `next()` would return, **without advancing**.
Calling `peek()` any number of times must not change the sequence. `None` when exhausted.

### Constraints
- Up to 5·10⁴ sources and 2·10⁵ calls. Values and range bounds fit in |x| ≤ 10¹⁵.

*Reconstructed from candidate reports: the interview asks you to define the interface yourself in a blank editor;
the concrete classes (range, interleave over a list of iterators, then peek/filter-style follow-ups) vary by interviewer.*
