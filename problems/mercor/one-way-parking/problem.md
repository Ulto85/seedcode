---
title: One-Way Street Parking
difficulty: Medium
source: Mercor MLE onsite, coding round (reported on PracHub, 2026). Part 1 is the reported question; Part 2 and the departures follow-up are our extensions in the same spirit.
order: 1
minutes: 45
tags: simulation, greedy, union-find, segment tree
---
A one-way street has `n` parking spots in a row, numbered `0` to `n - 1` in the direction of travel. All spots
start empty. Cars arrive one at a time; car `i` prefers spot `preferences[i]`.

When a car arrives it drives to its preferred spot. If that spot is empty it parks there. Otherwise it keeps
driving **forward** and parks in the first empty spot with a higher number. Cars never reverse, and a parked car
never moves. If there is no empty spot at or after its preference, the car fails to park.

### Part 1
```
can_all_park(n: int, preferences: list[int]) -> bool
```
Return `True` if every car parks, `False` if at least one fails. An empty `preferences` list returns `True`.

```
can_all_park(3, [0, 0, 1])  -> True     # spots 0, 1, 2
can_all_park(3, [1, 1, 2])  -> False    # third car wants 2, it's taken, nothing after it (spot 0 is behind it)
can_all_park(4, [2, 0])     -> True     # spots 2 and 0
```
Having no more cars than spots is **not** enough, as the second example shows.

### Part 2
```
parking_spots(n: int, preferences: list[int]) -> list[int]
```
Return where each car ends up, in arrival order. A car that fails to park gets `-1`, **drives off the street and
takes no spot**; later cars still arrive and try to park as usual.

```
parking_spots(3, [1, 1, 1, 0])  -> [1, 2, -1, 0]
```
Car 0 takes spot 1, car 1 overflows to 2, car 2 finds nothing at or after 1 and leaves, car 3 takes spot 0.

Walking forward one spot at a time is too slow when many cars want the same spot (e.g. `10^5` cars all preferring
spot 0).

### Follow-up: cars leave
```
parking_log(n: int, events: list) -> list[int]
```
Each event is either `["arrive", p]` (a new car preferring spot `p`, parked by the same rule) or `["leave", k]`
(the car from the `k`-th **arrival** event, 0-indexed, leaves and its spot becomes empty again).
Return one entry per arrival, in order: the spot it took, or `-1` if it failed to park.

- A `leave` for a car that failed to park, has already left, or hasn't arrived yet (`k` out of range) is ignored.
- A freed spot can be taken by any later car whose preference is at or before it.

```
parking_log(3, [["arrive", 2], ["arrive", 2], ["leave", 0], ["arrive", 1]])  -> [2, -1, 1]
```
Arrival 0 takes spot 2. Arrival 1 also wants 2, finds it taken with nothing after it, and fails. Then arrival 0
leaves, freeing spot 2. Arrival 2 prefers spot 1, which is empty, so it parks there and spot 2 stays free.

### Constraints
- `1 <= n <= 10^5`, `0 <= preferences[i] < n`
- Up to `10^5` cars / events
- Every `arrive` preference satisfies `0 <= p < n`

### What the interviewer cares about
- Part 1: noticing the counting argument (cars preferring `j` or later must fit in spots `j..n-1`) instead of simulating
- Part 2: not re-scanning occupied runs (path-compressed "next free spot" pointers)
- Follow-up: explaining why union-find stops working once spots can become free again, and what replaces it
