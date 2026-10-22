import heapq
from collections import defaultdict, deque

VALUE = {"UP": 1, "DOWN": -1}


class VoteTracker:
    """vote / get_last_votes / score: O(1).  top_article: amortized O(log n) via a lazy max-heap.
    Space O(#user-article pairs + #votes) (the heap holds one entry per counted vote until popped)."""

    def __init__(self):
        self.latest = {}                                   # (user, article) -> "UP" | "DOWN"
        self.recent = defaultdict(lambda: deque(maxlen=3))  # user -> last 3 counted votes
        self.events = 0
        self.scores = {}                                   # article -> score (only voted articles)
        self.heap = []                                     # (-score, article), possibly stale

    def vote(self, user_id, article_id, vote):
        key = (user_id, article_id)
        prev = self.latest.get(key)
        if prev == vote:
            return "DUPLICATE"
        self.latest[key] = vote
        self.events += 1
        self.recent[user_id].append([article_id, vote, self.events])
        delta = VALUE[vote] - (VALUE[prev] if prev else 0)
        self.scores[article_id] = self.scores.get(article_id, 0) + delta
        heapq.heappush(self.heap, (-self.scores[article_id], article_id))
        return "NEW" if prev is None else "FLIP"

    def get_last_votes(self, user_id):
        if user_id not in self.recent:
            return []
        return [list(e) for e in reversed(self.recent[user_id])]

    def score(self, article_id):
        return self.scores.get(article_id, 0)

    def top_article(self):
        while self.heap:
            neg, article = self.heap[0]
            if -neg == self.scores[article]:
                return article
            heapq.heappop(self.heap)                       # stale entry
        return None
