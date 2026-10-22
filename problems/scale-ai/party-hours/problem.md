---
title: Party Hours by Town
difficulty: Medium
source: Scale AI SWE technical screen, party-planning app intervals (reported Sep 2025 – Dec 2025)
order: 2
minutes: 45
tags: intervals, sorting, hash map
---
A party-planning app tracks when parties happen in each town. You get two in-memory tables:

```
regions: list[dict]   # one row per town: {"town": str, "city": str, "state": str}
parties: list[list]   # [town, start, end] in integer minutes, start < end
```

Every town in `parties` appears in `regions`. Each town belongs to exactly one city. A town may have any number of
parties; they arrive **unsorted** and may **overlap**, **touch** (`[60, 120]` and `[120, 150]`), or stick out past
the edges of the day.

### Part 1
```
party_hours(regions, parties) -> list[list]   # [[town, hours], ...]
```
The day is the window `[0, 1440]` (minutes). For each town, compute how much of the day is covered by **at least one**
party: clamp every party to the window (drop it if nothing is left), then take the length of the union.

- Return one `[town, hours]` row per town, **in the same order as `regions`**.
- `hours` = covered minutes / 60, **rounded to 2 decimals**. A town with no parties gets `0.0`.

```
regions = [{"town": "t1", "city": "c1", "state": "s1"}, {"town": "t2", "city": "c1", "state": "s1"},
           {"town": "t3", "city": "c2", "state": "s1"}]
parties = [["t1", 90, 180], ["t1", 60, 120], ["t1", 180, 210], ["t3", -30, 30], ["t3", 1400, 1500]]

t1: [60,120] ∪ [90,180] ∪ [180,210] = [60,210]  -> 150 min -> 2.5
t2: no parties                                   -> 0.0
t3: clamped to [0,30] and [1400,1440]            -> 70 min  -> 1.17
-> [["t1", 2.5], ["t2", 0.0], ["t3", 1.17]]
```

### Follow-up: idle time grouped by city
```
idle_segments(regions, parties, day_start, day_end) -> dict[str, list[list]]
```
Now the window is `[day_start, day_end]` (`day_start < day_end`). For each town, the **idle segments** are the maximal
gaps inside the window that no party covers, as `[town, gap_start, gap_end]` (always `gap_start < gap_end`).

- Return a dict mapping **every city in `regions`** to the idle segments of its towns. A city whose towns are all
  busy all day maps to `[]`.
- Inside a city's list: towns in `regions` order, then each town's segments by start time.
- A town with no parties is idle for the whole window. Touching parties leave no gap between them.

```
day_start = 0, day_end = 600, same regions as above
parties = [["t1", 60, 180], ["t2", 300, 360], ["t3", -10, 700]]
-> {"c1": [["t1", 0, 60], ["t1", 180, 600], ["t2", 0, 300], ["t2", 360, 600]],
    "c2": []}
```

### Constraints
- Up to 10⁵ towns and 2·10⁵ parties; times are integers (possibly negative or > the window).
- Aim for O(P log P + T). Re-scanning the whole party list for each town is too slow.

*The reported question uses wider region tables (ids + names for town/city/state) and a few variants
("party time blocks per neighborhood", "community ranges and town idle hours"); this version keeps only the fields
the computation needs and pins down output order and rounding.*
