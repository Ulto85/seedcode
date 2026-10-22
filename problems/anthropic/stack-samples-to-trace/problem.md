---
title: Stack Samples to Trace Events
difficulty: Medium
source: Anthropic SWE phone screen / onsite, "profiler sampling" (most reported, 2025-2026)
order: 1
minutes: 45
tags: stack, simulation, profiling
---
A **sampling profiler** pauses a program at regular intervals and records the current call stack. You get those
samples in time order and must turn them into a trace of `start` / `end` events, the way a trace viewer like
Chrome's `about:tracing` expects.

```
samples: list[[ts, stack]]     # ts is a number, stack is a list of function names, OUTERMOST first
```

### Part 1
```
convert_to_trace(samples) -> list[[kind, ts, name]]     # kind is "start" or "end"
```

Assume the stack only changes **at** a sample. So between two consecutive samples `prev` and `cur` (taken at time `ts`):

- Frames are matched **by position**, from the outermost frame. The calls that keep running are the longest common
  prefix of `prev` and `cur`: frame `i` is the same call only if `prev[j] == cur[j]` for **every** `j <= i`.
- Every frame of `prev` past that prefix has **ended** at `ts`; every frame of `cur` past it has **started** at `ts`.
- At one timestamp, emit all `end` events first, **innermost first**, then all `start` events, **outermost first**.
- A name can appear several times in one stack (recursion). `["a", "b", "a"]` is three different calls.
- Calls still on the stack in the **last** sample have not finished: emit **no** `end` event for them.
- A sample may have an empty stack (the program was idle): everything still open ends there.
- Two identical consecutive stacks produce no events.

### Example
```
samples = [[0, ["main"]],
           [1, ["main", "a"]],
           [2, ["main", "a", "b"]],
           [3, ["main", "c"]],
           [4, []]]

-> [["start", 0, "main"],
    ["start", 1, "a"],
    ["start", 2, "b"],
    ["end", 3, "b"], ["end", 3, "a"], ["start", 3, "c"],
    ["end", 4, "c"], ["end", 4, "main"]]
```
At `t=3` the common prefix is just `["main"]`: `a` is replaced by `c` at depth 1, so `b` and then `a` end before `c`
starts. `main` never ends inside the samples until the idle sample at `t=4`.

Also: `[[0, ["a", "b"]], [1, ["c", "b"]]]` ends **both** frames and starts both again. The `b` at depth 1 is a new
call because its caller changed.

### Follow-up: de-noising
Samples are noisy: a function that shows up in a single sample is often not worth showing. Implement
```
convert_to_trace_min(samples, n) -> list[[kind, ts, name]]
```
A **call** (a frame, as identified in Part 1) is observed in some number of consecutive samples. Drop every call
observed in **fewer than `n`** samples: it produces no `start` and no `end` event. All other events are emitted
exactly as in Part 1 (same timestamps, same ordering). A call that is still open after the last sample is kept if it
was observed in at least `n` samples (and still gets no `end` event).

With the example above and `n = 2`: `main` is seen in 4 samples, `a` in 2, `b` in 1 and `c` in 1, so
```
-> [["start", 0, "main"], ["start", 1, "a"], ["end", 3, "a"], ["end", 4, "main"]]
```
(A callee is never seen in more samples than its caller, so dropping calls never orphans a kept child.)
`n <= 1` keeps everything and equals Part 1.

### Constraints
- `0 <= len(samples) <= 10^5`, timestamps are non-decreasing, total number of frames across all samples `<= 2 * 10^6`.
- Function names are non-empty strings.

*The input/output shapes are reconstructed from several candidate reports (the original was posed with a `Sample`
struct and `Event` objects; here they are plain lists so tests are JSON).*
