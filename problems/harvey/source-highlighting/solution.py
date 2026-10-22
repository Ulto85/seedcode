"""Find every occurrence with str.find, merge spans with a sweep, build the output once.
Time O(n * k + M log M) worst case (k sources, M occurrences), space O(n + M)."""

OPEN, CLOSE = "<yellow>", "</yellow>"


def _occurrences(text, src):
    """Start indices of every (overlapping) occurrence of src in text."""
    if not src:
        return []
    out, i = [], text.find(src)
    while i != -1:
        out.append(i)
        i = text.find(src, i + 1)
    return out


def _regions(text, sources):
    """Merged regions as [start, end, set_of_source_indices]."""
    spans = []
    for idx, src in enumerate(sources):
        for i in _occurrences(text, src):
            spans.append((i, i + len(src), idx))
    spans.sort()
    regions = []
    for s, e, idx in spans:
        if regions and s <= regions[-1][1]:          # overlap or touch
            r = regions[-1]
            r[1] = max(r[1], e)
            r[2].add(idx)
        else:
            regions.append([s, e, {idx}])
    return regions


def _render(text, regions, cite):
    out, pos = [], 0
    for s, e, ids in regions:
        out.append(text[pos:s])
        out.append(OPEN + text[s:e] + CLOSE)
        if cite:
            out.append("".join(f"[{i}]" for i in sorted(ids)))
        pos = e
    out.append(text[pos:])
    return "".join(out)


def highlight(text: str, sources: list) -> str:
    return _render(text, _regions(text, sources), False)


def count_matches(text: str, sources: list) -> list:
    return [len(_occurrences(text, s)) for s in sources]


def highlight_with_citations(text: str, sources: list) -> str:
    return _render(text, _regions(text, sources), True)
