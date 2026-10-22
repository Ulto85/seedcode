import random
from engine.spec import fn

WORDS = "reset password refund order ship track cancel plan billing agent login email phone wait help".split()


def is_header(line):
    n = len(line) - len(line.lstrip("#"))
    return n if 1 <= n <= 6 and line[n:n + 1] == " " else 0


def min_size(md):
    """Smallest max_size that satisfies the guarantee: every line plus its prefix fits."""
    active, need = [None] * 7, 1
    for line in md.split("\n"):
        lvl = is_header(line)
        pre = [h for h in active[1:(lvl or 7)] if h is not None]
        need = max(need, sum(map(len, pre)) + len(pre) + len(line))
        if lvl:
            active[lvl] = line
            active[lvl + 1:] = [None] * (6 - lvl)
    return need


def random_doc(rng, n_lines, max_words=6, deep=6):
    out = []
    for _ in range(n_lines):
        r = rng.random()
        if r < 0.2:
            out.append("#" * rng.randint(1, deep) + " " + " ".join(rng.choice(WORDS) for _ in range(rng.randint(0, 3))))
        elif r < 0.27:
            out.append(rng.choice(["#tag", "####### seven", " # indented", "#", "##"]))
        elif r < 0.37:
            out.append("")
        else:
            out.append(" ".join(rng.choice(WORDS) for _ in range(rng.randint(1, max_words))))
    return "\n".join(out)


EX = "# Guide\nIntro line\n## Setup\nStep one\nStep two\n## Usage\nRun it"


def tests():
    rng = random.Random(31)
    t = [
        fn("Example", "split_markdown", EX, 30),
        fn("Whole doc fits", "split_markdown", EX, 100),
        fn("Empty string", "split_markdown", "", 10),
        fn("No headers", "split_markdown", "aaa\nbb\ncccc\nd", 7),
        fn("Blank lines are kept", "split_markdown", "# T\n\n\nx\n", 5),
        fn("Shallower header clears deeper ones", "split_markdown", "# A\n## B\n### C\nx\n## D\ny\nz", 16),
        fn("Skipped levels", "split_markdown", "# A\n### C\nx\nyy\n## B\nz", 12),
        fn("Things that aren't headers", "split_markdown", "# A\n#tag\n####### seven\n # indented\n#\nend", 17),
        fn("Every line its own chunk", "split_markdown", "# H\none\ntwo\n# K\nthree", 9),
        fn("Size exactly max_size", "split_markdown", "# A\nbcd\nefg", 11),
        fn("Header as first line repeats only parents", "split_markdown", "# A\n## B\nxxxxxx\n## C\n### D\nyy", 17),
    ]
    for s in range(5):
        md = random_doc(rng, rng.randint(5, 40))
        t.append(fn(f"Random doc #{s + 1}", "split_markdown", md, min_size(md) + rng.randint(0, 40), hidden=True))
    md = random_doc(rng, 15000, 3)
    t.append(fn("Big doc, big chunks", "split_markdown", md, 150000, hidden=True))
    md = random_doc(rng, 10000)
    t.append(fn("Big doc, small chunks", "split_markdown", md, min_size(md) + 20, hidden=True))
    tiny = "\n".join(rng.choice(["a", "", "bb", "# h", "## s", "c"]) for _ in range(70000))
    t.append(fn("70k tiny lines", "split_markdown", tiny, 100000, hidden=True))
    return t


def scale(n):
    md = random_doc(random.Random(n), n, 3)
    return fn(f"{n} lines", "split_markdown", md, len(md) // 2)


SCALE = {"sizes": [1250, 2500, 5000, 10000, 20000, 40000], "label": "n = number of lines"}
