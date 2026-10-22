import random
from engine.spec import fn

F, G = "convert_to_trace", "convert_to_trace_min"
EX = [[0, ["main"]], [1, ["main", "a"]], [2, ["main", "a", "b"]], [3, ["main", "c"]], [4, []]]
NAMES = ["main", "a", "b", "c", "d", "parse", "eval"]


def random_samples(rng, n, max_depth=12, names=NAMES):
    """Random walk over stacks: push / pop / swap the top / jump, with repeats."""
    out, stack, t = [], [], 0
    for _ in range(n):
        r = rng.random()
        if r < 0.35 and len(stack) < max_depth:
            stack = stack + [rng.choice(names)]
        elif r < 0.6 and stack:
            stack = stack[:-rng.randint(1, len(stack))]
        elif r < 0.75 and stack:
            stack = stack[:-1] + [rng.choice(names)]
        elif r < 0.8:
            stack = [rng.choice(names) for _ in range(rng.randint(0, 4))]
        out.append([t, list(stack)])
        t += rng.choice([0, 1, 1, 2, 5])
    return out


def tests():
    rng = random.Random(7)
    t = [
        fn("Example", F, EX),
        fn("Empty input", F, []),
        fn("Single sample: nothing ends", F, [[5, ["main", "a"]]]),
        fn("Identical consecutive stacks", F, [[0, ["a", "b"]], [1, ["a", "b"]], [2, ["a", "b"]], [3, ["a"]]]),
        fn("Recursion: same name, new call", F, [[0, ["a"]], [1, ["a", "a"]], [2, ["a", "a", "a"]], [3, ["a"]], [4, ["a", "a"]]]),
        fn("Caller changed -> callee is a new call", F, [[0, ["a", "b"]], [1, ["c", "b"]]]),
        fn("Idle sample in the middle", F, [[0, ["main", "x"]], [1, []], [2, []], [3, ["main", "x"]]]),
        fn("Starts with empty stack", F, [[0, []], [1, ["f"]], [2, ["f", "g", "h"]], [3, ["f", "g", "h"]], [4, ["f"]]]),
        fn("Equal timestamps", F, [[1, ["a"]], [1, ["b"]], [1, ["b", "c"]], [2, []]]),
        fn("Example, n = 2", G, EX, 2, tag="Follow-up"),
        fn("n = 1 equals Part 1", G, EX, 1, tag="Follow-up"),
        fn("Open call at the end, kept and dropped", G, [[0, ["m"]], [1, ["m", "a"]], [2, ["m", "a"]], [3, ["m", "a", "z"]]], 2, tag="Follow-up"),
        fn("Recursive frames filtered", G, [[0, ["a"]], [1, ["a", "a"]], [2, ["a", "a", "a"]], [3, ["a", "a"]], [4, ["a"]], [5, []]], 3, tag="Follow-up"),
        fn("Everything dropped", G, [[0, ["a"]], [1, ["b"]], [2, ["c"]]], 2, tag="Follow-up"),
    ]
    for s in range(3):
        t.append(fn(f"Random #{s + 1}", F, random_samples(rng, 25), hidden=True))
    for s in range(3):
        t.append(fn(f"Random de-noise #{s + 1}", G, random_samples(rng, 30), rng.randint(2, 4), tag="Follow-up", hidden=True))
    t.append(fn("100k samples", F, random_samples(rng, 100000, max_depth=40), hidden=True))
    t.append(fn("100k samples, de-noise", G, random_samples(rng, 100000, max_depth=40), 3, tag="Follow-up", hidden=True))
    return t


def scale(n):
    return fn(f"n={n}", F, random_samples(random.Random(n), n, max_depth=30))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of samples"}
