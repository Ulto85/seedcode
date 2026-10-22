---
title: Directory Sync Plan
difficulty: Medium
source: Loosely inspired by a reported Codeium (Windsurf, now part of Cognition) OA on file replication (1point3acres; details locked). Not the reported question.
order: 3
minutes: 45
tags: hash map, sets, sorting, file systems
---
Before an agent runs in a remote sandbox, the user's workspace has to be mirrored there. Computing the operations
that turn the sandbox's copy (`dst`) into the user's copy (`src`) is a "file replication" problem. A Codeium OA
reportedly asked one; its details aren't public, so this spec is our own.

```
sync_plan(src: dict[str, str], dst: dict[str, str]) -> list[list[str]]                 # Part 1
sync_plan_with_moves(src: dict[str, str], dst: dict[str, str]) -> list[list[str]]      # Follow-up
```

Each tree maps a **file path** to that file's **content hash**. Paths use `/` and are relative (`"src/app.py"`).
There are no empty directories: a **directory exists** in a tree if and only if it is a proper prefix
(`"a"`, `"a/b"`) of some file path in that tree. No name is ever a file in one place and a directory in another,
across both trees combined.

### Part 1
Return the operations that make `dst` identical to `src`, as lists:

| op | when |
|---|---|
| `["mkdir", d]` | directory `d` exists in `src` but not in `dst` |
| `["delete", p]` | file `p` is in `dst` but not in `src` |
| `["rmdir", d]` | directory `d` exists in `dst` but not in `src` |
| `["copy", p]` | file `p` is in `src` and is missing from `dst` or has a different hash |

Files whose path and hash are the same in both trees need nothing. The plan must be in this exact order:
1. all `mkdir`, parents before children: sorted by (depth, path). Depth = number of `/` in the path.
2. all `delete`, sorted by path
3. all `rmdir`, children before parents: sorted by (depth **descending**, path ascending)
4. all `copy`, sorted by path

Paths are compared as plain strings.

### Example
```
src = {"a/x.py": "h1", "a/b/y.py": "h2", "c.txt": "h3"}
dst = {"a/x.py": "h1", "a/b/y.py": "OLD", "d/e/z.py": "h9"}
sync_plan(src, dst) ->
  [["delete", "d/e/z.py"], ["rmdir", "d/e"], ["rmdir", "d"], ["copy", "a/b/y.py"], ["copy", "c.txt"]]
```

### Follow-up: detect moves
Copying is the expensive part. If a file that would be **deleted** has exactly the hash of a file that would be
**copied to a path missing from `dst`**, rename it on the remote instead: `["move", from, to]`.
- Only files at **missing** paths can be move targets. A path that exists in `dst` with a different hash is still
  a `copy`.
- **Pairing.** For each hash, sort that hash's would-be-deleted paths, and sort its would-be-copied-to-missing
  paths. Pair them in order: 1st with 1st, 2nd with 2nd, and so on. Paired files become `move`s. Any unpaired
  files stay `delete` / `copy`.
- `move`s come **after all `mkdir`** and **before all `delete`**, sorted by `from` path. `mkdir`/`rmdir` are
  decided exactly as in Part 1. They depend only on the two trees, not on how the files got there.

```
src = {"lib/util.py": "h1", "lib/new.py": "h1", "main.py": "h2"}
dst = {"util.py": "h1", "old/main.py": "h2", "old/x.py": "h1"}
sync_plan_with_moves(src, dst) ->
  [["mkdir", "lib"],
   ["move", "old/main.py", "main.py"],
   ["move", "old/x.py", "lib/new.py"],      # h1: deleted [old/x.py, util.py] pair with copied [lib/new.py, lib/util.py]
   ["move", "util.py", "lib/util.py"],
   ["rmdir", "old"]]
```

### Constraints
- Up to `10^5` files per tree. Paths are at most 6 levels deep.

### What the interviewer cares about
- Set arithmetic over paths, computing directories from file paths, and getting the operation order right (you
  can't `rmdir` a non-empty directory or copy into a directory that doesn't exist yet).
- Grouping by hash for move detection in linear time, not comparing every deleted file with every new one.
- A deterministic plan, so that tests and retries are reproducible.
