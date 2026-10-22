---
title: Apply a Model-Generated Patch
difficulty: Hard
source: In the style of Cognition's reported "build your own Devin" interview (CEO Scott Wu, 2025). Not a reported question.
order: 1
minutes: 60
tags: strings, parsing, diff, search
---
Your coding agent asks the model for code changes in **unified diff** format. Write the tool that applies the
model's patch to a file. Models often get line numbers slightly wrong, so the follow-up asks you to apply hunks
where their context actually is.

> This is **not** a reported question. It practices a core piece of the "build your own Devin" interview format.

```
apply_patch(original: str, patch: str) -> str | None          # Part 1
apply_patch_fuzzy(original: str, patch: str) -> str | None    # Follow-up
```

**File lines.** The file's lines are `original.split("\n")`, numbered from 1. The result is the new lines joined
with `"\n"`.

**Patch format.** Split `patch` on `"\n"`, then **skip completely empty lines**. The rest is one or more **hunks**.
Each hunk is a header line followed by body lines:
```
@@ -A,B +C,D @@          header: A = start line in the ORIGINAL file. ",B" may be missing. Ignore B, C and D.
 some line               ' ' context: must match the file, and is kept
-some line               '-' removal: must match the file, and is removed
+some line               '+' addition: inserted
```
The rest of a body line after its first character is the line's text. The header regex is
`^@@ -(\d+)(,\d+)? \+(\d+)(,\d+)? @@$`. You may assume every patch is well-formed.

A hunk's **old block** is its context and `-` lines, in order. Its **new block** is its context and `+` lines, in
order.

### Part 1: exact line numbers
- The old block must match the original file **exactly**, starting at line `A`: old line `i` equals file line
  `A + i`.
- **Pure insertion.** If the old block is empty, insert the new block **after** line `A`. `A = 0` means at the top.
- All line numbers refer to the **original** file. Applying hunk 1 doesn't shift the numbers for hunk 2.
- **Ordering.** Let `E` be the last original line the previous hunk "used": the last line of its old block, or `A`
  for a pure insertion after line `A`. Use `E = 0` before the first hunk.
  - A hunk with a non-empty old block must start at a line `> E`.
  - A pure insertion needs `E <= A <= number of lines`.
- If any hunk fails (it doesn't match, it runs past the end of the file, it starts before line 1, or it breaks the
  ordering rule), return `None`. The patch is all-or-nothing.

### Example
```
original = "import os\ndef f():\n    return 1\n\ndef g():\n    return 2"
patch    = "@@ -2,2 +2,3 @@\n def f():\n-    return 1\n+    x = 1\n+    return x\n@@ -6 +7 @@\n-    return 2\n+    return 3"
apply_patch(original, patch)
  -> "import os\ndef f():\n    x = 1\n    return x\n\ndef g():\n    return 3"
apply_patch(original, "@@ -1 +1 @@\n-import sys\n+import re")   -> None    # line 1 is "import os"
apply_patch("a\nb", "@@ -0,0 +1 @@\n+top")                      -> "top\na\nb"
```

### Follow-up: fuzzy line numbers
Implement `apply_patch_fuzzy`. A hunk's header line number is now only a **hint**. Process the hunks in order:
- **Expected position** = `A + delta`. `delta` is (actual start − header `A`) of the previously applied hunk, and
  `0` for the first hunk. So if hunk 1 was found 3 lines lower than its header said, hunk 2 is first looked for 3
  lines lower too.
- Find the start position `q` where the old block matches the file exactly. `q` must not overlap any earlier hunk:
  `q > E`, with `E` the last line of the previous hunk's old block (`E = 0` for the first hunk). Of all valid `q`, choose
  the one with the **smallest `|q - expected|`**. On a tie, choose the **smaller `q`**.
- If no position matches, return `None`.
- Every hunk in the follow-up has a non-empty old block. Positions are still in **original-file** line numbers.

```
original = "x\ny\na\nb\nc\nb\nc"
apply_patch_fuzzy(original, "@@ -3 +3 @@\n b\n-c\n+C")   -> "x\ny\na\nb\nC\nb\nc"
    # "b,c" matches at 4 and 6. Expected is 3, so 4 is closer.
apply_patch_fuzzy(original, "@@ -5 +5 @@\n b\n-c\n+C")   -> "x\ny\na\nb\nC\nb\nc"
    # 4 and 6 are both 1 away from 5. The tie goes to the smaller, 4.
```

### Constraints
- The file has up to `2 * 10^5` lines. A patch has up to `2000` hunks, each with up to 10 old lines.
- In the large tests, the fuzzy hunks are displaced by up to ~50 lines from where their headers say.

### What the interviewer cares about
- Careful parsing, and a precise definition of "match" before writing code.
- **Efficiency:** build the output in one pass. Don't splice a list once per hunk, which is O(file × hunks). In the
  fuzzy search, scan **outward** from the expected position instead of finding every match in the file for every
  hunk.
- All-or-nothing behavior: an agent must never half-apply a patch.
