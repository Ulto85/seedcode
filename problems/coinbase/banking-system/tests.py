import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "Bank", [], ops, **kw)


EXAMPLE = [
    ["create_account", ["alice"]], ["deposit", ["alice", 100]], ["create_account", ["bob"]],
    ["transfer", ["alice", "bob", 30]], ["transfer", ["bob", "alice", 50]],
]


def random_ops(rng, n, level, n_acc=8, top_rate=0.08):
    accs = [f"acc{i:03d}" for i in range(n_acc)]
    ops, clock, pids = [], 0, 0
    for i in range(n):
        r = rng.random()
        if r < 0.1 or i < n_acc // 2:
            ops.append(["create_account", [rng.choice(accs)]])
        elif r < 0.35:
            ops.append(["deposit", [rng.choice(accs + ["ghost"]), rng.choice([0, -5, 10, 50, 100, 250])]])
        elif r < 0.6:
            ops.append(["transfer", [rng.choice(accs), rng.choice(accs), rng.choice([0, 5, 20, 60, 150, 400])]])
        elif r < 0.65:
            ops.append(["get_balance", [rng.choice(accs + ["ghost"])]])
        elif level >= 2 and r < 0.65 + top_rate:
            ops.append(["top_spenders", [rng.randint(-1, 5)]])
        elif level >= 3 and r < 0.85:
            ops.append(["schedule_payment", [rng.choice(accs), rng.choice(accs), rng.choice([0, 10, 40, 120]),
                                             clock + rng.randint(-2, 30)]])
            pids += 1
        elif level >= 3 and r < 0.9 and pids:
            ops.append(["cancel_payment", [f"p{rng.randint(1, pids + 1)}"]])
        elif level >= 3:
            clock += rng.randint(-3, 15)
            ops.append(["process_until", [clock]])
            clock = max(clock, 0) if rng.random() < 0.5 else clock
        else:
            ops.append(["get_balance", [rng.choice(accs)]])
    return ops


def tests():
    rng = random.Random(3)
    t = [
        C("Example (Part 1)", EXAMPLE + [["get_balance", ["alice"]], ["get_balance", ["bob"]]]),
        C("Duplicate account", [["create_account", ["a"]], ["create_account", ["a"]], ["get_balance", ["a"]]]),
        C("Unknown accounts", [["deposit", ["x", 10]], ["get_balance", ["x"]], ["create_account", ["a"]],
                               ["transfer", ["a", "x", 0]], ["transfer", ["x", "a", 5]]]),
        C("Bad amounts and self-transfer", [["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 0]],
                                            ["deposit", ["a", -3]], ["deposit", ["a", 10]], ["transfer", ["a", "a", 5]],
                                            ["transfer", ["a", "b", 0]], ["transfer", ["a", "b", 11]],
                                            ["transfer", ["a", "b", 10]], ["get_balance", ["a"]], ["get_balance", ["b"]]]),
        C("Example (Part 2)", EXAMPLE + [["top_spenders", [5]]], tag="Part 2"),
        C("Top spenders ties + zero spenders", [["create_account", ["c"]], ["create_account", ["b"]], ["create_account", ["a"]],
                                               ["deposit", ["c", 100]], ["deposit", ["b", 100]],
                                               ["transfer", ["c", "a", 40]], ["transfer", ["b", "a", 40]],
                                               ["transfer", ["b", "c", 999]], ["top_spenders", [2]], ["top_spenders", [10]],
                                               ["top_spenders", [0]]], tag="Part 2"),
        C("Top spenders on empty bank", [["top_spenders", [3]]], tag="Part 2"),
        C("Example (follow-up)", EXAMPLE + [["schedule_payment", ["bob", "alice", 20, 10]],
                                            ["schedule_payment", ["alice", "bob", 500, 5]],
                                            ["schedule_payment", ["alice", "bob", 1, 0]],
                                            ["process_until", [10]], ["get_balance", ["bob"]], ["top_spenders", [1]]], tag="Follow-up"),
        C("Schedule validation", [["create_account", ["a"]], ["create_account", ["b"]],
                                  ["schedule_payment", ["a", "a", 5, 3]], ["schedule_payment", ["a", "z", 5, 3]],
                                  ["schedule_payment", ["a", "b", 0, 3]], ["schedule_payment", ["a", "b", 5, 3]],
                                  ["process_until", [3]], ["schedule_payment", ["a", "b", 5, 3]],
                                  ["schedule_payment", ["a", "b", 5, 4]]], tag="Follow-up"),
        C("Cancel and clock rules", [["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 50]],
                                     ["schedule_payment", ["a", "b", 10, 5]], ["schedule_payment", ["a", "b", 10, 5]],
                                     ["cancel_payment", ["p1"]], ["cancel_payment", ["p1"]], ["cancel_payment", ["p9"]],
                                     ["process_until", [4]], ["process_until", [3]], ["process_until", [4]],
                                     ["process_until", [5]], ["cancel_payment", ["p2"]], ["get_balance", ["b"]]], tag="Follow-up"),
        C("Same time -> scheduling order", [["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 15]],
                                            ["schedule_payment", ["a", "b", 10, 7]], ["schedule_payment", ["b", "a", 10, 3]],
                                            ["schedule_payment", ["a", "b", 10, 7]], ["process_until", [100]],
                                            ["get_balance", ["a"]], ["top_spenders", [2]]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random level 1 #{s + 1}", random_ops(rng, 50, 1), hidden=True))
    for s in range(2):
        t.append(C(f"Random level 2 #{s + 1}", random_ops(rng, 60, 2), tag="Part 2", hidden=True))
    for s in range(3):
        t.append(C(f"Random scheduled #{s + 1}", random_ops(rng, 80, 3), tag="Follow-up", hidden=True))
    t.append(C("100k ops, 5k accounts", random_ops(rng, 100000, 3, n_acc=5000, top_rate=0.01), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, 3, n_acc=200, top_rate=0.02), tag="Follow-up")


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of operations"}
