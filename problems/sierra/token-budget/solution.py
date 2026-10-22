class TransientError(Exception):
    """Raised by MockAPI.fetch when a call fails but would succeed if retried."""


class MockAPI:
    """Provided (same as the starter). Simulates a cursor-paginated data API."""

    def __init__(self, spec: dict):
        self.pages = spec["pages"]
        self.failures = dict(spec.get("failures", {}))
        self.calls = 0

    def fetch(self, cursor):
        self.calls += 1
        key = "" if cursor is None else cursor
        if self.failures.get(key, 0) > 0:
            self.failures[key] -= 1
            raise TransientError(f"temporary failure fetching {key!r}")
        page = self.pages.get(key, {"records": [], "next": None})
        return [dict(r) for r in page["records"]], page["next"]


MAX_RETRIES = 3


def fetch_all(api_spec: dict) -> dict:
    """Part 1. O(total records + calls) time, O(records + pages) space:
    seen cursors and seen ids live in sets so cycle/duplicate checks are O(1)."""
    api = MockAPI(api_spec)
    records, seen_ids, seen_cursors = [], set(), set()
    cursor, status = None, "complete"
    while True:
        seen_cursors.add(cursor)
        for attempt in range(MAX_RETRIES + 1):
            try:
                batch, nxt = api.fetch(cursor)
                break
            except TransientError:
                continue
        else:
            status = "failed"
            break
        if not batch:
            break
        for r in batch:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                records.append(r)
        if nxt is None:
            break
        if nxt in seen_cursors:
            status = "cycle"
            break
        cursor = nxt
    return {"records": records, "status": status, "calls": api.calls}


def compact(records: list, trigger: int, target: int, mode: str = "count") -> list:
    """Part 2 + Follow-up. Sliding window, O(n) time, O(1) extra space.
    Tokens are non-negative, so for each right end r the smallest valid left end l
    gives the longest AND the largest-total run ending at r."""
    if sum(r["tokens"] for r in records) <= trigger:
        return records
    best = None                      # (key, l, r) ; larger key wins, ties keep earliest
    l = total = 0
    for r, rec in enumerate(records):
        total += rec["tokens"]
        while l <= r and total > target:
            total -= records[l]["tokens"]
            l += 1
        if l > r:
            continue
        length = r - l + 1
        key = (length,) if mode == "count" else (total, length)
        if best is None or key > best[0]:
            best = (key, l, r)
    if best is None:
        return []
    return records[best[1]:best[2] + 1]
