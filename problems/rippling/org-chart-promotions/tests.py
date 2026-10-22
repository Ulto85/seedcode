import random
from engine.spec import fn

H, P = "org_height", "min_promotions"
EX = [7, [1, 2, 3, 4, 1, 6], [2, 3, 4, 5, 6, 7]]


def rand_tree(rng, n, chainy=0.5):
    """Random tree on 1..n rooted at 1, shuffled labels and edge order. chainy -> deeper trees."""
    par = [0, 0] + [i - 1 if rng.random() < chainy else rng.randint(1, i - 1) for i in range(2, n + 1)]
    labels = list(range(2, n + 1))
    rng.shuffle(labels)
    lab = {1: 1, **{i + 2: x for i, x in enumerate(labels)}}
    edges = [(lab[par[i]], lab[i]) for i in range(2, n + 1)]
    rng.shuffle(edges)
    return n, [m for m, _ in edges], [r for _, r in edges]


def chain(n):
    return n, list(range(1, n)), list(range(2, n + 1))


def tests():
    rng = random.Random(99)
    t = [
        fn("Example", H, *EX),
        fn("Only the CEO", H, 1, [], []),
        fn("Star: everyone reports to CEO", H, 5, [1, 1, 1, 1], [2, 3, 4, 5]),
        fn("Chain of 5", H, *chain(5)),
        fn("Edges out of order", H, 6, [3, 1, 5, 1, 3], [5, 3, 6, 2, 4]),
        fn("Example, h = 3", P, *EX, 3, tag="Follow-up"),
        fn("Example, h = 2", P, *EX, 2, tag="Follow-up"),
        fn("Already within h", P, *EX, 5, tag="Follow-up"),
        fn("Impossible: h = 1", P, *EX, 1, tag="Follow-up"),
        fn("Only the CEO, h = 1", P, 1, [], [], 1, tag="Follow-up"),
        fn("Chain of 10, h = 3", P, *chain(10), 3, tag="Follow-up"),
        fn("Chain of 10, h = 4", P, *chain(10), 4, tag="Follow-up"),
        fn("Promote the right ancestor (shared subtree)", P, 8, [1, 2, 3, 3, 4, 5, 2], [2, 3, 4, 5, 6, 7, 8], 3,
           tag="Follow-up"),
    ]
    for s in range(3):
        n = rng.randint(8, 25)
        t.append(fn(f"Random height #{s + 1}", H, *rand_tree(rng, n), hidden=True))
    for s in range(5):
        n = rng.randint(8, 40)
        tr = rand_tree(rng, n, chainy=rng.choice([0.3, 0.6, 0.85]))
        t.append(fn(f"Random promotions #{s + 1}", P, *tr, rng.randint(2, 6), tag="Follow-up", hidden=True))
    t.append(fn("Chain of 100000 (no recursion)", H, *chain(100000), hidden=True))
    t.append(fn("Chain of 100000, h = 2", P, *chain(100000), 2, tag="Follow-up", hidden=True))
    t.append(fn("Random 100k tree, h = 4", P, *rand_tree(rng, 100000, chainy=0.9), 4, tag="Follow-up", hidden=True))
    t.append(fn("Deep 100k tree, h = 50", P, *rand_tree(rng, 100000, chainy=0.995), 50, tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return fn(f"n={n}", P, *rand_tree(rng, n, chainy=0.9), 5)


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of employees"}
