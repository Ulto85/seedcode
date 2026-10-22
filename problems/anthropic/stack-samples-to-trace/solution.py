def _common_prefix(a, b):
    p = 0
    m = min(len(a), len(b))
    while p < m and a[p] == b[p]:
        p += 1
    return p


def convert_to_trace(samples):
    """Diff each stack against the previous one by longest common prefix.
    O(total frames) time, O(max depth) extra space (plus the output)."""
    events = []
    prev = []
    for ts, stack in samples:
        p = _common_prefix(prev, stack)
        for name in reversed(prev[p:]):
            events.append(["end", ts, name])
        for name in stack[p:]:
            events.append(["start", ts, name])
        prev = stack
    return events


def convert_to_trace_min(samples, n):
    """Pass 1 builds every call as [name, first_sample, end_ts, samples_seen].
    Pass 2 emits events only for calls seen in >= n samples, in Part 1 order.
    O(total frames) time and space."""
    calls = []                 # all calls ever opened
    open_calls = []            # indices into calls, outermost first
    starts_at = []             # starts_at[i] = call indices starting at sample i (outer first)
    ends_at = []               # ends_at[i]   = call indices ending at sample i (inner first)
    prev = []
    for i, (ts, stack) in enumerate(samples):
        p = _common_prefix(prev, stack)
        ended = []
        while len(open_calls) > p:
            ended.append(open_calls.pop())
        for c in ended:
            calls[c][2] = ts
        for c in open_calls:
            calls[c][3] += 1
        started = []
        for name in stack[p:]:
            calls.append([name, i, None, 1])
            open_calls.append(len(calls) - 1)
            started.append(len(calls) - 1)
        starts_at.append(started)
        ends_at.append(ended)
        prev = stack

    events = []
    for i, (ts, _) in enumerate(samples):
        for c in ends_at[i]:
            if calls[c][3] >= n:
                events.append(["end", ts, calls[c][0]])
        for c in starts_at[i]:
            if calls[c][3] >= n:
                events.append(["start", ts, calls[c][0]])
    return events
