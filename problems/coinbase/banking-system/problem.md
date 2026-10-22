---
title: In-Memory Banking System
difficulty: Medium
source: Coinbase SWE online assessment / coding round, progressive "levels" banking system (reported 2025-2026)
order: 3
minutes: 60
tags: design, hash map, heap, sorting, simulation
---
Build a small in-memory bank. The question comes in levels: each part builds on the code you already wrote,
so design for change. Amounts are integers (think cents).

### Part 1: accounts and transfers
```
Bank()
create_account(account_id: str) -> bool        # False if the id already exists
deposit(account_id: str, amount: int) -> int | None
transfer(from_id: str, to_id: str, amount: int) -> int | None
get_balance(account_id: str) -> int | None
```
- `deposit` returns the account's **new balance**.
- `transfer` moves money and returns the **sender's** new balance.
- Return `None` (and change **nothing**) for: an unknown account, `amount ≤ 0`, a transfer to the same
  account, or a transfer larger than the sender's balance. Validate *before* mutating anything.
- `get_balance` returns `None` for an unknown account. New accounts start at `0`.

### Part 2: top spenders
```
top_spenders(k: int) -> list[list]     # [[account_id, total_spent], ...]
```
An account's **spending** is the sum of its successful **outgoing** transfers (including executed scheduled
payments from the follow-up). Deposits, incoming money and failed transfers don't count.
- Sort by spending **descending**, ties by `account_id` **ascending** (plain string order).
- Accounts that never spent anything are included with `0`.
- Return the first `k`. If `k` exceeds the number of accounts return them all. `k ≤ 0` gives `[]`.

### Follow-up: scheduled payments
The bank now has a clock that starts at `0` and only moves when you call `process_until`.
```
schedule_payment(from_id, to_id, amount, at) -> str | None
cancel_payment(payment_id) -> bool
process_until(t) -> list[list[str]] | None
```
- `schedule_payment` returns ids `"p1"`, `"p2"`, … (the counter only advances on success). It returns `None` if
  either account is unknown, `from_id == to_id`, `amount ≤ 0`, or `at` isn't **strictly after** the current clock.
  Funds are **not** checked when scheduling.
- `cancel_payment` returns `True` only if the payment exists and is still pending. Otherwise `False`.
- `process_until(t)`: returns `None` if `t` is before the current clock (`t` equal to the clock is fine).
  Otherwise it runs every pending payment with `at ≤ t`, ordered by `at` then by scheduling order. Each one is
  either `"executed"` (works exactly like `transfer`) or `"failed"` (sender can't cover it at that moment;
  never retried). Then the clock becomes `t`. It returns `[[payment_id, "executed" | "failed"], ...]` in
  processing order, or `[]` if nothing was due. Cancelled payments don't appear.

### Example
```
create_account("alice") -> True     deposit("alice", 100) -> 100
create_account("bob")   -> True     transfer("alice", "bob", 30) -> 70
transfer("bob", "alice", 50) -> None            # bob only has 30
top_spenders(5) -> [["alice", 30], ["bob", 0]]
schedule_payment("bob", "alice", 20, 10) -> "p1"
schedule_payment("alice", "bob", 500, 5) -> "p2"
schedule_payment("alice", "bob", 1, 0)   -> None  # at must be > clock (0)
process_until(10) -> [["p2", "failed"], ["p1", "executed"]]
get_balance("bob") -> 10
top_spenders(1) -> [["alice", 30]]                # bob has spent 20 (via p1)
```

### Constraints
- Up to 10⁵ operations, up to 10⁴ accounts. `process_until` should not re-scan payments that aren't due
  (keep pending payments in a heap).

*Reconstructed in our own words from reports of Coinbase's levelled banking question. Some versions add
account merges or balance history as a 4th level.*
