class _Cycle(Exception):
    pass


def cd(cwd, path, links):
    """Stack-based walk; after each step into a child, one dict lookup decides whether to redirect.
    A link is 'active' while its target is being resolved; meeting it again inside means a cycle.
    O(P * D) time for P components and depth D (building the lookup key), O(D) extra space."""

    def walk(start, p, active):
        parts = [] if p.startswith("/") else list(start)
        for name in p.split("/"):
            if name in ("", "."):
                continue
            if name == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(name)
            key = "/" + "/".join(parts)
            if key in links:
                if key in active:
                    raise _Cycle
                active.add(key)
                parts = walk([], links[key], active)
                active.discard(key)
        return parts

    try:
        parts = walk([x for x in cwd.split("/") if x], path, set())
    except _Cycle:
        return None
    return "/" + "/".join(parts)
