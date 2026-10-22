---
title: Cosine Retrieval and Recall@k
difficulty: Medium
source: Harvey SWE onsite, notebook exercise "embedding retrieval with cosine similarity" + "retrieval and evaluation for a simple RAG (Recall@10, MRR@10)" (reported 2026). The reported round uses numpy and a provided embed(); this version uses plain integer vectors so it runs here.
order: 4
minutes: 40
tags: vectors, ranking, top-k, evaluation, rag
---
Before Harvey's assistant answers a question about a deal room, it **retrieves** the most relevant passages. The
passages have already been embedded. Build the retriever, then measure how good it is.

```
Retriever(docs: list[list[int]])
search(query: list[int], k: int) -> list[int]
evaluate(queries: list[list[int]], relevant: list[list[int]], k: int) -> dict
```

Embeddings are given as **integer vectors** (think quantized embeddings). All vectors, docs and queries, have the
same dimension `d >= 1`. Document `i` is `docs[i]`.

**Cosine similarity** of `a` and `b` is `dot(a, b) / (|a| * |b|)`, where `|a|` is the Euclidean norm. If either
vector is all zeros, the similarity is defined as `0`.

### Part 1: search
Return the indices of the `k` documents most similar to `query`, best first.
- Sort by similarity **descending**; ties go to the **lower document index**. Treat two similarities as tied if they
  differ by less than `1e-9` (the tests never have two genuinely different similarities that close where it
  would change the answer), e.g.
  `[1, 2]` and `[2, 4]` always tie.
- Return `min(k, len(docs))` indices; `k = 0` or an empty corpus returns `[]`.
- Negative similarities are still ranked (they just come last).
- Precompute whatever you can per document in the constructor; `search` is called many times.

```
r = Retriever([[1, 0], [0, 1], [1, 1], [2, 2], [0, 0], [-1, 0]])
r.search([3, 1], 4)
  similarities: doc0 0.949, doc1 0.316, doc2 0.894, doc3 0.894, doc4 0, doc5 -0.949
  -> [0, 2, 3, 1]          # docs 2 and 3 tie, lower index first
r.search([0, 0], 3)  -> [0, 1, 2]        # everything is 0, so index order
```

### Follow-up: evaluate
`queries[j]` comes with `relevant[j]`, the list of document indices (distinct) a lawyer marked as relevant.
For each query, run `search(queries[j], k)` and compute:
- **Recall@k** = (number of relevant docs in the top `k`) / (number of relevant docs)
- **Reciprocal rank@k** = `1 / p` where `p` is the 1-based position of the first relevant doc in the top `k`,
  or `0` if none appears

Return `{"recall": mean Recall@k, "mrr": mean reciprocal rank@k}`, averaging over the queries whose `relevant` list
is **non-empty** (skip the others). If no query counts, return `{"recall": 0.0, "mrr": 0.0}`. Floats are checked
to `1e-6`.
```
r.evaluate([[3, 1], [0, 5], [1, 1]], [[2, 1], [1], []], 2)
  q0: top-2 [0, 2]   relevant {2, 1}: recall 1/2, first hit at position 2 -> 1/2
  q1: top-2 [1, 2]   relevant {1}:    recall 1,   first hit at position 1 -> 1
  q2: skipped (no relevant docs)
  -> {"recall": 0.75, "mrr": 0.75}
```

### Constraints
- `0 <= len(docs) <= 2 * 10^4`, `1 <= d <= 64`, entries in `[-100, 100]`
- Up to `200` queries per test; `0 <= k <= 50`

### What the interviewer cares about
- Normalising documents once (or caching their norms), not per query
- A deterministic tie-break, and a clear answer for zero vectors, `k` larger than the corpus, and empty inputs
- Picking the top `k` with a heap (`O(n log k)`) instead of sorting everything; knowing what Recall@k and MRR
  actually measure (in the real round they also ask how this changes at 50M documents: approximate nearest
  neighbour indexes)
