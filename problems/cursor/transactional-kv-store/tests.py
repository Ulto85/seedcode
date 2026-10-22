import random
from engine.spec import cls


def K(name, ops, **kw):
    return cls(name, "KVStore", [], ops, **kw)


def O(name, ops, **kw):
    return cls(name, "OCCStore", [], ops, tag="Follow-up", **kw)


def g(k): return ["get", [k]]
def s(k, v): return ["set", [k, v]]
def d(k): return ["delete", [k]]
B, C, R = ["begin", []], ["commit", []], ["rollback", []]


def tg(t, k): return ["get", [t, k]]
def ts(t, k, v): return ["set", [t, k, v]]
def td(t, k): return ["delete", [t, k]]
def tb(): return ["begin", []]
def tc(t): return ["commit", [t]]
def tr(t): return ["rollback", [t]]
def rd(k): return ["read", [k]]


KEYS = ["a", "b", "c", "d", "e"]


def rand_kv_ops(rng, n, keys, p_begin=0.12):
    ops = []
    for _ in range(n):
        r = rng.random()
        k = rng.choice(keys)
        if r < 0.3: ops.append(s(k, str(rng.randint(0, 99))))
        elif r < 0.55: ops.append(g(k))
        elif r < 0.65: ops.append(d(k))
        elif r < 0.65 + p_begin: ops.append(B)
        elif r < 0.9: ops.append(C)
        else: ops.append(R)
    return ops


def rand_occ_ops(rng, n, keys, max_open=4):
    ops, opened = [], 0
    for _ in range(n):
        r = rng.random()
        t = rng.randint(max(1, opened - max_open), opened + 1)
        k = rng.choice(keys)
        if r < 0.12 or opened == 0:
            ops.append(tb()); opened += 1
        elif r < 0.35: ops.append(tg(t, k))
        elif r < 0.6: ops.append(ts(t, k, str(rng.randint(0, 99))))
        elif r < 0.66: ops.append(td(t, k))
        elif r < 0.84: ops.append(tc(t))
        elif r < 0.9: ops.append(tr(t))
        else: ops.append(rd(k))
    return ops


def deep_nesting(depth, gets):
    ops = [s("root", "0")] + [s(f"k{i}", str(i)) for i in range(200)]
    for i in range(depth):
        ops += [B, s(f"n{i}", str(i))]
    ops += [g("root"), g("k5")] * (gets // 2)
    ops += [s("root", "deep"), R, g("root"), g(f"n{depth - 1}"), g(f"n{depth - 2}")]
    ops += [C] * (depth - 1) + [g("root"), g("n0"), g(f"n{depth - 2}"), C, C]
    return ops


def big_store_short_txns(keys, txns):
    """Copying the whole store on begin() is O(keys) per transaction."""
    ops = [s(f"k{i}", "v") for i in range(keys)]
    for i in range(txns):
        k = f"k{(i * 7919) % keys}"
        ops += [B, g(k), s(k, str(i)), d(f"k{(i * 104729) % keys}")]
        ops.append(C if i % 3 else R)
    ops += [g("k0"), g("k1"), g(f"k{keys - 1}")]
    return ops


def tests():
    rng = random.Random(8)
    t = [
        K("Basic get/set/delete", [g("a"), s("a", "1"), g("a"), s("a", "2"), g("a"), d("a"), g("a"), d("a")]),
        K("Rollback discards writes", [s("a", "1"), B, s("a", "2"), s("b", "x"), g("a"), R, g("a"), g("b")]),
        K("Commit keeps writes", [B, s("a", "1"), d("zzz"), C, g("a"), R, C]),
        K("Commit/rollback with nothing open", [C, R, s("a", "1"), C, g("a")]),
        K("Nested: inner commit, outer rollback", [s("a", "base"), B, s("a", "outer"), B, s("a", "inner"), s("b", "new"), C, g("a"), R, g("a"), g("b")]),
        K("Nested: inner rollback keeps outer", [B, s("a", "1"), B, s("a", "2"), d("a"), g("a"), R, g("a"), C, g("a")]),
        K("Delete inside a transaction, then rollback", [s("a", "1"), s("b", "2"), B, d("a"), s("b", "3"), d("b"), g("a"), g("b"), R, g("a"), g("b")]),
        K("Set the same key repeatedly", [s("a", "0"), B, s("a", "1"), s("a", "2"), B, s("a", "3"), C, s("a", "4"), R, g("a")]),
        O("Example: write-write conflict", [tb(), tb(), ts(1, "x", "a"), ts(2, "x", "b"), tc(1), tc(2), rd("x")]),
        O("Snapshot isolation", [tb(), ts(1, "x", "1"), tc(1), tb(), tb(), ts(2, "x", "2"), tg(3, "x"), tc(2), tg(3, "x"), rd("x"), tb(), tg(4, "x")]),
        O("Own writes are visible, others' uncommitted are not", [tb(), tb(), ts(1, "k", "v"), tg(1, "k"), tg(2, "k"), rd("k"), td(1, "k"), tg(1, "k")]),
        O("Read-write conflict", [tb(), tb(), tg(1, "x"), ts(1, "y", "1"), ts(2, "x", "9"), tc(2), tc(1), rd("y")]),
        O("Disjoint keys both commit", [tb(), tb(), ts(1, "a", "1"), ts(2, "b", "2"), tg(1, "c"), tg(2, "d"), tc(2), tc(1), rd("a"), rd("b")]),
        O("Reading a missing key still conflicts", [tb(), tg(1, "x"), ts(1, "y", "1"), tb(), ts(2, "x", "new"), tc(2), tc(1)]),
        O("Finished or unknown transactions", [tb(), tc(1), tc(1), ts(1, "a", "1"), tg(1, "a"), tr(1), tc(7), tb(), tr(2), tc(2), td(2, "a"), rd("a")]),
        O("Rollback leaves no trace", [tb(), ts(1, "a", "1"), tr(1), tb(), tg(2, "a"), ts(2, "a", "2"), tc(2), rd("a")]),
        O("Delete commits and conflicts like a write", [tb(), ts(1, "a", "1"), tc(1), tb(), tb(), td(2, "a"), tg(3, "a"), tc(2), rd("a"), ts(3, "b", "x"), tc(3), rd("b")]),
        O("Started after the commit: no conflict", [tb(), ts(1, "x", "1"), tc(1), tb(), tg(2, "x"), ts(2, "x", "2"), tc(2), rd("x")]),
    ]
    for i in range(3):
        t.append(K(f"Random nested ops #{i + 1}", rand_kv_ops(rng, 80, KEYS), hidden=True))
    for i in range(3):
        t.append(O(f"Random concurrent txns #{i + 1}", rand_occ_ops(rng, 80, KEYS), hidden=True))
    t.append(K("Nesting 3,000 deep with 60,000 reads", deep_nesting(3000, 60000), hidden=True))
    t.append(K("100,000 keys, 10,000 short transactions", big_store_short_txns(100000, 10000), hidden=True))
    t.append(O("Long-lived snapshot over 20,000 commits", long_snapshot(20000), hidden=True))
    return t


def long_snapshot(n):
    """One transaction reads old values while n small transactions commit over 2000 keys."""
    ops = [tb()] + [ts(1, f"k{i}", "0") for i in range(2000)] + [tc(1), tb()]   # txn 2 is long-lived
    tid = 2
    for i in range(n):
        tid += 1
        k = f"k{i % 2000}"
        ops += [tb(), tg(tid, k), ts(tid, k, str(i)), tc(tid)]
        if i % 50 == 0:
            ops.append(tg(2, k))
    ops += [tg(2, "k7"), ts(2, "k7", "late"), tc(2), rd("k7"), rd("k1999")]
    return ops


def scale(n):
    rng = random.Random(n)
    return O(f"{n} ops", rand_occ_ops(rng, n, [f"k{i}" for i in range(max(5, n // 10))], max_open=50))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of operations"}
