---
title: Parallel Document Indexers
difficulty: Medium
source: Glean SWE technical screen / phone screen, "Parallel document indexing" (reported 2026 on PracHub and 1point3acres; exact rules follow the PracHub write-up)
order: 1
minutes: 45
tags: simulation, heap, scheduling, top-k
---
Glean's crawlers push documents into a pool of `m` **indexers** (numbered `0 .. m-1`). Each indexer handles one
document at a time. Simulate the pool and report how the load was spread.

There are `n` documents, numbered `0 .. n-1` in the order they arrive. Document `i` arrives at `queue_time[i]` and
keeps an indexer busy for `processing_time[i]`.

**Assignment rule.** Documents are handled strictly in index order. Document `i`:
1. tries indexer `i % m` first (always `i % m`, even if earlier documents were dropped);
2. if that one is busy, tries `i % m + 1`, `i % m + 2`, ... wrapping around from `m - 1` back to `0`, and takes the
   **first free** indexer it finds;
3. if all `m` indexers are busy, the document is **dropped** (not retried, not counted anywhere).

An indexer that starts a document at time `s` with processing time `p` is busy during `[s, s + p)`. It is **free
again at exactly `s + p`**, so a document arriving at `s + p` may take it.

`queue_time` is non-decreasing. Documents with the same arrival time are still handled one by one in index order.

### Part 1
```
indexer_stats(m: int, queue_time: list[int], processing_time: list[int]) -> list[int]
```
Return `[processed, busiest]`: the number of documents that were indexed (not dropped), and the indexer that
handled the most documents. Ties go to the **smallest** indexer id. If no documents were processed, `busiest` is `0`.

### Follow-up: top-k report
```
top_indexers(m: int, queue_time: list[int], processing_time: list[int], k: int) -> list
```
Rank all indexers by number of documents handled (descending), ties by id (ascending). Indexers that handled
nothing still take part. Take the top `k` and return `[ids, percentage]`:
- `ids`: those `k` indexer ids, sorted **ascending**;
- `percentage`: the share of **all `n` documents** (dropped ones included) handled by those `k` indexers, computed
  exactly as `round(100 * handled / n, 2)`. If `n == 0` it is `0.0`.

### Example
```
m = 3, queue_time = [1, 2, 3, 7], processing_time = [5, 4, 3, 2]

doc 0 at t=1 -> indexer 0 (busy [1, 6))
doc 1 at t=2 -> indexer 1 (busy [2, 6))
doc 2 at t=3 -> indexer 2 (busy [3, 6))
doc 3 at t=7 -> tries 3 % 3 = 0, which is free again -> indexer 0

counts = [2, 1, 1]
indexer_stats(...)        -> [4, 0]
top_indexers(..., k=2)    -> [[0, 1], 75.0]     # 3 of 4 documents
top_indexers(..., k=1)    -> [[0], 50.0]
```
A drop:
```
m = 3, queue_time = [0, 0, 0, 1, 2, 5], processing_time = [1, 9, 9, 4, 3, 2]
doc 3 at t=1 takes indexer 0 (free at 1). doc 4 at t=2: indexers 1, 2, 0 all busy -> dropped.
doc 5 at t=5: tries 2 (busy until 9), then 0 (free at exactly 5) -> indexer 0.
counts = [3, 1, 1]   ->   indexer_stats = [5, 0]
```

### Constraints
- `1 <= m <= 10^5`, `0 <= n <= 10^5`, `1 <= k <= m`
- `0 <= queue_time[i] <= 10^9` (non-decreasing), `1 <= processing_time[i] <= 10^9`

### What the interviewer cares about
- A correct simulation first, then a fast one: scanning all `m` indexers per document is `O(n * m)`. Aim for
  `O((n + m) log m)` with a min-heap of busy indexers keyed by free time plus an ordered set of free indexers
  supporting "first free id `>= i % m`, with wrap-around".
- The boundary rules: free at exactly `s + p`, drops are not retried, zero-count indexers are still ranked.
