import random
from engine.spec import fn

F = "update_neurons"


def grid(rng, m, n, p_zero=0.5, hi=5):
    return [[0 if rng.random() < p_zero else rng.randint(1, hi) for _ in range(n)] for _ in range(m)]


def tests():
    rng = random.Random(3)
    t = [
        fn("Example: all firing 3x3", F, [[0, 0, 0], [0, 0, 0], [0, 0, 0]]),
        fn("Single non-firing cell", F, [[5]]),
        fn("Single firing cell", F, [[0]]),
        fn("Empty grid", F, []),
        fn("Two cells", F, [[1, 0]]),
        fn("Never below zero", F, [[1, 2, 1], [2, 1, 2]]),
        fn("Many firing neighbours -> minus 1", F, [[0, 0, 0], [0, 9, 0], [0, 0, 0]]),
        fn("Exactly 2 or 3 firing neighbours -> unchanged", F, [[0, 0, 4], [7, 7, 7]]),
        fn("Simultaneous update (new 6s don't count)", F, [[0, 0, 1], [0, 3, 1], [1, 1, 1]]),
        fn("Single row", F, [[0, 3, 0, 0, 2, 0, 0, 0, 1]]),
        fn("Single column", F, [[0], [4], [0], [0], [1]]),
    ]
    for s in range(4):
        t.append(fn(f"Random #{s + 1}", F, grid(rng, rng.randint(2, 8), rng.randint(2, 8)), hidden=True))
    t.append(fn("300 x 300", F, grid(rng, 300, 300, p_zero=0.4, hi=10**6), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return fn(f"{n} cells", F, grid(rng, n // 50, 50))


SCALE = {"sizes": [2500, 5000, 10000, 20000, 40000, 80000], "label": "n = number of cells (rows x 50)"}
