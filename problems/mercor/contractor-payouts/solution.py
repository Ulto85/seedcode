"""Contractor Payouts.

Aggregate minutes per (contractor, week) in a dict, then price each week once.
Both functions run in O(T + R + C) time and O(T + C) space for T timesheet rows,
R referrals and C contractors."""

WEEKLY_REGULAR_MINUTES = 40 * 60
REFERRAL_PERCENT = 20


def _weekly_pay(rates, timesheets):
    minutes = {}
    for cid, week, mins in timesheets:
        if cid in rates:
            minutes[(cid, week)] = minutes.get((cid, week), 0) + mins
    pay = {}
    for (cid, week), m in minutes.items():
        m = max(0, m)
        regular = min(m, WEEKLY_REGULAR_MINUTES)
        overtime = m - regular
        pay[(cid, week)] = rates[cid] * (2 * regular + 3 * overtime) // 120
    return pay


def weekly_earnings(rates, timesheets):
    total = {cid: 0 for cid in rates}
    for (cid, _), p in _weekly_pay(rates, timesheets).items():
        total[cid] += p
    return total


def payouts_with_referrals(rates, timesheets, referrals, cap_cents):
    pay = _weekly_pay(rates, timesheets)
    total = {cid: 0 for cid in rates}
    by_contractor = {cid: [] for cid in rates}
    for (cid, week), p in pay.items():
        total[cid] += p
        by_contractor[cid].append((week, p))

    referred = set()
    for referrer, referee, start in referrals:
        if referrer not in rates or referee not in rates or referrer == referee or referee in referred:
            continue
        referred.add(referee)
        bonus = sum(p * REFERRAL_PERCENT // 100 for week, p in by_contractor[referee] if week >= start)
        total[referrer] += min(bonus, max(0, cap_cents))
    return total
