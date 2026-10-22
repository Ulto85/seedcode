import random
from engine.spec import fn


def act(): return {"status": "active", "replacement": None}
def disc(rep=None): return {"status": "discontinued", "replacement": rep}


EX_CAT = {"p1": act(), "p2": disc("p3"), "p3": disc("p1"), "p4": disc(), "p5": disc("p6"), "p6": disc("p5"), "p7": disc("p9")}
EX_REQ = ["p2", "p4", "p5", "p7", "p2"]


def random_catalog(rng, n, flaky_rate=0.2, max_flaky=4):
    ids = [f"p{i}" for i in range(n)]
    cat = {}
    for i in ids:
        r = rng.random()
        if r < 0.35:
            cat[i] = act()
        elif r < 0.45:
            cat[i] = disc()
        else:
            cat[i] = disc(rng.choice(ids + ["ghost1", "ghost2"]))
    flaky = {i: rng.randint(1, max_flaky) for i in ids + ["ghost1"] if rng.random() < flaky_rate}
    return cat, flaky


def chain_catalog(rng, n):
    """One long replacement chain c0 -> c1 -> ... -> c{n-1} (active), plus many old ids feeding into it."""
    cat = {f"c{i}": disc(f"c{i + 1}") for i in range(n - 1)}
    cat[f"c{n - 1}"] = act()
    for k in range(n):
        cat[f"old{k}"] = disc(f"c{rng.randrange(n)}")
    flaky = {f"c{rng.randrange(n)}": rng.randint(1, 3) for _ in range(n // 50)}
    reqs = [rng.choice([f"old{rng.randrange(n)}", f"c{rng.randrange(n)}"]) for _ in range(n)]
    return reqs, cat, flaky


def tests():
    rng = random.Random(5)
    t = [
        fn("Example, no cache", "resolve_products", EX_REQ, EX_CAT, {"p3": 2}, 3, 100),
        fn("Example, failure then success", "resolve_products", ["p2", "p2"], EX_CAT, {"p3": 2}, 1, 100),
        fn("No requests", "resolve_products", [], EX_CAT, {}, 3, 100),
        fn("Already active", "resolve_products", ["p1", "p1"], EX_CAT, {}, 3, 100),
        fn("Self replacement is a cycle", "resolve_products", ["s"], {"s": disc("s")}, {}, 2, 10),
        fn("No retries allowed", "resolve_products", ["a", "a", "a"], {"a": act()}, {"a": 2}, 0, 50),
        fn("Backoff doubles", "resolve_products", ["a"], {"a": act()}, {"a": 4}, 5, 10),
        fn("Retries exhausted mid-chain", "resolve_products", ["x", "y"], {"x": disc("y"), "y": act()}, {"y": 3}, 2, 7),
        fn("Unknown id is flaky too", "resolve_products", ["nope"], {}, {"nope": 1}, 1, 5),
        fn("Example with cache", "resolve_products", EX_REQ, EX_CAT, {"p3": 2}, 3, 100, True, tag="Follow-up"),
        fn("Cache: failures are retried later", "resolve_products", ["p2", "p2", "p3"], EX_CAT, {"p3": 2}, 1, 100, True, tag="Follow-up"),
        fn("Cache: shared chain fetched once", "resolve_products", ["a", "b", "c", "a"],
           {"a": disc("c"), "b": disc("c"), "c": disc("d"), "d": act()}, {"d": 1}, 2, 10, True, tag="Follow-up"),
        fn("Cache: cycle reached from a tail", "resolve_products", ["t", "x", "y"],
           {"t": disc("x"), "x": disc("y"), "y": disc("x")}, {}, 1, 1, True, tag="Follow-up"),
        fn("Cache: not-found is remembered", "resolve_products", ["a", "b", "zz"], {"a": disc("zz"), "b": disc("zz")}, {"zz": 1}, 1, 3, True, tag="Follow-up"),
    ]
    for s in range(3):
        cat, flaky = random_catalog(rng, 25)
        reqs = [rng.choice(list(cat) + ["ghost2"]) for _ in range(30)]
        mr, base = rng.randint(0, 3), rng.choice([1, 10, 100])
        t.append(fn(f"Random catalog #{s + 1}", "resolve_products", reqs, cat, flaky, mr, base, hidden=True))
        t.append(fn(f"Random catalog, cached #{s + 1}", "resolve_products", reqs, cat, flaky, mr, base, True, tag="Follow-up", hidden=True))
    cat, flaky = random_catalog(rng, 3000)
    reqs = [rng.choice(list(cat)) for _ in range(3000)]
    t.append(fn("3000 requests, no cache", "resolve_products", reqs, cat, flaky, 3, 20, hidden=True))
    reqs, cat, flaky = chain_catalog(rng, 25000)
    t.append(fn("25k requests on one long chain", "resolve_products", reqs, cat, flaky, 3, 20, True, tag="Follow-up", hidden=True))
    return t


def scale(n):
    reqs, cat, flaky = chain_catalog(random.Random(n), n)
    return fn(f"n={n}", "resolve_products", reqs, cat, flaky, 3, 20, True)


SCALE = {"sizes": [1500, 3000, 6000, 12000, 24000, 48000], "label": "n = requests = chain length (cached)"}
