import heapq
from collections import deque
from urllib.parse import urlparse


def _strip(url):
    return url.split("#", 1)[0]


def _host(url):
    return urlparse(url).hostname


def crawl(start_url, pages):
    """BFS with a visited set. O(P + L) time (P pages, L links), O(P) space."""
    start = _strip(start_url)
    host = _host(start)
    seen = {start}
    q = deque([start])
    while q:
        url = q.popleft()
        for link in pages.get(url, []):
            link = _strip(link)
            if link not in seen and _host(link) == host:
                seen.add(link)
                q.append(link)
    return list(seen)


def crawl_times(start_url, pages, latency, workers):
    """Event simulation: FIFO queue of discovered URLs + min-heap of in-flight fetches
    keyed by (finish_time, start_seq). O((P + L) + P log W) time, O(P) space."""
    start = _strip(start_url)
    host = _host(start)
    seen = {start}
    queue = deque([start])
    running = []                  # (finish, seq, url)
    seq = 0
    done = {}
    t = 0
    while queue or running:
        while queue and len(running) < workers:
            url = queue.popleft()
            heapq.heappush(running, (t + latency.get(url, 1), seq, url))
            seq += 1
        t = running[0][0]
        while running and running[0][0] == t:
            _, _, url = heapq.heappop(running)
            done[url] = t
            for link in pages.get(url, []):
                link = _strip(link)
                if link not in seen and _host(link) == host:
                    seen.add(link)
                    queue.append(link)
    return done
