import random
from engine.spec import fn

NAMES = ["Walk", "Bike", "Car", "Train"]
EX = ["S2221",
      "1XXX1",
      "1111D"]


def city(rng, R, C, k=4, roads=None, wall=0.12, far=False, dashed=False):
    """Mostly walking cells ('1'), with straight road segments of other modes and some blocked cells."""
    g = [["1" if rng.random() > wall else "X" for _ in range(C)] for _ in range(R)]
    for _ in range(roads if roads is not None else (R + C) // 6):
        m = str(rng.randint(2, k)) if k > 1 else "1"
        r, c = rng.randrange(R), rng.randrange(C)
        if rng.random() < 0.5:
            for cc in range(c, min(C, c + rng.randint(2, max(2, C // 2)))):
                if cc % 6 or not dashed:    # dashed roads leave crossings for walkers
                    g[r][cc] = m
        else:
            for rr in range(r, min(R, r + rng.randint(2, max(2, R // 2)))):
                if rr % 6 or not dashed:
                    g[rr][c] = m
    if far:   # opposite corners, with a train line along the top and right edges
        for cc in range(C):
            g[0][cc] = str(k)
        for rr in range(R):
            g[rr][C - 1] = str(k)
        g[1][0] = g[R - 1][C - 2] = "1"
        (sr, sc), (dr, dc) = (0, 0), (R - 1, C - 1)
    else:
        cells = [(r, c) for r in range(R) for c in range(C)]
        (sr, sc), (dr, dc) = rng.sample(cells, 2)
    g[sr][sc], g[dr][dc] = "S", "D"
    return ["".join(row) for row in g]


def tests():
    rng = random.Random(5)
    t = [
        fn("Example", "best_mode", EX, NAMES[:2], [3, 1], [0, 2]),
        fn("Faster mode wins", "best_mode", ["S1D", "222"], ["Walk", "Bike"], [5, 1], [0, 3]),
        fn("Tie on time -> cheaper wins", "best_mode", ["S1D", "222"], ["Walk", "Bike"], [4, 2], [3, 1]),
        fn("Full tie -> earlier in list", "best_mode", ["S1", "2D"], ["Walk", "Bike"], [2, 2], [1, 1]),
        fn("Nobody can reach", "best_mode", ["S1X", "XXD"], ["Walk", "Bike"], [1, 1], [1, 1]),
        fn("S next to D", "best_mode", ["SD"], ["Walk", "Bike", "Car"], [5, 3, 1], [0, 1, 9]),
        fn("Slow per step but fewer steps", "best_mode",
           ["S111D", "2X2X2", "22222"], ["Walk", "Bike"], [3, 2], [0, 0]),
        fn("Single column", "best_mode", ["S", "3", "3", "D"], ["Walk", "Bike", "Car"], [1, 1, 1], [5, 5, 5]),
        fn("Example (switching)", "fastest_with_switches", EX, [3, 1], 2, tag="Follow-up"),
        fn("Penalty too high to bother", "fastest_with_switches", EX, [3, 1], 100, tag="Follow-up"),
        fn("Zero penalty", "fastest_with_switches", EX, [3, 1], 0, tag="Follow-up"),
        fn("Unreachable", "fastest_with_switches", ["S1X", "XXD"], [1, 1], 0, tag="Follow-up"),
        fn("S next to D (switching)", "fastest_with_switches", ["SD"], [7, 4], 3, tag="Follow-up"),
        fn("Must switch twice", "fastest_with_switches", ["S1222221D"], [4, 1], 3, tag="Follow-up"),
    ]
    for s in range(4):
        R, C = rng.randint(3, 8), rng.randint(3, 8)
        g = city(rng, R, C, roads=rng.randint(2, 6))
        times = [rng.randint(3, 6), rng.randint(2, 4), 1, 2]
        costs = [0, rng.randint(1, 3), rng.randint(3, 6), rng.randint(2, 4)]
        t.append(fn(f"Random small #{s + 1}", "best_mode", g, NAMES, times, costs, hidden=True))
        t.append(fn(f"Random small switching #{s + 1}", "fastest_with_switches", g, times, rng.randint(0, 6),
                    hidden=True, tag="Follow-up"))
    big = city(rng, 300, 300, k=4, wall=0.1, far=True, dashed=True)
    t.append(fn("300x300 city", "best_mode", big, NAMES, [5, 3, 1, 2], [0, 1, 5, 3], hidden=True))
    big = city(rng, 120, 120, k=4, wall=0.1, far=True, dashed=True)
    t.append(fn("120x120 city (switching)", "fastest_with_switches", big, [4, 3, 1, 6], 4, hidden=True, tag="Follow-up"))
    return t


def scale(n):
    side = int(n ** 0.5)
    g = city(random.Random(n), side, side, k=4, wall=0.1, far=True, dashed=True)
    return fn(f"{side}x{side}", "best_mode", g, NAMES, [5, 3, 1, 2], [0, 1, 5, 3])


SCALE = {"sizes": [4096, 8192, 16384, 32768, 65536, 131072], "label": "n = rows × cols"}
