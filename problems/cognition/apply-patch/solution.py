import re

HEADER = re.compile(r"^@@ -(\d+)(,\d+)? \+(\d+)(,\d+)? @@$")


def _parse(patch):
    """-> list of (A, old_block, new_block)."""
    hunks = []
    for line in patch.split("\n"):
        if line == "":
            continue
        m = HEADER.match(line)
        if m:
            hunks.append((int(m.group(1)), [], []))
            continue
        kind, text = line[0], line[1:]
        _, old, new = hunks[-1]
        if kind in " -":
            old.append(text)
        if kind in " +":
            new.append(text)
    return hunks


def _matches(lines, block, q):
    """Does block match lines starting at 1-indexed line q?"""
    if q < 1 or q - 1 + len(block) > len(lines):
        return False
    for i, b in enumerate(block):
        if lines[q - 1 + i] != b:
            return False
    return True


def _build(lines, placed):
    """placed: list of (start, old_len, new_block) in order; start is 1-indexed (for pure insertion,
    the block goes after line start - 1). Builds the output in one pass."""
    out, cur = [], 0                     # cur = number of original lines already emitted
    for start, old_len, new in placed:
        out.extend(lines[cur:start - 1])
        out.extend(new)
        cur = start - 1 + old_len
    out.extend(lines[cur:])
    return "\n".join(out)


def apply_patch(original, patch):
    """O(L + P): every hunk is checked at its exact position, output built in one pass."""
    lines = original.split("\n")
    placed, prev_end = [], 0             # prev_end = last original line consumed by earlier hunks
    for a, old, new in _parse(patch):
        if not old:
            if a < prev_end or a > len(lines):
                return None
            placed.append((a + 1, 0, new))
            prev_end = a
            continue
        if a <= prev_end or not _matches(lines, old, a):
            return None
        placed.append((a, len(old), new))
        prev_end = a + len(old) - 1
    return _build(lines, placed)


def apply_patch_fuzzy(original, patch):
    """Searches outward from the expected position: O(L + sum over hunks of displacement * block size)."""
    lines = original.split("\n")
    n = len(lines)
    placed, prev_end, delta = [], 0, 0
    for a, old, new in _parse(patch):
        k = len(old)
        lo, hi = prev_end + 1, n - k + 1          # valid start range
        exp = a + delta
        found = None
        d = 0
        while True:
            below, above = exp - d, exp + d
            if below < lo and above > hi:
                break
            if lo <= below <= hi and _matches(lines, old, below):
                found = below
                break
            if d and lo <= above <= hi and _matches(lines, old, above):
                found = above
                break
            d += 1
        if found is None:
            return None
        placed.append((found, k, new))
        prev_end = found + k - 1
        delta = found - a
    return _build(lines, placed)
