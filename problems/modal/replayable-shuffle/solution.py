def shuffle(items: list, draws: list):
    """Replay forward Fisher-Yates. O(n) time, O(n) for the output copy."""
    n = len(items)
    if len(draws) != max(n - 1, 0):
        return None
    for i, d in enumerate(draws):
        if not 0 <= d <= n - 1 - i:
            return None
    out = list(items)
    for i, d in enumerate(draws):
        j = i + d
        out[i], out[j] = out[j], out[i]
    return out


def recover_draws(items: list, shuffled: list):
    """Re-run the shuffle, choosing at each step the swap that puts shuffled[i] at position i.
    A value -> position map keeps each step O(1): O(n) time and space overall."""
    n = len(items)
    if len(shuffled) != n or len(set(shuffled)) != n or set(shuffled) != set(items):
        return None
    cur = list(items)
    pos = {v: i for i, v in enumerate(cur)}
    draws = []
    for i in range(n - 1):
        j = pos[shuffled[i]]
        draws.append(j - i)
        cur[i], cur[j] = cur[j], cur[i]
        pos[cur[i]], pos[cur[j]] = i, j
    return draws
