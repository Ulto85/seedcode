---
title: Streaming Code Fence Parser
difficulty: Medium
source: Cursor SWE technical screen, "Build a streaming Markdown code fence parser" (reported 2026). Only the title and theme are public; the event format and exact rules below are reconstructed.
order: 2
minutes: 45
tags: streaming, state machine, parsing
---
The chat panel renders the model's answer **while it streams**. Code blocks need to become syntax-highlighted editors
as soon as they start, so you need a parser that turns the stream into structured events. The model's output arrives
in chunks that split text anywhere: in the middle of a word, a line, or a ```` ``` ```` fence.

```
FenceParser()
feed(chunk: str) -> list[event]     # events completed by this chunk, in order
finish() -> list[event]             # end of stream: flush whatever is left
```

### Events
```
["text", line]      a line of prose (outside any code block)
["open", lang]      a code block starts; lang is "" if none was given
["code", line]      a line inside a code block
["close"]           the code block ends
```
`line` never includes the `"\n"`.

### Rules
- The parser works **line by line**. A line ends at `"\n"`. `feed` emits events only for lines that are complete
  (their `"\n"` has arrived); a partial line is held until it completes or until `finish()`.
- `finish()` processes the leftover partial line, if it's non-empty (a stream ending in `"\n"` has no extra empty
  line). Then, if a code block is still open, it emits `["close"]`. `feed` is never called after `finish`.
- An empty line is a normal line: `["text", ""]` or `["code", ""]`.

### Part 1: backtick fences
- **Opening fence** (only outside a code block): the line **starts** with 3 or more backticks (no leading spaces).
  The rest of the line is the info string; `lang` is its first whitespace-separated word, or `""`.
- **Closing fence** (only inside a code block): after removing trailing spaces, the line consists only of backticks,
  and at least as many as the opening fence. Anything else inside a block, including ```` ```python ````, a shorter
  run of backticks or an indented fence, is just a `code` line.

### Example
```
p = FenceParser()
p.feed("Here is the fix:\n``")                -> [["text", "Here is the fix:"]]
p.feed("`py")                                 -> []
p.feed("thon\ndef add(a, b):\n    return a + b\n")
                                              -> [["open", "python"], ["code", "def add(a, b):"],
                                                  ["code", "    return a + b"]]
p.feed("``")                                  -> []
p.feed("`\nDone")                             -> [["close"]]
p.feed("!")                                   -> []
p.finish()                                    -> [["text", "Done!"]]
```

### Follow-up: tildes and info strings
Models sometimes emit `~~~` fences. Extend the parser:
- A line starting with 3 or more `~` also opens a block (same `lang` rule).
- A block is closed only by a fence of the **same character**: inside a `~~~` block a ```` ``` ```` line is code,
  and vice versa. The length rule is unchanged (at least as many as the opener).
- A **backtick** opening fence's info string may not contain a backtick: ```` ```js` ```` is a `text` line.
  A tilde fence's info string may contain anything.

### Constraints
- Total streamed text up to ~`5 * 10^5` characters, in up to `3 * 10^4` chunks; a single line can be very long
- Only `"\n"` ends a line (no `"\r"`)

### What the interviewer cares about
- A small, explicit state machine (outside / inside a fence of char `c` and length `k`)
- Never re-scanning text you've already processed: total work should be linear in the stream, however it's chunked
- Delimiters split across chunks, unterminated blocks and the final line without `"\n"`
- Discussing what you'd change to show code **before** its line completes (lower latency) and how you'd bound the
  buffer for a pathological never-ending line
