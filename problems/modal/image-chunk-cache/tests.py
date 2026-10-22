import random
from engine.spec import cls


def C(name, cap, ops, **kw):
    return cls(name, "ChunkCache", [cap], ops, **kw)


def rd(h, s): return ["read", [h, s]]
def mnt(c, chunks): return ["mount", [c, chunks]]
def umnt(c): return ["unmount", [c]]
USED = ["used", []]
STATS = ["stats", []]


def sizes_for(rng, n_chunks, lo, hi):
    return {f"sha{i:05d}": rng.randint(lo, hi) for i in range(n_chunks)}


def read_ops(rng, n, n_chunks, lo, hi):
    sz = sizes_for(rng, n_chunks, lo, hi)
    keys = list(sz)
    ops = []
    for _ in range(n):
        # skewed popularity: a few hot chunks, a long tail
        k = keys[min(int(rng.expovariate(1 / (n_chunks / 4))), n_chunks - 1)]
        ops.append(rd(k, sz[k]))
        if rng.random() < 0.05:
            ops.append(USED)
    ops.append(STATS)
    ops.append(USED)
    return ops


def pin_ops(rng, n, n_chunks, lo, hi, n_containers, per_mount):
    sz = sizes_for(rng, n_chunks, lo, hi)
    keys = list(sz)
    ops, live, next_id = [], [], 0
    for _ in range(n):
        r = rng.random()
        if r < 0.3:
            k = rng.choice(keys)
            ops.append(rd(k, sz[k]))
        elif r < 0.6 and len(live) < n_containers:
            cid = f"ctr{next_id}"
            next_id += 1
            chunks = [[k, sz[k]] for k in (rng.choice(keys) for _ in range(rng.randint(0, per_mount)))]
            ops.append(mnt(cid, chunks))
            live.append(cid)
        elif r < 0.9 and live:
            cid = live.pop(rng.randrange(len(live)))
            ops.append(umnt(cid))
        elif r < 0.95:
            ops.append(umnt(f"ctr{rng.randint(0, next_id + 2)}") if rng.random() < 0.5 else mnt(rng.choice(live) if live else "ctr0", []))
        else:
            ops.append(USED)
    ops.append(STATS)
    ops.append(USED)
    return ops


def tests():
    rng = random.Random(3)
    t = [
        C("Example", 10, [rd("a", 4), rd("b", 4), rd("a", 4), rd("c", 4), USED, STATS]),
        C("Empty cache", 5, [USED, STATS]),
        C("Oversized chunk is never stored", 5, [rd("a", 3), rd("big", 6), USED, rd("big", 6), rd("a", 3), STATS]),
        C("Exact fit", 8, [rd("a", 3), rd("b", 5), USED, rd("a", 3), rd("b", 5), STATS]),
        C("Evicts several to make room", 10, [rd("a", 3), rd("b", 3), rd("c", 3), rd("d", 9), USED, rd("a", 3), rd("d", 9), STATS]),
        C("Hit refreshes recency", 6, [rd("a", 2), rd("b", 2), rd("c", 2), rd("a", 2), rd("d", 2), rd("a", 2), rd("b", 2), STATS]),
        C("Follow-up example", 10, [mnt("x", [["a", 4], ["b", 4]]), rd("c", 4), mnt("y", [["b", 4], ["d", 2]]),
                                     umnt("x"), rd("e", 4), umnt("x"), USED, STATS], tag="Follow-up"),
        C("Mount twice is rejected", 10, [mnt("x", [["a", 2]]), mnt("x", [["b", 2]]), USED, STATS, umnt("x"), mnt("x", []), umnt("x")], tag="Follow-up"),
        C("Mount never evicts its own chunks", 6, [mnt("x", [["a", 3], ["b", 3], ["c", 3]]), USED, STATS, rd("a", 3), rd("c", 3)], tag="Follow-up"),
        C("Duplicate hash inside one mount", 10, [mnt("x", [["a", 5], ["a", 5]]), umnt("x"), rd("b", 6), rd("a", 5), STATS], tag="Follow-up"),
        C("Shared pin needs every container gone", 8, [mnt("x", [["a", 4]]), mnt("y", [["a", 4]]), umnt("x"), rd("b", 4), rd("c", 4),
                                                        rd("a", 4), umnt("y"), rd("d", 4), rd("a", 4), STATS], tag="Follow-up"),
        C("Unmount keeps old recency", 6, [rd("a", 2), mnt("x", [["b", 2]]), rd("c", 2), rd("a", 2), umnt("x"),
                                           rd("d", 2), rd("b", 2), rd("c", 2), rd("a", 2), STATS], tag="Follow-up"),
        C("Unknown unmount", 4, [umnt("ghost"), mnt("x", []), umnt("x"), umnt("x")], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random reads #{s + 1}", rng.randint(20, 60), read_ops(rng, 120, 25, 1, 12), hidden=True))
    for s in range(4):
        t.append(C(f"Random mounts #{s + 1}", rng.randint(30, 80), pin_ops(rng, 150, 30, 1, 10, 5, 6), tag="Follow-up", hidden=True))
    t.append(C("60k reads, thousands cached", 40000, read_ops(rng, 60000, 20000, 1, 20), hidden=True))
    t.append(C("30k calls with pins", 30000, pin_ops(rng, 30000, 15000, 1, 20, 200, 20), tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return C(f"{n} reads", n // 2, read_ops(rng, n, n // 2, 1, 20))


SCALE = {"sizes": [4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of reads"}
