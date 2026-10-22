---
title: Hierarchical Notification Rate Limiter
difficulty: Medium
source: Cursor Backend Engineer (new grad) technical screen, "Implement Notification Rate Limiter" (reported 2026). Part 1 follows the reported spec; the configurable-limits follow-up is in the style of the reported design follow-up, not a reported question.
order: 3
minutes: 40
tags: sliding window, deque, hash map, simulation
---
Cursor sends notifications to users (agent finished, review requested, usage alerts). To avoid spamming, a
notification is rate limited at **three levels** at once: the user, the user's team, and the team's company.

```
should_send_notifications(user_to_team: dict, team_to_company: dict, attempts: list[[user, timestamp]]) -> list[bool]
```

- `user_to_team` maps every user to exactly one team; `team_to_company` maps every team to exactly one company.
  Every user in `attempts` is in `user_to_team`, and every team is in `team_to_company`. IDs are strings.
- `attempts` are processed **in order**; timestamps are integer seconds and **non-decreasing** (several attempts can
  share a timestamp).

### Part 1
Within any **600-second sliding window** at most:
- **3** accepted notifications per user
- **10** accepted notifications per team
- **20** accepted notifications per company

An earlier **accepted** notification at time `s` counts against an attempt at time `t` only if `t - s < 600`
(so at `t = s + 600` it has expired). An attempt is accepted only if, counting it, **all three** of its user, team and
company stay within their limits. Accepted attempts are recorded at all three levels immediately; **denied attempts
are not recorded anywhere**. Return one boolean per attempt.

### Example 1
```
user_to_team = {"u1": "t1"},  team_to_company = {"t1": "acme"}
attempts = [["u1", 1], ["u1", 2], ["u1", 3], ["u1", 4], ["u1", 601], ["u1", 602]]
-> [True, True, True, False, True, True]
```
The 4th attempt would be u1's 4th in the window. At `601` the send at `1` has expired (`601 - 1 = 600`).

### Example 2
```
user_to_team = {"u1": "t1", "u2": "t1", "u3": "t1", "u4": "t1", "u5": "t1"},  team_to_company = {"t1": "acme"}
attempts = [["u1", 1], ["u2", 2], ["u3", 3], ["u4", 4], ["u5", 5],
            ["u1", 6], ["u2", 7], ["u3", 8], ["u4", 9], ["u5", 10], ["u1", 11], ["u2", 601]]
-> [True] * 10 + [False, True]
```
The first ten fill team `t1`. At `11` the team is full (u1 itself has only 2). At `601` the send at `1` has expired.

### Follow-up: configurable limits
Product wants to tune each level separately, including a different window per level.
```
should_send_with_limits(user_to_team, team_to_company, attempts, limits: dict) -> list[bool]
```
`limits` maps a level (`"user"`, `"team"`, `"company"`) to `[max_count, window_seconds]`. The expiry rule is the same
per level (`t - s < window` counts). A level **missing** from `limits` is unlimited. `max_count` may be `0` (that level
blocks everything); `window_seconds >= 1`. A denied attempt is still not recorded at *any* level, even levels that had
room.

### Constraints
- Up to `2 * 10^5` attempts, users, teams and companies
- Timestamps fit in a 64-bit integer

### What the interviewer cares about
- A deque of accepted timestamps per user / team / company, popping expired entries from the front (amortized O(1))
- Checking all levels **before** recording anything, so a denial leaves no trace
- The `<` vs `<=` boundary at exactly the window length
- Discussing how this changes in production: many servers (a shared store like Redis, atomic check-and-increment),
  out-of-order timestamps, and memory for millions of idle users
