import random
from engine.spec import cls


def C(name, ops, **kw):
    return cls(name, "BPETokenizer", [], ops, **kw)


def tr(text, th): return ["train", [text, th]]
def enc(text): return ["encode", [text]]
def dec(ids): return ["decode", [ids]]


def rand_text(rng, alphabet, n):
    return "".join(rng.choice(alphabet) for _ in range(n))


def corpus(rng, n, letters="abcdefgh", vocab=60):
    words = [rand_text(rng, letters, rng.randint(2, 6)) for _ in range(vocab)]
    out, length = [], 0
    while length < n:
        w = rng.choice(words)
        out.append(w)
        length += len(w) + 1
    return " ".join(out)[:n]


def tests():
    rng = random.Random(21)
    t = [
        C("Example: train", [tr("abababa", 2)]),
        C("Overlapping pairs count, merge left to right", [tr("aaa", 1), tr("aaaa", 2), tr("aaaaa", 3)]),
        C("Threshold too high learns nothing", [tr("hello", 2)]),
        C("Empty text", [tr("", 1)]),
        C("Tie-break compares (left, right)", [tr("ba ab", 1)]),
        C("Spaces are ordinary characters", [tr("to be or not to be", 2)]),
        C("Example: encode / decode", [tr("abababa", 2), enc("ababab"), enc("abc"), dec([3, 0]), dec([4])], tag="Part 2"),
        C("Round trip", [tr("the cat sat on the mat", 2), enc("the mat sat"), dec([]), enc(""),
                         ["decode", [[0, 1, 2]]]], tag="Part 2"),
        C("Rules apply in training order", [tr("abcabcabc bcbc", 2), enc("abcbc"), enc("bcabc")], tag="Part 2"),
        C("Unknown characters and ids", [tr("abab", 2), enc("xabx"), dec([-1]), dec([0, 2, 5]), dec([2, 1, 0])], tag="Part 2"),
        C("Retraining replaces the vocabulary", [tr("aaaa", 2), enc("aaaa"), tr("bbbb", 2), enc("aaaa"), enc("bbbb")], tag="Part 2"),
    ]
    for s in range(3):
        alpha = rng.choice(["ab", "abc", "a b", "aab"])
        text = rand_text(rng, alpha, 60)
        ops = [tr(text, rng.randint(1, 3))]
        for _ in range(4):
            ops.append(enc(rand_text(rng, alpha + "z", rng.randint(0, 25))))
        ops.append(dec([rng.randint(-1, 12) for _ in range(5)]))
        t.append(C(f"Random small #{s + 1}", ops, tag="Part 2", hidden=True))
    t.append(C("Train on 20k random chars", [tr(rand_text(rng, "abcdefghijklmnop", 20000), 2)], hidden=True))
    t.append(C("Train on a 20k-char corpus", [tr(corpus(rng, 20000), 2)], hidden=True))
    big = rand_text(rng, "abcdefghij", 20000)
    t.append(C("Train 20k, encode 10k", [tr(big, 2), enc(big[5000:15000])], tag="Part 2", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return C(f"len={n}", [tr(rand_text(rng, "abcdefghijklmnop", n), 2)])


SCALE = {"sizes": [1000, 2000, 4000, 8000, 16000, 32000, 64000], "label": "n = len(training text)"}
