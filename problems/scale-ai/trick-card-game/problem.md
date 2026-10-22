---
title: Four-Player Trick-Taking Game
difficulty: Hard
source: Scale AI SWE coding round, object-oriented card game (reported Oct 2025 – 2026)
order: 4
minutes: 60
tags: simulation, object-oriented design, sorting
---
Build a small four-player trick-taking card game in stages. Scale interviewers grade this one on **modelling**
(`Card` / `Deck` / `Player` with clear ownership), explicit state transitions and edge cases, so design your classes
even though the tests call plain functions.

**Cards** are strings `rank + suit`: ranks `2 3 4 5 6 7 8 9 10 J Q K A` (low → high), suits `C D H S`
(clubs, diamonds, hearts, spades). Examples: `"10H"`, `"QS"`, `"2C"`.

The `deck` argument is the deck **already shuffled** (shuffling is injected so games are reproducible). It holds
distinct cards and its length is a multiple of 4 (a full deck is 52 cards; tests also use smaller decks).

### Part 1: deal and sort
```
deal(deck: list[str]) -> list[list[str]]
```
Deal round-robin: `deck[0]` to player 0, `deck[1]` to player 1, `deck[2]` to player 2, `deck[3]` to player 3,
`deck[4]` to player 0, and so on. Return the 4 hands, each **sorted by suit (C, D, H, S), then by rank (low → high)**.
```
deal(["AS", "2C", "10H", "KD", "3S", "JC", "5H", "2D"])
-> [["3S", "AS"], ["2C", "JC"], ["5H", "10H"], ["2D", "KD"]]
```

### Part 2: play the tricks
```
play_tricks(deck: list[str]) -> list[list]    # one [leader, cards_played, winner] per trick
```
Deal as in Part 1, then play `len(deck) // 4` tricks. Player 0 leads the first trick; play goes clockwise
(`leader, leader+1, …` mod 4); the **winner of a trick leads the next one**. Every player uses this fixed strategy:

- **Leader:** plays their **highest-ranked** card. Rank ties → the suit that comes **first** in `C, D, H, S`.
- **Others, if they hold the led suit:** must follow suit, and play their **lowest** card of that suit.
- **Others, if void in the led suit:** discard their **lowest-ranked** card. Rank ties → suit first in `C, D, H, S`.
- **Winner:** the highest card **of the led suit**. There are no trumps; off-suit cards never win.

`cards_played` lists the 4 cards **in play order** (starting with the leader). Played cards leave the hand.

```
deck = ["AS", "2C", "10H", "KD", "3S", "JC", "5H", "2D"]   # hands as in Part 1
trick 1: P0 leads AS; P1 void in S -> discards 2C; P2 -> 5H; P3 -> 2D.   AS wins -> [0, ["AS","2C","5H","2D"], 0]
trick 2: P0 leads 3S; P1 -> JC; P2 -> 10H; P3 -> KD.                      3S wins -> [0, ["3S","JC","10H","KD"], 0]
```

### Part 3: score the game
```
score_game(deck: list[str]) -> dict    # {"scores": [int, int, int, int], "winner": int}
```
Scoring cards: every **5** is worth 5 points, every **10** is worth 10, every **K** is worth 10; all other cards are
worth 0. The winner of a trick earns the points of all 4 cards in it. `winner` is the player with the most points;
ties → the **lowest** player index (so if nobody scores, the winner is 0).

For the example deck: trick 1 holds `5H` (5) and trick 2 holds `10H`, `KD` (20), both won by player 0
→ `{"scores": [25, 0, 0, 0], "winner": 0}`.

### Discussion follow-ups
- How would you replay a game exactly from an event log? (Hint: your Part 2 output *is* that log.)
- How would you plug in a different scoring variant or player strategy without touching the game loop?

*Reconstructed: the reports describe the three stages, Card/Deck/Player classes and 5/10/K as scoring cards, but
leave strategy, point values and tie rules to the candidate. The concrete rules above are one fully specified
choice.*
