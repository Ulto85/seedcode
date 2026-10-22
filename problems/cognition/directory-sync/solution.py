from collections import defaultdict


def _dirs(tree):
    out = set()
    for p in tree:
        parts = p.split("/")
        for i in range(1, len(parts)):
            out.add("/".join(parts[:i]))
    return out


def _plan(src, dst, moves_enabled):
    """O(N * depth + N log N) for N = total files: set differences, hash grouping, sorts."""
    sd, dd = _dirs(src), _dirs(dst)
    mkdirs = sorted(sd - dd, key=lambda d: (d.count("/"), d))
    rmdirs = sorted(dd - sd, key=lambda d: (-d.count("/"), d))
    deletes = [p for p in dst if p not in src]
    missing = [p for p in src if p not in dst]
    changed = [p for p in src if p in dst and dst[p] != src[p]]
    moves = []
    if moves_enabled:
        del_by_hash, new_by_hash = defaultdict(list), defaultdict(list)
        for p in deletes:
            del_by_hash[dst[p]].append(p)
        for p in missing:
            new_by_hash[src[p]].append(p)
        moved_from, moved_to = set(), set()
        for h, olds in del_by_hash.items():
            news = new_by_hash.get(h)
            if not news:
                continue
            olds.sort()
            news.sort()
            for a, b in zip(olds, news):
                moves.append(["move", a, b])
                moved_from.add(a)
                moved_to.add(b)
        moves.sort(key=lambda m: m[1])
        deletes = [p for p in deletes if p not in moved_from]
        missing = [p for p in missing if p not in moved_to]
    return ([["mkdir", d] for d in mkdirs] + moves
            + [["delete", p] for p in sorted(deletes)]
            + [["rmdir", d] for d in rmdirs]
            + [["copy", p] for p in sorted(missing + changed)])


def sync_plan(src, dst):
    return _plan(src, dst, False)


def sync_plan_with_moves(src, dst):
    return _plan(src, dst, True)
