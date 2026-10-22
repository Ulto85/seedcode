---
title: Concatenation Spreadsheet
difficulty: Medium
source: Ramp SWE coding round, "spreadsheet with dependent cells" (reported Sep 2026)
order: 4
minutes: 45
tags: graph, dfs, memoization, cycle detection
---
Build a tiny in-memory spreadsheet. The grid has columns `A`–`Z` and rows `1`–`100`, so cells are named like `A1`,
`C42`, `Z100`. Every cell holds a **string**. A cell can also hold a **formula** that concatenates other cells.

```
run_sheet(ops: list[list[str]]) -> list[str]
#   ["set", cell, raw]  -> "OK"
#   ["get", cell]       -> "VALUE:" + computed value,  or "CYCLE"
```
Return one string per operation, in order.

### Rules
- A raw value starting with `=` is a **formula**: `=` followed by 1–20 cell references with **no separators**, e.g.
  `=A1B2A1`. Its value is the concatenation of the referenced cells' values in the order written (repeats repeat).
- Any other raw value is a **literal**, kept exactly as given (spaces included, may be empty, may even be the text
  `CYCLE`).
- A cell that was never set evaluates to `""`.
- `set` replaces whatever the cell held before. Reads always reflect the **latest** contents of every cell they
  depend on (no stale caching across `set`s).
- If evaluating the requested cell **reaches** a circular reference (including a cell referring to itself), the `get`
  returns `"CYCLE"`. A cycle elsewhere in the sheet that the requested cell can't reach doesn't matter. The cycle stays
  stored: a later `set` that breaks it makes reads work again.

### Example
```
["set", "C1", "Hello"]   -> "OK"
["set", "C2", " world"]  -> "OK"
["set", "A1", "=C1C2"]   -> "OK"
["get", "A1"]            -> "VALUE:Hello world"
["set", "C1", "Bye"]     -> "OK"
["get", "A1"]            -> "VALUE:Bye world"
["get", "B7"]            -> "VALUE:"               # never set
["set", "B1", "=A1B1"]   -> "OK"
["get", "B1"]            -> "CYCLE"
["get", "A1"]            -> "VALUE:Bye world"      # A1 doesn't reach the cycle
```

### What the interviewer cares about
- Parsing formulas (`=A10B2` is `A10` then `B2`) and treating `=` vs literal correctly.
- Cycle detection via DFS with an "on the current path" set, which is different from "already computed".
- **Memoize within a single read**: in `A1=B1B1, B1=C1C1, C1=D1D1, …` the same cell is reached exponentially many
  ways. Compute each cell once per `get`, but throw that cache away after a `set`.

### Constraints
- Up to 2·10⁴ operations; literals are at most 100 characters.
- Every successful `get` value has length ≤ 10⁴; dependency chains are at most 400 cells deep.
- Formulas are always well-formed references to cells inside the grid (no leading zeros).

*This is a fully specified reconstruction of the reported prompt (the `VALUE:` prefix keeps a literal "CYCLE" apart from a real cycle).*
