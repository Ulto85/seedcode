import random
from engine.spec import cls

AIRPORTS = ["JFK", "SFO", "LAX", "SEA", "ORD", "BOS", "MIA", "DEN", "ATL", "AUS"]
EX = [["SFO", 600, "JFK", 900, "alice"], ["JFK", 100, "SFO", 460, "alice"], ["LAX", 200, "SEA", 350, "bob"]]


def C(name, flights, ops, **kw):
    return cls(name, "FlightLog", [flights], ops, **kw)


def rand_log(rng, n_flights, n_users):
    """Non-overlapping random itineraries per user, then shuffled."""
    users = [f"u{i:05d}" for i in range(n_users)]
    clock = {u: rng.randint(0, 500) for u in users}
    flights = []
    for _ in range(n_flights):
        u = rng.choice(users)
        dep_t = clock[u] + rng.choice([0, 0, 1, 30, 200, 1000])
        arr_t = dep_t + rng.randint(1, 600)
        clock[u] = arr_t
        flights.append([rng.choice(AIRPORTS), dep_t, rng.choice(AIRPORTS), arr_t, u])
    rng.shuffle(flights)
    return flights, users


def rand_queries(rng, flights, users, q):
    times = [f[1] for f in flights] + [f[3] for f in flights] or [0]
    hi = max(times) + 100
    ops = []
    for _ in range(q):
        r = rng.random()
        if r < 0.05:
            ops.append(["most_flights", []])
            continue
        u = rng.choice(users) if r > 0.1 else "nobody"
        t = rng.choice(times) if rng.random() < 0.4 else rng.randint(0, hi)
        ops.append(["location", [u, t]])
    return ops


def tests():
    rng = random.Random(7)
    t = [
        C("Example: most flights", EX, [["most_flights", []]]),
        C("Empty log", [], [["most_flights", []]]),
        C("Single record", [["BOS", 5, "MIA", 9, "zed"]], [["most_flights", []]]),
        C("Tie -> smallest user id", [["A", 1, "B", 2, "mike"], ["B", 3, "C", 4, "mike"], ["A", 1, "B", 2, "anna"], ["B", 5, "A", 6, "anna"], ["X", 1, "Y", 2, "zoe"]], [["most_flights", []]]),
        C("Example: locations", EX, [["location", ["alice", 50]], ["location", ["alice", 100]], ["location", ["alice", 460]], ["location", ["alice", 500]], ["location", ["alice", 2000]], ["location", ["carol", 300]]], tag="Follow-up"),
        C("Exact departure and arrival boundaries", [["JFK", 10, "SFO", 20, "a"], ["SFO", 20, "LAX", 30, "a"]], [["location", ["a", 9]], ["location", ["a", 10]], ["location", ["a", 19]], ["location", ["a", 20]], ["location", ["a", 29]], ["location", ["a", 30]]], tag="Follow-up"),
        C("Unsorted input, non-connecting flights", [["OAK", 500, "DEN", 700, "b"], ["JFK", 0, "SFO", 100, "b"], ["SEA", 300, "BOS", 400, "b"]], [["location", ["b", 150]], ["location", ["b", 450]], ["location", ["b", 600]], ["location", ["b", 701]]], tag="Follow-up"),
        C("Unknown user and empty log", [], [["location", ["ghost", 10]], ["most_flights", []]], tag="Follow-up"),
        C("Users don't interfere", [["A", 0, "B", 100, "x"], ["C", 50, "D", 60, "y"]], [["location", ["y", 70]], ["location", ["x", 70]], ["location", ["y", 49]]], tag="Follow-up"),
    ]
    for s in range(3):
        fl, us = rand_log(rng, rng.randint(5, 40), rng.randint(1, 5))
        t.append(C(f"Random log #{s + 1}", fl, rand_queries(rng, fl, us, 40), tag="Follow-up", hidden=True))
    fl, us = rand_log(rng, 100000, 20)
    t.append(C("100k flights, 100k queries (few heavy users)", fl, rand_queries(rng, fl, us, 100000), tag="Follow-up", hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    fl, us = rand_log(rng, n, 8)
    return C(f"n={n}", fl, rand_queries(rng, fl, us, n))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = flights = queries"}
