---
title: GPU Credit Ledger
difficulty: Medium
source: OpenAI SWE phone screen + onsite, "GPU credits" (most reported, 2025–2026; exact rules reconstructed)
order: 1
minutes: 45
tags: design, heap, simulation, timestamps
---
OpenAI hands out **GPU credits** to customers. Each grant is usable only for a limited window of time, and
usage is charged against whatever credits are live at that moment. Build the ledger.

```
GPUCredits()
add_credit(amount, timestamp, expiration) -> None
subtract(amount, timestamp) -> None
get_balance(timestamp) -> int | None
```

- `add_credit(amount, timestamp, expiration)` grants `amount` credits that are usable at every time `t` with
  `timestamp <= t < timestamp + expiration`. At time `timestamp + expiration` the grant has **expired**, and
  whatever is left of it is lost.
- `subtract(amount, timestamp)` spends `amount` credits at time `timestamp`. It always draws from the live grant
  that **expires soonest** first, then the next soonest, and so on. (Which of two grants with the same expiry time
  is used first doesn't change any answer, since they expire together.)
- `get_balance(timestamp)` returns the total credits still left in grants that are live at `timestamp`, counting
  every grant and every subtraction whose timestamp is `<= timestamp`.
- **Overdraft:** if a subtraction at time `s` needs more credits than are live at `s`, the ledger is broken from
  then on: `get_balance(t)` returns `None` for every `t >= s`. (Queries at `t < s` are unaffected.)

**Same timestamp rule.** All events at time `t` are applied in this order: first grants whose window ends at `t`
expire, then grants made at `t` become live, then subtractions at `t` are charged. So a grant can be spent at the
very moment it's granted, but not at the moment it expires.

### Example
```
add_credit(10, 0, 30)     # A: 10 credits, live during [0, 30)
add_credit(5, 10, 10)     # B: 5 credits,  live during [10, 20)
subtract(7, 15)           # B expires first: take all 5 from B, then 2 from A
get_balance(15)  -> 8     # A has 8 left, B has 0
get_balance(25)  -> 8     # B is gone (it was empty anyway)
get_balance(30)  -> 0     # A expired at exactly t = 30
subtract(1, 40)           # nothing is live at t = 40: overdraft
get_balance(40)  -> None
```
If `subtract(7, 15)` had drawn from A first instead, B's 5 credits would have expired unused and the balance at
`t = 25` would be wrong. Ordering by expiry matters.

### Part 1
Calls arrive in **time order**: each call's `timestamp` is `>=` the timestamp of every earlier call (of any kind),
and at any one timestamp all `add_credit` calls come before any `subtract` calls.
`get_balance` will be called a lot, so it shouldn't replay the whole history each time.

### Follow-up: out-of-order events
Events now arrive in **any order**, like log lines from different machines. A late `add_credit` or `subtract` with
an old timestamp must change the history: `get_balance(t)` always reflects *all* calls made so far whose timestamp
is `<= t`, applied in timestamp order (with the same-timestamp rule above). Queries can also ask about any time,
past or future.
```
add_credit(5, 0, 100)
subtract(8, 10)
get_balance(20) -> None     # overdraft at t = 10
add_credit(5, 5, 100)       # a late grant arrives with timestamp 5
get_balance(20) -> 2        # history is fixed: 10 live at t = 10, 2 left
get_balance(3)  -> 5
```

### Constraints
- `1 <= amount <= 10^4`, `0 <= timestamp <= 10^9`, `1 <= expiration <= 10^9`
- Up to `10^5` calls in total

### What the interviewer cares about
- Picking the right structure for "soonest-expiring first" (a min-heap keyed on expiry time)
- Getting the boundaries right: expiry is exclusive, and overdraft is sticky
- In the follow-up, explaining what state you can keep between queries and when it must be rebuilt
