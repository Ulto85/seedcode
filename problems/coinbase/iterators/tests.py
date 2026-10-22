import random
from engine.spec import cls

BIG = 10 ** 15


def R(name, init, ops, **kw):
    return cls(name, "RangeIterator", init, ops, **kw)


def I(name, sources, ops, **kw):
    return cls(name, "InterleavingIterator", [sources], ops, **kw)


def drain(k):
    return [["next", []]] * k


def mixed(k):
    return [["has_next", []], ["next", []]] * k


def rand_sources(rng, k, max_len):
    out = []
    for _ in range(k):
        L = rng.randint(0, max_len)
        if rng.random() < 0.5:
            out.append([rng.randint(-100, 100) for _ in range(L)])
        else:
            st = rng.choice([-3, -2, -1, 0, 1, 2, 3])
            s = rng.randint(-50, 50)
            out.append({"range": [s, s + st * (L - 1) if st else s + rng.randint(-5, 5), st]})
    return out


def rand_ops(rng, n, peek):
    names = ["next", "next", "next", "has_next"] + (["peek"] if peek else [])
    return [[rng.choice(names), []] for _ in range(n)]


def tests():
    rng = random.Random(2025)
    t = [
        R("Range example", [0, 10, 4], [["next", []], ["next", []], ["has_next", []], ["next", []], ["has_next", []], ["next", []]]),
        R("End is inclusive", [1, 5, 1], drain(6)),
        R("Negative step", [5, -5, -3], mixed(5)),
        R("Empty: start past end", [5, 1, 1], [["has_next", []], ["next", []]]),
        R("Empty: step 0", [3, 3, 0], [["has_next", []], ["next", []], ["next", []]]),
        R("Single element", [7, 7, -2], mixed(2)),
        R("Huge range stays lazy", [-BIG, BIG, 1], drain(5) + [["has_next", []]]),
        I("Interleave example", [[1, 2, 3], [], {"range": [10, 30, 10]}, [7]], drain(8), tag="Part 2"),
        I("Two arrays, uneven", [[1, 2, 3, 4, 5], [9]], mixed(7), tag="Part 2"),
        I("All empty sources", [[], {"range": [1, 0, 1]}, []], [["has_next", []], ["next", []]], tag="Part 2"),
        I("No sources", [], [["has_next", []], ["next", []]], tag="Part 2"),
        I("Lazy infinite-ish ranges", [{"range": [0, BIG, 1]}, [100, 200], {"range": [-1, -BIG, -1]}], drain(9), tag="Part 2"),
        I("Peek doesn't advance", [[1, 2], [3]], [["peek", []], ["peek", []], ["next", []], ["peek", []], ["next", []],
                                                   ["peek", []], ["next", []], ["peek", []], ["has_next", []], ["next", []]], tag="Follow-up"),
        I("Peek on ranges", [{"range": [5, 1, -2]}, {"range": [0, 0, 5]}], [["peek", []], ["next", []], ["peek", []], ["next", []],
                                                                          ["peek", []], ["next", []], ["peek", []], ["next", []], ["peek", []]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(I(f"Random interleave #{s + 1}", rand_sources(rng, rng.randint(1, 6), 6), rand_ops(rng, 40, False), tag="Part 2", hidden=True))
    for s in range(2):
        t.append(I(f"Random with peek #{s + 1}", rand_sources(rng, rng.randint(1, 6), 6), rand_ops(rng, 40, True), tag="Follow-up", hidden=True))
    # Many short sources + one long one: scanning past dead sources each call is O(k) per next.
    srcs = rand_sources(rng, 50000, 3) + [{"range": [0, BIG, 7]}]
    t.append(I("50k sources, 200k calls", srcs, [["next", []]] * 150000 + [["has_next", []]] * 50000, tag="Part 2", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return I(f"n={n}", rand_sources(rng, n // 4, 6) + [{"range": [0, BIG, 1]}], rand_ops(rng, n, True), tag="Follow-up")


SCALE = {"sizes": [5000, 10000, 20000, 40000, 80000, 160000], "label": "n = number of calls (sources = n/4)"}
