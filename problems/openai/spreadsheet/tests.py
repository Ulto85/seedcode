import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "Spreadsheet", [], ops, **kw)


def s(c, v): return ["set_cell", [c, v]]
def g(c): return ["get_cell", [c]]


def rand_formula(rng, pool):
    parts = []
    for i in range(rng.randint(1, 4)):
        term = rng.choice(pool) if pool and rng.random() < 0.75 else str(rng.randint(0, 20))
        sign = rng.choice("+-") if i else rng.choice(["", "", "-"])
        parts.append(sign + term)
    return "=" + "".join(parts)


def acyclic_ops(rng, n, cells):
    """Each cell only references cells earlier in `cells`, so no write can create a cycle."""
    ops = []
    for _ in range(n):
        r = rng.random()
        i = rng.randrange(len(cells))
        if r < 0.3:
            ops.append(s(cells[i], str(rng.randint(-50, 50))))
        elif r < 0.6:
            ops.append(s(cells[i], rand_formula(rng, cells[:i])))
        else:
            ops.append(g(rng.choice(cells)))
    return ops


def any_ops(rng, n, cells):
    ops = []
    for _ in range(n):
        r = rng.random()
        if r < 0.25:
            ops.append(s(rng.choice(cells), str(rng.randint(-50, 50))))
        elif r < 0.6:
            ops.append(s(rng.choice(cells), rand_formula(rng, cells)))
        else:
            ops.append(g(rng.choice(cells)))
    return ops


def doubling_chain(k):
    """A1 = 1, A(i) = A(i-1) + A(i-1). Re-evaluating recursively without caching is O(2^k)."""
    ops = [s("A1", "1")] + [s(f"A{i}", f"=A{i - 1}+A{i - 1}") for i in range(2, k + 1)]
    ops += [g(f"A{k}"), g(f"A{k // 2}"), s("A1", "3"), g(f"A{k}"), g(f"A{k - 1}")]
    return ops


def long_chain(n, gets):
    ops = [s("B1", "1")] + [s(f"B{i}", f"=B{i - 1}+1") for i in range(2, n + 1)]
    ops += [g(f"B{n}")] * gets
    ops += [s("B1", "100"), g(f"B{n}"), g(f"B{n // 2}")]
    return ops


GRID = [f"{c}{r}" for c in "ABCD" for r in range(1, 5)]


def tests():
    rng = random.Random(3)
    t = [
        C("Example", [s("A1", "5"), s("B1", "=A1+3"), s("C1", "=A1+B1-1"), g("C1"), s("A1", "10"), g("B1"), g("C1"), g("Z9")]),
        C("Unset cells read as 0", [g("A1"), s("B2", "=A1+C3+4"), g("B2"), g("A1")]),
        C("Setting a referenced cell later", [s("B1", "=A1"), g("B1"), s("A1", "7"), g("B1")]),
        C("Negative literals and leading minus", [s("A1", "-4"), s("B1", "=-A1+10"), s("C1", "=-3-A1-B1"), g("B1"), g("C1")]),
        C("Same cell referenced twice", [s("A1", "6"), s("B1", "=A1+A1-A1+A1"), g("B1"), s("A1", "1"), g("B1")]),
        C("Formula replaced by a literal", [s("A1", "2"), s("B1", "=A1+1"), s("B1", "50"), s("A1", "9"), g("B1"), s("C1", "=B1"), g("C1")]),
        C("Literal replaced by a formula", [s("A1", "2"), s("B1", "=A1+1"), s("A1", "=C1+C1"), g("B1"), s("C1", "5"), g("A1"), g("B1")]),
        C("Diamond updates once each", [s("A1", "1"), s("B1", "=A1+1"), s("C1", "=A1+2"), s("D1", "=B1+C1"), s("A1", "10"), g("D1"), g("B1"), g("C1")]),
        C("Constant-only formula and multi-letter names", [s("AA10", "=7+8-2"), s("AB1", "=AA10+AA10"), g("AA10"), g("AB1")]),
        C("Follow-up example", [s("A1", "=B1+1"), g("A1"), s("B1", "=A1+1"), g("B1"), s("B1", "4"), g("A1")], tag="Follow-up"),
        C("Self reference", [s("A1", "3"), s("A1", "=A1+1"), g("A1"), s("A1", "=5-A1"), g("A1")], tag="Follow-up"),
        C("Three-cell cycle via an update", [s("A1", "=B1"), s("B1", "=C1"), s("C1", "2"), g("A1"), s("C1", "=A1+1"), g("C1"), g("A1"), g("B1")], tag="Follow-up"),
        C("Rejected write leaves dependencies intact", [s("A1", "1"), s("B1", "=A1+1"), s("A1", "=B1"), s("A1", "20"), g("B1"), g("A1")], tag="Follow-up"),
        C("Breaking the chain makes the write legal", [s("A1", "=B1"), s("B1", "=A1"), s("A1", "8"), s("B1", "=A1+1"), g("B1"), s("A1", "=C1"), g("B1")], tag="Follow-up"),
    ]
    for i in range(3):
        t.append(C(f"Random acyclic #{i + 1}", acyclic_ops(rng, 60, GRID), hidden=True))
    for i in range(3):
        t.append(C(f"Random with cycles #{i + 1}", any_ops(rng, 80, GRID), tag="Follow-up", hidden=True))
    t.append(C("Doubling chain of 40 cells", doubling_chain(40), hidden=True))
    t.append(C("Chain of 400 cells, 5000 reads", long_chain(400, 5000), hidden=True))
    big = [f"C{i}" for i in range(1, 301)]
    t.append(C("3000 random writes with cycles", any_ops(rng, 3000, big), tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    cells = [f"A{i}" for i in range(1, n + 1)]
    ops = []
    for i, c in enumerate(cells):
        refs = rng.sample(cells[max(0, i - 50):i], min(i, 2))
        ops.append(s(c, "=" + "+".join(refs + [str(rng.randint(0, 9))])))
    ops += [g(rng.choice(cells)) for _ in range(n)]
    for _ in range(5):
        ops.append(s(cells[rng.randrange(5)], str(rng.randint(0, 9))))
        ops.append(g(cells[-1]))
    return C(f"{n} cells", ops)


SCALE = {"sizes": [500, 1000, 2000, 4000, 8000, 16000], "label": "n = number of formula cells"}
