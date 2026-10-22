---
title: Update a Neuron Grid
difficulty: Easy
source: Scale AI SWE technical screen (reported Feb 2026)
order: 3
minutes: 30
tags: matrix, simulation, in-place
---
You're given an `m x n` grid `neurons` of non-negative integers. A cell is **firing** if its value is `0`, and
**non-firing** if its value is `> 0`. Every cell has up to **8 neighbours** (horizontal, vertical and diagonal; cells
off the edge of the grid don't exist).

Update every cell **simultaneously**, i.e. based only on the *original* grid:

| cell | firing neighbours | new value |
|---|---|---|
| firing (`0`) | exactly 3 | becomes `6` |
| non-firing (`> 0`) | 0 or 1 | decreases by 2 (not below 0) |
| non-firing (`> 0`) | 4 or more | decreases by 1 (not below 0) |
| anything else | | unchanged |

```
update_neurons(neurons: list[list[int]]) -> list[list[int]]
```
Return the updated grid (you may modify the input in place and return it). An empty grid `[]` returns `[]`.

### Example
```
[[0, 0, 0],          [[6, 0, 6],
 [0, 0, 0],    ->     [0, 0, 0],
 [0, 0, 0]]           [6, 0, 6]]
```
Corners see exactly 3 firing neighbours → 6. Edge cells see 5 and the centre sees 8, so they stay 0.

```
[[5]]  -> [[3]]      # no firing neighbours: 5 - 2
[[1, 0]] -> [[0, 0]] # 1 has one firing neighbour: max(0, 1 - 2) = 0; the 0 has no firing neighbours, so stays 0
```

### Follow-up (discussion)
First solve it with a copy of the grid. Then do it with **O(1) extra space**: encode both the old and new state in
each cell during the first pass (e.g. store `new * K + old`, or mark firing-ness in a spare bit) and decode in a
second pass. The tests only check the returned grid, so either approach passes.

### Constraints
- 0 ≤ m, n ≤ 300, 0 ≤ neurons[i][j] ≤ 10⁶
