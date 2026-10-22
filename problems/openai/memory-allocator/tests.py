import random
from engine.spec import cls


def A(name, n, ops, **kw):
    return cls(name, "Allocator", [n], ops, **kw)


def m(o, s): return ["malloc", [o, s]]
def f(o): return ["free", [o]]


def rand_ops(rng, n, count, owners, max_size):
    ops = []
    for _ in range(count):
        if rng.random() < 0.6:
            ops.append(m(rng.randint(1, owners), rng.randint(1, max_size)))
        else:
            ops.append(f(rng.randint(1, owners)))
    return ops


def tests():
    rng = random.Random(5)
    t = [
        A("Example", 10, [m(1, 3), m(2, 2), m(1, 4), f(2), m(3, 3), m(3, 2), f(1), m(4, 6), m(4, 5), f(7)]),
        A("Fill exactly, then fail", 5, [m(1, 2), m(2, 3), m(3, 1), f(1), m(3, 1), m(3, 1), m(3, 1)]),
        A("Size larger than memory", 4, [m(1, 5), m(1, 4), f(1), f(1)]),
        A("Free an owner with nothing", 6, [f(9), m(9, 2), f(9), f(9)]),
        A("Leftmost fit, not best fit", 12, [m(1, 2), m(2, 1), m(3, 5), m(4, 1), f(1), f(3), m(5, 2), m(6, 4), m(7, 3)]),
        A("Neighbouring frees merge", 9, [m(1, 3), m(2, 3), m(3, 3), f(1), f(2), m(4, 6), m(5, 1)]),
        A("Owner with many blocks", 10, [m(1, 2), m(2, 1), m(1, 2), m(2, 1), m(1, 2), f(1), m(3, 2), m(3, 3), f(3), f(2)]),
        A("Single unit memory", 1, [m(1, 1), m(2, 1), f(1), m(2, 1), f(2)]),
        A("Big owner ids", 8, [m(10 ** 9, 3), m(123456789, 5), f(10 ** 9), m(1, 4), m(1, 3)]),
    ]
    for i in range(4):
        n = rng.randint(5, 30)
        t.append(A(f"Random small #{i + 1}", n, rand_ops(rng, n, 60, 6, max(1, n // 3)), hidden=True))
    t.append(A("Random medium (n = 500, 2k calls)", 500, rand_ops(rng, 500, 2000, 40, 60), hidden=True))
    t.append(A("n = 100000, 30k calls", 100000, rand_ops(rng, 100000, 30000, 2000, 300), tag="Follow-up", hidden=True))
    t.append(A("n = 100000, fragmented memory", 100000, [m(i, 1) for i in range(1, 50001)] +
               [x for i in range(2, 50001, 2) for x in (f(i),)] + [m(7, 2) for _ in range(5000)] + [m(8, 1) for _ in range(5000)] + [m(9, 50000) for _ in range(2000)],
               tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return A(f"n={n}", n, rand_ops(rng, n, n, max(2, n // 50), 30))


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = memory units = number of calls"}
