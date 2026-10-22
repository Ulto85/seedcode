import random
from engine.spec import cls


def stream(rng, n, window):
    t, ops = 0, []
    for _ in range(n):
        t += rng.randint(0, 4)
        r = rng.random()
        if r < 0.6: ops.append(["add_score", [t, rng.randint(1, 5)]])
        elif r < 0.8: ops.append(["get_average", [t]])
        else: ops.append(["get_csat_percent", [t]])
    return ops


def tests():
    rng = random.Random(7)
    t = [
        cls("Basic average", "CSATTracker", [10], [["add_score", [1, 5]], ["add_score", [2, 3]], ["get_average", [2]]], float=True),
        cls("Old scores expire", "CSATTracker", [10], [["add_score", [1, 5]], ["add_score", [5, 1]], ["get_average", [10]], ["get_average", [11]], ["get_average", [14]], ["get_average", [15]], ["get_average", [100]]], float=True),
        cls("No scores -> 0.0", "CSATTracker", [5], [["get_average", [3]]], float=True),
        cls("Same timestamp", "CSATTracker", [3], [["add_score", [4, 2]], ["add_score", [4, 4]], ["add_score", [4, 5]], ["get_average", [4]], ["get_average", [6]], ["get_average", [7]]], float=True),
        cls("CSAT percent", "CSATTracker", [60], [["add_score", [0, 5]], ["add_score", [10, 4]], ["add_score", [20, 2]], ["add_score", [30, 1]], ["get_csat_percent", [30]], ["get_csat_percent", [65]], ["get_csat_percent", [75]]], tag="Follow-up", float=True),
        cls("CSAT percent empty", "CSATTracker", [60], [["get_csat_percent", [0]]], tag="Follow-up", float=True),
    ]
    for s in range(2):
        w = rng.choice([5, 30, 100])
        t.append(cls(f"Random stream #{s + 1}", "CSATTracker", [w], stream(rng, 50, w), tag="Follow-up", hidden=True, float=True))
    t.append(cls("200k ops (needs amortized O(1))", "CSATTracker", [100], stream(rng, 200000, 100), tag="Follow-up", hidden=True, float=True))
    return t


def scale(n):
    return cls(f"{n} ops", "CSATTracker", [n // 10 + 1], stream(random.Random(n), n, n // 10 + 1), float=True)


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of operations", "per_op": True}
