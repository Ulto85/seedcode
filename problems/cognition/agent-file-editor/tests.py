import random
from engine.spec import cls

C_ = "FileEditor"
WORDS = ["x", "y", "foo", "bar", "return", "def", "=", "1", "2", "(", ")"]


def C(name, ops, **kw):
    return cls(name, C_, [], ops, **kw)


def rand_text(rng, max_lines, max_words=4, ids=None, counter=None):
    """Random lines of code-ish words. When ids is given, ~70% of lines start with a fresh unique name
    v<k>_ (recorded in ids) so str_replace targets often match exactly once."""
    lines = []
    for _ in range(rng.randint(0, max_lines)):
        words = [rng.choice(WORDS) for _ in range(rng.randint(0, max_words))]
        if ids is not None and rng.random() < 0.7:
            counter[0] += 1
            ids.append(counter[0])
            words.insert(0, f"v{counter[0]}_")
        lines.append(" ".join(words))
    return "\n".join(lines)


def random_ops(rng, n, paths, with_undo, max_lines=8):
    ops, ids, counter = [], {q: [] for q in paths}, [0]

    def text(p, *a):
        return rand_text(rng, *a, ids=ids[p], counter=counter)

    for p in paths[:-1]:
        ops.append(["create", [p, text(p, max_lines)]])
    for _ in range(n):
        p = rng.choice(paths)
        r = rng.random()
        if r < 0.05:
            ops.append(["create", [p, text(p, 3)]])
        elif r < 0.25:
            a = rng.randint(-1, 10)
            ops.append(["view", [p, a, rng.choice([-1, a + rng.randint(-1, 5)])]])
        elif r < 0.6:
            # old: a recent unique name (often exactly one match), random words, a 2-line span, or empty
            if ids[p] and rng.random() < 0.6:
                old = f"v{rng.choice(ids[p][-10:])}" + rng.choice(["_", ""])
            elif rng.random() < 0.15:
                old = rng.choice(WORDS) + "\n" + rng.choice(WORDS)
            else:
                old = " ".join(rng.choice(WORDS) for _ in range(rng.randint(0, 2)))
            ops.append(["str_replace", [p, old, text(p, 2, 2)]])
        elif r < (0.8 if with_undo else 1.0):
            ops.append(["insert", [p, rng.randint(-1, 10), text(p, 2, 3)]])
        else:
            ops.append(["undo", [p]])
    return ops


def tests():
    rng = random.Random(2024)
    src = "def f():\n    return 1\n"
    t = [
        C("Example", [["create", ["app.py", src]], ["view", ["app.py", 1, -1]],
                      ["str_replace", ["app.py", "return 1", "return 2"]],
                      ["str_replace", ["app.py", "x = 9", "y"]],
                      ["insert", ["app.py", 0, "import os"]], ["view", ["app.py", 1, 2]],
                      ["create", ["app.py", ""]], ["view", ["app.py", 9, 10]]]),
        C("Missing file everywhere", [["view", ["nope", 1, 1]], ["str_replace", ["nope", "a", "b"]],
                                       ["insert", ["nope", 0, "a"]]]),
        C("Empty file has one empty line", [["create", ["e", ""]], ["view", ["e", 1, -1]], ["view", ["e", 2, -1]],
                                             ["insert", ["e", 1, "tail"]], ["view", ["e", 1, -1]],
                                             ["insert", ["e", 3, "x"]]]),
        C("Ambiguous and empty old", [["create", ["m", "a = 1\nb = 1\nc = 2"]],
                                      ["str_replace", ["m", "= 1", "= 5"]],
                                      ["str_replace", ["m", "", "z"]],
                                      ["str_replace", ["m", "b = 1", "b = 5"]], ["view", ["m", 1, -1]]]),
        C("Non-overlapping count", [["create", ["o", "aaaa"]], ["str_replace", ["o", "aa", "b"]],
                                    ["str_replace", ["o", "aaa", "b"]], ["view", ["o", 1, 1]]]),
        C("Multi-line old and new", [["create", ["f", "one\ntwo\nthree\nfour"]],
                                     ["str_replace", ["f", "two\nthree", "2\n2.5\n3"]], ["view", ["f", 1, -1]],
                                     ["str_replace", ["f", "four", ""]], ["view", ["f", 4, 99]]]),
        C("Range checks", [["create", ["r", "a\nb\nc"]], ["view", ["r", 0, 2]], ["view", ["r", 2, 1]],
                           ["view", ["r", 3, 3]], ["view", ["r", 2, 2]], ["view", ["r", 1, 100]],
                           ["insert", ["r", -1, "x"]], ["insert", ["r", 4, "x"]], ["insert", ["r", 3, "d"]],
                           ["view", ["r", 3, -1]]]),
        C("Insert multi-line in middle", [["create", ["g", "top\nbottom"]], ["insert", ["g", 1, "m1\nm2"]],
                                          ["view", ["g", 1, -1]]]),
        C("Undo walkthrough", [["create", ["a.py", "x = 1"]], ["str_replace", ["a.py", "1", "2"]],
                               ["insert", ["a.py", 1, "y = 3"]], ["undo", ["a.py"]], ["view", ["a.py", 1, -1]],
                               ["undo", ["a.py"]], ["view", ["a.py", 1, -1]], ["undo", ["a.py"]]], tag="Follow-up"),
        C("Undo ignores failed edits", [["create", ["a", "k = 1"]], ["str_replace", ["a", "k", "j"]],
                                        ["str_replace", ["a", "zzz", "q"]], ["insert", ["a", 9, "bad"]],
                                        ["undo", ["a"]], ["view", ["a", 1, -1]], ["undo", ["a"]]], tag="Follow-up"),
        C("Undo is per file", [["create", ["a", "1"]], ["create", ["b", "2"]], ["str_replace", ["a", "1", "one"]],
                               ["str_replace", ["b", "2", "two"]], ["undo", ["a"]], ["view", ["a", 1, -1]],
                               ["view", ["b", 1, -1]], ["undo", ["missing"]], ["undo", ["a"]]], tag="Follow-up"),
        C("Edit after undo", [["create", ["a", "p\nq"]], ["insert", ["a", 0, "h"]], ["undo", ["a"]],
                              ["insert", ["a", 2, "t"]], ["view", ["a", 1, -1]], ["undo", ["a"]],
                              ["view", ["a", 1, -1]], ["undo", ["a"]]], tag="Follow-up"),
        C("Undo insert into empty file", [["create", ["e", ""]], ["insert", ["e", 0, "x"]], ["insert", ["e", 2, "y"]],
                                          ["view", ["e", 1, -1]], ["undo", ["e"]], ["undo", ["e"]],
                                          ["view", ["e", 1, -1]]], tag="Follow-up"),
    ]
    paths = ["a.py", "b.py", "ghost.py"]
    for i in range(3):
        t.append(C(f"Random edits #{i + 1}", random_ops(rng, 80, paths, False), hidden=True))
    for i in range(3):
        t.append(C(f"Random edits + undo #{i + 1}", random_ops(rng, 120, paths, True), tag="Follow-up", hidden=True))
    t.append(C("Long session (20k calls)", big_session(random.Random(7), 20000), tag="Follow-up", hidden=True))
    return t


def big_session(rng, n, size=3000):
    """A `size`-line file, many unique-line edits, inserts and undos."""
    base = "\n".join(f"line_{i} = {i}" for i in range(size))
    ops = [["create", ["big.py", base]]]
    for _ in range(n):
        r = rng.random()
        if r < 0.4:
            i = rng.randrange(size)
            ops.append(["str_replace", ["big.py", f"line_{i} = {i}\n", f"line_{i} = {i}\n# touched\n"]])
        elif r < 0.65:
            ops.append(["insert", ["big.py", rng.randint(0, size), f"# note {rng.randrange(10**6)}"]])
        elif r < 0.9:
            ops.append(["undo", ["big.py"]])
        else:
            a = rng.randint(1, size)
            ops.append(["view", ["big.py", a, a + 3]])
    return ops


def scale(n):
    return C(f"{n} calls", big_session(random.Random(n), n, 1000))


SCALE = {"sizes": [250, 500, 1000, 2000, 4000, 8000], "label": "n = tool calls on a 1000-line file"}
