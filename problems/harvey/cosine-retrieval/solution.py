"""Docs are normalised once in the constructor (O(n * d)). search is O(n * d + n log k) with a heap;
evaluate runs search per query. Similarities are rounded to 9 decimals so exact ties (e.g. [1,2] vs [2,4])
compare equal despite float noise; the lower index then wins."""
import heapq
import math


def _unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else None


class Retriever:
    def __init__(self, docs: list):
        self.units = [_unit(d) for d in docs]

    def search(self, query: list, k: int) -> list:
        if k <= 0 or not self.units:
            return []
        q = _unit(query)
        scored = []
        for i, u in enumerate(self.units):
            s = 0.0 if q is None or u is None else sum(a * b for a, b in zip(q, u))
            scored.append((-round(s, 9), i))
        return [i for _, i in heapq.nsmallest(k, scored)]

    def evaluate(self, queries: list, relevant: list, k: int) -> dict:
        recall = mrr = 0.0
        counted = 0
        for q, rel in zip(queries, relevant):
            if not rel:
                continue
            counted += 1
            rel = set(rel)
            top = self.search(q, k)
            recall += sum(1 for i in top if i in rel) / len(rel)
            for pos, i in enumerate(top, 1):
                if i in rel:
                    mrr += 1 / pos
                    break
        if not counted:
            return {"recall": 0.0, "mrr": 0.0}
        return {"recall": recall / counted, "mrr": mrr / counted}
