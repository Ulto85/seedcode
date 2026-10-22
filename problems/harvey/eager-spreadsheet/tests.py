import random
from engine.spec import fn

F = "eager_sheet"


def name(i):
    return "ABCDEFGH"[i % 8] + str(i // 8 + 1)


def rand_formula(rng, refs):
    terms = []
    for _ in range(rng.randint(1, 4)):
        terms.append(rng.choice(refs) if refs and rng.random() < 0.75 else str(rng.randint(0, 20)))
    s = terms[0]
    for tm in terms[1:]:
        s += rng.choice(["+", "-", " + ", " - "]) + tm
    return "=" + (" " if rng.random() < 0.2 else "") + s


def random_ops(rng, n, cells, acyclic):
    ops = []
    for _ in range(n):
        if rng.random() < 0.35:
            ops.append(["get", name(rng.randrange(cells + 2))])
            continue
        i = rng.randrange(cells)
        if rng.random() < 0.35:
            lit = str(rng.randint(-50, 50))
            if rng.random() < 0.2:
                lit = ("-" if lit[0] == "-" else "+") + "00" + lit.lstrip("-")
            ops.append(["set", name(i), lit])
        else:
            pool = list(range(i)) if acyclic else list(range(cells))
            ops.append(["set", name(i), rand_formula(rng, [name(j) for j in pool])])
    return ops


def S(c, v): return ["set", c, v]
def G(c): return ["get", c]


def tests():
    rng = random.Random(3)
    t = [
        fn("Example", F, [S("A1", "2"), S("B1", "=A1+1"), S("C1", "=A1+B1"), S("A1", "5"), G("C1"), G("Z9")]),
        fn("Empty", F, []),
        fn("Literal forms", F, [G("A1"), S("A1", "+0007"), G("A1"), S("A1", "-0"), G("A1"), S("A1", "-0012"), G("A1")]),
        fn("Spaces and subtraction", F, [S("A1", "10"), S("B2", "= A1 - 3 + 4 "), G("B2"), S("C3", "=B2-A1-20"), G("C3")]),
        fn("Repeated reference counts twice", F, [S("A1", "3"), S("B1", "=A1+A1+A1"), G("B1"), S("A1", "-2"), G("B1")]),
        fn("Formula -> literal drops dependency", F, [S("A1", "1"), S("B1", "=A1+1"), S("B1", "100"), S("A1", "50"), G("B1")]),
        fn("References to unset cells are 0", F, [S("C1", "=A1+B1+5"), G("C1"), S("B1", "4"), G("C1"), G("A1")]),
        fn("Diamond updates once correctly", F, [S("A1", "1"), S("B1", "=A1+1"), S("C1", "=A1+2"), S("D1", "=B1+C1+A1"), S("A1", "10"), G("D1")]),
        fn("Multi-letter columns", F, [S("AA10", "7"), S("AB1", "=AA10+AA10"), G("AB1"), S("AA10", "1"), G("AB1")]),
        fn("Cycle example", F, [S("A1", "=B1"), S("B1", "=A1+1"), G("A1"), S("A1", "3"), S("B1", "=A1+1"), G("B1")], tag="Follow-up"),
        fn("Self reference rejected", F, [S("A1", "5"), S("A1", "=A1+1"), G("A1"), S("A1", "=A1-A1"), G("A1")], tag="Follow-up"),
        fn("Long cycle rejected, old formula kept", F, [S("A1", "1"), S("B1", "=A1+1"), S("C1", "=B1+1"), S("D1", "=C1+1"),
                                                        S("A1", "=D1"), G("A1"), G("D1"), S("A1", "2"), G("D1")], tag="Follow-up"),
        fn("Rejected write leaves values untouched", F, [S("A1", "4"), S("B1", "=A1+A1"), S("A1", "=B1+3"), G("A1"), G("B1")], tag="Follow-up"),
        fn("Breaking a cycle path then closing it is OK", F, [S("A1", "=B1+C1"), S("C1", "=A1"), S("B1", "2"), S("C1", "5"), S("B1", "=C1+1"), G("A1"), G("B1")], tag="Follow-up"),
    ]
    for s in range(4):
        t.append(fn(f"Random acyclic #{s + 1}", F, random_ops(rng, 80, 10, True), hidden=True))
    for s in range(4):
        t.append(fn(f"Random with cycles #{s + 1}", F, random_ops(rng, 80, 8, False), tag="Follow-up", hidden=True))
    diamond = [S("A1", "1")] + [S(f"A{i}", f"=A{i - 1}+A{i - 1}") for i in range(2, 61)]
    diamond += [S("A1", "3"), G("A60"), S("A1", "-1"), G("A60"), G("A30")]
    t.append(fn("Doubling chain of 60 cells", F, diamond, hidden=True))
    chain = [S("A1", "0")] + [S(f"A{i}", f"=A{i - 1}+1") for i in range(2, 2001)]
    for k in range(200):
        chain += [S("A1", str(k)), G(f"A{rng.randint(1, 2000)}")]
    t.append(fn("2000-cell chain, 200 root updates", F, chain, hidden=True))
    t.append(fn("Random with cycles (4000 ops)", F, random_ops(rng, 4000, 200, False), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return fn(f"{n} ops", F, random_ops(random.Random(n), n, max(10, n // 20), True))


SCALE = {"sizes": [250, 500, 1000, 2000, 4000, 8000], "label": "n = number of operations (n/20 cells)"}
