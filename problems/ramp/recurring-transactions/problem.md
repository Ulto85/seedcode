---
title: Recurring Transactions
difficulty: Hard
source: Ramp SWE technical phone screen, "identify recurring transactions" (reported 2025)
order: 3
minutes: 50
timeout: 20
tags: hash map, dates, dynamic programming, sorting
---
Ramp wants to flag subscriptions automatically: given a card ledger, find the charges that **recur on a schedule**.

```
find_recurring(transactions: list[list]) -> list[list]
# each transaction: [date, merchant, amount, currency]
#   date: "YYYY-MM-DD",  amount: positive int in minor units (cents),  currency: "USD", "EUR", ...
```
The ledger is in **no particular order**.

### Rules
1. **Group** transactions by `(merchant, amount, currency)`; all three must match exactly. Within a group, only the set
   of distinct dates matters (two charges on the same day count once).
2. A **streak** is a sequence of dates from the group, each one step after the previous one:
   - `DAILY`: exactly 1 day later.
   - `WEEKLY`: exactly 7 days later.
   - `MONTHLY`: in the **next calendar month**, and either on the **same day of month**, or both dates are the **last
     day of their months**. (Jan 31 → Feb 28 ✓, Jan 30 → Feb 28 ✗, Feb 28 → Mar 28 ✓, and in a non-leap year
     Feb 28 → Mar 31 ✓ as well.)
   Dates of the group that aren't in the streak are simply ignored (a one-off charge on another day doesn't break it).
3. For each group and frequency, find its **longest** streak. A group is **recurring** if some frequency has a streak of
   **at least 3** dates. It is reported **once**, with the frequency whose longest streak is longest
   (**ties → DAILY, then WEEKLY, then MONTHLY**).

Return `[merchant, amount, currency, frequency]` for every recurring group, **sorted by merchant, then amount, then
currency**. An empty ledger (or no recurring group) returns `[]`.

### Example
```
transactions = [
  ["2026-01-15", "Netflix", 1599, "USD"], ["2026-02-15", "Netflix", 1599, "USD"],
  ["2026-03-15", "Netflix", 1599, "USD"], ["2026-02-20", "Netflix", 1599, "USD"],   # extra date: ignored
  ["2026-01-05", "Uber", 2300, "USD"],    ["2026-01-12", "Uber", 2300, "USD"],
  ["2026-01-19", "Uber", 2300, "USD"],    ["2026-01-19", "Uber", 1250, "USD"],      # different amount: own group
  ["2026-01-31", "AWS", 9900, "USD"],     ["2026-02-28", "AWS", 9900, "USD"],
  ["2026-03-31", "AWS", 9900, "USD"],     ["2026-04-15", "Spotify", 999, "EUR"],
]
-> [["AWS", 9900, "USD", "MONTHLY"], ["Netflix", 1599, "USD", "MONTHLY"], ["Uber", 2300, "USD", "WEEKLY"]]
```

### What the interviewer cares about
- Explaining the definition of "recurring" and its trade-offs (the open-ended version asks you to choose tolerances
  yourself; here they're fixed so answers are checkable).
- Date arithmetic done right (month lengths, leap years). Use your language's date library.
- Complexity: a group can have tens of thousands of dates. Comparing every pair of dates is too slow; for each date
  you can look up its one predecessor directly (`date - 1`, `date - 7`, or the 1–2 possible previous-month dates).

### Constraints
- 0 ≤ len(transactions) ≤ 10⁵; dates between 2000-01-01 and 2099-12-31.
- Merchant names are non-empty strings and are compared exactly (case-sensitive).

*The phone-screen version leaves "recurring" for you to define. These exact rules (exact amounts, no date jitter,
month-end rule, ≥ 3 occurrences, tie order) are a fully specified reconstruction.*
