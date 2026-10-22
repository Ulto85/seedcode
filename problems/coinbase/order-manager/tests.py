import random
from engine.spec import cls

SYMS = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"]


def C(name, ops, **kw):
    return cls(name, "OrderManager", [], ops, **kw)


def random_ops(rng, n, follow_up=True, n_syms=4):
    ids = []
    ops = []
    syms = SYMS[:n_syms] if n_syms <= 4 else [f"C{i}-USD" for i in range(n_syms)]
    for _ in range(n):
        r = rng.random()
        if r < 0.3 or not ids:
            oid = f"o{len(ids)}" if rng.random() < 0.95 or not ids else rng.choice(ids)
            if oid not in ids:
                ids.append(oid)
            side = rng.choice(["buy", "sell", "buy", "sell", "hold"])
            ops.append(["create", [oid, rng.choice(syms), side, rng.choice([1, 2, 5, 10, 0, -3])]])
        elif r < 0.45:
            ops.append(["pause", [rng.choice(ids)]])
        elif r < 0.6:
            ops.append(["resume", [rng.choice(ids)]])
        elif r < 0.68:
            ops.append(["cancel", [rng.choice(ids + ["nope"])]])
        elif r < 0.78:
            ops.append(["get", [rng.choice(ids + ["nope"])]])
        elif r < 0.9 or not follow_up:
            ops.append(["count", [rng.choice(["LIVE", "PAUSED", "CANCELLED"])]])
        elif r < 0.93:
            ops.append(["cancel_all", [rng.choice(syms)]])
        else:
            ops.append(["live_orders", [rng.choice(syms)]])
    return ops


def tests():
    rng = random.Random(7)
    t = [
        C("Example", [["create", ["o1", "BTC-USD", "buy", 2]], ["create", ["o2", "BTC-USD", "sell", 1]],
                      ["create", ["o1", "ETH-USD", "buy", 5]], ["pause", ["o1"]], ["resume", ["o2"]],
                      ["count", ["LIVE"]], ["get", ["o1"]], ["get", ["o2"]]]),
        C("Full lifecycle", [["create", ["a", "ETH-USD", "sell", 3]], ["pause", ["a"]], ["resume", ["a"]],
                             ["pause", ["a"]], ["cancel", ["a"]], ["get", ["a"]], ["count", ["CANCELLED"]],
                             ["count", ["PAUSED"]], ["count", ["LIVE"]]]),
        C("Illegal transitions", [["create", ["a", "BTC-USD", "buy", 1]], ["resume", ["a"]], ["pause", ["a"]],
                                  ["pause", ["a"]], ["cancel", ["a"]], ["cancel", ["a"]], ["resume", ["a"]],
                                  ["pause", ["a"]], ["get", ["a"]]]),
        C("Unknown ids", [["get", ["x"]], ["pause", ["x"]], ["resume", ["x"]], ["cancel", ["x"]], ["count", ["LIVE"]]]),
        C("Bad create input", [["create", ["a", "BTC-USD", "hold", 1]], ["create", ["b", "BTC-USD", "buy", 0]],
                               ["create", ["c", "BTC-USD", "sell", -4]], ["create", ["d", "BTC-USD", "BUY", 1]],
                               ["get", ["a"]], ["count", ["LIVE"]]]),
        C("Cancelled id can't be reused", [["create", ["a", "BTC-USD", "buy", 1]], ["cancel", ["a"]],
                                           ["create", ["a", "BTC-USD", "buy", 1]], ["get", ["a"]]]),
        C("Count of unknown state", [["create", ["a", "BTC-USD", "buy", 1]], ["count", ["FILLED"]], ["count", ["live"]]]),
        C("Cancel all for a symbol", [["create", ["a", "BTC-USD", "buy", 1]], ["create", ["b", "ETH-USD", "buy", 1]],
                                      ["create", ["c", "BTC-USD", "sell", 2]], ["create", ["d", "BTC-USD", "sell", 2]],
                                      ["pause", ["c"]], ["cancel", ["d"]], ["cancel_all", ["BTC-USD"]],
                                      ["get", ["a"]], ["get", ["c"]], ["get", ["b"]], ["count", ["CANCELLED"]],
                                      ["cancel_all", ["BTC-USD"]], ["cancel_all", ["XRP-USD"]]], tag="Follow-up"),
        C("Live orders keep creation order", [["create", ["a", "BTC-USD", "buy", 1]], ["create", ["b", "BTC-USD", "buy", 1]],
                                              ["create", ["c", "BTC-USD", "buy", 1]], ["pause", ["a"]],
                                              ["live_orders", ["BTC-USD"]], ["resume", ["a"]],
                                              ["live_orders", ["BTC-USD"]], ["cancel", ["b"]],
                                              ["live_orders", ["BTC-USD"]], ["live_orders", ["ETH-USD"]]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random ops #{s + 1}", random_ops(rng, 60, follow_up=False), hidden=True))
    for s in range(2):
        t.append(C(f"Random follow-up ops #{s + 1}", random_ops(rng, 80), tag="Follow-up", hidden=True))
    t.append(C("200k ops", random_ops(rng, 200000, follow_up=False), hidden=True))
    t.append(C("100k ops, 500 symbols", random_ops(rng, 100000, n_syms=500), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, follow_up=False))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of operations"}
