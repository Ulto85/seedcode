---
title: CSAT Sliding Window Tracker
difficulty: Easy
source: Decagon phone screen (frequently reported)
order: 5
minutes: 30
tags: design, queue, sliding window
---
Decagon's AI agents handle support conversations, and each finished conversation gets a customer satisfaction (CSAT)
score from 1 to 5. Build a tracker for the scores in a rolling time window.

```
CSATTracker(window: int)
add_score(timestamp: int, score: int) -> None
get_average(timestamp: int) -> float      # average score in the window ending at timestamp
```

A score recorded at time `s` is in the window at time `t` if `t - window < s <= t`. Return `0.0` if the window is empty.
Timestamps passed to every method are **non-decreasing**.

### Follow-up
```
get_csat_percent(timestamp: int) -> float   # % of scores in the window that are 4 or 5 (0.0 if empty)
```
Make every operation **amortized O(1)**. A hidden test streams 200k operations.

### Example
```
t = CSATTracker(10)
t.add_score(1, 5); t.add_score(5, 1)
t.get_average(10)  -> 3.0
t.get_average(11)  -> 1.0   # score at t=1 dropped out (11 - 10 = 1, not < 1)
```
