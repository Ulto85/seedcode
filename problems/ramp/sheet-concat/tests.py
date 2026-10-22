import random
import re
from engine.spec import fn

F = "run_sheet"
REF = re.compile(r"[A-Z][0-9]+")
EX = [["set", "C1", "Hello"], ["set", "C2", " world"], ["set", "A1", "=C1C2"], ["get", "A1"], ["set", "C1", "Bye"],
      ["get", "A1"], ["get", "B7"], ["set", "B1", "=A1B1"], ["get", "B1"], ["get", "A1"]]


def S(c, raw): return ["set", c, raw]
def G(c): return ["get", c]


def _lengths(raw):
    """Value length of every cell (None if it reaches a cycle). Used to keep random outputs small."""
    memo, on = {}, set()

    def go(c):
        if c in memo: return memo[c]
        r = raw.get(c, "")
        if not r.startswith("="):
            memo[c] = len(r); return memo[c]
        if c in on: return None
        on.add(c)
        tot = 0
        for x in REF.findall(r):
            v = go(x)
            if v is None:
                tot = None
                break
            tot += v
        on.discard(c)
        memo[c] = tot
        return tot
    return [go(c) for c in raw]


def rand_ops(rng, n, pool, limit=200, p_get=0.45):
    raw, ops = {}, []
    words = ["a", "b", "x", "ab", " ", "Hi", "CYCLE", "", "=", "7"]
    while len(ops) < n:
        c = rng.choice(pool)
        if rng.random() < p_get:
            ops.append(G(c)); continue
        if rng.random() < 0.55:
            k = rng.choice([1, 1, 2, 2, 3])
            cand = "=" + "".join(rng.choice(pool) for _ in range(k))
        else:
            cand = rng.choice(words)
            if cand == "=": cand = "x=y"
        for v in (cand, ""):
            old = raw.get(c)
            raw[c] = v
            if all(L is None or L <= limit for L in _lengths(raw)):
                ops.append(S(c, v)); break
            if old is None: del raw[c]
            else: raw[c] = old
    return ops


def doubling_chain(depth):
    """C1 = C2C2, C2 = C3C3, ..., last = "" : 2^depth paths, empty result. Needs a per-read memo."""
    cells = [f"{chr(ord('A') + i // 100)}{i % 100 + 1}" for i in range(depth + 1)]
    ops = [S(cells[i], "=" + cells[i + 1] * 2) for i in range(depth)]
    ops += [S(cells[depth], ""), G(cells[0])]
    return ops, cells


def deep_chain(depth):
    cells = [f"{chr(ord('A') + i // 100)}{i % 100 + 1}" for i in range(depth + 1)]
    ops = [S(cells[i], "=" + cells[i + 1]) for i in range(depth)] + [S(cells[depth], "end")]
    return ops, cells


def tests():
    rng = random.Random(9)
    t = [
        fn("Example", F, EX),
        fn("Unset cell is empty", F, [G("Z100"), S("A1", "=B1C1"), G("A1")]),
        fn("Literals kept exactly", F, [S("A1", "  padded "), S("A2", "CYCLE"), S("A3", ""), G("A1"), G("A2"), G("A3")]),
        fn("Multi-digit refs and repeats", F, [S("A10", "x"), S("B2", "y"), S("C3", "=A10B2A10"), G("C3")]),
        fn("Formula of formulas, update propagates", F, [S("A1", "1"), S("B1", "=A1A1"), S("C1", "=B1A1"), G("C1"), S("A1", "22"), G("C1")]),
        fn("Self reference", F, [S("A1", "=A1"), G("A1")]),
        fn("Two-cell cycle, then broken", F, [S("A1", "=B1B1"), S("B1", "=A1"), G("A1"), G("B1"), S("B1", "ok"), G("A1")]),
        fn("Reaching a cycle through a chain", F, [S("A1", "=B1"), S("B1", "=C1"), S("C1", "=D1"), S("D1", "=B1"), S("E1", "fine"), G("A1"), G("E1")]),
        fn("Diamond is not a cycle", F, [S("D1", "d"), S("B1", "=D1"), S("C1", "=D1"), S("A1", "=B1C1D1"), G("A1")]),
        fn("Formula replaced by literal", F, [S("A1", "=A1"), G("A1"), S("A1", "plain"), G("A1")]),
    ]
    for s in range(4):
        pool = [f"{c}{r}" for c in "ABC" for r in range(1, 4)]
        t.append(fn(f"Random sheet #{s + 1}", F, rand_ops(rng, 60, pool), hidden=True))
    ops, cells = doubling_chain(60)
    t.append(fn("Exponential paths: memoize within a read", F, ops, hidden=True))
    ops, cells = deep_chain(400)
    ops += [G(cells[0]), S(cells[200], "=" + cells[0]), G(cells[0]), G(cells[300]), S(cells[200], "mid"), G(cells[0])]
    t.append(fn("400-deep chain, cycle in the middle", F, ops, hidden=True))
    ops, cells = deep_chain(300)
    ops += [G(cells[rng.randrange(300)]) for _ in range(3000)]
    t.append(fn("Many reads of a deep chain", F, ops, hidden=True))
    pool = [f"{c}{r}" for c in "ABCDEFGH" for r in range(1, 6)]
    t.append(fn("8000 random ops", F, rand_ops(rng, 8000, pool), hidden=True))
    return t


def scale(n):
    pool = [f"{c}{r}" for c in "ABCDEFGH" for r in range(1, 5)]
    return fn(f"n={n}", F, rand_ops(random.Random(n), n, pool))


SCALE = {"sizes": [500, 1000, 2000, 4000, 8000, 16000], "label": "n = operations (32-cell sheet)"}
