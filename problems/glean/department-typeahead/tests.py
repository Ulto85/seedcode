import random
from engine.spec import cls

EXAMPLE = [
    ["sales deck", 1, 50], ["salesforce", 1, 90], ["salary bands", 2, 70],
    ["sales kickoff", 1, 50], ["security", 1, 99], ["salesforce", 2, 10],
]


def C(name, sugg, ops, **kw):
    return cls(name, "Typeahead", [sugg], ops, **kw)


def q(query, dept, k):
    return ["top", [query, dept, k]]


def word(rng, letters, lo, hi):
    return "".join(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def gen(rng, n, depts, letters="abcde", maxlen=8, maxscore=10 ** 6):
    return [[word(rng, letters, 1, maxlen), rng.randint(1, depts), rng.randint(0, maxscore)] for _ in range(n)]


def gen_queries(rng, n, depts, letters="abcde", kmax=10):
    ops = []
    for _ in range(n):
        r = rng.random()
        plen = 0 if r < 0.15 else 1 if r < 0.55 else 2 if r < 0.8 else rng.randint(3, 5)
        ops.append(q(word(rng, letters, plen, plen), rng.randint(0, depts + 1), rng.randint(0, kmax)))
    return ops


def tests():
    rng = random.Random(3)
    t = [
        C("Example", EXAMPLE, [q("sal", 1, 2), q("sal", 1, 10), q("sal", 2, 10), q("", 1, 1), q("sal", 3, 5)]),
        C("Empty suggestion list", [], [q("", 1, 5), q("a", 0, 1)]),
        C("k = 0 and no prefix match", EXAMPLE, [q("sal", 1, 0), q("zzz", 1, 3), q("salesforcex", 1, 3)]),
        C("Query equal to a whole ngram", EXAMPLE, [q("salesforce", 1, 5), q("sales", 1, 5)]),
        C("Ties broken by ngram ascending", [["bb", 1, 5], ["ba", 1, 5], ["b", 1, 5], ["bc", 1, 7], ["a", 1, 5]],
          [q("b", 1, 3), q("", 1, 10)]),
        C("Duplicates keep the highest score", [["doc", 1, 3], ["doc", 1, 8], ["dog", 1, 5], ["doc", 2, 1]],
          [q("do", 1, 5), q("do", 2, 5), q("do", 1, 1)]),
        C("Departments never leak", [["alpha", 1, 1], ["alpha", 2, 100], ["alps", 2, 50], ["alto", 1, 2]],
          [q("al", 1, 5), q("al", 2, 5), q("alp", 2, 1)]),
        C("Case-sensitive, space is a character", [["new hire", 1, 4], ["newsletter", 1, 9], ["New", 1, 20]],
          [q("new ", 1, 5), q("new", 1, 5), q("N", 1, 5)]),
    ]
    for s in range(3):
        sugg = gen(rng, 80, 3, "abc", 4, 20)
        t.append(C(f"Random small #{s + 1}", sugg, gen_queries(rng, 60, 3, "abc"), hidden=True))
    big = gen(rng, 60000, 4)
    t.append(C("60k suggestions, 20k queries", big, gen_queries(rng, 20000, 4), tag="Part 2", hidden=True))
    one = gen(rng, 40000, 1, "ab", 16)
    t.append(C("One huge department, broad prefixes", one, gen_queries(rng, 15000, 1, "ab", 20), tag="Part 2", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return C(f"{n} suggestions", gen(rng, n, 2), gen_queries(rng, n // 3, 2), tag="Part 2")


SCALE = {"sizes": [1500, 3000, 6000, 12000, 24000, 48000], "label": "n = suggestions (n/3 queries, mostly broad prefixes)"}
