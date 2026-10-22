import random
import string
from engine.spec import fn

F, G = "tokenize", "tokenize_spans"
V = {"a": 1, "ab": 2, "abc": 3, "b": 4, "cd": 5}


def random_vocab(rng, size, max_len, alphabet):
    vocab = {}
    while len(vocab) < size:
        w = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, max_len)))
        vocab.setdefault(w, len(vocab) + 1)
    return vocab


def random_text(rng, n, vocab, alphabet, noise):
    words = list(vocab)
    parts, size = [], 0
    while size < n:
        p = rng.choice(alphabet + "#!?") if rng.random() < noise else rng.choice(words)
        parts.append(p)
        size += len(p)
    return "".join(parts)[:n]


def tests():
    rng = random.Random(5)
    t = [
        fn("Example", F, "abcdxabzzb", V, 0),
        fn("Empty text", F, "", V, 0),
        fn("All unknown", F, "xyz", V, -1),
        fn("Greedy is not optimal", F, "abcd", {"ab": 1, "abc": 2, "cd": 3}, 99),
        fn("Prefix of a key is not a match", F, "hel hello", {"hello": 7, " ": 1, "he": 2}, 0),
        fn("Case-sensitive", F, "Abab", {"ab": 3, "A": 4}, 0),
        fn("Repeated character, many lengths", F, "xxxxxxx", {"x": 1, "xx": 2, "xxx": 3}, 0),
        fn("Literal 'UNK' in the text is ordinary text", F, "<UNK>a", {"a": 1, "<": 2}, 0),
        fn("Example (spans)", G, "abcdxabzzb", V, 0, tag="Follow-up"),
        fn("Empty text (spans)", G, "", V, 0, tag="Follow-up"),
        fn("Whole text unknown -> one span", G, "zzzz", V, 0, tag="Follow-up"),
        fn("Unknown runs split by a known token", G, "qqaqq", V, -1, tag="Follow-up"),
        fn("Unicode code points", G, "héllo wörld", {"h": 1, "llo": 2, " w": 3, "rld": 4}, 0, tag="Follow-up"),
    ]
    for s in range(3):
        vocab = random_vocab(rng, 30, 4, "abcde")
        t.append(fn(f"Random #{s + 1}", F, random_text(rng, 60, vocab, "abcdefg", 0.2), vocab, 0, hidden=True))
        t.append(fn(f"Random spans #{s + 1}", G, random_text(rng, 60, vocab, "abcdefg", 0.3), vocab, 0, tag="Follow-up", hidden=True))
    big_vocab = random_vocab(rng, 4000, 14, string.ascii_lowercase[:10])
    t.append(fn("200k chars, 4000-word vocab", F, random_text(rng, 200000, big_vocab, "abcdefghijk", 0.05), big_vocab, 0, hidden=True))
    t.append(fn("200k chars, spans", G, random_text(rng, 200000, big_vocab, "abcdefghijk", 0.05), big_vocab, 0, tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    vocab = random_vocab(rng, 2000, 12, "abcdefgh")
    return fn(f"n={n}", F, random_text(rng, n, vocab, "abcdefghi", 0.05), vocab, 0)


SCALE = {"sizes": [5000, 10000, 20000, 40000, 80000, 160000], "label": "n = len(text) (vocab fixed at 2000 words)"}
