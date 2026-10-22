---
title: Dependency-Aware Task Scheduler
difficulty: Medium
source: Scale AI SWE / new-grad technical screen, "TaskManager" (reported repeatedly, 2026)
order: 1
minutes: 45
tags: design, heap, topological sort
---
You're building the scheduler that hands work to Scale's workers. Tasks stream in over time, and workers repeatedly
ask "what should I run next?".

A task is `[task_id, deadline, prereqs]`:
- `task_id`: a unique integer
- `deadline`: an integer (can be negative). **Smaller = more urgent.**
- `prereqs`: a list of task ids that must be **consumed** before this task can run (Part 1 tests always pass `[]`)

```
TaskManager()
add_tasks(tasks: list[list]) -> None      # add one or more tasks; may be called many times
consume_task() -> int | None              # remove and return the next task id, or None if nothing can run
```

### Part 1: deadline order
Ignore prerequisites. `consume_task()` returns the task with the **smallest deadline**; ties go to the **smaller
`task_id`**. A consumed task is gone for good. If no tasks are waiting, return `None` (and keep working: tasks added
later can still be consumed).

```
add_tasks([[101, 5, []], [102, 2, []], [103, 8, []]])
consume_task() -> 102
add_tasks([[104, 2, []], [99, 5, []]])
consume_task() -> 104
consume_task() -> 99         # tie on deadline 5: 99 < 101
consume_task() -> 101
consume_task() -> 103
consume_task() -> None
```

### Follow-up: prerequisites
Now honour `prereqs`. A task is **ready** only when every prerequisite has already been returned by
`consume_task()`. Among ready tasks, pick by (deadline, task_id) exactly as before. If no task is ready (even if some
are blocked), return `None`.

- A prerequisite may refer to a task that **hasn't been added yet**: the task stays blocked until that prerequisite is
  added *and* consumed.
- A prerequisite may refer to a task that was **already consumed**: that prerequisite is already satisfied.
- Duplicate ids inside one `prereqs` list count once. The dependency graph never has cycles and ids are never reused.

```
add_tasks([[1, 9, []], [2, 1, [1]], [3, 4, []]])
consume_task() -> 3          # 2 is more urgent but blocked by 1
consume_task() -> 1
consume_task() -> 2          # unlocked once 1 was consumed
add_tasks([[5, 0, [4]]])
consume_task() -> None       # 5 waits for task 4, which doesn't exist yet
add_tasks([[4, 7, [1]]])     # 1 is already consumed, so 4 is ready immediately
consume_task() -> 4
consume_task() -> 5
```

### What the interviewer cares about
- Part 1 should be a min-heap, not a scan of every waiting task on each call.
- Follow-up: per-task count of unmet prerequisites plus a "who's waiting on me" map (Kahn's algorithm, but online).
  Each call should be about O(log n) amortized; a full rescan of blocked tasks is too slow for the hidden tests.

### Constraints
- Up to 10⁵ tasks and 2·10⁵ prerequisite links in total; up to 2·10⁵ calls.
- -10⁹ ≤ deadline ≤ 10⁹

*The three Scale AI reports (TaskManager / Task Processor / Schedule Ready Tasks by Deadline) describe the same core
idea; the exact method names and the online "prereq added later" rule here are a reconstruction that combines them.*
