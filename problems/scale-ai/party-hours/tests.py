import random
from engine.spec import fn


def R(*rows):
    return [{"town": t, "city": c, "state": s} for t, c, s in rows]


EX_REGIONS = R(("t1", "c1", "s1"), ("t2", "c1", "s1"), ("t3", "c2", "s1"))


def random_case(rng, n_towns, n_parties, lo=-60, hi=1500, max_len=240):
    n_cities = max(1, n_towns // 3)
    regions = [{"town": f"t{i}", "city": f"c{rng.randrange(n_cities)}", "state": f"s{i % 3}"} for i in range(n_towns)]
    rng.shuffle(regions)
    parties = []
    for _ in range(n_parties):
        town = f"t{rng.randrange(n_towns)}"
        s = rng.randint(lo, hi)
        parties.append([town, s, s + rng.randint(1, max_len)])
    return regions, parties


def tests():
    rng = random.Random(5)
    t = [
        fn("Example", "party_hours", EX_REGIONS,
           [["t1", 90, 180], ["t1", 60, 120], ["t1", 180, 210], ["t3", -30, 30], ["t3", 1400, 1500]], float=True),
        fn("No parties at all", "party_hours", EX_REGIONS, [], float=True),
        fn("Touching intervals count once", "party_hours", R(("a", "c", "s")), [["a", 0, 60], ["a", 60, 90], ["a", 90, 91]], float=True),
        fn("Nested + duplicate intervals", "party_hours", R(("a", "c", "s")), [["a", 100, 400], ["a", 150, 200], ["a", 100, 400]], float=True),
        fn("Entirely outside the day", "party_hours", R(("a", "c", "s"), ("b", "c", "s")),
           [["a", -100, 0], ["a", 1440, 2000], ["b", -5000, 5000]], float=True),
        fn("Rounding (20 min, 1 min)", "party_hours", R(("a", "c", "s"), ("b", "c", "s")), [["a", 10, 30], ["b", 5, 6]], float=True),
        fn("Follow-up example", "idle_segments", EX_REGIONS, [["t1", 60, 180], ["t2", 300, 360], ["t3", -10, 700]], 0, 600,
           tag="Follow-up"),
        fn("Clamping + touching gaps", "idle_segments", EX_REGIONS,
           [["t1", -30, 30], ["t1", 90, 150], ["t3", 50, 60], ["t3", 60, 80]], 0, 120, tag="Follow-up"),
        fn("Non-zero window start", "idle_segments", R(("a", "x", "s"), ("b", "y", "s")), [["a", 100, 200], ["a", 400, 600]], 300, 500,
           tag="Follow-up"),
        fn("Towns grouped in regions order", "idle_segments", R(("a", "z", "s"), ("b", "y", "s"), ("c", "z", "s")),
           [["c", 0, 5], ["a", 5, 10]], 0, 10, tag="Follow-up"),
    ]
    for s in range(3):
        reg, par = random_case(rng, 6, 15)
        t.append(fn(f"Random hours #{s + 1}", "party_hours", reg, par, float=True, hidden=True))
    for s in range(3):
        reg, par = random_case(rng, 6, 15)
        t.append(fn(f"Random idle #{s + 1}", "idle_segments", reg, par, -30, 1470, tag="Follow-up", hidden=True))
    reg, par = random_case(rng, 50000, 150000)
    t.append(fn("50k towns, 150k parties", "party_hours", reg, par, float=True, hidden=True))
    reg, par = random_case(rng, 50000, 150000)
    t.append(fn("50k towns, 150k parties (idle)", "idle_segments", reg, par, 0, 1440, tag="Follow-up", hidden=True))
    return t


def scale(n):
    reg, par = random_case(random.Random(n), max(1, n // 3), n)
    return fn(f"P={n}", "party_hours", reg, par, float=True)


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000, 128000], "label": "P = number of parties (T = P/3 towns)"}
