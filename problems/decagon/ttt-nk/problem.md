---
title: N×N, K-in-a-Row Game Count
difficulty: Hard
source: Decagon follow-up ("Enumerate 4×4 Tic-Tac-Toe Games", win = 3 in a row)
order: 4
minutes: 45
timeout: 300
tags: memoization, dynamic programming, backtracking
---
Generalize the game: the board is `n × n`, `X` moves first, and a player wins as soon as they have `k` of their marks
consecutively in a row, column or diagonal. A game also ends when the board is full.

Return the number of distinct legal games (move order matters).

```
count_games_nk(n: int, k: int) -> int
```

### Examples
```
count_games_nk(3, 3) -> 255168
count_games_nk(2, 2) -> 24
```

### Why this is hard
Plain backtracking works for 3×3 but not for 4×4 (16! ≈ 2×10¹³ sequences). Many move orders reach the **same board**,
and the number of ways to finish depends only on the board, so memoize on it. Then make the win check fast: only look
at lines through the cell just played (walk the 4 directions outward from it).

### Constraints
- 1 ≤ k ≤ n ≤ 4
- The 4×4 tests are **Stretch** tests: they only run on Submit and share a 5-minute limit. A good memoized Python
  solution takes about 40–80s each.
