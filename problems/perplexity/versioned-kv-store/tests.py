import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "VersionedKV", [], ops, **kw)


def s(k, v, t): return ["set", [k, v, t]]
def d(k, t): return ["delete", [k, t]]
def g(k, t): return ["get", [k, t]]
def rng_(k, a, b): return ["get_range", [k, a, b]]
def r(t): return ["restore", [t]]


def random_ops(rng, n, keys, parts, step=3, values=4):
    """parts: 1 = set/delete/get, 2 = + get_range, 3 = + restore."""
    ks = [f"k{i}" for i in range(keys)]
    kept = []                                  # timestamps of kept mutations (non-decreasing)
    ops = []
    for _ in range(n):
        top = kept[-1] if kept else 0
        x = rng.random()
        if x < 0.35:
            t = top + rng.randint(0, step)
            ops.append(s(rng.choice(ks), rng.choice(["v%d" % i for i in range(values)] + list(range(values))), t))
            kept.append(t)
        elif x < 0.45:
            t = top + rng.randint(0, step)
            ops.append(d(rng.choice(ks), t))
            kept.append(t)
        elif x < 0.7 or parts == 1:
            ops.append(g(rng.choice(ks + ["nope"]), rng.randint(0, top + 5)))
        elif x < 0.9 or parts == 2:
            a = rng.randint(0, top + 3)
            ops.append(rng_(rng.choice(ks), a, a + rng.randint(-2, 4 * step)))
        else:
            t = rng.randint(0, top + 2)
            ops.append(r(t))
            while kept and kept[-1] > t:
                kept.pop()
    return ops


def hot_key(n):
    """One key with n versions, then many point and narrow range queries and small restores."""
    ops = [s("hot", i % 7, i) for i in range(n)]
    for i in range(n):
        ops.append(g("hot", (i * 7919) % n))
    for i in range(0, n, 4):
        ops.append(rng_("hot", (i * 104729) % n, (i * 104729) % n + 3))
    return ops


def hot_key_restores(n):
    ops = [s("hot", i, i) for i in range(n)]
    for i in range(n - 1, n // 2, -1):
        ops.append(r(i))
        ops.append(g("hot", n))
    return ops


def tests():
    rnd = random.Random(31)
    t = [
        C("Example (Part 1)", [s("a", "x", 1), s("a", "y", 4), g("a", 3), g("a", 0), g("a", 4), d("a", 6), g("a", 6), g("a", 5)]),
        C("Missing keys", [g("nope", 5), d("ghost", 1), g("ghost", 1), s("a", 1, 2), g("b", 2)]),
        C("Same timestamp: last write wins", [s("a", "x", 3), s("a", "y", 3), g("a", 3), d("a", 5), s("a", "z", 5), g("a", 5), g("a", 4)]),
        C("Query far past and future", [s("k", 10, 100), g("k", 99), g("k", 100), g("k", 10 ** 9), s("k", 0, 200), g("k", 150), g("k", 200)]),
        C("Range basics", [s("a", "x", 1), s("a", "y", 4), rng_("a", 1, 5), rng_("a", 2, 3), rng_("a", 0, 0), rng_("a", 5, 2), rng_("zzz", 0, 9)], tag="Part 2"),
        C("Range with deletes", [s("a", "x", 1), d("a", 3), d("a", 4), s("a", "x", 6), rng_("a", 0, 10), rng_("a", 3, 10), rng_("a", 4, 5)], tag="Part 2"),
        C("Range skips non-changes", [s("a", 1, 1), s("a", 1, 2), d("b", 2), s("a", 2, 3), s("a", 1, 3), s("b", 7, 4), d("b", 4),
                                      rng_("a", 0, 5), rng_("b", 0, 5), rng_("a", 3, 3)], tag="Part 2"),
        C("Range: int vs string values differ", [s("a", 1, 1), s("a", "1", 2), rng_("a", 1, 2)], tag="Part 2"),
        C("Follow-up example", [s("a", "x", 1), s("a", "y", 4), d("a", 6), s("b", 20, 6), rng_("a", 0, 10), r(4), g("a", 100), g("b", 100),
                                s("a", "z", 5), rng_("a", 3, 9)], tag="Follow-up"),
        C("Restore keeps ties at the boundary", [s("a", 1, 2), s("a", 2, 2), s("a", 3, 3), r(2), g("a", 9), r(1), g("a", 9), g("a", 2)], tag="Follow-up"),
        C("Restore is a no-op when nothing is newer", [s("a", 1, 2), r(5), g("a", 9), r(2), g("a", 9)], tag="Follow-up"),
        C("Discarded mutations never come back", [s("a", 1, 1), s("a", 2, 10), r(5), g("a", 10), s("a", 3, 6), g("a", 10), rng_("a", 0, 20), r(5), g("a", 20)], tag="Follow-up"),
    ]
    for i in range(3):
        t.append(C(f"Random set/get #{i + 1}", random_ops(rnd, 80, 3, 1), hidden=True))
    for i in range(2):
        t.append(C(f"Random with ranges #{i + 1}", random_ops(rnd, 100, 3, 2), tag="Part 2", hidden=True))
    for i in range(3):
        t.append(C(f"Random with restores #{i + 1}", random_ops(rnd, 120, 3, 3), tag="Follow-up", hidden=True))
    t.append(C("One key, 40k versions", hot_key(40000), tag="Part 2", hidden=True))
    t.append(C("Random 60k ops with restores", random_ops(rnd, 60000, 50, 3, step=2), tag="Follow-up", hidden=True))
    t.append(C("20k restores on one key", hot_key_restores(40000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"one key, {n} versions", hot_key(n), tag="Part 2")


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = versions of one key (n gets, n/4 ranges)"}
