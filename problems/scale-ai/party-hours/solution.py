from collections import defaultdict


def _merged_by_town(parties, lo, hi):
    """Group parties by town, clamp to [lo, hi], sort and merge (touching intervals merge).
    O(P log P) time, O(P) space."""
    by_town = defaultdict(list)
    for town, s, e in parties:
        s, e = max(s, lo), min(e, hi)
        if s < e:
            by_town[town].append((s, e))
    merged = {}
    for town, ivs in by_town.items():
        ivs.sort()
        out = [list(ivs[0])]
        for s, e in ivs[1:]:
            if s <= out[-1][1]:
                out[-1][1] = max(out[-1][1], e)
            else:
                out.append([s, e])
        merged[town] = out
    return merged


def party_hours(regions, parties):
    """O(P log P + T)."""
    merged = _merged_by_town(parties, 0, 1440)
    res = []
    for row in regions:
        minutes = sum(e - s for s, e in merged.get(row["town"], []))
        res.append([row["town"], round(minutes / 60, 2)])
    return res


def idle_segments(regions, parties, day_start, day_end):
    """Complement of each town's merged coverage, grouped by city. O(P log P + T)."""
    merged = _merged_by_town(parties, day_start, day_end)
    res = {}
    for row in regions:
        gaps = res.setdefault(row["city"], [])
        cur = day_start
        for s, e in merged.get(row["town"], []):
            if s > cur:
                gaps.append([row["town"], cur, s])
            cur = e
        if cur < day_end:
            gaps.append([row["town"], cur, day_end])
    return res
