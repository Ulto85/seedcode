from collections import deque


class ConversationHistory:
    """Messages are grouped into droppable units kept in a deque (oldest first), plus pinned
    system messages. A running total makes every add O(1) amortized (each message is
    dropped at most once); context() is O(size of the history)."""

    def __init__(self, limit: int):
        self.limit = limit
        self.units = deque()      # each unit: [list of message seqs, token total]
        self.pinned = 0           # tokens held by system messages
        self.total = 0            # all tokens in the history
        self.alive = {}           # seq -> id, insertion-ordered
        self.seq = 0

    def _store(self, msg_id):
        self.seq += 1
        self.alive[self.seq] = msg_id
        return self.seq

    def _compact(self):
        dropped = 0
        while self.total > self.limit:
            seqs, tokens = self.units.popleft()   # never the newest unit (caller checked it fits)
            self.total -= tokens
            for s in seqs:
                del self.alive[s]
            dropped += len(seqs)
        return dropped

    def add(self, msg_id: str, role: str, tokens: int) -> int:
        if role == "system":
            if self.pinned + tokens > self.limit:
                return -1
            self._store(msg_id)
            self.pinned += tokens
        elif role == "tool" and self.units:
            unit = self.units[-1]
            if self.pinned + unit[1] + tokens > self.limit:
                return -1
            unit[0].append(self._store(msg_id))
            unit[1] += tokens
        else:
            if self.pinned + tokens > self.limit:
                return -1
            self.units.append([[self._store(msg_id)], tokens])
        self.total += tokens
        return self._compact()

    def context(self) -> list:
        return list(self.alive.values())

    def total_tokens(self) -> int:
        return self.total
