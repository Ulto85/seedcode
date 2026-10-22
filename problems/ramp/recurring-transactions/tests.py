import calendar
import random
from datetime import date, timedelta
from engine.spec import fn

F = "find_recurring"
EX = [
    ["2026-01-15", "Netflix", 1599, "USD"], ["2026-02-15", "Netflix", 1599, "USD"],
    ["2026-03-15", "Netflix", 1599, "USD"], ["2026-02-20", "Netflix", 1599, "USD"],
    ["2026-01-05", "Uber", 2300, "USD"], ["2026-01-12", "Uber", 2300, "USD"],
    ["2026-01-19", "Uber", 2300, "USD"], ["2026-01-19", "Uber", 1250, "USD"],
    ["2026-01-31", "AWS", 9900, "USD"], ["2026-02-28", "AWS", 9900, "USD"],
    ["2026-03-31", "AWS", 9900, "USD"], ["2026-04-15", "Spotify", 999, "EUR"],
]
MERCHANTS = ["Netflix", "Spotify", "AWS", "Uber", "Lyft", "Figma", "Slack", "Zoom", "GitHub", "Notion", "Delta", "WeWork"]


def T(d, m, a, c="USD"):
    return [d, m, a, c]


def add_months(d, k):
    m0 = d.month - 1 + k
    y, m = d.year + m0 // 12, m0 % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def rand_ledger(rng, n, n_merchants=12, span_days=1500, base=date(2022, 1, 1)):
    """Mix of real subscriptions (daily/weekly/monthly runs, sometimes with gaps) and random noise."""
    out = []
    merchants = MERCHANTS[:n_merchants] + [f"Vendor{i}" for i in range(max(0, n_merchants - len(MERCHANTS)))]
    while len(out) < n:
        m = rng.choice(merchants)
        amt = rng.choice([999, 1599, 2300, 4900, 9900, rng.randint(100, 20000)])
        cur = rng.choice(["USD", "USD", "USD", "EUR"])
        kind = rng.random()
        start = base + timedelta(days=rng.randrange(span_days))
        length = rng.randint(1, 8)
        if kind < 0.25:
            ds = [start + timedelta(days=i) for i in range(length)]
        elif kind < 0.5:
            ds = [start + timedelta(days=7 * i) for i in range(length)]
        elif kind < 0.75:
            if rng.random() < 0.3:      # month-end subscriptions
                start = date(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
            ds = [add_months(start, i) for i in range(length)]
        else:
            ds = [base + timedelta(days=rng.randrange(span_days)) for _ in range(length)]
        if len(ds) > 3 and rng.random() < 0.3:
            del ds[rng.randrange(1, len(ds) - 1)]   # a missed payment splits the streak
        out += [T(d.isoformat(), m, amt, cur) for d in ds]
    out = out[:n]
    rng.shuffle(out)
    return out


def dense_group(rng, n):
    """One merchant charging the same amount on ~n random distinct days: punishes pairwise comparisons."""
    base = date(2000, 1, 1)
    days = rng.sample(range(36000), n)
    return [T((base + timedelta(days=d)).isoformat(), "Utility", 4200, "USD") for d in days]


def tests():
    rng = random.Random(3)
    t = [
        fn("Example", F, EX),
        fn("Empty ledger", F, []),
        fn("Only two charges: not recurring", F, [T("2026-01-01", "Zoom", 1500), T("2026-02-01", "Zoom", 1500)]),
        fn("Daily", F, [T("2026-03-01", "Coffee", 450), T("2026-03-03", "Coffee", 450), T("2026-03-02", "Coffee", 450)]),
        fn("Amount or currency mismatch splits groups", F, [T("2026-01-01", "Slack", 800), T("2026-02-01", "Slack", 800), T("2026-03-01", "Slack", 801), T("2026-04-01", "Slack", 800, "EUR")]),
        fn("Same-day duplicates count once", F, [T("2026-05-01", "Gym", 3000), T("2026-05-01", "Gym", 3000), T("2026-05-08", "Gym", 3000)]),
        fn("Month-end rule incl. leap year", F, [T("2024-01-31", "Rent", 200000), T("2024-02-29", "Rent", 200000), T("2024-03-31", "Rent", 200000), T("2024-04-30", "Rent", 200000)]),
        fn("Jan 30 -> Feb 28 is not monthly", F, [T("2026-01-30", "Rent", 100000), T("2026-02-28", "Rent", 100000), T("2026-03-30", "Rent", 100000)]),
        fn("Feb 28 -> Mar 28 and Feb 28 -> Mar 31", F, [T("2025-01-28", "A", 100), T("2025-02-28", "A", 100), T("2025-03-28", "A", 100), T("2025-01-31", "B", 100), T("2025-02-28", "B", 100), T("2025-03-31", "B", 100)]),
        fn("Monthly across a year boundary", F, [T("2025-11-10", "Figma", 1500), T("2025-12-10", "Figma", 1500), T("2026-01-10", "Figma", 1500)]),
        fn("Gap breaks the streak", F, [T("2026-01-01", "Lyft", 900), T("2026-01-08", "Lyft", 900), T("2026-01-22", "Lyft", 900), T("2026-01-29", "Lyft", 900)]),
        fn("Tie between frequencies -> DAILY first", F,
           [T("2026-01-01", "X", 100), T("2026-01-02", "X", 100), T("2026-01-03", "X", 100),
            T("2026-02-01", "X", 100), T("2026-03-01", "X", 100), T("2026-01-08", "X", 100), T("2026-01-15", "X", 100)]),
        fn("Longest streak wins", F,
           [T("2026-01-05", "Y", 100), T("2026-01-12", "Y", 100), T("2026-01-19", "Y", 100), T("2026-01-26", "Y", 100),
            T("2026-02-05", "Y", 100), T("2026-03-05", "Y", 100), T("2026-04-05", "Y", 100), T("2026-05-05", "Y", 100), T("2026-06-05", "Y", 100)]),
        fn("Sort by merchant, amount, currency", F,
           [T(f"2026-0{m}-01", name, amt, cur) for m in (1, 2, 3) for name, amt, cur in [("b", 5, "USD"), ("a", 20, "USD"), ("a", 3, "USD"), ("a", 3, "EUR")]]),
    ]
    for s in range(4):
        t.append(fn(f"Random ledger #{s + 1}", F, rand_ledger(rng, rng.randint(20, 80), n_merchants=4), hidden=True))
    t.append(fn("100k transactions", F, rand_ledger(rng, 100000, n_merchants=300), hidden=True))
    t.append(fn("One merchant, 30k distinct days", F, dense_group(rng, 30000), hidden=True))
    return t


def scale(n):
    rng = random.Random(n)
    return fn(f"n={n}", F, dense_group(rng, n // 2) + rand_ledger(rng, n - n // 2, n_merchants=50))


SCALE = {"sizes": [2000, 4000, 8000, 16000, 32000, 64000], "label": "n = transactions"}
