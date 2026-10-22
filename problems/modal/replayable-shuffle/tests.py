import random
from engine.spec import fn


def rand_draws(rng, n):
    return [rng.randint(0, n - 1 - i) for i in range(max(n - 1, 0))]


def tests():
    rng = random.Random(5)
    abcd = ["a", "b", "c", "d"]
    t = [
        fn("Example", "shuffle", abcd, [2, 0, 1]),
        fn("Draw out of range", "shuffle", ["a", "b"], [2]),
        fn("Too few draws", "shuffle", ["a", "b", "c"], [0]),
        fn("Too many draws", "shuffle", ["a", "b"], [0, 0]),
        fn("Negative draw", "shuffle", ["a", "b", "c"], [-1, 0]),
        fn("Empty list", "shuffle", [], []),
        fn("Single item needs no draws", "shuffle", ["x"], []),
        fn("All zeros is the identity", "shuffle", [1, 2, 3, 4, 5], [0, 0, 0, 0]),
        fn("Max draws rotate right", "shuffle", [1, 2, 3, 4, 5], [4, 3, 2, 1]),
        fn("Duplicates are fine", "shuffle", [7, 7, 8, 8], [3, 1, 0]),
        fn("Follow-up example", "recover_draws", abcd, ["c", "b", "d", "a"], tag="Follow-up"),
        fn("Identity", "recover_draws", ["a", "b", "c"], ["a", "b", "c"], tag="Follow-up"),
        fn("Repeated element", "recover_draws", ["a", "b"], ["a", "a"], tag="Follow-up"),
        fn("Length mismatch", "recover_draws", ["a", "b", "c"], ["a", "b"], tag="Follow-up"),
        fn("Foreign element", "recover_draws", [1, 2, 3], [1, 2, 4], tag="Follow-up"),
        fn("Empty and single", "recover_draws", [], [], tag="Follow-up"),
        fn("Reversed", "recover_draws", [1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], tag="Follow-up"),
    ]
    for s in range(3):
        n = rng.randint(2, 30)
        items = list(range(100, 100 + n))
        draws = rand_draws(rng, n)
        if s == 2:
            k = rng.randrange(len(draws))
            draws[k] = n - k            # one just out of range
        t.append(fn(f"Random replay #{s + 1}", "shuffle", items, draws, hidden=True))
    for s in range(3):
        n = rng.randint(2, 40)
        items = [f"c{i}" for i in range(n)]
        perm = items[:]
        rng.shuffle(perm)
        t.append(fn(f"Random inverse #{s + 1}", "recover_draws", items, perm, tag="Follow-up", hidden=True))
    n = 200000
    items = list(range(n))
    t.append(fn("200k replay", "shuffle", items, rand_draws(rng, n), hidden=True))
    perm = items[:]
    rng.shuffle(perm)
    t.append(fn("200k inverse", "recover_draws", items, perm, tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    items = list(range(n))
    perm = items[:]
    rng.shuffle(perm)
    return fn(f"n={n}", "recover_draws", items, perm)


SCALE = {"sizes": [10000, 20000, 40000, 80000, 160000, 320000], "label": "n = len(items) (recover_draws)"}
