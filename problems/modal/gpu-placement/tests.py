import random
from engine.spec import cls


def C(name, hosts, ops, **kw):
    return cls(name, "GpuCluster", [hosts], ops, **kw)


def pl(t, g, m): return ["place", [t, g, m]]
def sb(t, g, m): return ["submit", [t, g, m]]
def rel(t): return ["release", [t]]
def at(t): return ["host_of", [t]]
PEND = ["pending", []]


def rand_hosts(rng, n):
    out = []
    for _ in range(n):
        g = rng.choice([1, 2, 4, 8, 8])
        out.append([g, g * rng.choice([16, 32, 64, 80])])
    return out


def rand_task(rng):
    g = rng.choice([1, 1, 1, 2, 2, 4, 8])
    return g, rng.randint(0, g * 70)


def place_ops(rng, n, follow_up=False):
    ops, live, nid = [], [], 0
    for _ in range(n):
        r = rng.random()
        if r < 0.55 or not live:
            tid = f"t{nid}"
            nid += 1
            g, m = rand_task(rng)
            if follow_up and rng.random() < 0.03:
                g, m = rng.choice([[16, 10], [1, 4000]])
            ops.append((sb if follow_up else pl)(tid, g, m))
            live.append(tid)
        elif r < 0.9:
            ops.append(rel(live.pop(rng.randrange(len(live)))))
        elif r < 0.95:
            ops.append(at(f"t{rng.randint(0, nid)}"))
        else:
            ops.append(PEND if follow_up else rel(f"t{rng.randint(0, nid)}"))
    if follow_up:
        ops.append(PEND)
    return ops


def tests():
    rng = random.Random(9)
    ex1 = [[8, 512], [4, 256], [2, 64]]
    t = [
        C("Example", ex1, [pl("t1", 2, 32), pl("t2", 1, 300), pl("t3", 4, 100), pl("t4", 4, 250), rel("t2"),
                           pl("t4", 4, 250), at("t3"), at("t2"), rel("t2")]),
        C("Tie on GPUs: least memory left wins", [[4, 100], [4, 60], [4, 80]], [pl("a", 2, 50), pl("b", 2, 50), at("a")]),
        C("Full tie: lowest index", [[2, 64], [2, 64], [2, 64]], [pl("a", 1, 10), pl("b", 2, 10), pl("c", 2, 64), pl("d", 2, 0)]),
        C("Both dimensions must fit", [[8, 16], [1, 1000]], [pl("a", 2, 100), pl("b", 1, 100), pl("c", 8, 16), pl("d", 1, 0)]),
        C("Zero memory and exact fits", [[2, 10]], [pl("a", 2, 10), pl("b", 1, 0), rel("a"), pl("b", 1, 0), at("b")]),
        C("Release unknown and failed tasks", [[1, 8]], [rel("ghost"), pl("x", 2, 1), rel("x"), at("x"), pl("y", 1, 8), rel("y"), rel("y")]),
        C("Freed capacity is reused", [[8, 64]], [pl("a", 8, 64), pl("b", 1, 1), rel("a"), pl("b", 1, 1), pl("c", 7, 63), pl("d", 1, 0)]),
        C("Follow-up example", [[4, 100], [2, 100]], [sb("a", 4, 50), sb("b", 2, 80), sb("c", 2, 10), sb("d", 4, 10), sb("e", 1, 500),
                                                      sb("f", 1, 10), PEND, rel("b"), PEND, rel("a"), at("d"), at("f"), rel("f"), PEND],
          tag="Follow-up"),
        C("Too many GPUs is rejected", [[8, 512]], [sb("a", 9, 1), sb("b", 8, 513), sb("c", 8, 512), PEND], tag="Follow-up"),
        C("Never-fits needs one host with both", [[8, 10], [1, 500]], [sb("a", 2, 100), sb("b", 1, 500), sb("c", 1, 100), PEND, at("c")], tag="Follow-up"),
        C("Small tasks backfill around a big one", [[4, 100]], [sb("a", 3, 10), sb("big", 4, 10), sb("s1", 1, 10), sb("s2", 1, 10), PEND,
                                                               rel("a"), PEND, at("s2"), rel("s1"), PEND, rel("s2"), at("big"), PEND], tag="Follow-up"),
        C("Cancel a queued task", [[1, 10]], [sb("a", 1, 10), sb("b", 1, 10), sb("c", 1, 10), rel("b"), PEND, rel("a"), at("c"), at("b"), rel("b")],
          tag="Follow-up"),
        C("One release places several in order", [[4, 40], [2, 40]], [sb("x", 4, 40), sb("y", 2, 40), sb("p", 2, 20), sb("q", 2, 20), sb("r", 2, 20),
                                                                     rel("x"), at("p"), at("q"), at("r"), PEND], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random placements #{s + 1}", rand_hosts(rng, rng.randint(2, 8)), place_ops(rng, 120), hidden=True))
    for s in range(3):
        t.append(C(f"Random queueing #{s + 1}", rand_hosts(rng, rng.randint(2, 6)), place_ops(rng, 150, True), tag="Follow-up", hidden=True))
    t.append(C("10k hosts, 100k calls", rand_hosts(rng, 10000), place_ops(rng, 100000), hidden=True))
    t.append(C("300 hosts, 20k queued calls", rand_hosts(rng, 300), place_ops(rng, 20000, True), tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return C(f"{n} calls", rand_hosts(rng, n // 16), place_ops(rng, n))


SCALE = {"sizes": [4000, 8000, 16000, 32000, 64000, 128000], "label": "n = calls (hosts = n/16)"}
