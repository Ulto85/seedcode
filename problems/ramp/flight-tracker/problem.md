---
title: Flight Tracker
difficulty: Medium
source: Ramp SWE technical phone screen, "flight records" (most reported, 2025-2026)
order: 1
minutes: 45
tags: design, hash map, sorting, binary search
---
Ramp's travel product gets a feed of flight records for employees. Build a small query layer on top of it.

Each record is a list:
```
[departure_airport, departure_time, arrival_airport, arrival_time, user_id]
# e.g. ["JFK", 100, "SFO", 460, "alice"]
```
Times are integers (minutes since some epoch; the real question used ISO-8601 UTC strings, which compare the same way).
The records arrive in **no particular order**.

### Part 1
```
FlightLog(flights: list[list])
most_flights() -> str | None
```
Return the user who appears in the most records. **Ties → the lexicographically smallest user id.** If there are no
records, return `None`.

### Follow-up: where is a user at time t?
```
location(user_id: str, t: int) -> str | list | None
```
- `None` if `user_id` has no flights at all.
- `"unknown"` if `t` is before the user's first departure.
- `["in_transit", departure_airport, arrival_airport]` if some flight of the user has `departure_time <= t < arrival_time`.
- Otherwise, the `arrival_airport` of the user's most recent flight that has landed (`arrival_time <= t`). This covers
  waiting between flights and being done for good.

Boundaries: at exactly `departure_time` the user is already **in transit**; at exactly `arrival_time` they are **at the
arrival airport**.

### Example
```
log = FlightLog([["SFO", 600, "JFK", 900, "alice"],
                 ["JFK", 100, "SFO", 460, "alice"],
                 ["LAX", 200, "SEA", 350, "bob"]])
log.most_flights()          -> "alice"
log.location("alice", 50)   -> "unknown"
log.location("alice", 100)  -> ["in_transit", "JFK", "SFO"]
log.location("alice", 460)  -> "SFO"        # landed exactly now
log.location("alice", 2000) -> "JFK"
log.location("carol", 300)  -> None
```

### What the interviewer cares about
- Group flights by user and sort each user's flights by departure **once**, then answer each `location` query with
  **binary search**. Many queries are made against the same log, so re-scanning every flight per query is too slow.
- Getting the boundary rules exactly right.

### Constraints
- 0 ≤ number of records ≤ 2·10⁵, up to 2·10⁵ queries
- `0 ≤ departure_time < arrival_time ≤ 10⁹`
- A single user's flights never overlap in time (one may land at the exact minute the next departs). Consecutive
  flights don't have to connect (you may land at SFO and next depart from OAK).

*Integer timestamps and the `None`/`"unknown"` conventions are a fully specified reconstruction of the reported question.*
