import random
from engine.spec import fn

EX = "import os\ndef f():\n    return 1\n\ndef g():\n    return 2"
EX_PATCH = "@@ -2,2 +2,3 @@\n def f():\n-    return 1\n+    x = 1\n+    return x\n@@ -6 +7 @@\n-    return 2\n+    return 3"
FZ = "x\ny\na\nb\nc\nb\nc"


def make_file(rng, n, vocab):
    return [rng.choice(vocab) for _ in range(n)]


def make_patch(rng, lines, n_hunks, noise=0, max_old=4, corrupt=0.0, inserts=False, drift=0, min_old=1):
    """Builds hunks from real positions (so they apply), then optionally shifts headers by up to
    `noise` lines (independently per hunk) plus a random-walk `drift` offset (like a file that was edited
    after the diff was made), and corrupts a line with probability `corrupt`."""
    n = len(lines)
    starts = sorted(rng.sample(range(1, n + 1), min(n_hunks, n)))
    out, last_end, offset = [], 0, 0
    for s in starts:
        if s <= last_end:
            continue
        k = rng.randint(0 if inserts else min_old, max_old)
        k = min(k, n - s + 1)
        if k == 0:
            a = s - 1
            if a < last_end:
                continue
            body = ["+" + f"new{rng.randrange(100)}" for _ in range(rng.randint(1, 3))]
            out.append(f"@@ -{a},0 +{a + 1},{len(body)} @@")
            out.extend(body)
            last_end = a
            continue
        body = []
        for i in range(k):
            text = lines[s - 1 + i]
            if rng.random() < corrupt:
                text = text + "_typo"
            if rng.random() < 0.3:
                body.append("+" + f"add{rng.randrange(100)}")
            body.append(("-" if rng.random() < 0.5 else " ") + text)
        if rng.random() < 0.5:
            body.append("+" + f"add{rng.randrange(100)}")
        if drift:
            offset = max(-50, min(50, offset + rng.randint(-drift, drift)))
        a = s + offset + (rng.randint(-noise, noise) if noise else 0)
        a = max(1, a)
        out.append(f"@@ -{a},{k} +{a},{k} @@")
        out.extend(body)
        last_end = s + k - 1
    return "\n".join(out)


def tests():
    rng = random.Random(77)
    small_vocab = ["a", "b", "c", "", "  pass", "return x"]
    t = [
        fn("Example", "apply_patch", EX, EX_PATCH),
        fn("Mismatch returns None", "apply_patch", EX, "@@ -1 +1 @@\n-import sys\n+import re"),
        fn("Insert at top", "apply_patch", "a\nb", "@@ -0,0 +1 @@\n+top"),
        fn("Insert at bottom", "apply_patch", "a\nb", "@@ -2,0 +3,2 @@\n+c\n+d"),
        fn("Delete everything", "apply_patch", "a\nb\nc", "@@ -1,3 +0,0 @@\n-a\n-b\n-c"),
        fn("Trailing newline in file and patch", "apply_patch", "a\nb\n", "@@ -2,2 +2,2 @@\n-b\n-\n+B\n+\n"),
        fn("Hunk past end of file", "apply_patch", "a\nb", "@@ -2,2 +2,2 @@\n b\n-c\n+C"),
        fn("Hunks out of order", "apply_patch", "a\nb\nc\nd", "@@ -3 +3 @@\n-c\n+C\n@@ -1 +1 @@\n-a\n+A"),
        fn("Overlapping hunks", "apply_patch", "a\nb\nc\nd", "@@ -1,2 +1,2 @@\n a\n-b\n+B\n@@ -2 +2 @@\n-b\n+X"),
        fn("Adjacent hunks are fine", "apply_patch", "a\nb\nc\nd", "@@ -1,2 +1,2 @@\n a\n-b\n+B\n@@ -3 +3 @@\n-c\n+C"),
        fn("Line numbers refer to the original", "apply_patch", "1\n2\n3\n4\n5",
           "@@ -1 +1,3 @@\n-1\n+one\n+uno\n+ein\n@@ -4 +6 @@\n-4\n+four"),
        fn("Header with no counts", "apply_patch", "p\nq", "@@ -2 +2 @@\n q\n+r"),
        fn("Second hunk fails: nothing applied", "apply_patch", "a\nb\nc", "@@ -1 +1 @@\n-a\n+A\n@@ -3 +3 @@\n-z\n+Z"),
        fn("Insertion after a hunk's last line", "apply_patch", "a\nb\nc", "@@ -1,2 +1,2 @@\n a\n-b\n+B\n@@ -2,0 +3 @@\n+mid"),
        fn("Fuzzy: nearest match", "apply_patch_fuzzy", FZ, "@@ -3 +3 @@\n b\n-c\n+C", tag="Follow-up"),
        fn("Fuzzy: tie goes to smaller line", "apply_patch_fuzzy", FZ, "@@ -5 +5 @@\n b\n-c\n+C", tag="Follow-up"),
        fn("Fuzzy: exact position still wins", "apply_patch_fuzzy", FZ, "@@ -6 +6 @@\n b\n-c\n+C", tag="Follow-up"),
        fn("Fuzzy: delta carries to the next hunk", "apply_patch_fuzzy", "h\nh\nh\nk1\nm\nk2\nm\nm\nk2",
           "@@ -1 +1 @@\n-k1\n+K1\n@@ -5 +5 @@\n-k2\n+K2", tag="Follow-up"),
        fn("Fuzzy: must not overlap earlier hunk", "apply_patch_fuzzy", "a\nb\nq\nz",
           "@@ -2 +2 @@\n a\n-b\n+B\n@@ -1 +1 @@\n-a\n+A", tag="Follow-up"),
        fn("Fuzzy: no match anywhere", "apply_patch_fuzzy", FZ, "@@ -1 +1 @@\n-nope\n+yes", tag="Follow-up"),
        fn("Fuzzy: header beyond end of file", "apply_patch_fuzzy", FZ, "@@ -50 +50 @@\n-y\n+Y", tag="Follow-up"),
    ]
    for i in range(4):
        lines = make_file(rng, rng.randint(5, 40), small_vocab)
        t.append(fn(f"Random exact #{i + 1}", "apply_patch", "\n".join(lines),
                    make_patch(rng, lines, rng.randint(1, 6), corrupt=0.05 if i % 2 else 0, inserts=True), hidden=True))
    for i in range(4):
        lines = make_file(rng, rng.randint(5, 40), small_vocab)
        t.append(fn(f"Random exact, some typos #{i + 1}", "apply_patch", "\n".join(lines),
                    make_patch(rng, lines, 3, corrupt=0.12 if i % 2 else 0.04), hidden=True))
    for i in range(6):
        lines = make_file(rng, rng.randint(10, 60), small_vocab)
        t.append(fn(f"Random fuzzy #{i + 1}", "apply_patch_fuzzy", "\n".join(lines),
                    make_patch(rng, lines, rng.randint(1, 5), noise=3, drift=2, min_old=2, max_old=4,
                               corrupt=0.05 if i == 5 else 0),
                    tag="Follow-up", hidden=True))
    big_vocab = [f"stmt_{i}()" for i in range(3000)]
    lines = make_file(rng, 200000, big_vocab)
    t.append(fn("200k lines, 2000 exact hunks", "apply_patch", "\n".join(lines),
                make_patch(rng, lines, 2000, max_old=6), hidden=True))
    lines = make_file(rng, 200000, big_vocab)
    t.append(fn("200k lines, 2000 shifted hunks", "apply_patch_fuzzy", "\n".join(lines),
                make_patch(rng, lines, 2000, noise=3, drift=8, min_old=3, max_old=6), tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    lines = make_file(rng, n, [f"stmt_{i}()" for i in range(3000)])
    return fn(f"n={n}", "apply_patch_fuzzy", "\n".join(lines), make_patch(rng, lines, n // 100, noise=3, drift=8, min_old=3, max_old=6))


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = file lines (hunks = n / 100, headers off by up to ~50)"}
