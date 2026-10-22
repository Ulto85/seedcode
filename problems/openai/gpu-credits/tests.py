import random
from engine.spec import cls

C_NAME = "GPUCredits"


def C(name, ops, **kw):
    return cls(name, C_NAME, [], ops, **kw)


def add(a, t, e): return ["add_credit", [a, t, e]]
def sub(a, t): return ["subtract", [a, t]]
def bal(t): return ["get_balance", [t]]


def in_order_ops(rng, n, step=3):
    """Random calls with non-decreasing timestamps. Grants outpace spending, so overdrafts are rare."""
    ops, t, spent_at_t = [add(20, 0, 50)], 0, False
    for _ in range(n):
        step_t = rng.randint(0, step)
        t += step_t
        spent_at_t = spent_at_t and step_t == 0
        r = rng.random()
        if r < 0.4:
            if spent_at_t:          # Part 1 promise: no grant after a subtraction at the same timestamp
                t, spent_at_t = t + 1, False
            ops.append(add(rng.randint(5, 40), t, rng.randint(5, 300)))
        elif r < 0.65:
            ops.append(sub(rng.randint(1, 12), t))
            spent_at_t = True
        else:
            ops.append(bal(t))
    return ops


def shuffled_ops(rng, n, horizon):
    ops = []
    for _ in range(n):
        r = rng.random()
        t = rng.randint(0, horizon)
        if r < 0.4:
            ops.append(add(rng.randint(5, 40), t, rng.randint(5, horizon)))
        elif r < 0.6:
            ops.append(sub(rng.randint(1, 15), t))
        else:
            ops.append(bal(rng.randint(0, horizon + 20)))
    return ops


def tests():
    rng = random.Random(7)
    t = [
        C("Example", [add(10, 0, 30), add(5, 10, 10), sub(7, 15), bal(15), bal(25), bal(30), sub(1, 40), bal(40)]),
        C("Empty ledger", [bal(0), bal(100)]),
        C("Expiry is exclusive", [add(4, 5, 10), bal(4), bal(5), bal(14), bal(15)]),
        C("Spend soonest-expiring first", [add(10, 0, 100), add(10, 0, 20), sub(15, 5), bal(5), bal(19), bal(20), bal(99)]),
        C("Spend at the moment of granting", [add(3, 7, 5), sub(3, 7), bal(7), add(2, 8, 5), bal(8)]),
        C("Can't spend at the moment of expiry", [add(5, 0, 10), sub(1, 10), bal(10), bal(50)]),
        C("Overdraft is sticky", [add(5, 0, 100), sub(3, 10), bal(10), sub(3, 20), bal(20), add(100, 30, 100), bal(30)]),
        C("Exact spend to zero is fine", [add(5, 0, 100), add(5, 1, 100), sub(10, 2), bal(2), bal(50)]),
        C("Partial use across many grants", [add(1, 0, 10), add(2, 0, 11), add(3, 0, 12), add(4, 0, 13), sub(4, 5), bal(5), bal(10), bal(11), bal(12), bal(13)]),
        C("Follow-up example", [add(5, 0, 100), sub(8, 10), bal(20), add(5, 5, 100), bal(20), bal(3)], tag="Follow-up"),
        C("Late subtraction changes the past", [add(10, 0, 50), bal(30), sub(4, 10), bal(30), bal(5), sub(20, 40), bal(30), bal(45)], tag="Follow-up"),
        C("Query the future, then the past", [add(6, 10, 10), bal(100), bal(15), bal(9), bal(19), bal(20)], tag="Follow-up"),
        C("Late grant at the same timestamp as a spend", [add(2, 0, 100), sub(5, 10), bal(10), add(3, 10, 1), bal(10), bal(11)], tag="Follow-up"),
        C("Late spend picks soonest expiry at its own time", [add(10, 0, 100), add(10, 20, 10), sub(5, 25), bal(40), sub(12, 5), bal(40), bal(25)], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random in-order #{s + 1}", in_order_ops(rng, 80), hidden=True))
    for s in range(3):
        t.append(C(f"Random out-of-order #{s + 1}", shuffled_ops(rng, 80, 100), tag="Follow-up", hidden=True))
    t.append(C("40k in-order calls", in_order_ops(rng, 40000), hidden=True))
    t.append(C("1500 out-of-order calls", shuffled_ops(rng, 1500, 2000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} calls", in_order_ops(random.Random(n), n))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of calls (in time order)"}
