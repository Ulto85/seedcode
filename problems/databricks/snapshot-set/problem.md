---
title: Snapshot Set Iterator
difficulty: Hard
source: Databricks SWE phone screen + onsite, "SnapshotSet" / custom hashset with snapshot iterators (reported 2024–2026)
order: 2
minutes: 60
tags: design, hash map, iterator, versioning
---
Design a set of integers that can be **modified while it's being iterated**. An iterator sees the set exactly as it was
when the iterator was created; later adds and removes don't affect it.

```
SnapshotSet()
add(x: int) -> bool        # True if x was added, False if it was already present
remove(x: int) -> bool     # True if x was removed, False if it wasn't present
contains(x: int) -> bool
get_iterator() -> int      # creates a snapshot iterator and returns its id: 0, 1, 2, ... in creation order
has_next(it: int) -> bool  # does iterator `it` have more elements?
next(it: int) -> int|None  # next element of iterator `it`, or None if it is exhausted
```

Rules:
- Iterators yield the snapshot's elements in **insertion order**. If a value is removed and later re-added, it counts
  as a **new** insertion and goes to the end.
- Iterators are independent: advancing one never affects another.
- `has_next` / `next` on an iterator id that was never returned by `get_iterator` → `False` / `None`.

### Example
```
add(1), add(2), add(3)     -> True, True, True
it0 = get_iterator()       -> 0          # snapshot [1, 2, 3]
remove(2)                  -> True
add(4)                     -> True
add(1)                     -> False      # already present
next(0), next(0)           -> 1, 2       # still sees 2, doesn't see 4
it1 = get_iterator()       -> 1          # snapshot [1, 3, 4]
remove(3), add(2)          -> True, True
next(0)                    -> 3
has_next(0)                -> False
next(1), next(1), next(1)  -> 1, 3, 4
next(1)                    -> None
```

### What the interviewer cares about
- The obvious answer copies the set in `get_iterator()`: O(n) per iterator. That's the warm-up.
- The real target: `add` / `remove` / `contains` in amortized **O(1)** and `get_iterator` in **O(1) without copying**.
  Iterating a snapshot may skip over entries that were added later or removed earlier; that's fine as long as the
  total work is proportional to the log of changes. (Hint: version numbers.)
- Discussion: how would you garbage-collect history that no live iterator can see anymore?

### Constraints
- Up to 10⁵ operations. Hidden tests create many iterators on a large set, so copying per iterator times out.
- Exact method names are reconstructed from multiple candidate reports; the semantics match what's commonly asked.
