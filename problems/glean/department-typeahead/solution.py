import heapq
from bisect import bisect_left


class _Dept:
    """Ngrams of one department sorted ascending, plus an iterative max segment tree over their positions.
    Each leaf holds key = score * BIG - position, so a larger key means higher score, then smaller ngram."""

    def __init__(self, items):
        items.sort()
        self.ngrams = [g for g, _ in items]
        n = self.n = len(items)
        big = n + 1
        self.tree = [-1] * (2 * n)
        for i, (_, s) in enumerate(items):
            self.tree[n + i] = s * big + (n - i)      # (n - i) > 0 keeps keys distinct
        for i in range(n - 1, 0, -1):
            self.tree[i] = max(self.tree[2 * i], self.tree[2 * i + 1])
        self.big = big

    def range_max(self, lo, hi):
        """Max key over positions [lo, hi). Returns -1 for an empty range."""
        best, n, tree = -1, self.n, self.tree
        lo += n
        hi += n
        while lo < hi:
            if lo & 1:
                best = max(best, tree[lo]); lo += 1
            if hi & 1:
                hi -= 1; best = max(best, tree[hi])
            lo >>= 1; hi >>= 1
        return best

    def pos(self, key):
        return self.n - key % self.big


class Typeahead:
    """Preprocess O(N log N), extra memory O(N).
    top(): O(log N) binary search for the prefix range, then O(k log N) to pull the best k with a heap of
    sub-ranges (pop the best range, emit its max, split around it)."""

    def __init__(self, suggestions):
        best = {}
        for g, d, s in suggestions:
            if s > best.get((d, g), -1):
                best[(d, g)] = s
        groups = {}
        for (d, g), s in best.items():
            groups.setdefault(d, []).append((g, s))
        self.depts = {d: _Dept(items) for d, items in groups.items()}

    def top(self, query, dept, k):
        D = self.depts.get(dept)
        if D is None or k <= 0:
            return []
        lo = bisect_left(D.ngrams, query)
        hi = bisect_left(D.ngrams, query + "￿") if query else D.n
        out, heap = [], []

        def push(a, b):
            if a < b:
                heapq.heappush(heap, (-D.range_max(a, b), a, b))

        push(lo, hi)
        while heap and len(out) < k:
            negkey, a, b = heapq.heappop(heap)
            p = D.pos(-negkey)
            out.append(D.ngrams[p])
            push(a, p)
            push(p + 1, b)
        return out
