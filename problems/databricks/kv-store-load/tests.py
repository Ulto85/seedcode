import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "KVStore", [], ops, float=True, **kw)


def rand_ops(rng, n, follow_up=False, max_gap=3, keys=20):
    ops, t = [], 0
    for _ in range(n):
        t += rng.choice([0, 0, 1, 1, rng.randint(0, max_gap)])
        k = f"k{rng.randrange(keys)}"
        r = rng.random()
        if r < 0.35:
            ops.append(["put", [k, f"v{rng.randrange(1000)}", t]])
        elif r < 0.7:
            ops.append(["get", [k, t]])
        elif follow_up and r < 0.85:
            ops.append(["average_qps", [rng.choice(["put", "get"]), t, rng.choice([1, 10, 300, 5000, 10 ** 6])]])
        else:
            ops.append([rng.choice(["measure_put_load", "measure_get_load"]), [t]])
    return ops


def heavy(n):
    """n calls packed into a few hundred seconds, measured constantly: a full scan per measure is O(n^2)."""
    rng = random.Random(n)
    ops, t = [], 0
    for i in range(n):
        if i % 50 == 0:
            t += 1
        ops.append(["put", [f"k{i % 97}", "x", t]] if i % 2 else ["get", [f"k{i % 89}", t]])
        ops.append([("measure_put_load", "measure_get_load")[i % 2], [t]])
    return ops


def tests():
    rng = random.Random(9)
    t = [
        C("Example", [["put", ["a", "1", 1]], ["put", ["b", "2", 1]], ["get", ["a", 2]], ["get", ["z", 5]],
                      ["measure_put_load", [5]], ["measure_get_load", [300]], ["measure_get_load", [302]],
                      ["average_qps", ["put", 302, 1000]]]),
        C("Empty store", [["measure_put_load", [0]], ["measure_get_load", [100]], ["get", ["x", 100]],
                          ["measure_get_load", [100]]]),
        C("Overwrite and missing key both count", [["put", ["k", "1", 10]], ["put", ["k", "2", 10]], ["get", ["k", 11]],
                                                   ["get", ["nope", 11]], ["measure_put_load", [11]], ["measure_get_load", [11]]]),
        C("Window boundary is (t-300, t]", [["put", ["a", "1", 100]], ["measure_put_load", [399]],
                                            ["measure_put_load", [400]], ["measure_put_load", [401]]]),
        C("Many calls in one second", [["put", [f"k{i}", "v", 7]] for i in range(30)] + [["measure_put_load", [7]],
                                                                                        ["measure_get_load", [7]]]),
        C("Measure doesn't count as load", [["measure_get_load", [1]], ["measure_get_load", [1]], ["get", ["a", 1]],
                                            ["measure_get_load", [1]]]),
        C("Long idle gap", [["put", ["a", "1", 0]], ["get", ["a", 0]], ["measure_put_load", [1000000]],
                            ["get", ["a", 1000000]], ["measure_get_load", [1000000]]]),
        C("Arbitrary windows", [["put", ["a", "1", 1]], ["put", ["a", "2", 50]], ["get", ["a", 60]], ["put", ["b", "3", 400]],
                                ["average_qps", ["put", 400, 1]], ["average_qps", ["put", 400, 351]],
                                ["average_qps", ["put", 400, 400]], ["average_qps", ["get", 400, 340]],
                                ["average_qps", ["get", 400, 341]]], tag="Follow-up"),
        C("Huge window", [["put", ["a", "1", 5]], ["get", ["a", 6]], ["average_qps", ["put", 10, 10 ** 9]],
                          ["average_qps", ["get", 10, 3]]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random #{s + 1}", rand_ops(rng, 80, max_gap=200), hidden=True))
    for s in range(2):
        t.append(C(f"Random windows #{s + 1}", rand_ops(rng, 80, follow_up=True, max_gap=500), hidden=True, tag="Follow-up"))
    t.append(C("50k calls, measured constantly", heavy(50000), hidden=True))
    t.append(C("50k random calls with windows", rand_ops(rng, 50000, follow_up=True), hidden=True, tag="Follow-up"))
    return t


def scale(n):
    return C(f"n={n}", heavy(n))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of put/get calls"}
