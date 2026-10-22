---
title: Eager Spreadsheet
difficulty: Medium
source: Harvey SWE technical screen / onsite, "spreadsheet with set/get, cell-reference formulas and cycle-rejecting writes" (Harvey's most reported coding question, 2025–2026; I/O format follows the public write-up)
order: 3
minutes: 50
tags: design, graph, topological sort, cycle detection, parsing
---
Harvey's tabular review grid lets lawyers write small formulas over extracted values. Build the engine: a sheet
whose cells hold integers or formulas, where **every write leaves all values already computed**, so a read is a
plain lookup.

```
eager_sheet(operations: list[list[str]]) -> list[str]
```

Each operation is `["set", cell, raw]` or `["get", cell]`, applied in order to an initially empty sheet. Return one
string per operation:
- a `set` returns `"OK"` (or `"CYCLE"`, see the follow-up)
- a `get` returns the cell's current value as a canonical decimal string: no `+`, no leading zeros, `"0"` for zero,
  `"-12"` for negatives

**Cells** are named by uppercase letters followed by a row number with no leading zeros: `A1`, `B10`, `AA3`.
A cell that was never set (including one only referenced by formulas) has value `0`.

**`raw`** is one of:
- an **integer literal**, optionally signed and possibly with leading zeros: `"5"`, `"-12"`, `"+0007"` (= 7),
  `"-0"` (= 0)
- a **formula**: `=` then `term (("+" | "-") term)*`, where a term is a non-negative integer or a cell name.
  Spaces may appear around any token. There are no unary signs and no parentheses. Examples: `"=A1+B2"`,
  `"= A1 - 3 + C7 "`, `"=7"`. A repeated reference counts every time: `"=A1+A1"` is `2 * A1`.

A `set` **replaces** the cell's whole previous definition (a literal can become a formula and vice versa), and after
it every cell that depends on it, directly or indirectly, must already hold its new value before the next operation.
All inputs are well-formed.

### Example
```
["set","A1","2"]        -> "OK"
["set","B1","=A1+1"]    -> "OK"      # 3
["set","C1","=A1+B1"]   -> "OK"      # 5
["set","A1","5"]        -> "OK"      # B1 = 6, C1 = 11
["get","C1"]            -> "11"
["get","Z9"]            -> "0"
```

### Part 1
Implement it assuming no formula ever creates a circular reference (every `set` returns `"OK"`). Formulas may form
long chains or "diamonds" (`B = A + A`, `C = B + B`, …); evaluating them recursively on every read, without
caching, is far too slow.

### Follow-up: reject cycles
A `set` that would make a cell depend on itself, directly (`A1 = A1 + 1`) or through other cells, returns
`"CYCLE"` and leaves the sheet **completely unchanged**: the old definition stays and no value changes.
```
["set","A1","=B1"]      -> "OK"      # A1 = 0
["set","B1","=A1+1"]    -> "CYCLE"   # B1 -> A1 -> B1; B1 stays unset
["get","A1"]            -> "0"
["set","A1","3"]        -> "OK"      # A1 no longer references B1
["set","B1","=A1+1"]    -> "OK"
["get","B1"]            -> "4"
```

### Constraints
- Up to `5000` operations, at most `100` terms per formula
- Python integers, so no overflow concerns

### What the interviewer cares about
- Keeping **both** graph directions: a cell's inputs (to evaluate it and to undo its old edges) and its dependents
  (to find what must be recomputed)
- Recomputing the affected cells **once each in topological order**, only after their inputs are ready
- Checking for a cycle **before** touching any state, so a rejected write leaves no trace
