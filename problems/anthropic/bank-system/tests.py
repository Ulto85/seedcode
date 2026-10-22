import random
from engine.spec import cls

B = "Bank"


def ops_with_time(raw, start=1, step=1):
    """raw: [method, [args without timestamp]] -> prepends strictly increasing timestamps."""
    out, t = [], start
    for m, a in raw:
        out.append([m, [t] + list(a)])
        t += step
    return out


def C(name, raw, **kw):
    return cls(name, B, [], ops_with_time(raw), **kw)


def random_ops(rng, n, level, n_ids=8):
    ids = [f"acc{i}" for i in range(n_ids)]
    out, t, made = [], 0, 0
    for _ in range(n):
        t += rng.choice([1, 1, 2, 5, 20, 100, 400])
        r = rng.random()
        if r < 0.15 or made < 2:
            m, a = "create_account", [rng.choice(ids)]
            made += 1
        elif r < 0.35:
            m, a = "deposit", [rng.choice(ids), rng.randint(1, 500)]
        elif r < 0.5:
            m, a = "pay", [rng.choice(ids), rng.randint(1, 400)]
        elif r < 0.58:
            m, a = "top_activity", [rng.randint(1, n_ids)]
        elif level >= 3 and r < 0.72:
            m, a = "transfer", [rng.choice(ids), rng.choice(ids), rng.randint(1, 300)]
        elif level >= 3 and r < 0.84:
            m, a = "accept_transfer", [rng.choice(ids), f"transfer{rng.randint(1, max(1, n // 8))}"]
        elif level >= 4 and r < 0.9:
            m, a = "merge_accounts", [rng.choice(ids), rng.choice(ids)]
        elif level >= 4:
            m, a = "get_balance", [rng.choice(ids), rng.randint(0, t)]
        else:
            m, a = "deposit", [rng.choice(ids), rng.randint(1, 500)]
        out.append([m, [t] + a])
    return out


EXAMPLE = [
    ["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 500]], ["pay", ["a", 200]],
    ["transfer", ["a", "b", 100]], ["top_activity", [2]], ["accept_transfer", ["b", "transfer1"]],
    ["top_activity", [2]], ["merge_accounts", ["a", "b"]], ["get_balance", ["b", 8]], ["get_balance", ["b", 9]],
    ["get_balance", ["a", 8]], ["get_balance", ["a", 9]],
]


def tests():
    rng = random.Random(2024)
    t = [
        cls("Example (all levels)", B, [], ops_with_time(EXAMPLE), tag="Level 4"),
        C("Create, deposit, pay", [["create_account", ["x"]], ["create_account", ["x"]], ["deposit", ["x", 100]],
                                   ["pay", ["x", 30]], ["deposit", ["x", 5]]], tag="Level 1"),
        C("Missing account / insufficient funds", [["deposit", ["ghost", 10]], ["pay", ["ghost", 1]], ["create_account", ["y"]],
                                                   ["pay", ["y", 1]], ["deposit", ["y", 50]], ["pay", ["y", 51]], ["pay", ["y", 50]]], tag="Level 1"),
        C("Top activity ties + zero activity", [["create_account", ["c"]], ["create_account", ["a"]], ["create_account", ["b"]],
                                                ["create_account", ["d"]], ["deposit", ["c", 100]], ["deposit", ["b", 60]], ["pay", ["b", 40]],
                                                ["top_activity", [3]], ["top_activity", [10]]], tag="Level 2"),
        C("Failed ops add no activity", [["create_account", ["a"]], ["deposit", ["a", 10]], ["pay", ["a", 999]], ["top_activity", [1]]], tag="Level 2"),
        C("Transfer validation", [["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 100]],
                                  ["transfer", ["a", "a", 10]], ["transfer", ["a", "zzz", 10]], ["transfer", ["a", "b", 101]],
                                  ["transfer", ["a", "b", 40]], ["pay", ["a", 61]], ["top_activity", [2]]], tag="Level 3"),
        C("Accept: wrong account, twice, unknown id", [["create_account", ["a"]], ["create_account", ["b"]], ["deposit", ["a", 100]],
                                                       ["transfer", ["a", "b", 30]], ["accept_transfer", ["a", "transfer1"]],
                                                       ["accept_transfer", ["b", "transfer9"]], ["accept_transfer", ["b", "transfer1"]],
                                                       ["accept_transfer", ["b", "transfer1"]], ["deposit", ["b", 1]], ["top_activity", [2]]], tag="Level 3"),
        cls("Expiry refunds the source (boundary)", B, [], [
            ["create_account", [1, "a"]], ["create_account", [2, "b"]], ["deposit", [3, "a", 100]],
            ["transfer", [10, "a", "b", 60]], ["transfer", [20, "a", "b", 40]], ["pay", [1009, "a", 1]],
            ["accept_transfer", [1010, "b", "transfer1"]], ["deposit", [1011, "a", 5]],
            ["accept_transfer", [1019, "b", "transfer2"]], ["deposit", [1020, "b", 1]], ["top_activity", [1021, 2]]], tag="Level 3"),
        C("Merge rules", [["create_account", ["a"]], ["create_account", ["b"]], ["merge_accounts", ["a", "a"]],
                          ["merge_accounts", ["a", "nope"]], ["deposit", ["b", 70]], ["merge_accounts", ["a", "b"]],
                          ["deposit", ["b", 5]], ["create_account", ["b"]], ["deposit", ["b", 5]], ["top_activity", [5]],
                          ["get_balance", ["a", 7]]], tag="Level 4"),
        cls("Merge moves pending transfers", B, [], [
            ["create_account", [1, "a"]], ["create_account", [2, "b"]], ["create_account", [3, "c"]],
            ["deposit", [4, "b", 100]], ["deposit", [5, "c", 100]],
            ["transfer", [6, "b", "c", 10]], ["transfer", [7, "c", "b", 20]], ["transfer", [8, "b", "a", 30]],
            ["merge_accounts", [9, "a", "b"]], ["get_balance", [10, "a", 9]],
            ["accept_transfer", [11, "a", "transfer2"]], ["accept_transfer", [12, "b", "transfer2"]],
            ["get_balance", [2000, "a", 1999]], ["get_balance", [2001, "c", 2000]], ["top_activity", [2002, 3]]], tag="Level 4"),
        cls("Balance history: before creation, at merge", B, [], [
            ["create_account", [5, "a"]], ["get_balance", [6, "a", 4]], ["get_balance", [7, "a", 5]],
            ["create_account", [8, "b"]], ["deposit", [9, "b", 9]], ["merge_accounts", [10, "a", "b"]],
            ["create_account", [20, "b"]], ["get_balance", [21, "b", 9]], ["get_balance", [22, "b", 10]],
            ["get_balance", [23, "b", 15]], ["get_balance", [24, "b", 20]], ["get_balance", [25, "zz", 1]]], tag="Level 4"),
        cls("Balance history sees a refund at expiry time", B, [], [
            ["create_account", [1, "a"]], ["create_account", [2, "b"]], ["deposit", [3, "a", 50]],
            ["transfer", [4, "a", "b", 50]], ["get_balance", [5000, "a", 1003]], ["get_balance", [5001, "a", 1004]]], tag="Level 4"),
    ]
    for lvl in (1, 2, 3, 4):
        t.append(cls(f"Random level {lvl}", B, [], random_ops(rng, 80, lvl), tag=f"Level {lvl}", hidden=True))
    t.append(cls("Random level 4 (long)", B, [], random_ops(rng, 400, 4, n_ids=12), tag="Level 4", hidden=True))
    t.append(cls("40k ops, 2000 accounts", B, [], random_ops(rng, 40000, 4, n_ids=2000), tag="Level 4", hidden=True))
    return t


def scale(n):
    return cls(f"n={n}", B, [], random_ops(random.Random(n), n, 4, n_ids=100))


SCALE = {"sizes": [500, 1000, 2000, 4000, 8000, 16000], "label": "n = number of operations", "per_op": False}
