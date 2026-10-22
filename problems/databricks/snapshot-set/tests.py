import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "SnapshotSet", [], ops, **kw)


def drain(it, k):
    return [["next", [it]] for _ in range(k)]


def rand_ops(rng, n, universe, p_iter=0.05):
    ops, iters = [], 0
    for _ in range(n):
        r = rng.random()
        if r < 0.35:
            ops.append(["add", [rng.randrange(universe)]])
        elif r < 0.55:
            ops.append(["remove", [rng.randrange(universe)]])
        elif r < 0.62:
            ops.append(["contains", [rng.randrange(universe)]])
        elif r < 0.62 + p_iter or iters == 0:
            ops.append(["get_iterator", []])
            iters += 1
        elif r < 0.8:
            ops.append(["has_next", [rng.randrange(iters)]])
        else:
            ops.append(["next", [rng.randrange(iters)]])
    return ops


def many_iterators(n):
    """Big set, then many iterators each read only a few items: copying per iterator is O(n^2)."""
    rng = random.Random(n)
    ops = [["add", [i]] for i in range(n)]
    for j in range(n):
        ops.append(["get_iterator", []])
        ops.append(["remove", [rng.randrange(n)]])
        ops.append(["add", [rng.randrange(n)]])
        ops.append(["next", [rng.randrange(j + 1)]])
    return ops


def tests():
    rng = random.Random(3)
    t = [
        C("Example", [["add", [1]], ["add", [2]], ["add", [3]], ["get_iterator", []], ["remove", [2]], ["add", [4]],
                      ["add", [1]], ["next", [0]], ["next", [0]], ["get_iterator", []], ["remove", [3]], ["add", [2]],
                      ["next", [0]], ["has_next", [0]], ["next", [1]], ["next", [1]], ["next", [1]], ["next", [1]]]),
        C("Add / remove / contains return values", [["contains", [5]], ["add", [5]], ["add", [5]], ["contains", [5]],
                                                    ["remove", [5]], ["remove", [5]], ["contains", [5]], ["remove", [9]]]),
        C("Iterator on empty set", [["get_iterator", []], ["has_next", [0]], ["next", [0]], ["add", [1]],
                                    ["has_next", [0]], ["next", [0]]]),
        C("Unknown iterator id", [["add", [1]], ["has_next", [0]], ["next", [3]], ["get_iterator", []],
                                  ["next", [1]], ["next", [-1]], ["next", [0]]]),
        C("Re-add moves to the end", [["add", [1]], ["add", [2]], ["add", [3]], ["remove", [1]], ["add", [1]],
                                      ["get_iterator", []]] + drain(0, 4)),
        C("Remove then re-add after snapshot", [["add", [7]], ["add", [8]], ["get_iterator", []], ["remove", [7]],
                                                ["add", [7]], ["get_iterator", []]] + drain(0, 3) + drain(1, 3)),
        C("Independent iterators", [["add", [10]], ["add", [20]], ["add", [30]], ["get_iterator", []],
                                    ["get_iterator", []], ["next", [0]], ["next", [0]], ["next", [1]],
                                    ["has_next", [0]], ["next", [0]], ["has_next", [0]], ["has_next", [1]], ["next", [1]]]),
        C("has_next is idempotent", [["add", [1]], ["get_iterator", []], ["has_next", [0]], ["has_next", [0]],
                                     ["next", [0]], ["has_next", [0]], ["has_next", [0]]]),
        C("Negative and zero values", [["add", [0]], ["add", [-5]], ["add", [-5]], ["get_iterator", []], ["remove", [0]]]
          + drain(0, 3)),
        C("Remove everything mid-iteration", [["add", [1]], ["add", [2]], ["add", [3]], ["get_iterator", []], ["next", [0]],
                                              ["remove", [1]], ["remove", [2]], ["remove", [3]], ["get_iterator", []],
                                              ["has_next", [1]]] + drain(0, 3)),
    ]
    for s in range(4):
        t.append(C(f"Random #{s + 1}", rand_ops(rng, 80, 12, p_iter=0.08), hidden=True))
    t.append(C("Random 20k ops", rand_ops(rng, 20000, 2000), hidden=True))
    t.append(C("20k iterators over a 20k-element set", many_iterators(20000), hidden=True))
    return t


def scale(n):
    return C(f"n={n}", many_iterators(n))


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = set size = number of iterators"}
