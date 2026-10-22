---
title: In-Memory Banking System (4 Levels)
difficulty: Hard
source: Anthropic CodeSignal OA, progressive "bank system" (widely reported, 2025-2026)
order: 2
minutes: 90
tags: design, simulation, hash map, binary search
---
Build an in-memory bank in levels, the way Anthropic's 90-minute CodeSignal assessment does: each level adds
features, and code from earlier levels must keep working. Plan for the later levels, but pass Level 1 first.

Every method receives `timestamp` (an int, in ms) as its first argument. **Timestamps strictly increase** across all
calls. All `amount`s are positive ints. Account ids are strings.

```
Bank()
```

### Level 1: accounts, deposits, payments
```
create_account(timestamp, account_id) -> bool      # False if the account already exists
deposit(timestamp, account_id, amount) -> int|None # new balance; None if the account doesn't exist
pay(timestamp, account_id, amount) -> int|None     # withdraw; new balance. None if the account doesn't
                                                   # exist or its balance < amount (no change)
```

### Level 2: most active accounts
An account's **activity** is the total amount of money that moved through it in *successful* operations: every
deposit, every payment, and (Level 3) every *accepted* transfer, on both sides. Failed calls add nothing.
```
top_activity(timestamp, k) -> list[str]
```
Return up to `k` strings `"<account_id>(<activity>)"`, highest activity first, **ties broken by account id
ascending**. Accounts with 0 activity are included. If fewer than `k` accounts exist, return them all.

### Level 3: transfers that must be accepted
```
transfer(timestamp, source_id, target_id, amount) -> str|None
accept_transfer(timestamp, account_id, transfer_id) -> bool
```
- `transfer` fails (`None`, no change) if source == target, either account doesn't exist, or the source balance is
  `< amount`. Otherwise the amount is **withdrawn from the source immediately** and the call returns a new id:
  `"transfer1"`, `"transfer2"`, … (the counter only advances on success).
- `accept_transfer` succeeds only if the transfer exists, is still pending, `account_id` is its target and
  `timestamp < created_at + 1000`. On success the target is credited and **both** accounts gain `amount` activity.
  A transfer can be accepted only once.
- A pending transfer **expires at exactly `created_at + 1000`**: at that moment it is refunded to the source (no
  activity). Expirations at time `t` happen **before** the operation at time `t` runs.

*(The real assessment used a 24-hour window; it's shortened to 1000 ms here so tests stay readable.)*

### Level 4: merging accounts and balance history
```
merge_accounts(timestamp, account_id_1, account_id_2) -> bool
get_balance(timestamp, account_id, time_at) -> int|None
```
- `merge_accounts` merges account 2 **into** account 1. It fails (`False`) if the ids are equal or either account
  doesn't exist. On success: account 1 gets account 2's balance and activity, and account 2 stops existing.
  Pending transfers that involve account 2 now involve account 1 instead (refunds and acceptance go to account 1);
  a pending transfer **between** the two accounts is cancelled and refunded right away.
- After a merge, `create_account` with the old id 2 succeeds and creates a **brand-new** account (balance 0,
  activity 0).
- `get_balance` returns the balance `account_id` had at time `time_at` (`time_at <= timestamp`), i.e. after
  everything that happened at or before `time_at`. Return `None` if that account did not exist at `time_at`
  (not created yet, or already merged away: an account merged at time `m` does not exist at `m`).
  Account 1's history before the merge is unchanged by the merge.

### Example
```
create_account(1, "a") -> True       create_account(2, "b") -> True
deposit(3, "a", 500)   -> 500        pay(4, "a", 200)       -> 300
transfer(5, "a", "b", 100) -> "transfer1"            # a: 200
top_activity(6, 2)     -> ["a(700)", "b(0)"]         # transfer not accepted yet
accept_transfer(7, "b", "transfer1") -> True         # b: 100
top_activity(8, 2)     -> ["a(800)", "b(100)"]
merge_accounts(9, "a", "b") -> True                  # a: 300, b is gone
get_balance(10, "b", 8) -> 100      get_balance(11, "b", 9) -> None
get_balance(12, "a", 8) -> 200      get_balance(13, "a", 9) -> 300
```

### Constraints
- Up to 10⁵ operations; `top_activity` is called at most a few thousand times.

*Level contents are reconstructed from multiple candidate reports (accounts/pay/deposit → top activity → transfer +
accept → merge + historical balance). The exact wording, expiry window and edge-case rules here are this site's own
fully specified version.*
