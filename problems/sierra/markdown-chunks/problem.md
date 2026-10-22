---
title: Header-Aware Markdown Chunker
difficulty: Hard
source: Sierra SWE technical screen, "Split Markdown into header-aware chunks" (reported on PracHub, 2026)
order: 3
minutes: 45
tags: strings, parsing, greedy, RAG
---
Sierra's agents answer questions from a company's help-center articles, which are written in Markdown. Before
indexing, each article is split into chunks no bigger than `max_size` characters. A chunk that starts in the middle
of a section would lose its meaning ("Step two" of *what*?), so every chunk repeats the headers it lives under.

```
split_markdown(markdown: str, max_size: int) -> list[str]
```

**Lines and headers**
- Split the input on `"\n"`. Every line is kept, blank ones included. An empty string returns `[]`.
- A **header** is a line that starts at column 0 with 1 to 6 `#` characters followed by a space (`"## Setup"`,
  `"# "`). Not headers: `"#tag"`, `"####### seven"`, `" # indented"`.
- The **active headers** are tracked as you read the document: a level-`L` header replaces the active header at
  level `L` and clears every deeper level (`L+1` to `6`).

**Building chunks (greedy)**
1. A chunk starts at the next unread line. Its **prefix** is the active headers at that point (lowest level first):
   all of them if the first line is content, or only those with level `< L` if the first line is itself a
   level-`L` header (so it isn't repeated twice). At the very start of the document nothing is active, so there's no
   prefix.
2. Then add consecutive lines for as long as the chunk still fits.
3. A chunk is its prefix lines followed by its lines, joined with `"\n"` (no trailing newline). Its size is the
   length of that string, separators and repeated headers included, and must be `<= max_size`.
4. Headers inside a chunk update the active headers for later chunks.

You may assume every line, together with its prefix, fits in `max_size` on its own.

### Example
```
markdown = "# Guide\nIntro line\n## Setup\nStep one\nStep two\n## Usage\nRun it"
split_markdown(markdown, 30) ->
[
  "# Guide\nIntro line\n## Setup",     # 27 chars; adding "Step one" would make 36
  "# Guide\n## Setup\nStep one",       # starts mid-section: repeat both headers (25)
  "# Guide\n## Setup\nStep two",       # "## Usage" would make 34
  "# Guide\n## Usage\nRun it",         # starts with a level-2 header: repeat only "# Guide"
]
split_markdown(markdown, 100) -> [markdown]      # fits whole, nothing repeated
split_markdown("", 10)        -> []
```

### Constraints
- `0 <= len(markdown) <= 2 * 10^5`, `1 <= max_size <= 2 * 10^5`

### What the interviewer cares about
- Precise header detection and hierarchy updates (a `#` header clears `##` through `######`)
- Counting size exactly: newlines and repeated headers count
- Tracking a running length rather than re-joining the chunk after every line: re-joining is quadratic when
  chunks are large
