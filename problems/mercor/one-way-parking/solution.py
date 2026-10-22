"""One-Way Street Parking.

Part 1  can_all_park:  count cars by preferred spot, scan right to left.      O(n + m) time, O(n) space
Part 2  parking_spots: union-find "next free spot at or after i".            O((n + m) α(n)) time, O(n) space
Part 3  parking_log:   segment tree of free counts, descend to the first
                       free spot at or after p; departures re-free a spot.    O(n + q log n) time, O(n + q) space
"""


def can_all_park(n, preferences):
    count = [0] * n
    for p in preferences:
        count[p] += 1
    wanting = 0                      # cars that prefer spot j or later
    for j in range(n - 1, -1, -1):
        wanting += count[j]
        if wanting > n - j:          # only spots j..n-1 can hold them
            return False
    return True


def parking_spots(n, preferences):
    nxt = list(range(n + 1))         # nxt[i] -> some spot >= i that may be free; n means "off the end"

    def find(i):
        root = i
        while nxt[root] != root:
            root = nxt[root]
        while nxt[i] != root:
            nxt[i], i = root, nxt[i]
        return root

    out = []
    for p in preferences:
        s = find(p)
        if s == n:
            out.append(-1)
        else:
            out.append(s)
            nxt[s] = s + 1
    return out


def parking_log(n, events):
    size = 1
    while size < n:
        size *= 2
    free = [0] * (2 * size)
    for i in range(n):
        free[size + i] = 1
    for v in range(size - 1, 0, -1):
        free[v] = free[2 * v] + free[2 * v + 1]

    def update(i, val):
        v = size + i
        free[v] = val
        v //= 2
        while v:
            free[v] = free[2 * v] + free[2 * v + 1]
            v //= 2

    def first_free(p):
        """Smallest free index >= p, or -1."""
        def go(v, lo, hi):
            if hi <= p or free[v] == 0:
                return -1
            if hi - lo == 1:
                return lo
            mid = (lo + hi) // 2
            r = go(2 * v, lo, mid)
            return r if r != -1 else go(2 * v + 1, mid, hi)
        return go(1, 0, size)

    spot_of = []                     # arrival index -> spot it holds now, or -1
    out = []
    for ev in events:
        if ev[0] == "arrive":
            s = first_free(ev[1])
            if s != -1:
                update(s, 0)
            spot_of.append(s)
            out.append(s)
        else:
            k = ev[1]
            if 0 <= k < len(spot_of) and spot_of[k] != -1:
                update(spot_of[k], 1)
                spot_of[k] = -1
    return out
