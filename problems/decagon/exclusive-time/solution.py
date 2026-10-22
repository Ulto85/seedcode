def exclusive_time(n: int, logs: list[str]) -> list[int]:
    res = [0] * n
    stack = []
    prev = 0  # start of the current, not-yet-counted time slice
    for log in logs:
        fid, kind, t = log.split(":")
        fid, t = int(fid), int(t)
        if kind == "start":
            if stack:
                res[stack[-1]] += t - prev
            stack.append(fid)
            prev = t
        else:
            res[stack.pop()] += t - prev + 1
            prev = t + 1
    return res
