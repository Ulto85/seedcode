import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "ReferralNetwork", [], ops, **kw)


def au(u): return ["add_user", [u]]
def ar(a, b): return ["add_referral", [a, b]]
def dr(u): return ["get_direct_referrals", [u]]
def cnt(u): return ["total_referral_count", [u]]
def top(k): return ["top_referrers_by_reach", [k]]
def flow(u): return ["flow_centrality", [u]]


def uid(i):
    return f"u{i:05d}"


def random_ops(rng, n_users, n_ops, follow_up=False, part2=True):
    users = [uid(i) for i in range(n_users)] + ["ghost"]
    ops = [au(u) for u in users[:n_users // 2]]
    for _ in range(n_ops):
        r = rng.random()
        if r < 0.12:
            ops.append(au(rng.choice(users)))
        elif r < 0.6:
            a, b = rng.choice(users), rng.choice(users)
            ops.append(ar(a, b))
        elif r < 0.7 or not part2:
            ops.append(dr(rng.choice(users)))
        elif r < 0.82:
            ops.append(cnt(rng.choice(users)))
        elif r < 0.9 or not follow_up:
            ops.append(top(rng.randint(-1, 6)))
        else:
            ops.append(flow(rng.choice(users)))
    return ops


def build_then_query(rng, n, q, follow_up=True):
    """n users, a random forest built in random order (many referrals rejected), then q queries."""
    users = [uid(i) for i in range(n)]
    ops = [au(u) for u in users]
    for _ in range(n):
        ops.append(ar(rng.choice(users), rng.choice(users)))
    for _ in range(q):
        r = rng.random()
        if r < 0.5:
            ops.append(cnt(rng.choice(users)))
        elif r < 0.7 or not follow_up:
            ops.append(top(10))
        else:
            ops.append(flow(rng.choice(users)))
    return ops


EXAMPLE = [au("A"), au("B"), au("C"), au("D"), au("E"),
           ar("A", "B"), ar("A", "C"), ar("B", "D"), ar("D", "A"), ar("E", "B"), ar("C", "C"),
           dr("A")]


def tests():
    rng = random.Random(2026)
    t = [
        C("Example: building the graph", EXAMPLE),
        C("Duplicate users", [au("x"), au("x"), au("y"), au("x")]),
        C("Unknown users are rejected", [au("a"), ar("a", "b"), ar("b", "a"), dr("a"), dr("zzz")]),
        C("Longer cycle is rejected", [au("a"), au("b"), au("c"), au("d"), ar("a", "b"), ar("b", "c"), ar("c", "d"),
                                        ar("d", "a"), ar("d", "b"), ar("c", "a"), dr("d")]),
        C("Joining two trees is allowed", [au("a"), au("b"), au("c"), au("d"), ar("a", "b"), ar("c", "d"),
                                            ar("b", "c"), ar("d", "a"), dr("b")]),
        C("Direct referrals are sorted", [au("m"), au("z"), au("b"), au("k"), ar("m", "z"), ar("m", "b"), ar("m", "k"), dr("m"), dr("b")]),
        C("Part 2: example", EXAMPLE + [cnt("A"), cnt("B"), cnt("C"), cnt("Q"), top(5), top(1), top(0)], tag="Part 2"),
        C("Part 2: ties by id", [au("d"), au("c"), au("b"), au("a"), au("x"), au("y"), ar("d", "x"), ar("b", "y"),
                                 top(3), top(-2), cnt("x")], tag="Part 2"),
        C("Part 2: reach updates after a merge", [au("a"), au("b"), au("c"), au("d"), ar("a", "b"), cnt("a"),
                                                  ar("c", "d"), ar("b", "c"), cnt("a"), cnt("b"), top(10)], tag="Part 2"),
        C("Follow-up: example", EXAMPLE + [flow("B"), flow("A"), flow("D"), flow("nobody")], tag="Follow-up"),
        C("Follow-up: middle of a chain wins", [au("1"), au("2"), au("3"), au("4"), au("5"), au("6"),
                                                ar("1", "2"), ar("2", "3"), ar("3", "4"), ar("4", "5"), ar("3", "6"),
                                                flow("1"), flow("2"), flow("3"), flow("4"), flow("5"), top(2)], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Part 1 random #{s + 1}", random_ops(rng, 12, 60, part2=False), hidden=True))
    for s in range(3):
        t.append(C(f"Part 2 random #{s + 1}", random_ops(rng, 14, 80), tag="Part 2", hidden=True))
    for s in range(3):
        t.append(C(f"Follow-up random #{s + 1}", random_ops(rng, 14, 80, follow_up=True), tag="Follow-up", hidden=True))

    n = 30000
    chain = [au(uid(i)) for i in range(n)]
    down = chain + [ar(uid(i), uid(i + 1)) for i in range(n - 1)] + [ar(uid(n - 1), uid(0)), cnt(uid(0)), cnt(uid(n // 2)), top(3)]
    up = chain + [ar(uid(i), uid(i + 1)) for i in range(n - 2, -1, -1)] + [ar(uid(n - 1), uid(0)), cnt(uid(0)), top(3)]
    t.append(C("30k chain built top-down", down, tag="Part 2", hidden=True))
    t.append(C("30k chain built bottom-up", up, tag="Part 2", hidden=True))
    t.append(C("20k users, 20k queries", build_then_query(rng, 20000, 20000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} users", build_then_query(random.Random(n), n, n), tag="Follow-up")


SCALE = {"sizes": [2500, 5000, 10000, 20000, 40000, 80000], "label": "n = users (n referral attempts, n queries)"}
