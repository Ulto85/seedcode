---
title: Transactional Key-Value Store
difficulty: Hard
source: Cursor SWE technical screen, "Design an in-memory transactional key-value store" (reported 2026; begin/get/set/commit/rollback plus handling conflicting concurrent writes). The exact APIs and conflict rule below are reconstructed.
order: 4
minutes: 60
tags: design, transactions, undo log, MVCC, optimistic concurrency
---
Build an in-memory key-value store with transactions. Keys and values are strings.

### Part 1: nested transactions (one client)
```
KVStore()
get(key) -> str | None        # None if the key doesn't exist
set(key, value) -> None
delete(key) -> bool           # True if the key existed and was removed; False (no-op) if it didn't exist
begin() -> None               # open a transaction; transactions nest
commit() -> bool              # close the innermost transaction, keeping its changes; False if none is open
rollback() -> bool            # close the innermost transaction, undoing its changes; False if none is open
```
- Reads always see every change made so far, including those in open transactions.
- Committing an inner transaction folds its changes into the enclosing one: they are still undone if the outer
  transaction rolls back. Committing the outermost transaction makes changes permanent.
- `rollback` restores every key the transaction touched to exactly what it was when the transaction began
  (including deleting keys it created and restoring keys it deleted).

```
set("a", "base")
begin(); set("a", "outer")
begin(); set("a", "inner"); set("b", "new")
commit()         -> True        # inner folded into outer
get("a")         -> "inner"
rollback()       -> True        # undoes the outer transaction, including what the inner one did
get("a")         -> "base"
get("b")         -> None
commit()         -> False       # nothing open
```
`begin`, `get`, `set` and `delete` should be O(1) regardless of how deep the nesting is or how big the store is;
`commit`/`rollback` should cost O(keys changed in that transaction), not O(store size).

### Follow-up: concurrent transactions
Now many agents use the store at once. Each transaction gets an id and sees a **snapshot**; conflicts are detected
**optimistically** at commit.
```
OCCStore()
begin() -> int                       # ids are 1, 2, 3, ... in order of begin()
get(txn, key) -> str | None
set(txn, key, value) -> bool
delete(txn, key) -> bool
commit(txn) -> bool
rollback(txn) -> bool
read(key) -> str | None              # latest committed value, outside any transaction
```
- **Active** = begun and not yet committed or rolled back. Any call with an id that isn't active does nothing and
  returns `None` (`get`) or `False` (all others).
- `get` returns the transaction's own latest write to that key if it has one (a delete reads as `None`); otherwise
  the committed value **as of the moment the transaction began**. Later commits by others are invisible to it.
- `set`/`delete` only buffer the change in the transaction and return `True` (`delete` returns `True` even if the key
  doesn't exist). Nothing is visible to others until commit.
- `commit(txn)` **fails** (returns `False`) if any key the transaction **read** with `get` (served from the snapshot,
  including reads that returned `None`) or **wrote** was written by another transaction that committed after
  `txn` began. Otherwise it applies all writes atomically and returns `True`. Either way the transaction is no longer
  active. A transaction with no reads and no writes always commits.
- `rollback(txn)` discards the transaction and returns `True`.

```
begin() -> 1;  begin() -> 2
set(1, "x", "a") -> True
set(2, "x", "b") -> True
commit(1) -> True
commit(2) -> False      # x was committed by txn 1 after txn 2 began: first committer wins
read("x") -> "a"
```

### Constraints
- Up to `10^5` operations; nesting depth up to `10^4`
- Many transactions may be open at once; a transaction may stay open across thousands of others' commits

### What the interviewer cares about
- Part 1: an undo log (or a stack of change sets) per transaction instead of copying the whole store at `begin`
- Getting nested commit right: the outer transaction must still be able to undo what an inner one committed
- Follow-up: snapshot reads without copying (per-key version history), and a clear conflict rule. Be ready to
  compare optimistic vs pessimistic (locking) concurrency control, and explain why validating the **read set** too
  (not just write-write conflicts) prevents anomalies like write skew
