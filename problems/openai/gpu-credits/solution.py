import bisect
import heapq

ADD, SUB = 0, 1        # at equal timestamps, grants are applied before subtractions


class GPUCredits:
    """Keeps every event sorted by (timestamp, kind, seq) and an incremental replay state:
    a min-heap of live grants keyed on expiry plus their running total.
    In-order calls (Part 1): O(log n) amortized per call.
    A late event (or a query in the past) resets the replay, which then costs O(n log n)."""

    def __init__(self):
        self.events = []
        self.seq = 0
        self._reset()

    def _reset(self):
        self.done = 0          # events[:done] are applied
        self.heap = []         # [expires_at, seq, remaining]
        self.total = 0         # credits left in heap entries
        self.clock = None      # time the state reflects
        self.failed = False

    def _record(self, ev):
        i = bisect.bisect_right(self.events, ev)
        self.events.insert(i, ev)
        if i < self.done or (self.clock is not None and ev[0] < self.clock):
            self._reset()

    def add_credit(self, amount, timestamp, expiration):
        self.seq += 1
        self._record((timestamp, ADD, self.seq, amount, timestamp + expiration))

    def subtract(self, amount, timestamp):
        self.seq += 1
        self._record((timestamp, SUB, self.seq, amount, 0))

    def _expire(self, t):
        while self.heap and self.heap[0][0] <= t:
            self.total -= heapq.heappop(self.heap)[2]

    def _charge(self, amount):
        if amount > self.total:
            self.failed = True
            return
        self.total -= amount
        while amount:
            top = self.heap[0]
            take = min(amount, top[2])
            top[2] -= take
            amount -= take
            if top[2] == 0:
                heapq.heappop(self.heap)

    def get_balance(self, timestamp):
        if self.clock is not None and timestamp < self.clock:
            self._reset()
        ev = self.events
        while not self.failed and self.done < len(ev) and ev[self.done][0] <= timestamp:
            t, kind, seq, amount, expires = ev[self.done]
            self._expire(t)
            if kind == ADD:
                heapq.heappush(self.heap, [expires, seq, amount])
                self.total += amount
            else:
                self._charge(amount)
            self.done += 1
        self.clock = timestamp
        if self.failed:
            return None
        self._expire(timestamp)
        return self.total
