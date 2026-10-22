---
title: Referral Network
difficulty: Medium
source: Mercor MLE onsite, "Implement a Referral Network" (reported on PracHub, 2026). Only the topics are public (DAG modelling, reachability, flow centrality); the exact rules, method names and tie-breaks here are our reconstruction.
order: 2
minutes: 50
tags: design, graphs, trees, union-find
---
Mercor pays people for referring experts to its talent network. Build the data structure that tracks who referred
whom and ranks referrers by their influence.

```
ReferralNetwork()
add_user(user_id: str) -> bool
add_referral(referrer: str, candidate: str) -> bool
get_direct_referrals(user_id: str) -> list[str]
total_referral_count(user_id: str) -> int                 # Part 2
top_referrers_by_reach(k: int) -> list[[str, int]]        # Part 2
flow_centrality(user_id: str) -> int                      # Follow-up
```

### Part 1: the graph
- `add_user(user_id)` registers a user. Returns `True`, or `False` (and does nothing) if the user already exists.
- `add_referral(referrer, candidate)` records that `referrer` referred `candidate`. It returns `True` on success.
  It returns `False` and changes nothing if **any** of these hold:
  1. either user hasn't been added;
  2. `referrer == candidate` (no self-referrals);
  3. `candidate` already has a referrer (each candidate is referred at most once; the first referral wins);
  4. the referral would create a cycle, i.e. `candidate` is already a direct or indirect referrer of `referrer`.
- `get_direct_referrals(user_id)` returns the users `user_id` referred directly, sorted ascending (plain string
  order). Unknown user: `[]`.

### Part 2: reach
- The **reach** of a user is the number of users downstream of them: everyone they referred, everyone those
  people referred, and so on. The user themself is not counted.
- `total_referral_count(user_id)` returns that user's reach. Unknown user: `0`.
- `top_referrers_by_reach(k)` returns up to `k` pairs `[user_id, reach]`, highest reach first, ties broken by
  `user_id` ascending. Users with reach `0` are never listed. `k <= 0` returns `[]`; if fewer than `k` users have
  reach above 0, return all of them.

### Follow-up: flow centrality
Reach rewards the top of a chain, but a user in the middle of a long chain is the one the network actually *flows
through*. Define the flow centrality of `u` as the number of ordered pairs `(a, b)` with `a != u` and `b != u`
such that `a` is an upstream (direct or indirect) referrer of `u` and `b` is downstream of `u`. Equivalently,
referral paths from `a` to `b` that pass through `u` as an intermediate. Unknown user: `0`.

### Example
```
for u in ["A", "B", "C", "D", "E"]: add_user(u)    # all True
add_referral("A", "B")      -> True
add_referral("A", "C")      -> True
add_referral("B", "D")      -> True
add_referral("D", "A")      -> False   # A is upstream of D: cycle
add_referral("E", "B")      -> False   # B was already referred by A
add_referral("C", "C")      -> False   # self-referral
get_direct_referrals("A")   -> ["B", "C"]
total_referral_count("A")   -> 3       # B, C, D
total_referral_count("B")   -> 1       # D
top_referrers_by_reach(5)   -> [["A", 3], ["B", 1]]
flow_centrality("B")        -> 1       # only A -> B -> D
flow_centrality("A")        -> 0       # nobody is upstream of A
```

### Constraints
- Up to `10^5` calls; user ids are short non-empty strings.
- Referral chains can be very long (tens of thousands of users), so a cycle check that walks a whole chain on every
  `add_referral` is too slow. Queries may come in bulk after the network is built.

### What the interviewer cares about
- Recognising that the rules make the graph a forest, and using that to make the cycle check cheap
- Clean rejection rules with no partial state changes
- Choosing when to compute reach (eagerly per referral vs lazily per query) and explaining the trade-off
