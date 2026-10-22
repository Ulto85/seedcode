import random
from engine.spec import fn


def rand_prefs(rng, n, m, skew=False):
    if skew:      # bunch preferences toward the front so overflow chains get long
        return [min(n - 1, int(rng.random() ** 3 * n)) for _ in range(m)]
    return [rng.randrange(n) for _ in range(m)]


def rand_events(rng, n, q, leave_p=0.35):
    ev, arrivals = [], 0
    for _ in range(q):
        if arrivals and rng.random() < leave_p:
            ev.append(["leave", rng.randint(0, arrivals + 1)])     # occasionally out of range
        else:
            ev.append(["arrive", min(n - 1, int(rng.random() ** 2 * n))])
            arrivals += 1
    return ev


def tests():
    rng = random.Random(11)
    t = [
        fn("Example: everyone parks", "can_all_park", 3, [0, 0, 1]),
        fn("Example: free spot behind is useless", "can_all_park", 3, [1, 1, 2]),
        fn("Example: out of order", "can_all_park", 4, [2, 0]),
        fn("No cars", "can_all_park", 5, []),
        fn("More cars than spots", "can_all_park", 2, [0, 0, 0]),
        fn("All want the last spot", "can_all_park", 4, [3, 3]),
        fn("Full street, every spot used", "can_all_park", 5, [4, 0, 0, 2, 1]),
        fn("Part 2 example", "parking_spots", 3, [1, 1, 1, 0], tag="Part 2"),
        fn("Part 2: no cars", "parking_spots", 3, [], tag="Part 2"),
        fn("Part 2: failed car takes no spot", "parking_spots", 3, [2, 2, 2, 1, 0, 0, 0], tag="Part 2"),
        fn("Part 2: overflow chains merge", "parking_spots", 8, [3, 0, 1, 0, 3, 2, 0, 7, 7], tag="Part 2"),
        fn("Follow-up example", "parking_log", 3, [["arrive", 2], ["arrive", 2], ["leave", 0], ["arrive", 1]], tag="Follow-up"),
        fn("Follow-up: freed spot is reused", "parking_log", 3,
           [["arrive", 0], ["arrive", 0], ["arrive", 0], ["leave", 1], ["arrive", 0], ["arrive", 0]], tag="Follow-up"),
        fn("Follow-up: bad leaves are ignored", "parking_log", 2,
           [["leave", 0], ["arrive", 1], ["arrive", 1], ["leave", 1], ["leave", 0], ["leave", 0], ["leave", 9], ["arrive", 1], ["arrive", 1]],
           tag="Follow-up"),
    ]
    for s in range(4):
        n = rng.randint(1, 12)
        t.append(fn(f"Random small #{s + 1}", "can_all_park", n, rand_prefs(rng, n, rng.randint(0, n + 1), skew=s % 2 == 0), hidden=True))
    for s in range(3):
        n = rng.randint(5, 40)
        t.append(fn(f"Part 2 random #{s + 1}", "parking_spots", n, rand_prefs(rng, n, rng.randint(n // 2, n + 5), skew=True), tag="Part 2", hidden=True))
    for s in range(3):
        n = rng.randint(3, 30)
        t.append(fn(f"Follow-up random #{s + 1}", "parking_log", n, rand_events(rng, n, 80), tag="Follow-up", hidden=True))
    t.append(fn("100k cars, exact fit", "can_all_park", 100000, sorted(rand_prefs(rng, 100000, 100000, skew=True)), hidden=True))
    t.append(fn("100k cars all prefer spot 0", "parking_spots", 100000, [0] * 100000, tag="Part 2", hidden=True))
    t.append(fn("Part 2: 100k skewed cars", "parking_spots", 100000, rand_prefs(rng, 100000, 100000, skew=True), tag="Part 2", hidden=True))
    big = [["arrive", 0] for _ in range(50000)] + [["leave", k] for k in range(0, 50000, 2)] + [["arrive", 0] for _ in range(40000)]
    t.append(fn("Follow-up: 140k events, front-loaded", "parking_log", 50000, big, tag="Follow-up", hidden=True))
    return t


def scale(n):
    return fn(f"n={n}", "parking_spots", n, [0] * (n // 2) + rand_prefs(random.Random(n), n, n // 2, skew=True))


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = spots = cars"}
