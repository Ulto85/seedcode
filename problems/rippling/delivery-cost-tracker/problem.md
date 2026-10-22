---
title: Delivery Cost Tracker
difficulty: Medium
source: Rippling SWE phone screen / technical screen, "Delivery Dashboard" (most reported, 2025-2026)
order: 1
minutes: 60
timeout: 20
tags: design, money, heap, intervals, sweep line
---
A food-delivery company pays its drivers **by the hour**. Build the backend for its cost dashboard: register drivers
with an hourly rate, record deliveries, and report what the company owes.

- Times are integer **seconds** (e.g. Unix timestamps).
- Rates are integer **cents per hour**. A delivery from `start` to `end` costs `rate * (end - start) / 3600` cents,
  which is usually *not* a whole number.
- **Money rule:** never round per delivery. Keep the exact total (hint: keep the numerator `Σ rate * seconds` as an
  integer) and round only when reporting: round the exact cent amount to the nearest whole cent, halves round **up**.

### Part 1
```
DeliveryTracker()
add_driver(driver_id: int, rate: int) -> bool
    # False (and the existing rate is kept) if driver_id is already registered
record_delivery(driver_id: int, start: int, end: int) -> bool
    # False (nothing recorded) if the driver is unknown or end < start.
    # end == start is valid: a zero-length delivery that costs 0.
    # The same driver may have overlapping deliveries; each is charged in full.
get_total_cost() -> int
    # cents owed for ALL recorded deliveries (paid or not), rounded as above
```

### Part 2: paying drivers
```
pay_up_to(time: int) -> int
    # Settle every recorded, still-unpaid delivery whose end <= time.
    # Returns how many deliveries were settled by THIS call (0 if none).
    # A delivery that is still in progress at `time` (end > time) is not paid at all.
get_unpaid_cost() -> int
    # cents for recorded deliveries that are not yet paid, rounded as above
```
Paying is idempotent: calling `pay_up_to` again with the same or an earlier time settles nothing new, **unless** new
deliveries ending by then were recorded since; those get settled. `get_total_cost` is unaffected by payments.

### Follow-up: busiest moment of the last 24 hours
```
max_active_drivers(time: int) -> int
```
A driver is **active** at instant `x` if one of their recorded deliveries has `start <= x < end` (end exclusive;
paid or unpaid doesn't matter). Return the maximum number of *distinct* drivers active at the same instant, over all
`x` with `time - 86400 <= x < time`. A driver with two overlapping deliveries counts once. Return `0` if nobody was
active in that window.

### Example
```
t = DeliveryTracker()
t.add_driver(1, 2000)              -> True     # $20.00 / hour
t.add_driver(2, 1500)              -> True
t.add_driver(1, 9999)              -> False    # already registered, rate stays 2000
t.record_delivery(1, 0, 5400)      -> True     # 1.5 h * 2000 = 3000 cents
t.record_delivery(2, 3600, 4500)   -> True     # 0.25 h * 1500 = 375 cents
t.record_delivery(3, 0, 10)        -> False    # unknown driver
t.get_total_cost()                 -> 3375
t.record_delivery(2, 0, 100)       -> True     # 41.666... cents
t.get_total_cost()                 -> 3417     # exact 3416.666... -> 3417
t.pay_up_to(5000)                  -> 2        # both driver-2 deliveries; the one ending at 5400 is still running
t.get_unpaid_cost()                -> 3000
t.pay_up_to(5000)                  -> 0
t.max_active_drivers(5000)         -> 2        # drivers 1 and 2 both active at x = 3600
```

### Constraints
- Up to 10⁵ operations. `0 <= start, end, time <= 10⁹`, `1 <= rate <= 10⁶`.
- `get_total_cost`, `get_unpaid_cost` and `pay_up_to` are called often: don't rescan every delivery on each call.
  `max_active_drivers` is called rarely; `O(n log n)` per call is fine.

### What the interviewer cares about
- **Money handling.** Floats drift (`0.1 + 0.2 != 0.3`). Integer cents + an exact numerator, rounded once, is the answer
  they're looking for. Expect to be asked *why*.
- Clean class design that survives each new requirement without a rewrite; validation of bad input.
- Explaining the complexity of each method, and how you'd make `pay_up_to` cheap (keep unpaid deliveries ordered by end time).
