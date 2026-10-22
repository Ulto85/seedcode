---
title: Synonyms From Shared Context
difficulty: Medium
source: Glean SWE onsite, "group words into transitive synonym sets by shared two-words-before-and-after context" (reported 2026 on PracHub)
order: 4
minutes: 40
tags: hashing, union-find, strings, nlp
---
Search gets better when it knows that "laptop" and "notebook" mean the same thing to your company. One cheap way to
mine synonyms from a corpus: words that show up in the **exact same surroundings** are probably interchangeable.

```
synonym_groups(sentences: list[str]) -> list[list[str]]
```

Each sentence is lowercase words separated by single spaces. For the word at position `i` of a sentence `w`
(0-based), its **context** is the 4-tuple `(w[i-2], w[i-1], w[i+1], w[i+2])`. Only words with **at least two
words on each side** have a context; the first two and last two words of a sentence have none. Contexts are
compared across all sentences.

- Two **different** words are synonyms if some occurrence of one and some occurrence of the other have the same
  context.
- Synonymy is **transitive**: if `a ~ b` and `b ~ c`, then `a, b, c` are one group (even if `a` and `c` never share
  a context).
- A word that appears in the same context as only itself (e.g. the same sentence twice) has no synonym from that.

Return every group with **at least two** words. Sort words within a group ascending, and groups by their first
word. No groups: `[]`.

### Example
```
sentences = [
    "i really like this movie a lot",
    "i really love this movie a lot",
    "we all love the new search",
    "we all enjoy the new search",
]
synonym_groups(sentences) -> [["enjoy", "like", "love"]]
```
`like` and `love` share the context `(i, really, this, movie)`; `love` and `enjoy` share `(we, all, the, new)`.
So all three join one group. `like` and `enjoy` never meet directly.
```
["p q red r s", "p q blue r s", "m n big o t", "m n large o t", "m n huge o u"]
  -> [["big", "large"], ["blue", "red"]]       # "huge" has a context nobody else has
["the cat sat"]   -> []                          # no word has two neighbours on each side
```

### Constraints
- `1 <= len(sentences) <= 10^4`, each sentence has 1-100 words, at most `2 * 10^5` words in total
- Words are 1-20 lowercase letters

### What the interviewer cares about
- Hashing each context once (a dict from context to the words seen there) instead of comparing occurrences pairwise
- Union-find (or BFS over a word graph) for the transitive closure
- Getting the output canonical: dedupe, sort inside groups, sort groups, drop singletons
- `O(W log W)` time for `W` total words
