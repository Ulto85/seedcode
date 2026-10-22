import heapq


class ChunkCache:
    """Cached chunks live in a dict (hash -> [size, last_access]). Evictable chunks are found through a
    min-heap of (last_access, hash) with lazy deletion: an entry is live only if the chunk is still cached,
    unpinned, and its last access matches. Pins are reference counts; pinned bytes are tracked so the
    "can this ever fit?" check is O(1).
    Every call is O(log n) amortized per chunk read; O(n) space."""

    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}            # hash -> [size, last_access]
        self.heap = []             # (last_access, hash) candidates for eviction
        self.pins = {}             # hash -> number of containers pinning it
        self.pinned_bytes = 0
        self.total = 0
        self.clock = 0
        self.hits = self.misses = self.fetched = 0
        self.mounts = {}           # container_id -> list of pinned hashes

    def _touch(self, h):
        self.clock += 1
        self.cache[h][1] = self.clock
        if h not in self.pins:
            heapq.heappush(self.heap, (self.clock, h))

    def _evict_one(self):
        while True:
            stamp, h = heapq.heappop(self.heap)
            entry = self.cache.get(h)
            if entry is not None and entry[1] == stamp and h not in self.pins:
                self.total -= entry[0]
                del self.cache[h]
                return

    def read(self, chunk_hash: str, size: int) -> bool:
        if chunk_hash in self.cache:
            self.hits += 1
            self._touch(chunk_hash)
            return True
        self.misses += 1
        self.fetched += size
        if size > self.cap - self.pinned_bytes:
            return False
        while self.total + size > self.cap:
            self._evict_one()
        self.cache[chunk_hash] = [size, 0]
        self.total += size
        self._touch(chunk_hash)
        return False

    def used(self) -> int:
        return self.total

    def stats(self) -> list:
        return [self.hits, self.misses, self.fetched]

    def mount(self, container_id: str, chunks: list) -> int:
        if container_id in self.mounts:
            return -1
        before = self.fetched
        pinned = set()
        for h, size in chunks:
            self.read(h, size)
            if h in self.cache and h not in pinned:
                pinned.add(h)
                if h not in self.pins:
                    self.pins[h] = 0
                    self.pinned_bytes += self.cache[h][0]
                self.pins[h] += 1
        self.mounts[container_id] = list(pinned)
        return self.fetched - before

    def unmount(self, container_id: str) -> bool:
        if container_id not in self.mounts:
            return False
        for h in self.mounts.pop(container_id):
            self.pins[h] -= 1
            if self.pins[h] == 0:
                del self.pins[h]
                self.pinned_bytes -= self.cache[h][0]
                heapq.heappush(self.heap, (self.cache[h][1], h))
        return True
