from bisect import bisect_right

_MISSING = object()


class KVStore:
    """Part 1: one live dict plus an undo log per open transaction.
    get/set/delete/begin: O(1). commit/rollback: O(keys changed in that transaction)."""

    def __init__(self):
        self.data = {}
        self.undo = []                 # stack of {key: value before this txn first touched it}

    def _record(self, key):
        if self.undo and key not in self.undo[-1]:
            self.undo[-1][key] = self.data.get(key, _MISSING)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self._record(key)
        self.data[key] = value

    def delete(self, key):
        if key not in self.data:
            return False
        self._record(key)
        del self.data[key]
        return True

    def begin(self):
        self.undo.append({})

    def commit(self):
        if not self.undo:
            return False
        log = self.undo.pop()
        if self.undo:
            parent = self.undo[-1]
            for k, old in log.items():
                parent.setdefault(k, old)      # the parent's older "before" value wins
        return True

    def rollback(self):
        if not self.undo:
            return False
        for k, old in self.undo.pop().items():
            if old is _MISSING:
                self.data.pop(k, None)
            else:
                self.data[k] = old
        return True


class OCCStore:
    """Follow-up: snapshot reads via per-key version history (MVCC) + optimistic validation at commit.
    get: O(log versions of that key). set/delete/begin/rollback: O(1).
    commit: O(|read set| + |write set|). Space: O(total committed writes)."""

    def __init__(self):
        self.version = 0
        self.history = {}              # key -> ([versions], [values]); value None = deleted
        self.txns = {}                 # id -> [start_version, writes dict, read set]
        self.next_id = 1

    def _at(self, key, version):
        h = self.history.get(key)
        if not h:
            return None
        i = bisect_right(h[0], version) - 1
        return h[1][i] if i >= 0 else None

    def begin(self):
        tid = self.next_id
        self.next_id += 1
        self.txns[tid] = [self.version, {}, set()]
        return tid

    def get(self, txn, key):
        t = self.txns.get(txn)
        if t is None:
            return None
        if key in t[1]:
            return t[1][key]
        t[2].add(key)
        return self._at(key, t[0])

    def set(self, txn, key, value):
        t = self.txns.get(txn)
        if t is None:
            return False
        t[1][key] = value
        return True

    def delete(self, txn, key):
        return self.set(txn, key, None)

    def commit(self, txn):
        t = self.txns.pop(txn, None)
        if t is None:
            return False
        start, writes, reads = t
        for key in reads | writes.keys():
            h = self.history.get(key)
            if h and h[0][-1] > start:
                return False
        self.version += 1
        for key, value in writes.items():
            h = self.history.setdefault(key, ([], []))
            h[0].append(self.version)
            h[1].append(value)
        return True

    def rollback(self, txn):
        return self.txns.pop(txn, None) is not None

    def read(self, key):
        return self._at(key, self.version)
