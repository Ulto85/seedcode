import random
from engine.spec import fn

H, C, Q = "highlight", "count_matches", "highlight_with_citations"


def rand_case(rng, n, alpha="abc", k=6):
    text = "".join(rng.choice(alpha) for _ in range(n))
    sources = []
    for _ in range(k):
        r = rng.random()
        if r < 0.5 and n > 0:                       # a real substring of the text
            i = rng.randrange(n)
            sources.append(text[i:i + rng.randint(1, 5)])
        elif r < 0.9:
            sources.append("".join(rng.choice(alpha) for _ in range(rng.randint(2, 5))))
        else:
            sources.append(rng.choice(["", "zz", "A"]))
    if sources and rng.random() < 0.3:
        sources.append(rng.choice(sources))             # duplicate source string
    return text, sources


def big_case(rng, n, k):
    text = "".join(rng.choice("abcd ") for _ in range(n))
    sources = []
    for _ in range(k):
        i = rng.randrange(n - 10)
        sources.append(text[i:i + rng.randint(3, 8)])
    return text, sources


def tests():
    rng = random.Random(11)
    t = [
        fn("Example: touching and overlapping merge", H, "abcxyz123", ["abc", "xyz", "z12"]),
        fn("Example: separate regions", H, "foobarbaz", ["foo", "baz"]),
        fn("No matches", H, "the quick brown fox", ["dog", "Fox"]),
        fn("Empty text and empty sources", H, "", ["", "a"]),
        fn("No sources", H, "liability cap", []),
        fn("Whole text covered", H, "indemnify", ["indem", "mnify"]),
        fn("Gap of one char keeps regions apart", H, "ab_cd", ["ab", "cd"]),
        fn("Self-overlapping source", H, "xaaaay", ["aa"]),
        fn("Substring inside a word still matches", H, "concatenate the cat", ["cat"]),
        fn("Case-sensitive", H, "Harvey harvey HARVEY", ["harvey"]),
        fn("Nested source inside a longer one", H, "governing law of Delaware", ["governing law of Delaware", "law"]),
        fn("Count example", C, "aaaaa", ["aa", "aaa", "b", ""], tag="Part 2"),
        fn("Count with duplicates and case", C, "Term. term. TERM.", ["term", "Term", "term", ".", "erm. t"], tag="Part 2"),
        fn("Count on empty text", C, "", ["a", ""], tag="Part 2"),
        fn("Citations example", Q, "abcxyz123", ["abc", "xyz", "z12"], tag="Follow-up"),
        fn("Citations per region", Q, "aaXXbbYYaa", ["aa", "bb", "YY", "q"], tag="Follow-up"),
        fn("Duplicate sources are both cited", Q, "net 30 days", ["net 30", "q", "net 30"], tag="Follow-up"),
        fn("Citations with no matches", Q, "plain text", ["", "zzz"], tag="Follow-up"),
        fn("Citation indices ascending", Q, "xyz", ["z", "y", "x", "xyz"], tag="Follow-up"),
    ]
    for s in range(4):
        text, src = rand_case(rng, rng.randint(20, 120))
        t.append(fn(f"Random highlight #{s + 1}", H, text, src, hidden=True))
    for s in range(3):
        text, src = rand_case(rng, rng.randint(20, 120))
        t.append(fn(f"Random count #{s + 1}", C, text, src, tag="Part 2", hidden=True))
    for s in range(4):
        text, src = rand_case(rng, rng.randint(20, 120), k=8)
        t.append(fn(f"Random citations #{s + 1}", Q, text, src, tag="Follow-up", hidden=True))
    text, src = big_case(rng, 200000, 150)
    t.append(fn("200k-char answer, 150 sources", H, text, src, hidden=True))
    t.append(fn("200k-char answer, citations", Q, text, src, tag="Follow-up", hidden=True))
    t.append(fn("100k identical chars", C, "a" * 100000, ["a", "aa", "aaaaa", "b"], tag="Part 2", hidden=True))
    return t


def scale(n):
    text, src = big_case(random.Random(n), n, 40)
    return fn(f"n={n}", Q, text, src)


SCALE = {"sizes": [4000, 8000, 16000, 32000, 64000, 128000], "label": "n = len(text), 40 sources"}
