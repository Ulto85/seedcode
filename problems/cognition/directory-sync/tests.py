import random
from engine.spec import fn

DIRS = ["a", "b", "c", "src"]
FILES = ["x.py", "y.py", "z.txt", "w.md"]


def rand_path(rng, max_depth, dirs=DIRS, files=FILES):
    return "/".join([rng.choice(dirs) for _ in range(rng.randint(0, max_depth))] + [rng.choice(files)])


def rand_tree(rng, n, max_depth, hashes):
    return {rand_path(rng, max_depth): f"h{rng.randrange(hashes)}" for _ in range(n)}


def derived(rng, src, p_keep, p_change, p_rename, n_extra, hashes, max_depth, dirs=DIRS, files=FILES):
    """A dst that shares most of src: some files kept, changed, renamed elsewhere, dropped; plus extras."""
    dst = {}
    for p, h in src.items():
        r = rng.random()
        if r < p_keep:
            dst[p] = h
        elif r < p_keep + p_change:
            dst[p] = f"h{rng.randrange(hashes)}"
        elif r < p_keep + p_change + p_rename:
            dst[rand_path(rng, max_depth, dirs, files)] = h
    for _ in range(n_extra):
        dst[rand_path(rng, max_depth, dirs, files)] = f"h{rng.randrange(hashes)}"
    return dst


def tests():
    rng = random.Random(9)
    ex_src = {"a/x.py": "h1", "a/b/y.py": "h2", "c.txt": "h3"}
    ex_dst = {"a/x.py": "h1", "a/b/y.py": "OLD", "d/e/z.py": "h9"}
    mv_src = {"lib/util.py": "h1", "lib/new.py": "h1", "main.py": "h2"}
    mv_dst = {"util.py": "h1", "old/main.py": "h2", "old/x.py": "h1"}
    t = [
        fn("Example", "sync_plan", ex_src, ex_dst),
        fn("Already in sync", "sync_plan", ex_src, dict(ex_src)),
        fn("Empty dst: build everything", "sync_plan", {"p/q/r.txt": "h", "p/s.txt": "h", "t.txt": "h"}, {}),
        fn("Empty src: tear everything down", "sync_plan", {}, {"p/q/r.txt": "h", "p/s.txt": "h", "t.txt": "h"}),
        fn("Both empty", "sync_plan", {}, {}),
        fn("Directory kept by another file", "sync_plan", {"d/keep.py": "1"}, {"d/keep.py": "1", "d/gone.py": "2", "d/sub/x.py": "3"}),
        fn("mkdir order is depth first, then path", "sync_plan",
           {"b/c/d/f.py": "1", "a/f.py": "1", "aa/b/f.py": "1"}, {}),
        fn("Example (moves)", "sync_plan_with_moves", mv_src, mv_dst, tag="Follow-up"),
        fn("Changed path is copied, not moved into", "sync_plan_with_moves",
           {"a.py": "new"}, {"a.py": "old", "b.py": "new"}, tag="Follow-up"),
        fn("More deletes than targets", "sync_plan_with_moves",
           {"n/1.py": "h"}, {"o/3.py": "h", "o/1.py": "h", "o/2.py": "h"}, tag="Follow-up"),
        fn("More targets than deletes", "sync_plan_with_moves",
           {"n/2.py": "h", "n/1.py": "h", "n/3.py": "h"}, {"zz.py": "h"}, tag="Follow-up"),
        fn("Kept file with same hash is not a source", "sync_plan_with_moves",
           {"keep.py": "h", "copy.py": "h"}, {"keep.py": "h"}, tag="Follow-up"),
        fn("Swap two paths: no moves possible", "sync_plan_with_moves",
           {"a.py": "1", "b.py": "2"}, {"a.py": "2", "b.py": "1"}, tag="Follow-up"),
    ]
    for i in range(3):
        src = rand_tree(rng, rng.randint(3, 15), 3, 6)
        t.append(fn(f"Random trees #{i + 1}", "sync_plan", src, derived(rng, src, 0.4, 0.2, 0.2, 4, 6, 3), hidden=True))
    for i in range(4):
        src = rand_tree(rng, rng.randint(3, 20), 3, 5)
        t.append(fn(f"Random trees with moves #{i + 1}", "sync_plan_with_moves", src,
                    derived(rng, src, 0.3, 0.2, 0.3, 5, 5, 3), tag="Follow-up", hidden=True))
    src, dst = big_pair(rng, 100000)
    t.append(fn("100k files", "sync_plan", src, dst, hidden=True))
    src, dst = big_pair(rng, 100000)
    t.append(fn("100k files with moves", "sync_plan_with_moves", src, dst, tag="Follow-up", hidden=True))
    return t


def big_pair(rng, n):
    dirs = [f"d{i}" for i in range(40)]
    files = [f"f{i}.py" for i in range(500)]
    src = {}
    while len(src) < n:
        src[rand_path(rng, 4, dirs, files)] = f"h{rng.randrange(n // 3)}"
    return src, derived(rng, src, 0.6, 0.1, 0.25, n // 20, n // 3, 4, dirs, files)


def scale(n):
    src, dst = big_pair(random.Random(n), n)
    return fn(f"n={n}", "sync_plan_with_moves", src, dst)


SCALE = {"sizes": [3125, 6250, 12500, 25000, 50000, 100000], "label": "n = files in src"}
