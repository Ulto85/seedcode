class SnapshotSet:
    """Append-only log of insertions: log[i] = [value, added_at, removed_at] (removed_at = inf while live).
    Every add/remove bumps a global version. An iterator stores (version_at_creation, position in log) and yields
    entries with added_at <= v < removed_at. Entries added after the snapshot sit at the end of the log, so the
    iterator can stop at the log length it saw at creation.
    add/remove/contains/get_iterator O(1); iterating is O(1) amortized per log entry skipped."""

    INF = float("inf")

    def __init__(self):
        self.version = 0
        self.log = []          # [value, added_at, removed_at]
        self.where = {}        # live value -> index in log
        self.iters = []        # [snapshot_version, position, end]

    def add(self, x):
        if x in self.where:
            return False
        self.version += 1
        self.where[x] = len(self.log)
        self.log.append([x, self.version, self.INF])
        return True

    def remove(self, x):
        i = self.where.pop(x, None)
        if i is None:
            return False
        self.version += 1
        self.log[i][2] = self.version
        return True

    def contains(self, x):
        return x in self.where

    def get_iterator(self):
        self.iters.append([self.version, 0, len(self.log)])
        return len(self.iters) - 1

    def _advance(self, state):
        v, pos, end = state
        while pos < end and not (self.log[pos][1] <= v < self.log[pos][2]):
            pos += 1
        state[1] = pos
        return pos < end

    def has_next(self, it):
        if not 0 <= it < len(self.iters):
            return False
        return self._advance(self.iters[it])

    def next(self, it):
        if not self.has_next(it):
            return None
        state = self.iters[it]
        value = self.log[state[1]][0]
        state[1] += 1
        return value
