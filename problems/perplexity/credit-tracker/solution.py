import heapq
from bisect import bisect_left, bisect_right


def track_credits(operations: list) -> list:
    """Offline: compress the times that are ever queried (subtract/check), so a grant covers a
    contiguous range of query positions.

    - A Fenwick tree (range add, point query) holds the live credit at each position, so check is O(log m).
    - A segment tree whose nodes hold min-heaps of (end, add_index) finds, for a subtract at position p,
      the earliest-ending grant covering p by looking at the O(log m) nodes on p's root-to-leaf path.
      Exhausted grants are dropped lazily, so each grant is popped at most once per node it lives in.

    Time O(n log^2 n), space O(n log n).
    """
    qtimes = sorted({op[1] for op in operations if op[0] != "add"})
    m = len(qtimes)
    if m == 0:
        return []

    fen = [0] * (m + 1)

    def fen_add(i, v):              # add v at index i (0-based)
        i += 1
        while i <= m:
            fen[i] += v
            i += i & -i

    def range_add(lo, hi, v):        # add v to every position in [lo, hi]
        fen_add(lo, v)
        if hi + 1 < m:
            fen_add(hi + 1, -v)

    def point(i):
        i += 1
        s = 0
        while i > 0:
            s += fen[i]
            i -= i & -i
        return s

    size = 1
    while size < m:
        size *= 2
    heaps = [[] for _ in range(2 * size)]
    remaining, spans = [], []

    def insert(lo, hi, item):        # put item in the canonical nodes covering [lo, hi]
        lo += size
        hi += size + 1
        while lo < hi:
            if lo & 1:
                heapq.heappush(heaps[lo], item)
                lo += 1
            if hi & 1:
                hi -= 1
                heapq.heappush(heaps[hi], item)
            lo //= 2
            hi //= 2

    def best(p):                     # earliest-ending live grant covering position p, or None
        node, found = p + size, None
        while node:
            h = heaps[node]
            while h and remaining[h[0][1]] == 0:
                heapq.heappop(h)
            if h and (found is None or h[0] < found):
                found = h[0]
            node //= 2
        return found

    out = []
    for op in operations:
        kind = op[0]
        if kind == "add":
            _, start, end, credit = op
            lo, hi = bisect_left(qtimes, start), bisect_right(qtimes, end) - 1
            gid = len(remaining)
            remaining.append(credit)
            spans.append((lo, hi))
            if lo <= hi:                 # otherwise it's never live at any time we look at
                range_add(lo, hi, credit)
                insert(lo, hi, (end, gid))
        elif kind == "subtract":
            _, time, amount = op
            p = bisect_left(qtimes, time)
            while amount > 0:
                top = best(p)
                if top is None:
                    break
                gid = top[1]
                take = min(amount, remaining[gid])
                remaining[gid] -= take
                amount -= take
                range_add(spans[gid][0], spans[gid][1], -take)
        else:
            out.append(point(bisect_left(qtimes, op[1])))
    return out
