---
title: cd With Symbolic Links
difficulty: Medium
source: OpenAI SWE technical phone screen, "implement cd" (reported 2024–2026; symlink rules reconstructed)
order: 0
minutes: 45
tags: strings, stack, recursion, cycle detection
---
Implement the shell's `cd`: given the current directory and the argument the user typed, return the absolute
directory you end up in.

```
cd(cwd: str, path: str, links: dict[str, str]) -> str | None
```

- `cwd` is an absolute, already-normalized path (`/` or `/a/b`, no trailing slash, no `.`/`..`, no links in it).
- `path` is what the user typed. If it starts with `/` it is **absolute** (start from `/`); otherwise it is
  **relative** to `cwd`.
- Walk `path` one component at a time (components are separated by `/`):
  - empty components (from `//` or a trailing `/`) and `.` do nothing
  - `..` moves to the parent directory; `..` at `/` stays at `/`
  - any other name moves into that child directory
- Return the result as a normalized absolute path: starts with `/`, no trailing slash (except `/` itself), no `.`,
  `..` or empty components. The directories don't need to exist; you're only manipulating strings.

### Example (Part 1, no links)
```
cd("/foo/bar", "baz", {})            -> "/foo/bar/baz"
cd("/foo/bar", "../baz/./qux", {})   -> "/foo/baz/qux"
cd("/foo/bar", "/x//y/", {})         -> "/x/y"
cd("/", "../../a", {})               -> "/a"
```

### Follow-up: symbolic links
`links` maps a **link path** to its **target**. Both are absolute, normalized paths, and a link path is never `/`.
- After you move into a child directory, if the full path you are at is a key in `links`, you are redirected:
  resolve the target (from `/`, by the same rules, so links inside the target are followed too) and continue from
  there.
- `..` always means the parent of where you **actually** are after redirects (like `cd -P`), not the parent of the
  link's name.
- **Cycles:** if resolving a link requires resolving that same link again before it finishes (`/a -> /b`,
  `/b -> /a`, or `/a -> /a/x`), return `None`. Using the same link twice *in sequence* is fine: with
  `{"/a/up": "/a"}`, `cd("/", "a/up/up", ...)` is `"/a"`.

```
links = {"/home/me": "/data/users/me", "/data/users/me/tmp": "/tmp", "/loop1": "/loop2", "/loop2": "/loop1"}
cd("/", "home/me/docs", links)      -> "/data/users/me/docs"
cd("/home", "me/..", links)         -> "/data/users"     # .. is applied after the redirect
cd("/", "home/me/tmp/x", links)     -> "/tmp/x"          # links are checked again after a redirect
cd("/", "loop1", links)             -> None
cd("/", "home/meh", links)          -> "/home/meh"       # only whole components match
```

### Constraints
- `path` has up to `10^5` components; `links` has up to `5 * 10^4` entries
- The resolved directory is never deeper than 100 components; a link's target never redirects through more than 100
  nested links before it either finishes or cycles
- Names contain only letters, digits, `_` and `-`

### What the interviewer cares about
- A clean stack-based walk for Part 1 (this part should take ~10 minutes)
- Looking links up in a hash map per step, not scanning every link for every component
- Telling a real cycle apart from re-using a link, and explaining why a global "visited" set gets that wrong
