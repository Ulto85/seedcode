---
title: Document Vault with Duplicate Names
difficulty: Medium
source: Harvey SWE technical screen / onsite, "constrained in-memory file system" and "file vault with duplicate-name handling" (reported 2025–2026; rules from the public write-ups, return values reconstructed)
order: 2
minutes: 45
tags: design, trie, strings, file system
---
Harvey's **Vault** lets lawyers drop thousands of documents into folders. Uploads never fail just because a file
with the same name exists: the new file gets a numbered name instead. Build the in-memory vault.

```
FileVault(max_children=None)
add_file(path: str) -> str
list_entries(path: str) -> list[str]
```

**Paths**
- A valid path is absolute: it starts with `/`, and its segments are separated by single `/`. `"/"` is the root.
- Invalid: anything not starting with `/`, an empty segment (`"/a//b"`), a trailing slash (`"/a/"`, but `"/"`
  itself is fine), or a `.` or `..` segment. Any other characters are allowed in a segment, and names are
  case-sensitive.

**`add_file(path)`** adds a file. The last segment is the file name; every earlier segment is a directory.
- Missing directories along the way are **created automatically**.
- If the parent directory already has a child (file **or** directory) with the requested name, the new file is
  renamed by inserting `(k)` **before the extension**, using the smallest positive `k` whose name is free.
  The extension is everything from the **last** `.` on, unless that dot is the first character of the name:

  | requested | 1st duplicate | why |
  |---|---|---|
  | `file.txt` | `file(1).txt` | |
  | `archive.tar.gz` | `archive.tar(1).gz` | only the last dot |
  | `.env` | `.env(1)` | leading dot is not an extension |
  | `README` | `README(1)` | no dot |

  Existing parentheses are plain text: a clash on `file(1).txt` tries `file(1)(1).txt`.
- Returns the **full path actually created** (e.g. `"/d/file(1).txt"`).
- Rejected (returns `""` and changes **nothing**, including not creating any directories) if the path is
  invalid, is `"/"`, or one of its directory segments already exists as a **file**.

**`list_entries(path)`** returns the names of the immediate children (files and directories) of the directory at
`path`, sorted lexicographically (plain string order). Returns `[]` if the path is invalid, missing, or a file.

Files are never deleted or renamed after creation.

### Example
```
v = FileVault()
v.add_file("/deals/acme/nda.pdf")        -> "/deals/acme/nda.pdf"     # creates /deals and /deals/acme
v.add_file("/deals/acme/nda.pdf")        -> "/deals/acme/nda(1).pdf"
v.add_file("/deals/acme/nda(1).pdf")     -> "/deals/acme/nda(1)(1).pdf"
v.add_file("/deals/acme/nda.pdf")        -> "/deals/acme/nda(2).pdf"
v.list_entries("/deals/acme")            -> ["nda(1)(1).pdf", "nda(1).pdf", "nda(2).pdf", "nda.pdf"]
v.add_file("/deals/acme/nda.pdf/x.txt")  -> ""                         # nda.pdf is a file
v.add_file("/deals")                     -> "/deals(1)"                # "deals" is taken by a directory
v.list_entries("/")                      -> ["deals", "deals(1)"]
```

### Part 1
Implement the class with no capacity limit (`max_children` is `None`). Clients bulk-upload the same file name
thousands of times into one folder, so finding the next free suffix must not rescan `(1), (2), …` from scratch
on every upload.

### Follow-up: folder capacity
When `max_children` is an integer (`>= 1`), no directory may ever hold more than `max_children` immediate
children. If an `add_file` would push **any** directory over the limit, reject the whole operation: return `""`
and leave the vault unchanged (no partially created directories). The root counts as a directory.
```
v = FileVault(2)
v.add_file("/a.txt")      -> "/a.txt"
v.add_file("/a.txt")      -> "/a(1).txt"
v.add_file("/b/c.txt")    -> ""          # root would get a 3rd child "b"
v.add_file("/a.txt/x")    -> ""          # a.txt is a file
v.list_entries("/")       -> ["a(1).txt", "a.txt"]
```

### Constraints
- Up to `5 * 10^4` calls; paths up to 200 characters

### What the interviewer cares about
- A tree (trie) of directory nodes rather than string-prefix scans over every stored path
- Validating everything **before** mutating, so a rejected call has no side effects
- Tracking the next candidate suffix per (directory, name) so repeated uploads stay fast (safe because nothing is
  ever deleted)
