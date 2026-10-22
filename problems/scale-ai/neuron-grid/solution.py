def update_neurons(neurons):
    """In place with O(1) extra space. Pass 1 overwrites each visited cell with new * 2 + was_firing,
    so later cells can still read whether an earlier neighbour was originally firing (low bit), while
    unvisited neighbours still hold their original value. Pass 2 shifts the bit away.
    O(m * n) time, O(1) extra space."""
    m = len(neurons)
    if m == 0:
        return neurons
    n = len(neurons[0])
    for i in range(m):
        for j in range(n):
            v = neurons[i][j]
            # cells already visited hold new*2 + was_firing; unvisited hold the original value
            cnt = 0
            for di in (-1, 0, 1):
                r = i + di
                if r < 0 or r >= m:
                    continue
                row = neurons[r]
                for dj in (-1, 0, 1):
                    c = j + dj
                    if (di or dj) and 0 <= c < n:
                        visited = r < i or (r == i and c < j)
                        if (row[c] & 1) if visited else row[c] == 0:
                            cnt += 1
            if v == 0:
                new = 6 if cnt == 3 else 0
            elif cnt <= 1:
                new = max(0, v - 2)
            elif cnt >= 4:
                new = max(0, v - 1)
            else:
                new = v
            neurons[i][j] = new * 2 + (v == 0)
    for row in neurons:
        for j in range(n):
            row[j] >>= 1
    return neurons
