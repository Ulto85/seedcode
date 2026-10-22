---
title: Greedy Longest-Match Tokenizer
difficulty: Easy
source: Anthropic SWE phone screen, tokenizer implement / debug (reported 2025-2026)
order: 4
minutes: 40
timeout: 10
tags: strings, trie, greedy
---
Before a model sees text, a tokenizer turns it into integer ids. Implement the simplest real one: **greedy
longest match** against a fixed vocabulary.

```
tokenize(text: str, vocab: dict[str, int], unk_id: int) -> list[int]
```

Scan `text` left to right. At position `i`:
- Find the **longest** vocabulary string that `text` continues with at `i`. Emit its id and move past it.
- If no vocabulary string matches at `i`, emit `unk_id` and move forward **one character**.

Matching is exact and case-sensitive. The greedy choice is **never revised**, even if a different split would have
produced fewer tokens or fewer unknowns. Empty text returns `[]`. Vocab keys are non-empty and `unk_id` is not a
vocab id.

### Example
```
vocab = {"a": 1, "ab": 2, "abc": 3, "b": 4, "cd": 5},  unk_id = 0
tokenize("abcdxabzzb", vocab, 0)
  "abc" -> 3   ("abcd" isn't in vocab, "abc" is the longest match)
  "d"   -> 0   (nothing starts with "dx" or "d")
  "x"   -> 0
  "ab"  -> 2
  "z", "z" -> 0, 0
  "b"   -> 4
-> [3, 0, 0, 2, 0, 0, 4]
```
Greedy is not optimal: with `{"ab": 1, "abc": 2, "cd": 3}`, `"abcd"` gives `[2, unk]`, not `[1, 3]`.

### Follow-up: keep the text, merge unknown runs
Downstream code needs to detokenize losslessly, and a run of garbage shouldn't become hundreds of `unk` tokens.
```
tokenize_spans(text: str, vocab: dict[str, int], unk_id: int) -> list[[int, str]]
```
Same greedy algorithm, but return `[id, piece]` pairs, where `piece` is the exact text consumed, and merge
**consecutive** unknown characters into a single `[unk_id, run]` pair. Joining every `piece` must give back `text`.
```
tokenize_spans("abcdxabzzb", vocab, 0)
-> [[3, "abc"], [0, "dx"], [2, "ab"], [0, "zz"], [4, "b"]]
```

### Performance
`len(text)` can be 2·10⁵ and the vocab can have thousands of entries of length up to ~16. Trying every vocab entry
at every position is too slow. Bound the work per position by the **longest vocab key** (check candidate lengths
longest-first in a hash set) or walk a **trie**.

*The tokenize/detokenize interview often starts as a code review of a buggy version (missing chars crash it, the
buffer isn't reset after emitting, a literal "UNK" in the text collides with the unknown marker). This is the
implement-it-yourself version, with rules spelled out by this site.*
