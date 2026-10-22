---
title: GPU Task Placement
difficulty: Medium
source: In the style of the "multi-dimensional GPU/CPU/memory allocator with a stated fit policy" and "scheduling primitive" themes that prep guides attribute to Modal's coding rounds (unverified, no first-hand report found). Not a reported question.
order: 4
minutes: 50
tags: design, bin packing, best fit, bisect, queue
---
Modal's scheduler places function calls onto a fleet of GPU hosts. Every host has some number of GPUs and some
GiB of memory. Every task asks for a number of GPUs and some memory, and holds them until it is released.
Build the placement logic.

```
GpuCluster(hosts: list[[gpus, mem]])        # host i has hosts[i][0] GPUs and hosts[i][1] GiB
place(task_id: str, gpus: int, mem: int) -> int
release(task_id: str) -> bool
host_of(task_id: str) -> int | None
```

### Part 1: best fit
- `place` puts the task on a host with **at least** `gpus` free GPUs **and** at least `mem` free GiB, and returns
  the host's index. If no host fits right now, return `-1` and change nothing.
- **Best fit:** choose the fitting host that will have the **fewest free GPUs** left after placing the task. Ties:
  the one with the **least free memory** left, then the **lowest index**. (GPUs are the scarce resource, so we
  pack them tightly and keep big hosts free for big jobs.)
- `release` frees the task's GPUs and memory and returns `True`, or returns `False` if the task isn't running
  (never placed, failed to place, or already released).
- `host_of` returns the host index of a running task, or `None` if it isn't running.
- Task ids are never reused: every `place` (and, in the follow-up, `submit`) call uses a brand-new id.

```
c = GpuCluster([[8, 512], [4, 256], [2, 64]])
c.place("t1", 2, 32)    -> 2     # all three fit; host 2 is left with 0 free GPUs
c.place("t2", 1, 300)   -> 0     # only host 0 has 300 GiB
c.place("t3", 4, 100)   -> 1     # host 1 is left with 0 free GPUs, host 0 would have 3
c.place("t4", 4, 250)   -> -1    # host 0 has 7 GPUs but only 212 GiB free
c.release("t2")         -> True
c.place("t4", 4, 250)   -> 0
c.host_of("t3")         -> 1
c.host_of("t2")         -> None
c.release("t2")         -> False
```

### Follow-up: queue what doesn't fit
Requests that don't fit shouldn't be dropped. They should wait.
```
submit(task_id: str, gpus: int, mem: int) -> int
pending() -> list[str]
```
- `submit` places the task immediately if it fits (same best-fit rule, even if other tasks are waiting) and
  returns the host index. Otherwise:
  - if **no host could ever fit it**, even completely empty, return `-2` and don't queue it;
  - else append it to a FIFO wait queue and return `-1`.
- Whenever `release` frees a **running** task, scan the queue from oldest to newest and place **every** waiting
  task that now fits, using best fit and the resources left by the placements made earlier in the same scan.
  Tasks that still don't fit keep their place in the queue.
- `release` on a **queued** task cancels it (removes it from the queue) and returns `True`. That frees nothing,
  so no scan happens.
- `host_of` returns `-1` for a queued task. `pending` returns the queued task ids, oldest first.
- `place` keeps its Part 1 behaviour (never queues).

```
c = GpuCluster([[4, 100], [2, 100]])
c.submit("a", 4, 50)   -> 0
c.submit("b", 2, 80)   -> 1
c.submit("c", 2, 10)   -> -1     # queued
c.submit("d", 4, 10)   -> -1     # queued
c.submit("e", 1, 500)  -> -2     # no host has 500 GiB, ever
c.submit("f", 1, 10)   -> -1     # queued
c.pending()            -> ["c", "d", "f"]
c.release("b")         -> True   # host 1 frees up: c goes there; d and f still don't fit
c.pending()            -> ["d", "f"]
c.release("a")         -> True   # host 0 frees up: d takes all 4 GPUs; f still waits
c.host_of("d")         -> 0
c.host_of("f")         -> -1
c.release("f")         -> True   # cancelled while queued
c.pending()            -> []
```

### Constraints
- `1 <= len(hosts) <= 10^4`, each host has `1..8` GPUs and `1..2048` GiB
- `1 <= gpus <= 16`, `0 <= mem <= 4096` per task
- Up to `10^5` calls. A linear scan over every host on every `place` is too slow for the larger hidden tests.
  Hint: there are at most 9 possible "free GPU" counts.

### What the interviewer cares about
- Stating the fit policy and tie-breaks precisely, and checking **both** dimensions
- An index that makes best fit fast: bucket hosts by free GPUs, keep each bucket sorted by free memory, and
  binary search for the first host with enough memory
- In the follow-up: why a big task at the head of the queue shouldn't block small ones (backfilling), and what
  that does to the big task (starvation). How would you fix it?
