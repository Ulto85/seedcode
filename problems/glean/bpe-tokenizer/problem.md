---
title: BPE Tokenizer
difficulty: Medium
source: Glean SWE tech phone screen / onsite, "Implement a BPE tokenizer" (reported 2026 on 1point3acres and PracHub; counting, tie and id rules are ours)
order: 3
minutes: 50
timeout: 10
tags: strings, hash map, simulation, heap
---
Build a tiny **byte-pair encoding** tokenizer, the thing that turns text into the integer ids a language model
reads. Training learns *merge rules* from a text; encoding applies them to new text; decoding turns ids back into
text.

```
BPETokenizer()
train(text: str, threshold: int) -> list[list[str]]
encode(text: str) -> list[int]
decode(ids: list[int]) -> str | None
```

### Part 1: train
Start with `text` split into single characters (every character, spaces included). Then repeat:
1. **Count pairs**: for every adjacent position, count the pair `(left_token, right_token)`. Overlapping occurrences
   all count: in `a a a` the pair `(a, a)` has count **2**.
2. **Pick** the pair with the highest count. Ties go to the smallest pair comparing `(left, right)` as a tuple of
   strings (so `("a", "b") < ("ab", "a") < ("b", "a")`).
3. If that count is **less than `threshold`**, stop.
4. **Merge** it: scan left to right and replace each occurrence of `left, right` with the single token
   `left + right`. Occurrences can't overlap: after merging at a position, scanning resumes after the new token.
   (`a a a` with rule `(a, a)` becomes `aa a`.)

Return the merge rules in the order they were learned, each as `[left, right]`. Calling `train` again replaces
any earlier training. `threshold >= 1`; an empty text learns nothing.

**Vocabulary ids.** The distinct characters of the training text get ids `0, 1, 2, ...` in sorted order. The
`r`-th merge rule (0-based) creates a new token with id `C + r`, where `C` is the number of distinct characters.
(Two different rules may spell the same string, e.g. `("a", "bc")` and `("ab", "c")`. They still get different ids.)

### Part 2: encode / decode
- `encode(text)`: split `text` into characters, then apply the merge rules **one at a time in training order**,
  each as a full left-to-right pass exactly like step 4. Return the ids of the final tokens. A character never seen
  in training becomes id `-1` and never merges with anything.
- `decode(ids)`: concatenate the strings of the ids. If **any** id is not in the vocabulary (including `-1`), return
  `None`. `decode([])` is `""`.
- `decode(encode(s)) == s` for any `s` made of training characters.

### Example
```
t = BPETokenizer()
t.train("abababa", 2)  -> [["a", "b"], ["ab", "ab"]]
```
- Characters `a, b` get ids `0, 1`. Counts: `(a,b)=3`, `(b,a)=3`; tie, and `("a","b") < ("b","a")`, so merge
  `(a, b)` -> `ab ab ab a`, id `2`.
- Counts: `(ab,ab)=2`, `(ab,a)=1`. Merge -> `abab ab a`, id `3`.
- Counts: `(abab,ab)=1`, `(ab,a)=1`. Best is 1 < 2: stop.
```
t.encode("ababab") -> [3, 2]          # "abab" + "ab"
t.encode("abc")    -> [2, -1]
t.decode([3, 0])   -> "ababa"
t.decode([4])      -> None
```

### Constraints
- `len(text) <= 2 * 10^4` for `train`, `len(text) <= 10^4` for `encode`
- Hidden tests train on long, repetitive text with a low threshold, which learns **hundreds to thousands** of
  merges. Recounting every pair from scratch after each merge is `O(merges * length)` and will time out; update
  the counts incrementally around each merge instead.

### What the interviewer cares about
- Settling the ambiguities (overlap counting, tie-break, id assignment, unknown input) and checking them against
  the example by hand
- Clean split between counting pairs, applying one merge, and the training loop
- Knowing the naive cost and how to make training fast: a linked list of tokens, a map from pair to its
  positions, and a max-heap of `(count, pair)` with lazy deletion
