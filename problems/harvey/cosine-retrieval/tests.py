import random
from engine.spec import cls

EX_DOCS = [[1, 0], [0, 1], [1, 1], [2, 2], [0, 0], [-1, 0]]


def R(name, docs, ops, **kw):
    return cls(name, "Retriever", [docs], ops, **kw)


def rand_docs(rng, n, d, lo=-5, hi=5):
    docs = []
    for _ in range(n):
        r = rng.random()
        if r < 0.05:
            docs.append([0] * d)
        elif r < 0.2 and docs:                       # scaled copy -> exact tie
            base = rng.choice(docs)
            docs.append([x * rng.randint(2, 3) for x in base])
        else:
            docs.append([rng.randint(lo, hi) for _ in range(d)])
    return docs


def rand_vec(rng, d, lo=-5, hi=5):
    return [rng.randint(lo, hi) for _ in range(d)]


def search_ops(rng, n_ops, n, d):
    return [["search", [rand_vec(rng, d), rng.randint(0, n + 2)]] for _ in range(n_ops)]


def eval_op(rng, n_q, n, d, k):
    queries = [rand_vec(rng, d) for _ in range(n_q)]
    relevant = [rng.sample(range(n), rng.randint(0, min(4, n))) if n else [] for _ in range(n_q)]
    return ["evaluate", [queries, relevant, k]]


def tests():
    rng = random.Random(2024)
    t = [
        R("Example search", EX_DOCS, [["search", [[3, 1], 4]], ["search", [[0, 0], 3]]]),
        R("k larger than corpus", EX_DOCS, [["search", [[1, 2], 100]]]),
        R("k = 0", EX_DOCS, [["search", [[1, 2], 0]]]),
        R("Empty corpus", [], [["search", [[1, 2, 3], 5]]]),
        R("Scaled vectors tie, lower index wins", [[2, 4], [1, 3], [1, 2], [3, 6]], [["search", [[1, 2], 4]], ["search", [[-1, -2], 4]]]),
        R("Magnitude is ignored", [[100, 0], [1, 1], [1, 0]], [["search", [[5, 1], 3]]]),
        R("Negative similarities rank last", [[-1, 0], [0, 0], [0, -1], [1, 0]], [["search", [[1, 0], 4]]]),
        R("Higher dimension", [[1, 2, 3, 4], [4, 3, 2, 1], [1, 0, 0, 1], [0, 0, 0, 0], [2, 4, 6, 8]], [["search", [[1, 2, 3, 5], 3]], ["search", [[0, 0, 0, 1], 5]]]),
        R("Evaluate example", EX_DOCS, [["evaluate", [[[3, 1], [0, 5], [1, 1]], [[2, 1], [1], []], 2]]], tag="Follow-up", float=True),
        R("Evaluate with nothing relevant", EX_DOCS, [["evaluate", [[[3, 1]], [[]], 3]], ["evaluate", [[], [], 3]]], tag="Follow-up", float=True),
        R("Evaluate miss gives zero", EX_DOCS, [["evaluate", [[[1, 0]], [[5]], 2]]], tag="Follow-up", float=True),
        R("Evaluate with k = 0", EX_DOCS, [["evaluate", [[[1, 0], [0, 1]], [[0], [1, 2]], 0]]], tag="Follow-up", float=True),
    ]
    for s in range(4):
        n, d = rng.randint(5, 25), rng.randint(2, 6)
        t.append(R(f"Random search #{s + 1}", rand_docs(rng, n, d), search_ops(rng, 6, n, d), hidden=True))
    for s in range(3):
        n, d = rng.randint(5, 25), rng.randint(2, 6)
        t.append(R(f"Random evaluate #{s + 1}", rand_docs(rng, n, d), [eval_op(rng, 8, n, d, rng.randint(1, 5))],
                   tag="Follow-up", hidden=True, float=True))
    docs = rand_docs(rng, 3000, 32, -100, 100)
    t.append(R("3000 docs x 100 queries", docs, search_ops(rng, 100, 50, 32), hidden=True))
    t.append(R("Evaluate 3000 docs x 100 queries", docs, [eval_op(rng, 100, 3000, 32, 10)], tag="Follow-up", hidden=True, float=True))
    return t


def scale(n):
    rng = random.Random(n)
    docs = rand_docs(rng, n, 8, -100, 100)
    return R(f"{n} docs", docs, search_ops(rng, 5, 10, 8))


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = number of docs (d = 8, 5 queries)", "per_op": False}
