import bisect


class GpuCluster:
    """Hosts are bucketed by free GPU count (0..8); each bucket is a sorted list of (free_mem, index).
    Best fit = first non-empty bucket with f >= gpus whose list has an entry with free_mem >= mem
    (found with bisect). place/release: O(G log H + H) worst case for the list insert/delete memmove,
    with G <= 9 buckets. The follow-up queue scan is O(Q * G log H) per release of a running task."""

    def __init__(self, hosts: list):
        self.free = [[g, m] for g, m in hosts]
        self.max_g = max((g for g, _ in hosts), default=0)
        self.buckets = [[] for _ in range(self.max_g + 1)]
        for i, (g, m) in enumerate(hosts):
            self.buckets[g].append((m, i))
        for b in self.buckets:
            b.sort()
        # best_mem[g] = largest total memory among hosts with >= g GPUs (for "could it ever fit?")
        self.best_mem = [-1] * (self.max_g + 2)
        for g, m in hosts:
            self.best_mem[g] = max(self.best_mem[g], m)
        for g in range(self.max_g - 1, -1, -1):
            self.best_mem[g] = max(self.best_mem[g], self.best_mem[g + 1])
        self.running = {}          # task_id -> (host, gpus, mem)
        self.queue = {}            # task_id -> (gpus, mem), insertion order = FIFO

    def _move(self, i, dg, dm):
        g, m = self.free[i]
        b = self.buckets[g]
        b.pop(bisect.bisect_left(b, (m, i)))
        g, m = g + dg, m + dm
        self.free[i] = [g, m]
        bisect.insort(self.buckets[g], (m, i))

    def _try_place(self, task_id, gpus, mem):
        for f in range(gpus, self.max_g + 1):
            b = self.buckets[f]
            k = bisect.bisect_left(b, (mem, -1))
            if k < len(b):
                i = b[k][1]
                self._move(i, -gpus, -mem)
                self.running[task_id] = (i, gpus, mem)
                return i
        return -1

    def place(self, task_id: str, gpus: int, mem: int) -> int:
        return self._try_place(task_id, gpus, mem)

    def release(self, task_id: str) -> bool:
        if task_id in self.queue:
            del self.queue[task_id]
            return True
        if task_id not in self.running:
            return False
        i, g, m = self.running.pop(task_id)
        self._move(i, g, m)
        for qid, (qg, qm) in list(self.queue.items()):
            if self._try_place(qid, qg, qm) != -1:
                del self.queue[qid]
        return True

    def host_of(self, task_id: str):
        if task_id in self.running:
            return self.running[task_id][0]
        return -1 if task_id in self.queue else None

    def submit(self, task_id: str, gpus: int, mem: int) -> int:
        i = self._try_place(task_id, gpus, mem)
        if i != -1:
            return i
        if gpus > self.max_g or self.best_mem[gpus] < mem:
            return -2
        self.queue[task_id] = (gpus, mem)
        return -1

    def pending(self) -> list:
        return list(self.queue)
