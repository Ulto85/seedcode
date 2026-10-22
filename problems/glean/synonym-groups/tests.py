import random
from engine.spec import fn

EX1 = [
    "i really like this movie a lot",
    "i really love this movie a lot",
    "we all love the new search",
    "we all enjoy the new search",
]
EX2 = ["p q red r s", "p q blue r s", "m n big o t", "m n large o t", "m n huge o u"]


def F(name, sentences, **kw):
    return fn(name, "synonym_groups", sentences, **kw)


def gen(rng, n_sent, frame_words, fill_words, length):
    """Sentences built from a small frame vocabulary, so contexts repeat and chains form."""
    out = []
    for _ in range(n_sent):
        k = rng.randint(1, length)
        out.append(" ".join(rng.choice(frame_words if i % 2 == 0 else fill_words) for i in range(k)))
    return out


def gen_chunks(rng, n_words, n_ctx, n_mid):
    """Sentences made of 5-word chunks "a b MID c d". Each chunk context has a few candidate middle words, so
    groups of real size form through chains of shared contexts."""
    vocab = [f"c{i}" for i in range(max(10, n_ctx // 4))]
    mids = [f"m{i}" for i in range(n_mid)]
    ctxs = [([rng.choice(vocab) for _ in range(4)], rng.sample(mids, 2)) for _ in range(n_ctx)]
    out, total = [], 0
    while total < n_words:
        words = []
        for _ in range(rng.randint(1, 19)):
            (a, b, c, d), cand = rng.choice(ctxs)
            words += [a, b, rng.choice(cand), c, d]
        out.append(" ".join(words))
        total += len(words)
    return out


def tests():
    rng = random.Random(8)
    t = [
        F("Example: transitive chain", EX1),
        F("Two groups, one loner", EX2),
        F("Too short for any context", ["the cat sat"]),
        F("Single word", ["hello"]),
        F("Same sentence twice is not a synonym", ["a b c d e", "a b c d e"]),
        F("Exactly five words, middle only", ["a b x d e", "a b y d e", "a b z d f"]),
        F("Edge words have no context", ["x y a b c", "z y a b c", "x y q b c"]),
        F("Long chain across many sentences", ["s t w1 u v", "s t w2 u v", "s2 t w2 u v", "s2 t w3 u v",
                                                "s3 t w3 u v", "s3 t w4 u v"]),
        F("Word in several groups merges them", ["a a x a a", "a a y a a", "b b y b b", "b b z b b", "c c q c c"]),
        F("Context words can themselves be grouped", ["a b c d e f g", "a b x d e f g"]),
    ]
    for s in range(3):
        t.append(F(f"Random small #{s + 1}", gen(rng, 40, list("abc"), [f"w{i}" for i in range(12)], 7), hidden=True))
    t.append(F("Random chunked corpus", gen_chunks(rng, 300, 20, 30), hidden=True))
    t.append(F("200k-word corpus", gen_chunks(rng, 200000, 8000, 12000), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return F(f"{n} words", gen_chunks(rng, n, n // 25, n // 16))


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = total words"}
