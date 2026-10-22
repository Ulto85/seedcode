from collections import deque


class RangeIterator:
    """O(1) time per call, O(1) space: just a cursor."""

    def __init__(self, start, end, step):
        self.cur, self.end, self.step = start, end, step

    def has_next(self):
        if self.step > 0:
            return self.cur <= self.end
        if self.step < 0:
            return self.cur >= self.end
        return False

    def next(self):
        if not self.has_next():
            return None
        v = self.cur
        self.cur += self.step
        return v


class ListIterator:
    def __init__(self, items):
        self.items, self.i = items, 0

    def has_next(self):
        return self.i < len(self.items)

    def next(self):
        if not self.has_next():
            return None
        self.i += 1
        return self.items[self.i - 1]


class InterleavingIterator:
    """Queue of non-empty child iterators. next() pops the front, takes one value and re-queues
    the child only if it still has elements, so dead sources are never visited again.
    O(k) construction, O(1) per call, O(k) space (ranges stay lazy)."""

    def __init__(self, sources):
        self.q = deque()
        for s in sources:
            it = RangeIterator(*s["range"]) if isinstance(s, dict) else ListIterator(s)
            if it.has_next():
                self.q.append(it)

    def has_next(self):
        return bool(self.q)

    def next(self):
        if not self.q:
            return None
        it = self.q.popleft()
        v = it.next()
        if it.has_next():
            self.q.append(it)
        return v

    def peek(self):
        if not self.q:
            return None
        it = self.q[0]
        # children are only queued while non-empty; peek a range or list without advancing
        if isinstance(it, RangeIterator):
            return it.cur
        return it.items[it.i]
