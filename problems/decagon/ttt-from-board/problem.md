---
title: Count Game Completions From a Board
difficulty: Medium
source: Decagon SWE technical screen (variant of the tic-tac-toe question)
order: 3
minutes: 30
tags: backtracking, recursion
---
You're given a **reachable** 3×3 tic-tac-toe position as a list of 3 strings (characters `'X'`, `'O'`, `'.'`) and the
player to move next.

Return the number of distinct move sequences that take this position to the end of the game. A game ends immediately on
a three-in-a-row or when the board is full. Different move orders count as different sequences.

If the position is **already terminal** (someone has won, or the board is full), return `1` (the empty sequence).

```
count_sequences(board: list[str], player: str) -> int
```

### Example
```
board = ["XOX",
         "OXX",
         "O.."], player = "O"
O at (2,1), then X at (2,2) wins on the diagonal -> 1 sequence
O at (2,2), then X at (2,1) fills the board      -> 1 sequence
answer = 2
```

### Constraints
- The board is always reachable in a legal game, and `player` is consistent with the mark counts.

### Discussion
The number of ways to finish depends only on the board, not on how you got there. That's the insight that makes the
N×N follow-up feasible.
