import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "OrderBook", [], ops, **kw)


EXAMPLE = [
    ["place", ["s1", "sell", 101, 5]], ["place", ["s2", "sell", 100, 2]], ["place", ["s3", "sell", 101, 3]],
    ["best_ask", []], ["place", ["b1", "buy", 101, 6]], ["best_ask", []], ["place", ["b2", "buy", 99, 4]],
    ["cancel", ["s1"]],
]


def random_ops(rng, n, follow_up, mid=1000, spread=20):
    ops, ids, k = [], [], 0
    for _ in range(n):
        r = rng.random()
        if r < 0.55:
            side = rng.choice(["buy", "sell"])
            # buys centred slightly below mid, sells slightly above, so some cross and some rest
            p = mid + rng.randint(-spread, spread // 2) if side == "buy" else mid + rng.randint(-spread // 2, spread)
            oid = f"o{k}"; k += 1; ids.append(oid)
            if rng.random() < 0.03:
                oid = rng.choice(ids)                 # reused id -> None
            ops.append(["place", [oid, side if rng.random() > 0.02 else "hold", p, rng.randint(0, 20) if rng.random() < 0.05 else rng.randint(1, 20)]])
        elif r < 0.75 and ids:
            ops.append(["cancel", [rng.choice(ids + ["ghost"])]])
        elif r < 0.85:
            ops.append([rng.choice(["best_bid", "best_ask"]), []])
        elif follow_up and r < 0.9:
            oid = f"o{k}"; k += 1; ids.append(oid)
            ops.append(["place_market", [oid, rng.choice(["buy", "sell"]), rng.randint(1, 40)]])
        elif follow_up:
            ops.append(["depth", [rng.choice(["buy", "sell"]), rng.randint(0, 6)]])
        else:
            ops.append([rng.choice(["best_bid", "best_ask"]), []])
    return ops


def tests():
    rng = random.Random(100)
    t = [
        C("Example (Part 1)", EXAMPLE + [["best_bid", []], ["best_ask", []]]),
        C("Empty book", [["best_bid", []], ["best_ask", []], ["cancel", ["x"]]]),
        C("No cross: both rest", [["place", ["b", "buy", 99, 5]], ["place", ["s", "sell", 100, 5]],
                                  ["best_bid", []], ["best_ask", []]]),
        C("Exact fill empties both", [["place", ["s", "sell", 100, 5]], ["place", ["b", "buy", 100, 5]],
                                      ["best_bid", []], ["best_ask", []], ["cancel", ["s"]], ["cancel", ["b"]]]),
        C("Trade at resting price", [["place", ["b1", "buy", 105, 3]], ["place", ["s1", "sell", 100, 5]],
                                     ["best_ask", []], ["best_bid", []]]),
        C("Time priority within a level", [["place", ["b1", "buy", 50, 2]], ["place", ["b2", "buy", 50, 2]],
                                           ["place", ["b3", "buy", 51, 1]], ["place", ["s1", "sell", 50, 4]],
                                           ["best_bid", []]]),
        C("Sweep several levels then rest", [["place", ["s1", "sell", 10, 1]], ["place", ["s2", "sell", 11, 1]],
                                             ["place", ["s3", "sell", 12, 1]], ["place", ["b1", "buy", 11, 5]],
                                             ["best_bid", []], ["best_ask", []]]),
        C("Invalid orders", [["place", ["a", "hold", 10, 1]], ["place", ["a", "buy", 0, 1]], ["place", ["a", "buy", 10, 0]],
                             ["place", ["a", "buy", 10, 1]], ["place", ["a", "sell", 10, 1]], ["best_bid", []]]),
        C("Ids never reused after fill/cancel", [["place", ["x", "sell", 10, 1]], ["place", ["y", "buy", 10, 1]],
                                                 ["place", ["x", "sell", 10, 1]], ["place", ["z", "buy", 5, 1]],
                                                 ["cancel", ["z"]], ["place", ["z", "buy", 5, 1]], ["best_bid", []]]),
        C("Cancel skipped during matching", [["place", ["s1", "sell", 10, 2]], ["place", ["s2", "sell", 10, 2]],
                                             ["place", ["s3", "sell", 10, 2]], ["cancel", ["s2"]], ["best_ask", []],
                                             ["place", ["b", "buy", 10, 3]], ["best_ask", []], ["cancel", ["s1"]],
                                             ["cancel", ["s3"]], ["best_ask", []]]),
        C("Example (follow-up)", EXAMPLE + [["depth", ["sell", 5]], ["place_market", ["m1", "sell", 10]],
                                            ["best_bid", []]], tag="Follow-up"),
        C("Market order on empty book", [["place_market", ["m", "buy", 5]], ["place_market", ["m", "buy", 5]],
                                         ["place", ["m", "sell", 5, 1]], ["best_ask", []]], tag="Follow-up"),
        C("Market sweeps all levels", [["place", ["s1", "sell", 10, 1]], ["place", ["s2", "sell", 30, 1]],
                                       ["place", ["s3", "sell", 20, 1]], ["place_market", ["m", "buy", 2]],
                                       ["depth", ["sell", 3]], ["place_market", ["m2", "buy", 0]]], tag="Follow-up"),
        C("Depth ordering and limits", [["place", ["b1", "buy", 10, 1]], ["place", ["b2", "buy", 12, 2]],
                                        ["place", ["b3", "buy", 11, 3]], ["place", ["b4", "buy", 12, 4]],
                                        ["depth", ["buy", 2]], ["depth", ["buy", 10]], ["depth", ["buy", 0]],
                                        ["depth", ["sell", 3]], ["depth", ["both", 3]]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random book #{s + 1}", random_ops(rng, 80, False, spread=6), hidden=True))
    for s in range(2):
        t.append(C(f"Random with market orders #{s + 1}", random_ops(rng, 80, True, spread=6), tag="Follow-up", hidden=True))
    t.append(C("100k ops, wide book", random_ops(rng, 100000, False, mid=500000, spread=20000), hidden=True))
    t.append(C("100k ops with market + depth", random_ops(rng, 100000, True, mid=500000, spread=5000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, False, mid=500000, spread=n // 4))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of operations"}
