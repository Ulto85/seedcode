---
title: Contractor Payouts with Referral Bonuses
difficulty: Easy
source: In the style of Mercor's reported practical data-processing coding (process an input dataset end to end, then extend it). Not a reported question. The referral rule mirrors Mercor's public referral terms (the referrer earns 20% of what their referral earns, up to a cap).
order: 4
minutes: 35
tags: hashing, aggregation, money, data processing
---
Experts on a talent marketplace bill hours against client projects and get paid weekly. Compute what everyone is
owed. All money is in **integer cents**.

### Part 1
```
weekly_earnings(rates: dict[str, int], timesheets: list[[str, int, int]]) -> dict[str, int]
```
- `rates[contractor_id]` is that contractor's hourly rate in cents (`> 0`).
- Each timesheet row is `[contractor_id, week, minutes]`. A contractor can have many rows in the same week (one per
  project or session). `minutes` may be **negative**: that's a correction to an earlier row.
- Rows for contractors not in `rates` are ignored.

For each contractor and week:
1. Add up that week's minutes. If the sum is negative, treat it as `0`.
2. The first `2400` minutes (40 hours) are regular time. Anything above that is overtime, paid at **1.5x**.
3. The week's pay is `floor(rate * (2 * regular + 3 * overtime) / 120)` cents. Round **once per week**, not per row.

Return a dict containing **every** contractor in `rates` (those with no hours get `0`), mapped to the sum of their
weekly pay.

### Follow-up: referral bonuses
```
payouts_with_referrals(rates, timesheets, referrals: list[[str, str, int]], cap_cents: int) -> dict[str, int]
```
Each referral is `[referrer, referee, start_week]`. Process them in list order. A referral is **ignored** if either
person is not in `rates`, if `referrer == referee`, or if the referee already has an accepted referral (the first
one wins).

For each accepted referral, the referrer earns 20% of the referee's pay for every week `>= start_week`:
`floor(week_pay * 20 / 100)` per week (week pay as in Part 1). The referrer's total bonus from **that referee** is
capped at `cap_cents`. Bonuses are based on the referee's own Part 1 pay only, never on bonuses the referee earned.
A referrer can collect from several referees, with a separate cap for each.

Return every contractor in `rates` mapped to Part 1 pay plus referral bonuses.

### Example
```
rates = {"ana": 6000, "bo": 4500, "cy": 3000}          # $60/h, $45/h, $30/h
timesheets = [["ana", 1, 1500], ["ana", 1, 1200], ["bo", 1, 90], ["bo", 1, -30],
              ["ana", 2, 61], ["eve", 1, 600]]

weekly_earnings(rates, timesheets) -> {"ana": 291100, "bo": 4500, "cy": 0}
```
- ana, week 1: 2700 minutes = 2400 regular + 300 overtime, so `6000 * (4800 + 900) // 120 = 285000`.
- ana, week 2: 61 minutes, so `6000 * 122 // 120 = 6100` (rounded once for the whole week).
- bo, week 1: `90 - 30 = 60` minutes, so `4500`. eve isn't in `rates`; cy has no hours.

```
payouts_with_referrals(rates, timesheets,
                       [["bo", "ana", 2], ["cy", "ana", 1], ["ana", "ana", 1]], 1000)
  -> {"ana": 291100, "bo": 5500, "cy": 0}
```
bo referred ana from week 2: 20% of 6100 is 1220, capped at 1000. cy's referral is ignored because ana already has
a referrer, and ana can't refer herself.

### Constraints
- Up to `2 * 10^5` timesheet rows and `10^5` referrals; weeks are integers `>= 0`; `0 <= cap_cents <= 10^9`.

### What the interviewer cares about
- Aggregating before pricing (rounding per week, not per row; overtime from the weekly total)
- Integer money, explicit handling of unknown ids, corrections and duplicates
- Code that is easy to extend when the bonus rule arrives
