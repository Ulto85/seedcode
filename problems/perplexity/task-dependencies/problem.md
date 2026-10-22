---
title: Task Dependencies and Failure
difficulty: Medium
source: Perplexity SWE technical screen, "task dependencies and failure" / "task list with dependencies" (reported 2025–2026). Part 1 follows the report; the Follow-up is reconstructed from the related "dependency-aware to-do list" report.
order: 1
minutes: 45
tags: design, graph, BFS, hash map
---
Perplexity's AI workflows run as many small **tasks** that depend on each other: a step that summarizes search
results can't run until the searches finish, and if a search fails, everything downstream of it is useless.
Build the in-memory task manager.

If task `A` depends on task `B`, then `B` is a **dependency** of `A` and `A` is a **dependent** of `B`.

### Part 1
```
TaskManager()
add_task(task_id) -> None
add_dependency(task_id, dependency_id) -> None    # task_id depends on dependency_id
fail_task(task_id) -> None
get_status(task_id) -> str                         # "active" | "failed" | "not_found"
```

- `add_task(t)` creates `t` with status `"active"`. Adding a task that already exists does nothing.
- `add_dependency(t, d)` records that `t` depends on `d`. Either task is created (as `"active"`) first if it
  doesn't exist yet. Adding the same edge twice has no extra effect. If `d` is **already failed**, `t` fails right
  away, and that failure cascades like a `fail_task`.
- `fail_task(t)` creates `t` if needed, marks it `"failed"`, and fails **every task that depends on it, directly
  or transitively**. A task that is already failed stays failed.
- `get_status(t)` returns `"not_found"` if `t` was never created or mentioned by any call.
- The graph can contain **cycles** (including a task depending on itself) and shared descendants. Every task must
  be failed and processed at most once, even if it's reachable along many paths.

### Example
```
add_dependency("B", "A")     # B depends on A (both created)
add_dependency("C", "B")     # C depends on B
add_dependency("D", "B")
add_dependency("D", "C")     # D depends on B and C (a diamond)
add_task("E")
fail_task("A")               # A fails -> B -> C and D, D only once
get_status("D") -> "failed"
get_status("E") -> "active"
add_dependency("F", "C")     # C is already failed, so F fails immediately
get_status("F") -> "failed"
get_status("Z") -> "not_found"
```

### Follow-up: completing tasks
Tasks can now also finish successfully, with status `"done"`.
```
complete_task(task_id) -> bool
get_ready() -> list[str]
```
- `complete_task(t)` succeeds (returns `True`) only if `t` exists, is `"active"`, and **every** one of its
  dependencies is `"done"`. Otherwise it returns `False` and changes nothing.
- `get_ready()` returns every `"active"` task whose dependencies are all `"done"` (a task with no dependencies is
  ready), sorted in ascending string order. A task in a dependency cycle is never ready.
- A `"done"` task **never changes status again**:
  - `fail_task` on a done task does nothing (and fails nothing else).
  - A failure cascade does not fail a done dependent, and does **not** continue through it to its dependents.
  - `add_dependency(t, d)` where `t` is done still records the edge, but `t` stays done.
- `get_status` can now also return `"done"`.

```
add_dependency("B", "A")
get_ready()          -> ["A"]
complete_task("B")   -> False     # A isn't done yet
complete_task("A")   -> True
get_ready()          -> ["B"]
fail_task("A")                    # A is done: nothing happens
get_status("B")      -> "active"
```

### Constraints
- Task ids are non-empty strings of at most 50 characters.
- Up to `2 * 10^5` calls; distinct tasks plus distinct edges total at most `2 * 10^5`.
- Chains can be tens of thousands of tasks long.

### What the interviewer cares about
- Storing edges in **both** directions so a cascade only walks dependents
- An iterative BFS/DFS that skips tasks that are already failed. Re-walking failed subtrees, or recursing
  50,000 levels deep, is what times out (this is the reported reason candidates were rejected)
- Precise handling of the edge cases: duplicate edges, unknown ids, cycles, failing an already-failed task
