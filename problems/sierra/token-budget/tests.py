import random
from engine.spec import fn


def recs(tokens, start=0):
    return [{"id": f"r{start + i}", "tokens": t} for i, t in enumerate(tokens)]


def page(ids, nxt):
    return {"records": [{"id": i} for i in ids], "next": nxt}


def random_api(rng, n_pages, per_page, fail_rate=0.2, max_fail=5, cycle=False, dup_rate=0.1):
    cursors = [""] + [f"c{i}" for i in range(1, n_pages)]
    pages, failures, nid = {}, {}, 0
    for i, c in enumerate(cursors):
        ids = []
        for _ in range(rng.randint(0 if i == n_pages - 1 else 1, per_page)):
            if nid and rng.random() < dup_rate:
                ids.append(f"x{rng.randrange(nid)}")
            else:
                ids.append(f"x{nid}")
                nid += 1
        nxt = cursors[i + 1] if i + 1 < n_pages else (rng.choice(cursors[1:]) if cycle and n_pages > 1 else None)
        pages[c] = page(ids, nxt)
        if rng.random() < fail_rate:
            failures[c] = rng.randint(1, max_fail)
    return {"pages": pages, "failures": failures}


EX = [4000, 3000, 5000, 2000, 1000, 6000, 3000]
EX_API = {"pages": {"": page(["a", "b"], "p2"), "p2": page(["b", "c"], "p3"), "p3": page([], None)},
          "failures": {"p2": 2}}


def tests():
    rng = random.Random(11)
    t = [
        fn("Example fetch", "fetch_all", EX_API),
        fn("Single page, next is None", "fetch_all", {"pages": {"": page(["a"], None)}}),
        fn("Empty first page", "fetch_all", {"pages": {"": page([], "p2"), "p2": page(["z"], None)}}),
        fn("Retries exhausted", "fetch_all", {"pages": {"": page(["a"], "p2"), "p2": page(["b"], None)}, "failures": {"p2": 4}}),
        fn("Exactly 3 retries succeeds", "fetch_all", {"pages": {"": page(["a"], "p2"), "p2": page(["b"], None)}, "failures": {"p2": 3, "": 1}}),
        fn("Cursor loop", "fetch_all", {"pages": {"": page(["a"], "p2"), "p2": page(["b"], "p3"), "p3": page(["c", "a"], "p2")}}),
        fn("Self loop", "fetch_all", {"pages": {"": page(["a"], "p"), "p": page(["b"], "p")}}),
        fn("Missing cursor means empty page", "fetch_all", {"pages": {"": page(["a"], "nowhere")}}),
        fn("Example compact", "compact", recs(EX), 20000, 10000, tag="Part 2"),
        fn("Under the trigger: unchanged", "compact", recs(EX), 30000, 10000, tag="Part 2"),
        fn("Exactly at the trigger: unchanged", "compact", recs(EX), 24000, 5000, tag="Part 2"),
        fn("Empty records", "compact", [], 10, 5, tag="Part 2"),
        fn("Nothing fits", "compact", recs([50, 60, 70]), 100, 40, tag="Part 2"),
        fn("Zero-token records", "compact", recs([9, 0, 0, 5, 0, 9, 0]), 10, 5, tag="Part 2"),
        fn("Tie goes to earliest", "compact", recs([3, 3, 9, 3, 3]), 15, 6, tag="Part 2"),
        fn("Example, tokens mode", "compact", recs(EX), 20000, 10000, "tokens", tag="Follow-up"),
        fn("Tokens mode beats count", "compact", recs([1, 1, 1, 1, 9, 2]), 12, 10, "tokens", tag="Follow-up"),
        fn("Tokens mode tie: more records", "compact", recs([8, 2, 0, 10, 5, 5]), 20, 10, "tokens", tag="Follow-up"),
        fn("Tokens mode, under trigger", "compact", recs([5, 5]), 10, 3, "tokens", tag="Follow-up"),
    ]
    for s in range(3):
        t.append(fn(f"Random fetch #{s + 1}", "fetch_all", random_api(rng, rng.randint(2, 12), 4, cycle=s == 2), hidden=True))
    for s in range(3):
        t.append(fn(f"Random compact #{s + 1}", "compact", recs([rng.randint(0, 60) for _ in range(40)]), 300, rng.randint(50, 200), tag="Part 2", hidden=True))
        t.append(fn(f"Random tokens mode #{s + 1}", "compact", recs([rng.randint(0, 60) for _ in range(40)]), 300, rng.randint(50, 200), "tokens", tag="Follow-up", hidden=True))
    t.append(fn("50k pages", "fetch_all", random_api(rng, 50000, 4, fail_rate=0.1, max_fail=3), hidden=True))
    big = recs([rng.randint(0, 10000) for _ in range(100000)])
    t.append(fn("100k records", "compact", big, 20000, 2_500_000, tag="Part 2", hidden=True))
    t.append(fn("100k records, tokens mode", "compact", big, 20000, 1_500_000, "tokens", tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return fn(f"n={n}", "compact", recs([rng.randint(0, 100) for _ in range(n)]), 0, n * 10)


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = number of records"}
