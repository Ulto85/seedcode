---
title: Fastest Commute Mode
difficulty: Medium
source: Databricks SWE technical phone screen, "best transportation mode on a grid" (most reported BFS question, 2024–2026)
order: 3
minutes: 50
tags: bfs, grid, dijkstra
---
A city is a grid of strings. Each cell is one of:

| char | meaning |
|---|---|
| `S` | your start (exactly one) |
| `D` | your destination (exactly one) |
| `X` | blocked, nobody can enter |
| `'1'` … `'9'` | a road usable only by transport mode 1 … 9 |

There are `k` modes (`k = len(times)`, mode `i` is written as the digit `str(i + 1)`). Mode `i` takes `times[i]`
minutes and costs `costs[i]` dollars **per step**. A step moves up, down, left or right by one cell. While using
mode `i` you may only **step into** cells labelled with mode `i`'s digit, `S` or `D`.

### Part 1
You must pick **one** mode for the whole trip.
```
best_mode(grid: list[str], names: list[str], times: list[int], costs: list[int]) -> str
```
For each mode, take the shortest route (fewest steps) using only that mode. Its total time is `steps * times[i]` and
its total cost is `steps * costs[i]`. Return the **name** of the mode with the smallest total time; break ties by
smaller total cost, then by the mode that comes first in `names`. If no mode can reach `D`, return `""`.

### Follow-up: switching modes
Now you may change mode during the trip. You start in any mode you like (for free). You may change mode on any cell
you are standing on; each change costs `switch_penalty` minutes and you stay on that cell. Every step costs the
current mode's `times[i]` and must obey the current mode's rule above. Costs are ignored in the follow-up.
```
fastest_with_switches(grid: list[str], times: list[int], switch_penalty: int) -> int
```
Return the minimum total minutes from `S` to `D`, or `-1` if `D` can't be reached.

### Example
```
grid = ["S2221",
        "1XXX1",
        "1111D"]
names = ["Walk", "Bike"], times = [3, 1], costs = [0, 2]

Walk: S→(1,0)→(2,0)→(2,1)→(2,2)→(2,3)→D     6 steps -> 18 min, $0
Bike: S→(0,1)→(0,2)→(0,3), but (0,4) is a walking cell -> can't reach D
best_mode(grid, names, times, costs) -> "Walk"

Follow-up, switch_penalty = 2:
bike S→(0,1)→(0,2)→(0,3)      3 min
switch to walking on (0,3)     2 min
walk (0,4)→(1,4)→D            9 min
fastest_with_switches(grid, [3, 1], 2) -> 14     (walking only would be 18)
```

### Constraints
- 1 ≤ rows, cols ≤ 300, 1 ≤ k ≤ 9, 1 ≤ times[i], costs[i] ≤ 100, 0 ≤ switch_penalty ≤ 1000.
- Part 1: one BFS per mode, O(k · R · C). Follow-up: a weighted shortest path over states (cell, mode).
- The grid encoding, tie-break order and switching rules are reconstructed from several candidate reports; the
  original asks the same thing (fastest mode, cost as tie-breaker, follow-up with a switching penalty).
