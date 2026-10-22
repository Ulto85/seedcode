import random
from engine.spec import cls


def V(name, ops, cap=None, **kw):
    return cls(name, "FileVault", [] if cap is None else [cap], ops, **kw)


def add(p): return ["add_file", [p]]
def ls(p): return ["list_entries", [p]]


NAMES = ["nda.pdf", "nda(1).pdf", "memo.docx", "archive.tar.gz", ".env", "README", "a", "a(1)", "x.y.z"]
DIRS = ["deals", "acme", "q3", "lit", "nda.pdf", "README"]


def rand_path(rng):
    depth = rng.randint(0, 2)
    segs = [rng.choice(DIRS) for _ in range(depth)] + [rng.choice(NAMES)]
    p = "/" + "/".join(segs)
    r = rng.random()
    if r < 0.04: p += "/"
    elif r < 0.07: p = p.replace("/", "//", 1)
    elif r < 0.09: p = p[1:]
    elif r < 0.10: p = "/"
    return p


def rand_dir(rng):
    depth = rng.randint(0, 2)
    p = "/" + "/".join(rng.choice(DIRS) for _ in range(depth))
    return p if rng.random() > 0.05 else p + "/"


def random_ops(rng, n):
    return [add(rand_path(rng)) if rng.random() < 0.75 else ls(rand_dir(rng)) for _ in range(n)]


def tests():
    rng = random.Random(5)
    t = [
        V("Example", [add("/deals/acme/nda.pdf"), add("/deals/acme/nda.pdf"), add("/deals/acme/nda(1).pdf"),
                      add("/deals/acme/nda.pdf"), ls("/deals/acme"), add("/deals/acme/nda.pdf/x.txt"),
                      add("/deals"), ls("/")]),
        V("Creates missing directories", [add("/path/to/somewhere/file.txt"), ls("/path/to/somewhere"), ls("/path/to"), ls("/path"), ls("/")]),
        V("Extension rules", [add("/archive.tar.gz"), add("/archive.tar.gz"), add("/.env"), add("/.env"),
                              add("/README"), add("/README"), add("/x."), add("/x."), ls("/")]),
        V("Literal parentheses", [add("/a(1)"), add("/a"), add("/a"), add("/A"), add("/a(1)"), ls("/")]),
        V("Invalid paths rejected", [add("/"), add("relative.txt"), add("/a//b.txt"), add("/a/"), add("/./a"),
                                     add("/a/../b"), add(""), ls("/")]),
        V("List edge cases", [add("/d/f.txt"), ls("/d/f.txt"), ls("/missing"), ls("/d/"), ls("d"), ls("/d"), ls("/")]),
        V("Empty vault", [ls("/"), ls("/a")]),
        V("Directory segment is a file, nothing created", [add("/a/b"), add("/a/b/c/d.txt"), ls("/a"), ls("/a/b")]),
        V("Name clash with a directory", [add("/docs/x/y.txt"), add("/docs/x"), add("/docs/x"), ls("/docs"), add("/docs/x/z.txt"), ls("/docs/x")]),
        V("Suffix fills the smallest gap", [add("/f(2).txt"), add("/f.txt"), add("/f.txt"), add("/f.txt"), add("/f.txt"), ls("/")]),
        V("Same name in different folders is independent", [add("/a/n.pdf"), add("/b/n.pdf"), add("/a/n.pdf"), ls("/a"), ls("/b")]),
        V("Capacity example", [add("/a.txt"), add("/a.txt"), add("/b/c.txt"), add("/a.txt/x"), ls("/")], cap=2, tag="Follow-up"),
        V("Capacity is atomic", [add("/d/1"), add("/d/2"), add("/d/3/deep/f"), ls("/d"), ls("/d/3"), add("/d/2/f"), ls("/d")], cap=2, tag="Follow-up"),
        V("Capacity of 1 still allows deep paths", [add("/a/b/c/d.txt"), add("/a/b/c/e.txt"), add("/a/x"), add("/a/b/c/d.txt"), ls("/a/b/c")], cap=1, tag="Follow-up"),
        V("Rename counts toward capacity", [add("/n"), add("/n"), add("/n"), add("/n"), ls("/")], cap=3, tag="Follow-up"),
    ]
    for s in range(4):
        t.append(V(f"Random ops #{s + 1}", random_ops(rng, 80), hidden=True))
    for s in range(3):
        t.append(V(f"Random ops with capacity #{s + 1}", random_ops(rng, 80), cap=rng.randint(2, 4), tag="Follow-up", hidden=True))
    bulk = [add("/bulk/contract.pdf") for _ in range(20000)] + [add("/bulk/contract(77).pdf"), add("/bulk/contract.pdf")]
    t.append(V("20k uploads of the same name", bulk + [ls("/bulk")], hidden=True))
    t.append(V("Random ops (20k)", random_ops(rng, 20000), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    ops = [add(f"/{rng.choice(['a', 'b'])}/{rng.choice(['m.pdf', 'n.docx', '.env'])}") for _ in range(n)]
    return V(f"{n} uploads", ops + [ls("/a")])


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of uploads", "per_op": False}
