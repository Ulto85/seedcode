class TaskManager:
    """Adjacency sets in both directions plus a status map.

    fail_task / add_dependency cascade with an iterative BFS that only visits tasks the moment they
    turn failed, so every task fails (and is expanded) at most once: O(V + E) total over all calls.
    Follow-up: pending[t] counts t's dependencies that are not done, and `ready` holds active tasks
    with pending == 0. complete_task is O(out-degree); get_ready is O(r log r) for r ready tasks.
    """

    def __init__(self):
        self.status = {}        # task -> "active" | "failed" | "done"
        self.deps = {}          # task -> set of tasks it depends on (parents)
        self.dependents = {}    # task -> set of tasks that depend on it (children)
        self.pending = {}       # task -> number of dependencies that are not done
        self.ready = set()      # active tasks with pending == 0

    def _ensure(self, t):
        if t not in self.status:
            self.status[t] = "active"
            self.deps[t] = set()
            self.dependents[t] = set()
            self.pending[t] = 0
            self.ready.add(t)

    def _cascade(self, start):
        """Fail `start` (must be active) and every active task reachable through dependents."""
        self.status[start] = "failed"
        self.ready.discard(start)
        queue = [start]
        while queue:
            cur = queue.pop()
            for child in self.dependents[cur]:
                if self.status[child] == "active":
                    self.status[child] = "failed"
                    self.ready.discard(child)
                    queue.append(child)

    def add_task(self, task_id: str) -> None:
        self._ensure(task_id)

    def add_dependency(self, task_id: str, dependency_id: str) -> None:
        self._ensure(task_id)
        self._ensure(dependency_id)
        if dependency_id in self.deps[task_id]:
            return
        self.deps[task_id].add(dependency_id)
        self.dependents[dependency_id].add(task_id)
        if self.status[dependency_id] != "done":
            self.pending[task_id] += 1
            self.ready.discard(task_id)
        if self.status[dependency_id] == "failed" and self.status[task_id] == "active":
            self._cascade(task_id)

    def fail_task(self, task_id: str) -> None:
        self._ensure(task_id)
        if self.status[task_id] == "active":
            self._cascade(task_id)

    def get_status(self, task_id: str) -> str:
        return self.status.get(task_id, "not_found")

    # ---- Follow-up ----
    def complete_task(self, task_id: str) -> bool:
        if self.status.get(task_id) != "active" or self.pending[task_id] != 0:
            return False
        self.status[task_id] = "done"
        self.ready.discard(task_id)
        for child in self.dependents[task_id]:
            self.pending[child] -= 1
            if self.pending[child] == 0 and self.status[child] == "active":
                self.ready.add(child)
        return True

    def get_ready(self) -> list:
        return sorted(self.ready)
