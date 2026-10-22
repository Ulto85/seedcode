def header_level(line: str) -> int:
    """1-6 if line is a header ('#'*L + ' ' at column 0), else 0."""
    n = 0
    while n < len(line) and n < 7 and line[n] == "#":
        n += 1
    return n if 1 <= n <= 6 and len(line) > n and line[n] == " " else 0


def split_markdown(markdown: str, max_size: int) -> list:
    """Greedy chunking with a running length. O(len(markdown)) time and space:
    each line is measured once and the header prefix is at most 6 lines."""
    if markdown == "":
        return []
    lines = markdown.split("\n")
    active = [None] * 7                      # active[L] = current header line at level L

    def take(line):
        lvl = header_level(line)
        if lvl:
            active[lvl] = line
            for k in range(lvl + 1, 7):
                active[k] = None

    chunks, i, n = [], 0, len(lines)
    while i < n:
        lvl = header_level(lines[i])
        upto = lvl if lvl else 7
        parts = [active[k] for k in range(1, upto) if active[k] is not None]
        parts.append(lines[i])
        size = sum(len(p) for p in parts) + len(parts) - 1
        take(lines[i])
        i += 1
        while i < n and size + 1 + len(lines[i]) <= max_size:
            size += 1 + len(lines[i])
            parts.append(lines[i])
            take(lines[i])
            i += 1
        chunks.append("\n".join(parts))
    return chunks
