from bisect import bisect_right


class VersionedKV:
    """Per-key append-only history (timestamps arrive non-decreasing, so appends keep it sorted)
    plus a global stack of every kept mutation for restore.

    set/delete: O(1). get: O(log h). get_range: O(log h + m) for m mutations in the range.
    restore: amortized O(1) per discarded mutation (each mutation is pushed and popped once).
    Space: O(total mutations kept).
    """

    def __init__(self):
        self.times = {}     # key -> [ts, ...]          non-decreasing
        self.vals = {}      # key -> [value | None, ...] None = delete
        self.log = []       # (ts, key) for every kept mutation, in order

    def _write(self, key, value, ts):
        self.times.setdefault(key, []).append(ts)
        self.vals.setdefault(key, []).append(value)
        self.log.append((ts, key))

    def set(self, key: str, value, ts: int) -> None:
        self._write(key, value, ts)

    def delete(self, key: str, ts: int) -> None:
        self._write(key, None, ts)

    def get(self, key: str, ts: int):
        times = self.times.get(key)
        if not times:
            return None
        i = bisect_right(times, ts)
        return self.vals[key][i - 1] if i else None

    def get_range(self, key: str, start: int, end: int) -> list:
        if start > end:
            return []
        times, vals = self.times.get(key, []), self.vals.get(key, [])
        i = bisect_right(times, start)
        prev = vals[i - 1] if i else None
        out = [[start, prev]] if prev is not None else []
        j = i
        while j < len(times) and times[j] <= end:
            t = times[j]
            while j + 1 < len(times) and times[j + 1] == t:   # the last write at t wins
                j += 1
            if vals[j] != prev:
                out.append([t, vals[j]])
                prev = vals[j]
            j += 1
        return out

    # ---- Follow-up ----
    def restore(self, ts: int) -> None:
        while self.log and self.log[-1][0] > ts:
            _, key = self.log.pop()
            self.times[key].pop()
            self.vals[key].pop()
