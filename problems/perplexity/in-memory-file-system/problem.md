---
title: In-Memory File System
difficulty: Hard
source: Perplexity SWE onsite, "in-memory file system: strict mkdir, touch, ls, rm, rmdir and a command runner" (reported 2026); Follow-up from the reported technical-screen variant "add cd and relative path support" (2026). Error strings and precedence are reconstructed.
order: 3
minutes: 60
tags: design, tree, parsing, strings
---
Build an in-memory file system with a single root `/`. Interviewers reportedly care less about cleverness and
more about getting **every error path right**, so the rules below are strict. Read them carefully.

Every method returns `"ok"` on success or one of these exact error strings:
`"error: invalid path"`, `"error: not found"`, `"error: not a directory"`, `"error: already exists"`,
`"error: is a directory"`, `"error: not empty"`, `"error: cannot remove root"`, `"error: busy"`.

### Paths
- A path is `/` (the root), or one or more **names** joined by single `/`. An **absolute** path starts with `/`.
- A name is one or more of `A-Z a-z 0-9 . _ -`. An empty path, an empty component (`/a//b`, a trailing `/`) or
  any other character makes the path **invalid**. Validity is checked **first**, before looking at the tree.
- **Every component except the last** must be an existing directory. If one doesn't exist, the result is
  `"error: not found"`; if one is a file, `"error: not a directory"`. Nothing is ever created implicitly
  (`mkdir /a/b` fails if `/a` is missing).
- In Part 1 and Part 2 all paths in the tests are absolute and contain no `.` or `..` components.

### Part 1
```
FileSystem()
mkdir(path) -> str           # create a directory
touch(path) -> str           # create an empty file
ls(path) -> list[str] | str  # list, or an error string
```
- `mkdir` / `touch`: if anything (file or directory) already exists at `path`, or `path` is `/`, return
  `"error: already exists"`. (`touch` on an existing file is an error, not a no-op.)
- `ls` on a directory returns its entry names sorted in ascending string order (`[]` if empty); on a file, a
  one-element list with the file's name; on a missing path, `"error: not found"`.

### Part 2: removing, and a command runner
```
rm(path) -> str
rmdir(path) -> str
execute(commands: list[str]) -> list[str]
```
- `rm` removes a **file**. On a directory (including `/`): `"error: is a directory"`. Missing: `"error: not found"`.
- `rmdir` removes an **empty directory**. Checks in order: `/` gives `"error: cannot remove root"`; missing gives
  `"error: not found"`; a file gives `"error: not a directory"`; a non-empty directory gives `"error: not empty"`.
- `execute` runs each command string on **this** file system (state persists across calls) and returns one
  output string per command, continuing after failures:
  - Split the command on whitespace. The first token is the command name: `mkdir`, `touch`, `ls`, `rm`, `rmdir`
    (and `cd`, `pwd` in the Follow-up). Anything else, or an empty command, gives `"error: unknown command"`.
  - `pwd` takes 0 arguments and every other command exactly 1; otherwise `"error: wrong number of arguments"`.
  - The output is the method's string result. For a successful `ls`, it's the names joined by single spaces
    (`""` for an empty directory).

### Follow-up: `cd` and relative paths
```
cd(path) -> str
pwd() -> str          # absolute path of the current directory; starts as "/"
```
- A path that doesn't start with `/` is **relative** to the current directory. Every method now accepts relative
  paths, and `.` (this directory) and `..` (parent; `..` at `/` stays at `/`) can appear anywhere.
- Paths are walked **through the real tree**, one component at a time. So `missing/../a` is `"error: not found"`
  even if `a` exists, because `missing` must exist to step through it.
- `cd` to a missing path gives `"error: not found"`; to a file, `"error: not a directory"`. A failed `cd`
  leaves the current directory unchanged.
- If the **last** component is `.` or `..`: for `rm`/`rmdir` the path is **invalid** (`"error: invalid path"`,
  checked first like any other invalid path, so `rm /missing/..` is invalid, not "not found"). For `mkdir`/`touch`
  the path is walked normally and then gives `"error: already exists"`. `ls` and `cd` work normally.
- `rmdir` of the current directory (once it's empty) returns `"error: busy"`. This check comes after the
  not-empty check.

### Example
```
mkdir("/docs")            -> "ok"
mkdir("/docs/2026/q1")    -> "error: not found"       # /docs/2026 doesn't exist
touch("/docs/a.txt")      -> "ok"
touch("/docs/a.txt/b")    -> "error: not a directory"
mkdir("/docs/")           -> "error: invalid path"
ls("/")                   -> ["docs"]
ls("/docs/a.txt")         -> ["a.txt"]
execute(["mkdir /tmp", "ls /", "rmdir /docs", "rm /docs", "cat /docs/a.txt", "ls"])
  -> ["ok", "docs tmp", "error: not empty", "error: is a directory",
      "error: unknown command", "error: wrong number of arguments"]
cd("docs")                -> "ok"
touch("../tmp/x")         -> "ok"
pwd()                     -> "/docs"
ls("..")                  -> ["docs", "tmp"]
rm("a.txt")               -> "ok"
rmdir("/docs")            -> "error: busy"
```

### What the interviewer cares about
- One path parser and one walker shared by every operation, plus a thin `execute` dispatcher
- Consistent, complete error handling: missing parents, wrong node type, duplicates, non-empty directories,
  bad commands and wrong argument counts
- Adding `cd` as a small, local change. If relative paths need edits in every method, the structure is wrong
- Complexity in terms of path depth and directory size
