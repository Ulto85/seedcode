from collections import deque


class CSATTracker:
    """Queue of (timestamp, score) + running sums. Each score is evicted once -> amortized O(1)."""

    def __init__(self, window: int):
        self.window = window
        self.q = deque()
        self.total = 0
        self.satisfied = 0

    def _evict(self, t):
        while self.q and self.q[0][0] <= t - self.window:
            _, s = self.q.popleft()
            self.total -= s
            self.satisfied -= s >= 4

    def add_score(self, timestamp: int, score: int) -> None:
        self._evict(timestamp)
        self.q.append((timestamp, score))
        self.total += score
        self.satisfied += score >= 4

    def get_average(self, timestamp: int) -> float:
        self._evict(timestamp)
        return self.total / len(self.q) if self.q else 0.0

    def get_csat_percent(self, timestamp: int) -> float:
        self._evict(timestamp)
        return 100.0 * self.satisfied / len(self.q) if self.q else 0.0
