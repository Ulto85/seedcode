import heapq
from collections import deque


def _find(grid, ch):
    for r, row in enumerate(grid):
        c = row.find(ch)
        if c != -1:
            return r, c


def _steps(grid, digit, start, goal):
    """BFS restricted to cells labelled `digit`, S or D. Returns steps or None."""
    R, C = len(grid), len(grid[0])
    dist = {start: 0}
    q = deque([start])
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return dist[(r, c)]
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in dist and grid[nr][nc] in (digit, "S", "D"):
                dist[(nr, nc)] = dist[(r, c)] + 1
                q.append((nr, nc))
    return None


def best_mode(grid, names, times, costs):
    """One BFS per mode: O(k * R * C) time, O(R * C) space."""
    start, goal = _find(grid, "S"), _find(grid, "D")
    best = None
    for i in range(len(times)):
        steps = _steps(grid, str(i + 1), start, goal)
        if steps is None:
            continue
        key = (steps * times[i], steps * costs[i], i)
        if best is None or key < best:
            best = key
    return "" if best is None else names[best[2]]


def fastest_with_switches(grid, times, switch_penalty):
    """Dijkstra over (cell, mode): O(k * R * C * (k + log(kRC))) time, O(k * R * C) space."""
    R, C, k = len(grid), len(grid[0]), len(times)
    (sr, sc), goal = _find(grid, "S"), _find(grid, "D")
    INF = float("inf")
    dist = [[[INF] * k for _ in range(C)] for _ in range(R)]
    pq = []
    for m in range(k):
        dist[sr][sc][m] = 0
        pq.append((0, sr, sc, m))
    heapq.heapify(pq)
    while pq:
        d, r, c, m = heapq.heappop(pq)
        if d > dist[r][c][m]:
            continue
        if (r, c) == goal:
            return d
        for m2 in range(k):          # switch mode in place
            if m2 != m:
                nd = d + switch_penalty
                if nd < dist[r][c][m2]:
                    dist[r][c][m2] = nd
                    heapq.heappush(pq, (nd, r, c, m2))
        digit, nd = str(m + 1), d + times[m]
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] in (digit, "S", "D") and nd < dist[nr][nc][m]:
                dist[nr][nc][m] = nd
                heapq.heappush(pq, (nd, nr, nc, m))
    return -1
