---
title: Merkle Tree Repo Diff
difficulty: Medium
source: Cursor SWE technical phone screen, "Merkle tree over a repository / find changed files" (most reported, 2026). The exact hash format in the follow-up is reconstructed.
order: 1
minutes: 45
tags: merkle tree, hashing, tree, recursion
---
Cursor indexes your codebase so the agent can search it. Re-indexing every file after every edit is too slow, so the
client keeps a **Merkle tree** over the repo: when two snapshots have the same directory hash, nothing under that
directory changed and the whole subtree can be skipped.

A **snapshot** is a dict mapping a relative file path to its contents:

```
{"README.md": "hello", "src/main.py": "v1", "src/utils/helpers.py": "h"}
```

- Paths use `/`, have no leading or trailing slash and no empty parts. Directories exist only because a file lives in
  them; there are no empty directories.
- Within one snapshot, no file path is also a directory of another file (`"a"` and `"a/b"` never both appear).

### Part 1
```
repo_diff(snapshot_a: dict, snapshot_b: dict) -> list[[path, change]]
```
Return one `[path, change]` pair for every **file** that differs between the two snapshots, where `change` is:
- `"ADDED"`: the path is a file only in `snapshot_b`
- `"REMOVED"`: the path is a file only in `snapshot_a`
- `"MODIFIED"`: the path is a file in both, with different contents

Sort the result by path (plain string order). Identical snapshots give `[]`. If a path is a file on one side and a
directory on the other, that's not special: the file is `REMOVED` (or `ADDED`) and every file under the directory is
`ADDED` (or `REMOVED`). An empty file `""` is still a file.

```
a = {"README.md": "hello", "src/main.py": "v1", "src/utils/helpers.py": "h", "docs/old.md": "old"}
b = {"README.md": "hello", "src/main.py": "v2", "src/utils/helpers.py": "h",
     "src/utils/new.py": "n", "tests/test_main.py": "t"}

repo_diff(a, b) -> [["docs/old.md", "REMOVED"],
                    ["src/main.py", "MODIFIED"],
                    ["src/utils/new.py", "ADDED"],
                    ["tests/test_main.py", "ADDED"]]
```

Solve it the way the interviewer wants: build a tree per snapshot (folders are internal nodes with any number of
children, files are leaves), hash it bottom-up, and walk both trees together, **skipping any directory whose hash
matches** on both sides. (A flat dict comparison passes the tests, but it isn't the point of the question and you'll
be asked why the tree helps.)

### Follow-up: deterministic hashing
Two machines must compute the same hash for the same repo, so the hash format is fixed:

```
tree_hash(snapshot: dict, path: str) -> str | None
```
Return the hex SHA-256 of the node at `path` (`""` means the repo root), or `None` if no file or directory exists at
that path (including a path that goes *through* a file, like `"README.md/x"`).

- **File:** `sha256("blob\0" + contents)`
- **Directory:** `sha256("tree\0" + entries)`, where `entries` concatenates one line per child, children sorted by name
  (plain string order): `"<kind> <name> <child_hash>\n"` with `kind` = `blob` or `tree`.
- Encode strings as UTF-8; return `hexdigest()`. `\0` is the NUL character. The root always exists, so an empty
  snapshot's root hash is `sha256("tree\0")`.

```
tree_hash(a, "src/utils/helpers.py") = sha256("blob\0h")
                                     = h1
tree_hash(a, "src/utils")            = sha256("tree\0blob helpers.py " + h1 + "\n")
                                     = "410be616df3ca0c462261c0143a19d8b41481feb6e09db65c0b3340cf21f0c3b"
tree_hash(a, "src/nope")             = None
```

### Constraints
- Up to `3 * 10^4` files per snapshot; total contents up to a few MB
- Paths are ASCII

### What the interviewer cares about
- A real n-ary directory tree, not a binary Merkle tree over a sorted file list
- Hashing children in a **deterministic** order and including the name and kind, so renames and file/dir swaps change the hash
- Skipping equal subtrees during the diff, and handling one-sided subtrees (everything under them is added or removed)
- Talking through incremental updates: after one file changes, only the hashes on its path to the root need recomputing
