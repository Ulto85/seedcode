import calendar
from collections import defaultdict
from datetime import date, timedelta

FREQS = ("DAILY", "WEEKLY", "MONTHLY")


def _month_end(d):
    return d.day == calendar.monthrange(d.year, d.month)[1]


def _prev_month_candidates(d):
    """Dates p in the previous month such that d is a valid MONTHLY step after p."""
    y, m = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
    last = calendar.monthrange(y, m)[1]
    out = []
    if d.day <= last:
        out.append(date(y, m, d.day))           # same day of month
    if _month_end(d) and d.day != last:
        out.append(date(y, m, last))            # both month-ends (different day numbers)
    return out


def _longest(dates, preds):
    """dates sorted ascending; longest chain where each date extends one of its predecessors."""
    best = {}
    for d in dates:
        best[d] = 1 + max((best.get(p, 0) for p in preds(d)), default=0)
    return max(best.values())


def find_recurring(transactions):
    """Group, then DP over each group's sorted distinct dates: each date has O(1) possible predecessors.
    O(n log n) time (sorting), O(n) space."""
    groups = defaultdict(set)
    for ds, merchant, amount, currency in transactions:
        groups[(merchant, amount, currency)].add(date.fromisoformat(ds))
    one, week = timedelta(days=1), timedelta(days=7)
    pred = {
        "DAILY": lambda d: (d - one,),
        "WEEKLY": lambda d: (d - week,),
        "MONTHLY": _prev_month_candidates,
    }
    out = []
    for (merchant, amount, currency), ds in groups.items():
        if len(ds) < 3:
            continue
        dates = sorted(ds)
        lengths = [_longest(dates, pred[f]) for f in FREQS]
        best = max(lengths)
        if best >= 3:
            out.append([merchant, amount, currency, FREQS[lengths.index(best)]])
    out.sort(key=lambda r: (r[0], r[1], r[2]))
    return out
