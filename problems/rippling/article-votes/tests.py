import random
from engine.spec import cls

K = "VoteTracker"


def C(name, ops, **kw):
    return cls(name, K, [], ops, **kw)


def random_ops(rng, n, users=6, articles=5, follow=False):
    us = [f"u{i}" for i in range(users)]
    arts = [f"a{i}" for i in range(articles)]
    ops = []
    for _ in range(n):
        r = rng.random()
        if r < 0.6:
            ops.append(["vote", [rng.choice(us), rng.choice(arts), rng.choice(["UP", "UP", "DOWN"])]])
        elif r < 0.8 or not follow:
            ops.append(["get_last_votes", [rng.choice(us + ["ghost"])]])
        elif r < 0.9:
            ops.append(["top_article", []])
        else:
            ops.append(["score", [rng.choice(arts + ["nope"])]])
    return ops


EXAMPLE = [
    ["vote", ["ann", "a1", "UP"]], ["vote", ["ann", "a1", "UP"]], ["vote", ["bob", "a2", "DOWN"]],
    ["vote", ["ann", "a1", "DOWN"]], ["vote", ["ann", "a3", "UP"]], ["vote", ["ann", "a2", "UP"]],
    ["get_last_votes", ["ann"]], ["get_last_votes", ["zed"]],
    ["score", ["a1"]], ["score", ["a2"]], ["top_article", []],
]


def tests():
    rng = random.Random(5)
    t = [
        C("Example (Part 1 calls)", EXAMPLE[:8]),
        C("No votes yet", [["get_last_votes", ["ann"]]]),
        C("Fewer than 3 votes", [["vote", ["ann", "x", "UP"]], ["vote", ["ann", "y", "DOWN"]], ["get_last_votes", ["ann"]]]),
        C("Duplicates don't consume event numbers", [["vote", ["ann", "x", "UP"]], ["vote", ["ann", "x", "UP"]],
                                                     ["vote", ["ann", "x", "UP"]], ["vote", ["bob", "x", "UP"]],
                                                     ["get_last_votes", ["bob"]], ["get_last_votes", ["ann"]]]),
        C("UP, DOWN, UP is three events", [["vote", ["ann", "x", "UP"]], ["vote", ["ann", "x", "DOWN"]],
                                           ["vote", ["ann", "x", "UP"]], ["get_last_votes", ["ann"]]]),
        C("Only the newest 3 are kept", [["vote", ["ann", "a", "UP"]], ["vote", ["ann", "b", "UP"]],
                                         ["vote", ["ann", "c", "UP"]], ["vote", ["ann", "d", "DOWN"]],
                                         ["vote", ["ann", "b", "DOWN"]], ["get_last_votes", ["ann"]]]),
        C("Same article, different users are independent", [["vote", ["ann", "x", "UP"]], ["vote", ["bob", "x", "UP"]],
                                                            ["vote", ["bob", "x", "DOWN"]], ["get_last_votes", ["ann"]],
                                                            ["get_last_votes", ["bob"]]]),
        C("Example (with follow-up)", EXAMPLE, tag="Follow-up"),
        C("No votes: top is None, score 0", [["top_article", []], ["score", ["x"]]], tag="Follow-up"),
        C("Flip moves score by 2", [["vote", ["ann", "x", "UP"]], ["vote", ["bob", "x", "UP"]], ["score", ["x"]],
                                    ["vote", ["ann", "x", "DOWN"]], ["score", ["x"]]], tag="Follow-up"),
        C("Tie -> smallest id; negative-only articles still count", [
            ["vote", ["ann", "b", "DOWN"]], ["top_article", []], ["vote", ["bob", "c", "DOWN"]], ["top_article", []],
            ["vote", ["ann", "c", "UP"]], ["vote", ["bob", "a", "UP"]], ["vote", ["bob", "c", "UP"]], ["top_article", []],
            ["vote", ["ann", "a", "UP"]], ["top_article", []], ["vote", ["bob", "a", "DOWN"]], ["top_article", []]],
          tag="Follow-up"),
        C("Top drops after a flip", [["vote", ["u1", "a", "UP"]], ["vote", ["u2", "a", "UP"]], ["vote", ["u1", "b", "UP"]],
                                     ["top_article", []], ["vote", ["u1", "a", "DOWN"]], ["top_article", []],
                                     ["vote", ["u2", "a", "DOWN"]], ["top_article", []]], tag="Follow-up"),
    ]
    for s in range(3):
        t.append(C(f"Random #{s + 1}", random_ops(rng, 60), hidden=True))
    for s in range(3):
        t.append(C(f"Random with scores #{s + 1}", random_ops(rng, 80, follow=True), tag="Follow-up", hidden=True))
    t.append(C("150k ops, 300 users", random_ops(rng, 150000, users=300, articles=50000), hidden=True))
    t.append(C("150k ops, 20k articles, frequent top", random_ops(rng, 150000, users=2000, articles=20000, follow=True),
               tag="Follow-up", hidden=True))
    return t


def scale(n):
    return C(f"{n} ops", random_ops(random.Random(n), n, users=max(5, n // 50), articles=max(5, n // 4), follow=True))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "n = number of operations"}
