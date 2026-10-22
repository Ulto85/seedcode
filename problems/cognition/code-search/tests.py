import random
from engine.spec import cls

EX = [["add_file", ["src/json_util.py", "def parseJSON(raw):\n    return json.loads(raw)"]],
      ["add_file", ["src/http.py", "class HTTPServer:\n    def parse_request(self, raw): return raw"]],
      ["add_file", ["README.md", "Parse JSON quickly. JSON json JSON!"]]]

BASE = ["get", "set", "user", "id", "parse", "json", "http", "server", "request", "cache", "load", "save",
        "token", "agent", "tool", "diff", "patch", "file", "path", "query", "index", "retry", "max", "config"]


def C(name, ops, **kw):
    return cls(name, "CodeSearch", [], ops, **kw)


def ident(rng, vocab):
    """A random identifier in a random style built from 1-3 vocab words, sometimes with a number."""
    ws = [rng.choice(vocab) for _ in range(rng.randint(1, 3))]
    style = rng.randrange(4)
    if style == 0:
        s = ws[0] + "".join(w.capitalize() for w in ws[1:])          # camelCase
    elif style == 1:
        s = "_".join(ws)                                               # snake_case
    elif style == 2:
        s = "".join(w.upper() if len(w) <= 4 and rng.random() < 0.5 else w.capitalize() for w in ws)  # HTTPServer
    else:
        s = "_".join(w.upper() for w in ws)                            # CONST_CASE
    if rng.random() < 0.15:
        s += str(rng.randrange(4))
    return s


def code(rng, vocab, n_tokens):
    seps = [" ", "(", ")", ".", ", ", "\n", " = ", ": ", "->"]
    return "".join(ident(rng, vocab) + rng.choice(seps) for _ in range(n_tokens))


def random_ops(rng, n, n_paths, vocab, with_updates, tokens=(0, 20)):
    paths = [f"src/{rng.choice(vocab)}_{i}.py" for i in range(n_paths)]
    ops, added = [], set()
    for _ in range(n):
        r = rng.random()
        if r < 0.3 and (with_updates or len(added) < n_paths):
            p = rng.choice(paths if with_updates else [q for q in paths if q not in added])
            added.add(p)
            ops.append(["add_file", [p, code(rng, vocab, rng.randint(*tokens))]])
        elif with_updates and r < 0.4:
            ops.append(["remove_file", [rng.choice(paths)]])
        else:
            q = " ".join(ident(rng, vocab) for _ in range(rng.randint(1, 2)))
            if rng.random() < 0.05:
                q = rng.choice(["", "__", "!!", "zzz"])
            ops.append(["search", [q, rng.choice([1, 2, 3, 5, 10, 0])]])
    return ops


def big(rng, n_files, n_queries, tokens=60):
    vocab = [f"w{i}" for i in range(1500)] + BASE
    ops = []
    for i in range(n_files):
        ops.append(["add_file", [f"pkg/m{i}.py", code(rng, vocab, tokens)]])
    for _ in range(n_queries):
        r = rng.random()
        if r < 0.05:
            ops.append(["add_file", [f"pkg/m{rng.randrange(n_files)}.py", code(rng, vocab, tokens)]])
        elif r < 0.07:
            ops.append(["remove_file", [f"pkg/m{rng.randrange(n_files)}.py"]])
        else:
            q = " ".join(rng.choice(vocab) for _ in range(rng.randint(1, 3)))
            ops.append(["search", [q, 10]])
    return ops


def tests():
    rng = random.Random(5)
    t = [
        C("Example", EX + [["search", ["parse json", 5]], ["search", ["raw", 1]], ["search", ["__", 3]]]),
        C("Tokenization: camel, acronyms, digits", [
            ["add_file", ["a", "getUserID2 HTTPServer parseJSON v2Beta"]],
            ["search", ["user id", 3]], ["search", ["http", 3]], ["search", ["2", 3]], ["search", ["beta v", 3]],
            ["search", ["userid", 3]], ["search", ["getuserid2", 3]]]),
        C("Underscore is a separator", [["add_file", ["c.py", "MAX_RETRIES = 10\nmax_retries_total"]],
                                        ["search", ["max retries", 5]], ["search", ["MaxRetries", 5]],
                                        ["search", ["10", 5]], ["search", ["total_max", 5]]]),
        C("All terms required", [["add_file", ["x", "alpha beta"]], ["add_file", ["y", "alpha alpha"]],
                                 ["search", ["alpha beta", 5]], ["search", ["alpha", 5]], ["search", ["gamma", 5]],
                                 ["search", ["alpha gamma", 5]]]),
        C("Duplicate query terms count once", [["add_file", ["x", "foo foo bar"]], ["add_file", ["y", "foo bar bar bar"]],
                                               ["search", ["foo foo foo bar", 5]], ["search", ["fooFoo", 5]]]),
        C("Ties by path, k limits", [["add_file", ["b", "tok"]], ["add_file", ["a", "tok"]], ["add_file", ["c", "tok tok"]],
                                     ["search", ["tok", 2]], ["search", ["tok", 10]], ["search", ["tok", 0]],
                                     ["search", ["tok", -1]]]),
        C("Empty index and empty file", [["search", ["x", 3]], ["add_file", ["empty", ""]], ["search", ["", 3]],
                                         ["search", ["empty", 3]]]),
        C("Replace a file", [["add_file", ["f", "oldName oldName"]], ["add_file", ["g", "old"]],
                             ["search", ["old", 5]], ["add_file", ["f", "newName"]], ["search", ["old", 5]],
                             ["search", ["new name", 5]]], tag="Follow-up"),
        C("Remove a file", [["add_file", ["f", "cache"]], ["add_file", ["g", "cache cache"]],
                            ["remove_file", ["g"]], ["search", ["cache", 5]], ["remove_file", ["g"]],
                            ["remove_file", ["nope"]], ["remove_file", ["f"]], ["search", ["cache", 5]],
                            ["add_file", ["g", "cache"]], ["search", ["cache", 5]]], tag="Follow-up"),
    ]
    for i in range(3):
        t.append(C(f"Random index #{i + 1}", random_ops(rng, 120, 30, BASE, False), hidden=True))
    for i in range(3):
        t.append(C(f"Random with updates #{i + 1}", random_ops(rng, 200, 15, BASE, True), tag="Follow-up", hidden=True))
    t.append(C("5000 files, 15000 calls", big(rng, 5000, 15000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"n={n}", big(random.Random(n), n, 3 * n, 20))


SCALE = {"sizes": [125, 250, 500, 1000, 2000, 4000], "label": "n = files of ~20 identifiers (then 3n searches/updates)"}
