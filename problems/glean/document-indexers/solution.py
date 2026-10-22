import heapq


def _counts(m, queue_time, processing_time):
    """Simulate the pool. O((n + m) log m) time, O(m) space.

    busy:  min-heap of (free_time, indexer).
    free:  min-heap of "virtual positions". An indexer j freed while handling document i is stored as
           i + (j - i) % m, i.e. its distance from i % m going round the ring. Any entry x that is >= the
           current document i lies in [i, i + m), so the smallest one is exactly the first free indexer at or
           after i % m with wrap-around. Entries left behind (x < i) are re-keyed lazily when they surface.
    """
    counts = [0] * m
    busy = []
    free = list(range(m))           # at document 0, position j is indexer j
    for i, (t, p) in enumerate(zip(queue_time, processing_time)):
        while busy and busy[0][0] <= t:
            _, j = heapq.heappop(busy)
            heapq.heappush(free, i + (j - i) % m)
        while free and free[0] < i:
            j = heapq.heappop(free) % m
            heapq.heappush(free, i + (j - i) % m)
        if not free:
            continue                # every indexer is busy: drop
        j = heapq.heappop(free) % m
        counts[j] += 1
        heapq.heappush(busy, (t + p, j))
    return counts


def indexer_stats(m, queue_time, processing_time):
    counts = _counts(m, queue_time, processing_time)
    best = max(range(m), key=lambda j: (counts[j], -j))
    return [sum(counts), best]


def top_indexers(m, queue_time, processing_time, k):
    counts = _counts(m, queue_time, processing_time)
    top = heapq.nsmallest(k, range(m), key=lambda j: (-counts[j], j))
    n = len(queue_time)
    handled = sum(counts[j] for j in top)
    pct = round(100 * handled / n, 2) if n else 0.0
    return [sorted(top), pct]
