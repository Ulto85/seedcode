import random
from engine.spec import fn

DIRS = ["src", "lib", "docs", "tests", "app"]
SUB = ["core", "utils", "api", "ui", "x"]
NAMES = ["main.py", "util.py", "README.md", "a.txt", "b.txt", "index.ts", "config.json", "x"]


def rand_path(rng):
    depth = rng.choice([0, 1, 1, 2, 2, 3])
    parts = [rng.choice(DIRS)] + [rng.choice(SUB) for _ in range(depth - 1)] if depth else []
    return "/".join(parts + [rng.choice(NAMES)])


def rand_snapshot(rng, n):
    """Random snapshot where no file path is also a directory prefix of another file."""
    snap = {}
    for _ in range(n * 3):
        if len(snap) >= n:
            break
        p = rand_path(rng)
        prefixes = {"/".join(p.split("/")[:i]) for i in range(1, p.count("/") + 1)}
        if p in snap or prefixes & snap.keys() or any(q.startswith(p + "/") for q in snap):
            continue
        snap[p] = rng.choice(["v1", "v2", "print('hi')\n", "", "x" * rng.randint(1, 5)])
    return snap


def mutate(rng, snap, k):
    b = dict(snap)
    keys = sorted(b)
    for _ in range(k):
        r = rng.random()
        if r < 0.35 and keys:
            p = rng.choice(keys)
            if p in b:
                b[p] += "!"
        elif r < 0.6 and keys:
            b.pop(rng.choice(keys), None)
        else:
            p = rand_path(rng)
            prefixes = {"/".join(p.split("/")[:i]) for i in range(1, p.count("/") + 1)}
            if not (prefixes & b.keys() or any(q.startswith(p + "/") for q in b)):
                b[p] = "new" + str(rng.randint(0, 9))
    return b


def big_repo(n, changed, seed):
    rng = random.Random(seed)
    a = {}
    for i in range(n):
        a[f"pkg{i % 37}/mod{i % 11}/file{i}.py"] = f"# file {i}\n" + "x = 1\n" * (i % 5)
    b = dict(a)
    keys = sorted(a)
    for p in rng.sample(keys, changed):
        b[p] += "y = 2\n"
    for p in rng.sample(keys, changed):
        b.pop(p, None)
    for i in range(changed):
        b[f"pkg{i}/new/added{i}.py"] = "new"
    return a, b


EX_A = {"README.md": "hello", "src/main.py": "v1", "src/utils/helpers.py": "h", "docs/old.md": "old"}
EX_B = {"README.md": "hello", "src/main.py": "v2", "src/utils/helpers.py": "h", "src/utils/new.py": "n",
        "tests/test_main.py": "t"}


def tests():
    rng = random.Random(7)
    t = [
        fn("Example", "repo_diff", EX_A, EX_B),
        fn("Identical snapshots", "repo_diff", {"README.md": "a", "src/main.py": "b"}, {"src/main.py": "b", "README.md": "a"}),
        fn("Both empty", "repo_diff", {}, {}),
        fn("Everything added", "repo_diff", {}, {"a/b/c.txt": "1", "a/d.txt": "2", "z": ""}),
        fn("Everything removed", "repo_diff", {"a/b/c.txt": "1", "a/d.txt": "2"}, {}),
        fn("File becomes a directory", "repo_diff", {"lib": "x", "keep": "k"}, {"lib/core.py": "x", "lib/z/y.py": "y", "keep": "k"}),
        fn("Directory becomes a file", "repo_diff", {"docs/a.md": "a", "docs/b/c.md": "c"}, {"docs": "now a file"}),
        fn("Empty contents vs missing", "repo_diff", {"a": "", "b": "x"}, {"a": "x", "b": ""}),
        fn("Hash: example root", "tree_hash", EX_A, "", tag="Follow-up"),
        fn("Hash: a file", "tree_hash", EX_A, "src/main.py", tag="Follow-up"),
        fn("Hash: a directory", "tree_hash", EX_A, "src/utils", tag="Follow-up"),
        fn("Hash: missing path", "tree_hash", EX_A, "src/nope", tag="Follow-up"),
        fn("Hash: path through a file", "tree_hash", EX_A, "README.md/x", tag="Follow-up"),
        fn("Hash: empty snapshot root", "tree_hash", {}, "", tag="Follow-up"),
        fn("Hash: insertion order doesn't matter", "tree_hash", {"b/x": "1", "a": "2", "b/c": "3"}, "", tag="Follow-up"),
    ]
    for i in range(4):
        a = rand_snapshot(rng, 25)
        t.append(fn(f"Random snapshots #{i + 1}", "repo_diff", a, mutate(rng, a, 8), hidden=True))
    for i in range(3):
        a = rand_snapshot(rng, 20)
        t.append(fn(f"Random hash #{i + 1}", "tree_hash", a, rng.choice(["", "src", "lib", "docs/core", rand_path(rng)]),
                    tag="Follow-up", hidden=True))
    a, b = big_repo(30000, 300, 1)
    t.append(fn("30,000-file repo, 900 changes", "repo_diff", a, b, hidden=True))
    t.append(fn("30,000-file repo root hash", "tree_hash", b, "", tag="Follow-up", hidden=True))
    return t


def scale(n):
    a, b = big_repo(n, max(1, n // 100), n)
    return fn(f"{n} files", "repo_diff", a, b)


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000], "label": "n = number of files"}
