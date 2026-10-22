---
title: Flatten the Org Chart
difficulty: Hard
source: Rippling SWE technical screen, "org height and minimal CEO promotions" (reported Feb 2026)
order: 3
minutes: 45
timeout: 20
tags: tree, BFS, greedy
---
Rippling's HR graph stores who reports to whom. A company has `n` employees labeled `1..n`; employee `1` is the
**CEO**. For every `i`, employee `reportee[i]` reports directly to `manager[i]`. The pairs always form one tree rooted
at the CEO (the arrays have length `n - 1` and may come in any order).

The **level** of an employee is the number of people on the chain from the CEO down to them, inclusive: the CEO is at
level `1`, the CEO's direct reports at level `2`, and so on. The org's **height** is the maximum level, so it is
measured in *people*, not edges: a company that is only the CEO has height `1`.

### Part 1
```
org_height(n: int, manager: list[int], reportee: list[int]) -> int
```
Return the height of the org.

### Follow-up: too many layers
Leadership wants **at most `h` levels**. The only tool is a **promotion**: pick any employee other than the CEO and
make them report directly to the CEO. Their whole team (their entire subtree) moves with them unchanged, so the
promoted employee lands at level `2` and everyone below them moves up accordingly.
```
min_promotions(n: int, manager: list[int], reportee: list[int], h: int) -> int
```
Return the minimum number of promotions needed so that the height is at most `h`. Return `0` if it already is, and
`-1` if it's impossible (that only happens when `h = 1` and there is anyone besides the CEO).

### Example
```
       1              n = 7
      / \             manager  = [1, 2, 3, 4, 1, 6]
     2   6            reportee = [2, 3, 4, 5, 6, 7]
     |   |
     3   7            org_height(...)        -> 5
     |                min_promotions(..., 3) -> 1   # promote 4: 4 is at level 2, 5 at level 3
     4                min_promotions(..., 2) -> 4   # promote 3, 4, 5 and 7
     |                min_promotions(..., 5) -> 0
     5                min_promotions(..., 1) -> -1
```

### Constraints
- `1 <= n <= 10⁵`, `1 <= h <= n`. The tree can be a single chain of length `10⁵`, so **recursive DFS will overflow
  Python's stack**: use BFS or an explicit stack.
- Aim for `O(n)` or `O(n log n)`. Simulating promotions and recomputing levels each time is too slow.

### Hints for the follow-up (expand only if stuck)
<details><summary>Hint 1</summary>
Look at the single deepest employee whose level is still over <code>h</code>. Some promotion must happen on their
chain. Which person on that chain is the best one to promote?
</details>
<details><summary>Hint 2</summary>
Promote the ancestor exactly <code>h - 2</code> levels above them (themself if <code>h = 2</code>). It fixes them and
moves the biggest possible subtree; everything in it is no deeper, so the whole subtree is now fine. Repeat with the
next deepest employee not already fixed.
</details>
