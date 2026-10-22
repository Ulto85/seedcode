---
title: Image Chunk Cache with Pinning
difficulty: Medium
source: In the style of the "content-addressed layer cache with eviction that pins in-use layers" theme that prep guides attribute to Modal's coding rounds (unverified, no first-hand report found), built on Modal's own blog about lazily loading container images. Not a reported question.
order: 3
minutes: 50
tags: design, LRU, heap, reference counting
---
Modal starts containers fast by **lazily loading** their images: the file system fetches content-addressed
chunks over the network the first time a container reads them, and keeps a local cache on each host so the
next container that needs the same chunk (Python, PyTorch, CUDA libraries...) gets it for free. Build that
host-local cache.

A chunk is identified by its content hash, so a given `chunk_hash` **always has the same size**. Sizes are
in MiB, `size >= 1`.

### Part 1: a byte-budget LRU
```
ChunkCache(capacity: int)
read(chunk_hash: str, size: int) -> bool     # True on a cache hit
used() -> int                                # total size of cached chunks
stats() -> [hits, misses, bytes_fetched]
```
- **Hit:** the chunk is cached. It becomes the most recently used chunk. Return `True`.
- **Miss:** count a miss and add `size` to `bytes_fetched` (it was fetched from the network). Then:
  - if `size > capacity`, the chunk is used but **not stored**, and nothing is evicted;
  - otherwise evict least-recently-used chunks, one at a time, until `used() + size <= capacity`, then store the
    chunk as the most recently used. Return `False`.

```
c = ChunkCache(10)
c.read("a", 4) -> False      # cache: a
c.read("b", 4) -> False      # cache: a, b
c.read("a", 4) -> True       # a is now more recent than b
c.read("c", 4) -> False      # 12 > 10: evict b (the LRU), cache: a, c
c.used()       -> 8
c.stats()      -> [1, 3, 12]
```

### Follow-up: containers pin their chunks
Evicting a chunk that a running container is using would force a refetch mid-run, so running containers
**pin** chunks.
```
mount(container_id: str, chunks: list[[chunk_hash, size]]) -> int
unmount(container_id: str) -> bool
```
- `mount` reads each chunk **in order**, with exactly the `read` rules (it updates `stats()` too). After each read,
  if the chunk is in the cache, this container pins it. Return the bytes fetched during this mount (the total size
  of its misses). If `container_id` is already mounted, return `-1` and change nothing. An empty list is fine
  (returns `0`). A container that lists a hash twice just gets a hit the second time and still pins it once.
- **Pinned chunks are never evicted.** Eviction removes the least recently used **unpinned** chunk. On a miss,
  if `size > capacity - (total size of pinned chunks)`, the chunk can't fit even after evicting everything
  evictable, so it is **not stored and nothing is evicted**. This applies to plain `read` calls too.
  Because chunks are pinned as soon as they are read, a mount never evicts its own earlier chunks.
- A chunk stays pinned while **any** mounted container pins it.
- `unmount` returns `False` if the container isn't mounted. Otherwise it releases the container's pins and
  returns `True`. Released chunks stay cached. Their recency is still their last read: unmounting is not a read.

```
c = ChunkCache(10)
c.mount("x", [["a", 4], ["b", 4]]) -> 8      # a, b pinned by x
c.read("c", 4)                     -> False  # only 10 - 8 = 2 MiB evictable room: c is not stored
c.mount("y", [["b", 4], ["d", 2]]) -> 2      # b hit; d fits exactly (used = 10)
c.unmount("x")                     -> True   # a is unpinned; b is still pinned by y
c.read("e", 4)                     -> False  # evict a (the only unpinned chunk), store e
c.unmount("x")                     -> False
c.used()                           -> 10     # b, d, e
c.stats()                          -> [1, 5, 18]
```

### Constraints
- `1 <= capacity <= 10^9`, `1 <= size <= 10^6`
- Up to `10^5` calls and `2 * 10^5` chunk reads in total
- Every operation should be `O(log n)` amortized: hidden tests keep thousands of chunks cached, so scanning the
  whole cache to find the LRU (or the LRU *unpinned*) chunk on every eviction is too slow.

### What the interviewer cares about
- Exact policy before code: what counts as a hit, what happens to an oversized chunk, recency on unmount
- An LRU that can skip pinned entries efficiently (keep only *evictable* chunks in the LRU structure, or a heap
  keyed on last access with lazy deletion)
- Reference counting pins across containers, and keeping `pinned bytes` up to date so "can it ever fit?" is `O(1)`
- Discussion: in production two containers miss on the same chunk at once. How do you make sure it is fetched
  only once (single-flight)?
