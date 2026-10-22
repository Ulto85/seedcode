import random
from engine.spec import fn


def gen(rng, n, m, gap, proc):
    q, t = [], 0
    for _ in range(n):
        t += rng.randint(0, gap)
        q.append(t)
    p = [rng.randint(1, proc) for _ in range(n)]
    return m, q, p


def S(name, m, q, p, **kw):
    return fn(name, "indexer_stats", m, q, p, **kw)


def T(name, m, q, p, k, **kw):
    return fn(f"Top-k: {name}", "top_indexers", m, q, p, k, tag="Follow-up", float=True, **kw)


def tests():
    rng = random.Random(11)
    ex1 = (3, [1, 2, 3, 7], [5, 4, 3, 2])
    ex2 = (3, [0, 0, 0, 1, 2, 5], [1, 9, 9, 4, 3, 2])
    t = [
        S("Example", *ex1),
        S("Example with a drop", *ex2),
        S("One indexer, second doc dropped", 1, [1, 2], [10, 5]),
        S("No documents", 4, [], []),
        S("Free again at exactly s + p", 2, [0, 5, 5], [5, 5, 5]),
        S("Start index ignores earlier drops", 2, [0, 0, 0, 0, 10], [100, 100, 1, 1, 1]),
        S("Wrap-around past the last indexer", 4, [0, 0, 0, 0, 3, 4], [9, 9, 2, 9, 1, 1]),
        S("Tie on busiest goes to smaller id", 3, [0, 10, 20], [1, 1, 1]),
        S("Burst at one timestamp", 3, [5] * 7, [1] * 7),
        T("Follow-up example k=2", *ex1, 2),
        T("Follow-up example k=1", *ex1, 1),
        T("Zero-count indexers are ranked too", 5, [0, 1], [10, 10], 4),
        T("k = m covers everyone processed", *ex2, 3),
        T("No documents", 3, [], [], 2),
        T("Repeating decimal percentage", 3, [0, 1, 2], [1, 100, 100], 1),
    ]
    for s in range(3):
        m, q, p = gen(rng, 60, rng.randint(1, 6), 3, 12)
        t.append(S(f"Random small #{s + 1}", m, q, p, hidden=True))
        t.append(T(f"Random small #{s + 1}", m, q, p, rng.randint(1, m), hidden=True))
    # Large: many indexers, almost all busy (long jobs), so a linear scan per document is O(n * m).
    m, q, p = 50000, list(range(100000)), [10 ** 9] * 49990 + [rng.randint(1, 30) for _ in range(50010)]
    t.append(S("100k docs, 50k mostly-busy indexers", m, q, p, hidden=True))
    t.append(T("100k docs, 50k mostly-busy indexers", m, q, p, 1000, hidden=True))
    m, q, p = gen(rng, 100000, 300, 2, 700)
    t.append(S("100k random docs", m, q, p, hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    m = n // 2
    q = list(range(n))
    p = [10 ** 9] * (m - 10) + [rng.randint(1, 30) for _ in range(n - m + 10)]
    return fn(f"n={n}", "indexer_stats", m, q, p)


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = documents (m = n/2 indexers, mostly busy)"}
