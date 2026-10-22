import heapq
from collections import defaultdict


class TaskManager:
    """Online Kahn's algorithm.
    ready:      min-heap of (deadline, id) for tasks whose prerequisites are all consumed
    missing:    id -> number of prerequisites not yet consumed
    dependents: prereq id -> tasks waiting on it
    add_tasks: O(k log n + links), consume_task: O(log n + unlocked) amortized. Space O(n + links)."""

    def __init__(self):
        self.ready = []
        self.deadline = {}
        self.missing = {}
        self.dependents = defaultdict(list)
        self.consumed = set()

    def add_tasks(self, tasks):
        for tid, ddl, prereqs in tasks:
            self.deadline[tid] = ddl
            pending = {p for p in prereqs if p not in self.consumed}
            if pending:
                self.missing[tid] = len(pending)
                for p in pending:
                    self.dependents[p].append(tid)
            else:
                heapq.heappush(self.ready, (ddl, tid))

    def consume_task(self):
        if not self.ready:
            return None
        _, tid = heapq.heappop(self.ready)
        self.consumed.add(tid)
        for d in self.dependents.pop(tid, ()):
            self.missing[d] -= 1
            if self.missing[d] == 0:
                del self.missing[d]
                heapq.heappush(self.ready, (self.deadline[d], d))
        return tid
