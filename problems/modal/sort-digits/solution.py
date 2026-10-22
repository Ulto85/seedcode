import bisect


def _counts(text):
    return [text.count(str(d)) for d in range(10)]


def sort_digits(digits: str) -> str:
    """Counting sort with ten counters. O(n) time, O(1) extra space besides the output."""
    counts = _counts(digits)
    return "".join(str(d) * c for d, c in enumerate(counts))


def sorted_digit_at(chunks: list, positions: list) -> list:
    """Count every chunk (O(total)), build prefix sums over the ten counts,
    then answer each position with a binary search over 10 boundaries: O(total + q)."""
    counts = [0] * 10
    for chunk in chunks:
        for d, c in enumerate(_counts(chunk)):
            counts[d] += c
    ends, run = [], 0              # ends[d] = number of digits <= d
    for c in counts:
        run += c
        ends.append(run)
    total = run
    out = []
    for p in positions:
        if p < 0 or p >= total:
            out.append(-1)
        else:
            out.append(bisect.bisect_right(ends, p))
    return out
