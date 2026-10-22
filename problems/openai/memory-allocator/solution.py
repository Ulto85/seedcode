from collections import defaultdict


class Allocator:
    """Segment tree over the n units. Each node keeps, for its range:
    pre = free run touching the left edge, suf = free run touching the right edge, best = longest free run,
    plus a lazy 'set all free / set all used' tag.
    malloc: O(log n) (descend for the leftmost fit, then one range assign).
    free:   O(k log n) for an owner with k blocks.  Space O(n)."""

    def __init__(self, n):
        self.n = n
        size = 1
        while size < n:
            size *= 2
        self.size = size
        self.pre = [0] * (2 * size)
        self.suf = [0] * (2 * size)
        self.best = [0] * (2 * size)
        self.lazy = [None] * (2 * size)    # None | 0 (free) | 1 (used)
        self._build(1, 0, size - 1)
        self.blocks = defaultdict(list)    # owner -> [(start, size)]

    def _set(self, node, lo, hi, used):
        length = 0 if used else min(hi, self.n - 1) - lo + 1
        length = max(length, 0)
        self.pre[node] = self.suf[node] = self.best[node] = length
        self.lazy[node] = used

    def _build(self, node, lo, hi):
        if lo == hi:
            self._set(node, lo, hi, 0 if lo < self.n else 1)
            self.lazy[node] = None
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid)
        self._build(2 * node + 1, mid + 1, hi)
        self._pull(node, lo, hi)

    def _pull(self, node, lo, hi):
        L, R = 2 * node, 2 * node + 1
        mid = (lo + hi) // 2
        llen, rlen = mid - lo + 1, hi - mid
        self.pre[node] = self.pre[L] + (self.pre[R] if self.pre[L] == llen else 0)
        self.suf[node] = self.suf[R] + (self.suf[L] if self.suf[R] == rlen else 0)
        self.best[node] = max(self.best[L], self.best[R], self.suf[L] + self.pre[R])

    def _push(self, node, lo, hi):
        if self.lazy[node] is not None:
            mid = (lo + hi) // 2
            self._set(2 * node, lo, mid, self.lazy[node])
            self._set(2 * node + 1, mid + 1, hi, self.lazy[node])
            self.lazy[node] = None

    def _assign(self, node, lo, hi, a, b, used):
        if b < lo or hi < a:
            return
        if a <= lo and hi <= b:
            self._set(node, lo, hi, used)
            return
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        self._assign(2 * node, lo, mid, a, b, used)
        self._assign(2 * node + 1, mid + 1, hi, a, b, used)
        self._pull(node, lo, hi)

    def _find(self, k):
        """Leftmost start of a free run of length >= k (caller checks best[1] >= k)."""
        node, lo, hi = 1, 0, self.size - 1
        while lo < hi:
            self._push(node, lo, hi)
            mid = (lo + hi) // 2
            L, R = 2 * node, 2 * node + 1
            if self.best[L] >= k:
                node, hi = L, mid
            elif self.suf[L] + self.pre[R] >= k:
                return mid - self.suf[L] + 1
            else:
                node, lo = R, mid + 1
        return lo

    def malloc(self, owner, size):
        if size > self.best[1]:
            return -1
        start = self._find(size)
        self._assign(1, 0, self.size - 1, start, start + size - 1, 1)
        self.blocks[owner].append((start, size))
        return start

    def free(self, owner):
        total = 0
        for start, size in self.blocks.pop(owner, []):
            self._assign(1, 0, self.size - 1, start, start + size - 1, 0)
            total += size
        return total
