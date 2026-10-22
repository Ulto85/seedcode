---
title: Count Legal Tic-Tac-Toe Games
difficulty: Hard
source: Decagon SWE technical screen / onsite (reported 2026)
order: 2
minutes: 45
tags: backtracking, game tree, recursion
---
Starting from an **empty 3×3 board** with `X` moving first, players take turns placing their mark in an empty cell.
A game ends **immediately** when a player gets three in a row (row, column or diagonal), or when the board is full.

Return the number of distinct legal **games**. Two games are different if their **move sequences** differ, even if they
end on the same final board.

**Don't hard-code the answer.** The interviewer wants you to derive it with a search.

### Part 1
```
count_games() -> int
```

### Follow-up
Break the total down by outcome:
```
game_outcomes() -> dict   # {"X": x_wins, "O": o_wins, "draw": draws}
```

### What they probe on
- A sanity bound before you code: at most how many sequences? (9!)
- Clean backtracking: place → check → recurse → undo
- Checking only the lines through the last move
- Complexity, and how it scales to bigger boards
