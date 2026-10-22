---
title: Agent File Editor Tool
difficulty: Medium
source: In the style of Cognition's reported "build your own Devin" interview (CEO Scott Wu, 2025). Not a reported question.
order: 0
minutes: 45
tags: design, strings, undo, tool use
---
Cognition's CEO has described the engineering interview as building **your own end-to-end coding agent** in a few
hours. Every coding agent needs a **file-editing tool** that the model calls with text arguments and that answers
with text the model reads back. Build that tool over an in-memory set of files.

> This is **not** a reported question. It practices one piece of what the "build your own Devin" format needs.

Every method returns a **string**, because the result goes straight back into the model's context. Errors are
**returned** as strings that start with `"ERROR: "`. Never raise an exception.

```
FileEditor()
create(path: str, text: str) -> str
view(path: str, start: int, end: int) -> str
str_replace(path: str, old: str, new: str) -> str
insert(path: str, line: int, text: str) -> str
undo(path: str) -> str              # Follow-up
```

**Lines.** A file's lines are always `text.split("\n")`. So `""` has one empty line, and `"a\n"` has two lines,
`"a"` and `""`. Line numbers start at 1.

### Part 1
Check errors in the order they're listed. The first one that applies is returned.

- `create(path, text)`
  - `"ERROR: file exists"` if `path` already exists.
  - Otherwise store the file and return `"OK"`.
- `view(path, start, end)`: show lines `start..end` inclusive. `end == -1` means "to the last line".
  - `"ERROR: no such file"`
  - `"ERROR: invalid range"` if `start < 1`, or `start > number of lines`, or `end != -1 and end < start`.
  - If `end` is past the last line, clamp it to the last line.
  - Each shown line is formatted as `f"{n}|{line}"`, and the lines are joined with `"\n"`.
- `str_replace(path, old, new)`: replace the **one** occurrence of `old` with `new`.
  - `"ERROR: no such file"`
  - `"ERROR: old is empty"` if `old == ""`
  - `"ERROR: old not found"` if it occurs 0 times
  - `"ERROR: old found N times"` if it occurs `N >= 2` times. Count non-overlapping occurrences, like
    Python's `str.count`.
  - On success, return `f"OK: line {L}"`. `L` is the line number where the match **started** in the file
    *before* the edit.
- `insert(path, line, text)`: insert `text` **after** line `line`. `line == 0` inserts at the very top.
  - `"ERROR: no such file"`
  - `"ERROR: invalid line"` unless `0 <= line <= number of lines`
  - The new lines are `lines[:line] + text.split("\n") + lines[line:]`. Return `"OK"`.

`old`, `new` and `text` may span several lines (contain `"\n"`).

### Example
```
create("app.py", "def f():\n    return 1\n")       -> "OK"
view("app.py", 1, -1)                              -> "1|def f():\n2|    return 1\n3|"
str_replace("app.py", "return 1", "return 2")      -> "OK: line 2"
str_replace("app.py", "x = 9", "y")                -> "ERROR: old not found"
insert("app.py", 0, "import os")                   -> "OK"
view("app.py", 1, 2)                               -> "1|import os\n2|def f():"
create("app.py", "")                               -> "ERROR: file exists"
view("app.py", 9, 10)                              -> "ERROR: invalid range"   # file has 4 lines
```

### Follow-up: undo
The model makes mistakes. Add `undo(path)`, which reverts the **most recent successful** `str_replace` or
`insert` on that file. Calling it repeatedly steps further back in that file's history.
- `"ERROR: no such file"`
- `"ERROR: nothing to undo"` if that file has no edits left to revert. `create` itself cannot be undone.
- Otherwise return `"OK"`.
- Failed edits are not recorded. Each file has its own history: undoing `a.py` never touches `b.py`.

```
create("a.py", "x = 1")             -> "OK"
str_replace("a.py", "1", "2")       -> "OK: line 1"
insert("a.py", 1, "y = 3")          -> "OK"
undo("a.py")                        -> "OK"      # back to "x = 2"
undo("a.py")                        -> "OK"      # back to "x = 1"
undo("a.py")                        -> "ERROR: nothing to undo"
```

### Constraints
- Up to `3 * 10^4` calls. Files are up to a few thousand lines.
- Paths are arbitrary non-empty strings. They are just keys; there are no directories.

### What the interviewer cares about
- Error messages a model can act on, and exact, predictable output formats. An agent loop is only as good as its
  tools' feedback.
- Getting the edge cases right: an empty file, a trailing newline, a multi-line `old`, a match that is ambiguous.
- For undo, deciding what to store (full snapshots vs. reverse edits) and explaining the memory trade-off.
