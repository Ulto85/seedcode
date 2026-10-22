import random
from engine.spec import fn


def A(s, e, c): return ["add", s, e, c]
def S(t, c): return ["subtract", t, c]
def K(t): return ["check", t]


def F(name, ops, **kw):
    return fn(name, "track_credits", ops, **kw)


def random_ops(rng, n, horizon, max_len, max_credit=50):
    ops = []
    for _ in range(n):
        x = rng.random()
        if x < 0.4:
            s = rng.randint(0, horizon)
            ops.append(A(s, s + rng.randint(0, max_len), rng.randint(1, max_credit)))
        elif x < 0.7:
            ops.append(S(rng.randint(0, horizon + max_len), rng.randint(1, max_credit)))
        else:
            ops.append(K(rng.randint(0, horizon + max_len)))
    return ops


EXAMPLE = [A(0, 10, 30), A(5, 8, 20), S(6, 25), K(6), K(3), K(9), A(0, 8, 10), S(2, 30), K(2), K(6), K(11), S(4, 50), K(4)]


def tests():
    rng = random.Random(8)
    t = [
        F("Example", EXAMPLE),
        F("Reported example", [A(10, 20, 100), K(15), A(5, 15, 50), K(12), S(12, 70), K(15), K(18)]),
        F("No grants", [K(5), S(5, 10), K(5)]),
        F("No checks", [A(0, 5, 10), S(1, 3)]),
        F("Inclusive window", [A(5, 10, 7), K(4), K(5), K(10), K(11), S(10, 2), K(5), S(11, 100), K(10)]),
        F("Single-instant grant", [A(3, 3, 9), K(2), K(3), K(4), S(3, 4), K(3)]),
        F("Earliest end first, ties go to the earlier grant", [A(0, 50, 10), A(0, 20, 10), A(0, 20, 10), S(5, 15), K(20), K(21),
                                                               S(15, 10), K(15), K(30)]),
        F("Overdraft takes what's there and stops", [A(0, 10, 5), A(0, 10, 5), S(4, 100), K(4), A(0, 10, 3), K(4), S(4, 1), K(9)]),
        F("Times go backward", [A(100, 200, 40), S(150, 10), A(0, 50, 25), K(120), K(10), S(10, 30), K(40), K(160)]),
        F("Grant that is only live where nobody looks", [A(1, 2, 10), A(0, 100, 5), S(50, 3), K(50), K(1)]),
        F("Large amounts", [A(0, 10 ** 9, 10 ** 9), A(0, 10 ** 9, 10 ** 9), S(10 ** 9, 10 ** 9 + 1), K(0), K(10 ** 9)]),
    ]
    for i in range(4):
        t.append(F(f"Random #{i + 1}", random_ops(rng, 60, 30, 15), hidden=True))
    for i in range(2):
        t.append(F(f"Random, wide windows #{i + 1}", random_ops(rng, 300, 200, 400), hidden=True))
    t.append(F("80k ops, long overlapping windows", random_ops(rng, 80000, 10 ** 6, 10 ** 6, 1000), tag="Follow-up", hidden=True))
    t.append(F("60k ops, short windows", random_ops(rng, 60000, 10 ** 9, 10 ** 5), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return F(f"{n} ops", random_ops(random.Random(n), n, 10 ** 6, 10 ** 6, 1000), tag="Follow-up")


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of operations"}
