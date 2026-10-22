from collections import defaultdict, deque


def _adjacency(edges):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    return adj


def find_exit(start, exits, edges):
    """Plain BFS. O(V + E) time and space."""
    adj, exits = _adjacency(edges), set(exits)
    seen, q = {start}, deque([start])
    while q:
        u = q.popleft()
        if u in exits:
            return u
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return None


def find_exit_with_keys(start, exits, edges, required_keys, keys_found, failures, max_retries):
    """BFS over (room, key) states. O((V + E) * K) for K distinct keys."""
    adj, exits = _adjacency(edges), set(exits)

    def can_enter(url, key):
        if failures.get(url, 0) > max_retries:
            return False
        need = required_keys.get(url)
        return need is None or need == key

    if not can_enter(start, None):
        return None
    s = (start, keys_found.get(start))
    seen, q = {s}, deque([s])
    while q:
        u, key = q.popleft()
        if u in exits:
            return u
        for v in adj[u]:
            if can_enter(v, key):
                st = (v, keys_found.get(v, key))
                if st not in seen:
                    seen.add(st)
                    q.append(st)
    return None
