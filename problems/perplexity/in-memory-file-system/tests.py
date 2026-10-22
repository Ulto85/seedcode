import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "FileSystem", [], ops, **kw)


def mk(p): return ["mkdir", [p]]
def to(p): return ["touch", [p]]
def ls(p): return ["ls", [p]]
def rm(p): return ["rm", [p]]
def rd(p): return ["rmdir", [p]]
def ex(cmds): return ["execute", [cmds]]
def cd(p): return ["cd", [p]]
def pwd(): return ["pwd", []]

NAMES = ["a", "b", "c", "d.txt", "e_1"]


def rand_path(rng, follow_up):
    depth = rng.randint(1, 3)
    comps = []
    for _ in range(depth):
        if follow_up and rng.random() < 0.2:
            comps.append(rng.choice([".", ".."]))
        else:
            comps.append(rng.choice(NAMES))
    x = rng.random()
    if x < 0.04:
        return rng.choice(["", "/", "//", "/a/", "/a b", "/a//b"])
    if follow_up and x < 0.45:
        return "/".join(comps)
    return "/" + "/".join(comps)


def random_ops(rng, n, part):
    fu = part == 3
    ops = []
    for _ in range(n):
        x = rng.random()
        p = rand_path(rng, fu)
        if x < 0.3:
            ops.append(mk(p))
        elif x < 0.45:
            ops.append(to(p))
        elif x < 0.6 or part == 1:
            ops.append(ls(p))
        elif x < 0.68:
            ops.append(rm(p))
        elif x < 0.76:
            ops.append(rd(p))
        elif x < 0.84 or not fu:
            names = ["mkdir", "touch", "ls", "rm", "rmdir", "cat"] + (["cd", "pwd"] if fu else [])
            cmds = []
            for _ in range(rng.randint(1, 4)):
                c = rng.choice(names)
                q = rand_path(rng, fu) or "/"
                cmds.append(c if c == "pwd" else f"{c} {q}" if rng.random() < 0.9 else c)
            ops.append(ex(cmds))
        elif x < 0.95:
            ops.append(cd(p))
        else:
            ops.append(pwd())
    return ops


def big_tree(n, rng):
    """n/2 directories created under random existing ones (deep and wide), then ls / rmdir / touch / rm."""
    dirs = ["/"]
    ops = []
    for i in range(n // 2):
        parent = dirs[rng.randrange(len(dirs))] if rng.random() < 0.7 else dirs[-1]
        path = (parent if parent != "/" else "") + f"/d{i}"
        ops.append(mk(path))
        dirs.append(path)
    for i in range(n // 2):
        d = dirs[rng.randrange(1, len(dirs))]
        x = rng.random()
        if x < 0.3:
            ops.append(ls(d))
        elif x < 0.6:
            ops.append(rd(d))
        elif x < 0.8:
            ops.append(to(d + f"/f{i}"))
        else:
            ops.append(rm(d + f"/f{i - 1}"))
    return ops


def tests():
    rng = random.Random(99)
    t = [
        C("Example (Part 1)", [mk("/docs"), mk("/docs/2026/q1"), to("/docs/a.txt"), to("/docs/a.txt/b"), mk("/docs/"),
                               ls("/"), ls("/docs/a.txt"), ls("/docs")]),
        C("Empty root and missing paths", [ls("/"), ls("/nope"), ls("/nope/deeper"), mk("/"), to("/")]),
        C("Invalid paths", [mk(""), mk("//"), mk("/a//b"), mk("/a/"), to("/has space"), to("/bad*char"), ls("/x/"), mk("/ok-name_1.v2")]),
        C("Duplicates are errors", [mk("/a"), mk("/a"), to("/a"), to("/f"), to("/f"), mk("/f"), ls("/")]),
        C("No implicit parents, files aren't directories", [mk("/a/b"), mk("/a"), mk("/a/b"), mk("/a/b/c"), to("/a/b/c/f"),
                                                             mk("/a/b/c/f/g"), ls("/a/b/c/f/g"), ls("/a/b/c")]),
        C("ls is sorted by string order", [mk("/z"), to("/B"), mk("/a"), to("/a10"), to("/a2"), to("/_x"), ls("/")]),
        C("rm and rmdir", [mk("/d"), to("/d/f"), rm("/d"), rd("/d"), rd("/d/f"), rm("/d/f"), rm("/d/f"), rd("/d"), rd("/d"), ls("/"),
                           rm("/"), rd("/")], tag="Part 2"),
        C("Execute example", [mk("/docs"), to("/docs/a.txt"),
                              ex(["mkdir /tmp", "ls /", "rmdir /docs", "rm /docs", "cat /docs/a.txt", "ls"])], tag="Part 2"),
        C("Execute formatting and arg counts", [ex(["", "   ", "ls /", "mkdir /a /b", "touch", "mkdir  /a", "ls /a", "touch /a/x",
                                                   "ls /a/x", "ls /a", "LS /", "rmdir /a /a"]), ex(["ls /"])], tag="Part 2"),
        C("Follow-up example", [mk("/docs"), to("/docs/a.txt"), mk("/tmp"), cd("docs"), to("../tmp/x"), pwd(), ls(".."),
                                rm("a.txt"), rd("/docs"), ls("/tmp")], tag="Follow-up"),
        C("cd errors leave cwd unchanged", [mk("/a"), to("/a/f"), cd("/a"), cd("f"), pwd(), cd("nope"), pwd(), cd("/a/f/.."), pwd(),
                                            cd(".."), pwd(), cd(".."), pwd(), cd(""), pwd()], tag="Follow-up"),
        C("Walk through the real tree", [mk("/a"), mk("/a/b"), ls("missing/../a"), ls("/a/./b/../.."), mk("./a/b/./c"), ls("a/b"),
                                         cd("a/b/c"), pwd(), ls("../../.."), cd("/../../a"), pwd()], tag="Follow-up"),
        C("Dot and dot-dot as the last component", [mk("/a"), mk("/a/."), to("/a/.."), mk("."), rm("/a/."), rd("/a/.."), rd("."),
                                                    rm(".."), ls("/a/.."), cd("/a/."), pwd()], tag="Follow-up"),
        C("Busy current directory", [mk("/a"), mk("/a/b"), cd("/a/b"), rd("/a/b"), rd("."), rd("/a"), cd("/"), rd("/a/b"), rd("/a"), ls("/")],
          tag="Follow-up"),
        C("Execute with cd and pwd", [ex(["mkdir /w", "cd w", "pwd", "touch f", "ls .", "pwd x", "cd", "cd /nope", "pwd", "ls ../w/f"])],
          tag="Follow-up"),
    ]
    for i in range(3):
        t.append(C(f"Random mkdir/touch/ls #{i + 1}", random_ops(rng, 80, 1), hidden=True))
    for i in range(3):
        t.append(C(f"Random with removes and execute #{i + 1}", random_ops(rng, 100, 2), tag="Part 2", hidden=True))
    for i in range(3):
        t.append(C(f"Random with cd and relative paths #{i + 1}", random_ops(rng, 150, 3), tag="Follow-up", hidden=True))
    t.append(C("Big tree (40k ops)", big_tree(40000, rng), tag="Part 2", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", big_tree(n, random.Random(n)), tag="Part 2")


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = number of operations (n/2 directories)"}
