---
title: Spreadsheet With Formulas
difficulty: Hard
source: OpenAI SWE onsite coding, "spreadsheet with cell references + cycle detection" (reported 2025–2026; grammar reconstructed)
order: 2
minutes: 60
tags: design, graph, topological sort, cycle detection
---
Build the engine behind a tiny spreadsheet. Cells hold either a number or a formula that adds and subtracts other
cells, and every cell's value must stay up to date as its inputs change.

```
Spreadsheet()
set_cell(cell: str, value: str) -> bool
get_cell(cell: str) -> int
```

**Cell names** are one or more uppercase letters followed by digits: `A1`, `B12`, `AA3`.

**Values** passed to `set_cell` are one of:
- an **integer literal**: `"5"`, `"-12"`, `"0"`
- a **formula**: `=` followed by one or more terms joined by `+` or `-`. A term is a non-negative integer or a cell
  name. The first term may have a leading `-`. There are no spaces or parentheses. Examples: `"=A1+B2"`,
  `"=A1-3+C7"`, `"=-A1+10"`, `"=A1+A1"`, `"=7"`.

Rules:
- `get_cell` of a cell that was never set (or only appears inside other formulas) returns `0`.
- A formula's value is computed from the **current** values of the cells it references. When a cell changes, every
  cell that depends on it, directly or through other cells, must reflect the new value.
- `set_cell` replaces whatever the cell held before: a literal can become a formula and vice versa.

### Example
```
set_cell("A1", "5")         -> True
set_cell("B1", "=A1+3")     -> True
set_cell("C1", "=A1+B1-1")  -> True
get_cell("C1")              -> 12     # 5 + 8 - 1
set_cell("A1", "10")        -> True
get_cell("B1")              -> 13
get_cell("C1")              -> 22     # 10 + 13 - 1
get_cell("Z9")              -> 0      # never set
```

### Part 1
Implement `set_cell` and `get_cell`. In Part 1 no formula will ever create a cycle, so `set_cell` always returns
`True`. Assume `get_cell` is called far more often than `set_cell`: it should not re-evaluate formulas from scratch
(a long chain of formulas, or one where each cell references the previous one twice, must still be fast).

### Follow-up: cycles
A write that would make a cell depend on itself, directly (`A1 = A1 + 1`) or through other cells (`A1 -> B1 -> A1`),
must be **rejected**: `set_cell` returns `False` and the spreadsheet is left exactly as it was (the cell keeps its
old value or formula). Every other write returns `True`.
```
set_cell("A1", "=B1+1")  -> True     # B1 is unset, so A1 = 1
set_cell("B1", "=A1+1")  -> False    # B1 -> A1 -> B1
get_cell("B1")           -> 0
set_cell("B1", "4")      -> True
get_cell("A1")           -> 5
```

### Constraints
- Up to `2 * 10^4` calls; each formula has at most 10 terms
- Values always fit in a 64-bit integer

### What the interviewer cares about
- Keeping a **reverse dependency graph** (cell -> cells that reference it) so an update touches only what it must
- Recomputing affected cells in **topological order**, so each is evaluated once and after all its inputs
- Detecting the cycle *before* mutating anything, so a rejected write leaves no trace
