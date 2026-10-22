---
title: Sort a Hundred Million Digits
difficulty: Easy
source: Modal SWE interview, "Sort One Hundred Million Digits" (title and preview listed on PracHub, 2026). Part 1 follows the reported prompt; the follow-up is our extension in the same spirit, not a reported question.
order: 1
minutes: 30
tags: counting sort, prefix sums, binary search
---
A log pipeline hands you a huge string made only of the characters `'0'` to `'9'`. Think about **one hundred
million** of them. Sort them.

A comparison sort would work, but it costs `O(n log n)` time and a full copy of the data. Every key is one of
only ten values, so you can do much better.

### Part 1
```
sort_digits(digits: str) -> str
```
Return the digits of `digits` in non-decreasing order, as a string. The empty string returns `""`.

```
sort_digits("3141592653")  -> "1123345569"
sort_digits("000")         -> "000"
sort_digits("")            -> ""
```
Aim for `O(n)` time and `O(1)` extra space besides the output: count each digit, then rebuild the string.

### Follow-up: don't build the sorted string
The digits now arrive as a list of **chunks** (strings of digits, some possibly empty), totalling up to `10^8`
characters. Nobody wants the whole sorted string. They want to know which digit sits at certain positions of it.

```
sorted_digit_at(chunks: list[str], positions: list[int]) -> list[int]
```
For each `p` in `positions`, return the digit (as an `int`) at 0-indexed position `p` of the sorted
concatenation of all chunks. If `p < 0` or `p >= total length`, return `-1` for that position. Answers come back
in the same order as `positions`, which are in no particular order and may repeat.

```
chunks    = ["3141", "", "5926"]       # sorted: "11234569"
positions = [0, 2, 7, 8, -1, 3]
-> [1, 2, 9, -1, -1, 3]
```
Positions `0..1` hold `1`, position `2` holds `2`, position `7` holds `9`. Position `8` is past the end.

### Constraints
- Part 1: `0 <= len(digits) <= 10^8` (tests use up to a few million)
- Follow-up: up to `10^5` chunks and `10^5` positions; `-10^9 <= p <= 10^9`

### What the interviewer cares about
- Spotting that ten counters replace the sort: `O(n)` time, constant extra space
- Rebuilding the output from the counts (and noticing you don't have to, if you only need lookups)
- In the follow-up: prefix sums over the ten counts, then each lookup is `O(1)` / `O(log 10)`. Re-scanning the
  data per query is far too slow
