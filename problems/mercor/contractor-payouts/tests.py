import random
from engine.spec import fn

RATES = {"ana": 6000, "bo": 4500, "cy": 3000}
TS = [["ana", 1, 1500], ["ana", 1, 1200], ["bo", 1, 90], ["bo", 1, -30], ["ana", 2, 61], ["eve", 1, 600]]


def random_case(rng, n_people, n_rows, n_refs, weeks=6):
    ids = [f"x{i:04d}" for i in range(n_people)]
    rates = {i: rng.randint(1500, 20000) for i in ids if rng.random() < 0.9}
    rows = []
    for _ in range(n_rows):
        mins = rng.randint(1, 900) if rng.random() < 0.9 else -rng.randint(1, 600)
        rows.append([rng.choice(ids), rng.randint(0, weeks), mins])
    refs = [[rng.choice(ids), rng.choice(ids), rng.randint(0, weeks + 1)] for _ in range(n_refs)]
    return rates, rows, refs, rng.choice([0, 500, 5000, 50000, 10**9])


def tests():
    rng = random.Random(4)
    t = [
        fn("Example", "weekly_earnings", RATES, TS),
        fn("No timesheets", "weekly_earnings", {"a": 100, "b": 200}, []),
        fn("Exactly 40 hours, then one more minute", "weekly_earnings", {"a": 6000, "b": 6000},
           [["a", 0, 2400], ["b", 0, 2400], ["b", 0, 1]]),
        fn("Overtime is per week, not overall", "weekly_earnings", {"a": 6000},
           [["a", 0, 2000], ["a", 1, 2000], ["a", 0, 300]]),
        fn("Round once per week", "weekly_earnings", {"a": 100},
           [["a", 3, 1], ["a", 3, 1], ["a", 3, 1]]),
        fn("Negative week clamps to zero", "weekly_earnings", {"a": 6000},
           [["a", 0, 60], ["a", 0, -120], ["a", 1, 60]]),
        fn("Unknown contractors ignored", "weekly_earnings", {}, [["ghost", 0, 600]]),
        fn("Follow-up example", "payouts_with_referrals", RATES, TS,
           [["bo", "ana", 2], ["cy", "ana", 1], ["ana", "ana", 1]], 1000, tag="Follow-up"),
        fn("Follow-up: uncapped", "payouts_with_referrals", RATES, TS, [["cy", "ana", 1]], 10**9, tag="Follow-up"),
        fn("Follow-up: separate cap per referee", "payouts_with_referrals",
           {"r": 1000, "a": 6000, "b": 6000}, [["a", 0, 600], ["b", 0, 600]], [["r", "a", 0], ["r", "b", 0]], 1500, tag="Follow-up"),
        fn("Follow-up: no bonus on bonuses, mutual referrals", "payouts_with_referrals",
           {"a": 6000, "b": 6000, "c": 6000}, [["a", 0, 600], ["b", 0, 60], ["c", 0, 120]],
           [["a", "b", 0], ["b", "a", 0], ["b", "c", 0], ["ghost", "c", 0]], 10**9, tag="Follow-up"),
        fn("Follow-up: start week and zero cap", "payouts_with_referrals",
           {"a": 6000, "b": 3000}, [["b", 0, 600], ["b", 5, 600], ["b", 9, 600]], [["a", "b", 5]], 0, tag="Follow-up"),
        fn("Follow-up: start week counts", "payouts_with_referrals",
           {"a": 6000, "b": 3000}, [["b", 0, 600], ["b", 5, 600], ["b", 9, 600]], [["a", "b", 5]], 10**6, tag="Follow-up"),
    ]
    for s in range(3):
        rates, rows, _, _ = random_case(rng, 8, 60, 0)
        t.append(fn(f"Random #{s + 1}", "weekly_earnings", rates, rows, hidden=True))
    for s in range(3):
        rates, rows, refs, cap = random_case(rng, 8, 60, 10)
        t.append(fn(f"Follow-up random #{s + 1}", "payouts_with_referrals", rates, rows, refs, cap, tag="Follow-up", hidden=True))
    rates, rows, refs, _ = random_case(rng, 20000, 200000, 100000, weeks=52)
    t.append(fn("200k rows", "weekly_earnings", rates, rows, hidden=True))
    t.append(fn("200k rows, 100k referrals", "payouts_with_referrals", rates, rows, refs, 250000, tag="Follow-up", hidden=True))
    return t


def scale(n):
    rates, rows, refs, _ = random_case(random.Random(n), max(1, n // 10), n, n // 2, weeks=52)
    return fn(f"n={n}", "payouts_with_referrals", rates, rows, refs, 250000, tag="Follow-up")


SCALE = {"sizes": [6250, 12500, 25000, 50000, 100000, 200000], "label": "n = timesheet rows (n/2 referrals)"}
