---
title: Replayable Shuffle
difficulty: Medium
source: Based on Modal's reported "Prove an Incremental Shuffle Is Uniform" (forward Fisher-Yates; title and preview listed on PracHub, 2026). The reported question is a proof; this coding version (replay, then invert) is our reconstruction, not the reported prompt.
order: 2
minutes: 40
tags: fisher-yates, permutations, hash map, randomness
---
A load-testing tool shuffles the order in which it fires requests at containers. To make bugs reproducible it
doesn't call a random generator inside the shuffle. Instead it records the **draws** up front, so any run can be
replayed exactly.

The shuffle is the **forward Fisher-Yates** shuffle. For a list of length `n`:
```
for i in 0 .. n-2:
    j = i + draws[i]          # draws[i] is in [0, n-1-i]
    swap items[i] and items[j]
```
Step `i` picks which of the `n - i` not-yet-fixed elements lands at position `i`. There are
`n * (n-1) * ... * 2 = n!` possible draw sequences.

### Part 1: replay
```
shuffle(items: list, draws: list[int]) -> list | None
```
Return the shuffled list. `items` may contain duplicates. Return `None` (and don't shuffle) if the draws are invalid:
- `len(draws)` must be exactly `n - 1` (or `0` when `n` is `0` or `1`), and
- every `draws[i]` must satisfy `0 <= draws[i] <= n - 1 - i`.

```
shuffle(["a", "b", "c", "d"], [2, 0, 1])
  i=0: swap 0,2 -> [c, b, a, d]
  i=1: swap 1,1 -> [c, b, a, d]
  i=2: swap 2,3 -> [c, b, d, a]
-> ["c", "b", "d", "a"]

shuffle(["a", "b"], [2])      -> None   # draws[0] must be 0 or 1
shuffle(["a", "b", "c"], [0]) -> None   # need exactly 2 draws
shuffle([], [])               -> []
```

### Follow-up: invert it
The interviewer asks why this shuffle is **uniform**: if each `draws[i]` is uniform on its range, every
permutation of `n` distinct items comes out with probability exactly `1/n!`. The cleanest argument is that
the map from draw sequences to permutations is a **bijection**: there are `n!` of each, and every permutation is
produced by exactly one draw sequence. Prove it constructively: write the inverse.
```
recover_draws(items: list, shuffled: list) -> list[int] | None
```
`items` are **distinct**. Return the unique `draws` such that `shuffle(items, draws) == shuffled`. Return `None` if
`shuffled` is not a permutation of `items` (different length, a missing or extra element, or a repeat).

```
recover_draws(["a", "b", "c", "d"], ["c", "b", "d", "a"]) -> [2, 0, 1]
recover_draws(["a", "b", "c"], ["a", "b", "c"])           -> [0, 0]
recover_draws(["a", "b"], ["a", "a"])                      -> None
```

### Constraints
- `0 <= n <= 2 * 10^5`; items are strings or integers
- Your solution should be `O(n)`: the hidden tests include lists large enough that an `O(n^2)` inverse
  (searching for each element with `list.index`) times out.

### What the interviewer cares about
- Getting the ranges exactly right (`draws[i]` can be `0`, i.e. "keep it in place"; the last element needs no draw)
- Explaining the uniformity argument: `n` choices, then `n-1`, ..., each sequence equally likely, and the
  inverse shows distinct sequences give distinct permutations
- Keeping a value -> position map up to date through the swaps so the inverse is linear
