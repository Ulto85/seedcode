import random
from engine.spec import fn

F1 = "should_send_notifications"
F2 = "should_send_with_limits"


def org(n_users, n_teams, n_companies, rng):
    teams = [f"t{i}" for i in range(n_teams)]
    u2t = {f"u{i}": rng.choice(teams) for i in range(n_users)}
    t2c = {t: f"c{rng.randrange(n_companies)}" for t in teams}
    return u2t, t2c


def rand_attempts(rng, users, n, max_gap):
    ts, out = 0, []
    for _ in range(n):
        ts += rng.choice([0, 0, rng.randint(0, max_gap)])
        out.append([rng.choice(users), ts])
    return out


ONE = ({"u1": "t1"}, {"t1": "acme"})
FIVE = ({f"u{i}": "t1" for i in range(1, 6)}, {"t1": "acme"})


def tests():
    rng = random.Random(21)
    ex2 = [[f"u{i % 5 + 1}", i + 1] for i in range(10)] + [["u1", 11], ["u2", 601]]
    three_teams = ({f"u{i}": f"t{i % 3}" for i in range(9)}, {"t0": "acme", "t1": "acme", "t2": "acme"})
    t = [
        fn("Example 1: user limit", F1, *ONE, [["u1", 1], ["u1", 2], ["u1", 3], ["u1", 4], ["u1", 601], ["u1", 602]]),
        fn("Example 2: team limit", F1, *FIVE, ex2),
        fn("No attempts", F1, *ONE, []),
        fn("Exactly 600s later has expired, 599s has not", F1, *ONE,
           [["u1", 0], ["u1", 0], ["u1", 0], ["u1", 599], ["u1", 600], ["u1", 600], ["u1", 600], ["u1", 1199]]),
        fn("Denied attempts aren't recorded", F1, *ONE,
           [["u1", 10], ["u1", 20], ["u1", 30], ["u1", 100], ["u1", 200], ["u1", 610], ["u1", 615]]),
        fn("Company limit across teams", F1, *three_teams,
           [[f"u{i % 9}", i] for i in range(24)] + [["u5", 600], ["u0", 610]]),
        fn("Separate companies don't interact", F1, {"a": "t1", "b": "t2"}, {"t1": "c1", "t2": "c2"},
           [["a", 1], ["a", 1], ["a", 1], ["b", 1], ["a", 1], ["b", 1], ["b", 1], ["b", 2]]),
        fn("Different windows per level", F2, *FIVE,
           [["u1", 0], ["u1", 5], ["u2", 6], ["u1", 10], ["u2", 12], ["u3", 40], ["u1", 61], ["u1", 70]],
           {"user": [2, 10], "team": [3, 60]}, tag="Follow-up"),
        fn("Missing level means unlimited", F2, *ONE, [["u1", 1]] * 6, {"company": [5, 100]}, tag="Follow-up"),
        fn("Zero limit blocks everything", F2, *FIVE, [["u1", 1], ["u2", 2]], {"user": [3, 600], "team": [0, 10]}, tag="Follow-up"),
        fn("Default limits through the follow-up API", F2, *FIVE, ex2, {"user": [3, 600], "team": [10, 600], "company": [20, 600]}, tag="Follow-up"),
    ]
    for i in range(3):
        u2t, t2c = org(12, 4, 2, rng)
        t.append(fn(f"Random org #{i + 1}", F1, u2t, t2c, rand_attempts(rng, sorted(u2t), 150, 60), hidden=True))
    for i in range(3):
        u2t, t2c = org(10, 4, 2, rng)
        limits = {lvl: [rng.randint(1, 6), rng.randint(1, 120)] for lvl in ("user", "team", "company") if rng.random() < 0.8}
        t.append(fn(f"Random limits #{i + 1}", F2, u2t, t2c, rand_attempts(rng, sorted(u2t), 150, 30), limits,
                    tag="Follow-up", hidden=True))
    u2t, t2c = org(5000, 500, 50, rng)
    t.append(fn("150,000 attempts", F1, u2t, t2c, rand_attempts(rng, sorted(u2t), 150000, 3), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    u2t, t2c = org(max(10, n // 20), max(3, n // 200), max(2, n // 2000), rng)
    return fn(f"{n} attempts", F1, u2t, t2c, rand_attempts(rng, sorted(u2t), n, 3))


SCALE = {"sizes": [5000, 10000, 20000, 40000, 80000, 160000], "label": "n = number of attempts"}
