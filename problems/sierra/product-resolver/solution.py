class TransientError(Exception):
    """Raised by CatalogAPI.get when a call fails but may succeed if retried."""


class CatalogAPI:
    """Provided (same as the starter). Simulates a flaky product-catalog service."""

    def __init__(self, catalog: dict, flaky: dict):
        self.catalog = catalog
        self.flaky = dict(flaky)
        self.calls = 0
        self.waited_ms = 0

    def get(self, product_id: str):
        self.calls += 1
        if self.flaky.get(product_id, 0) > 0:
            self.flaky[product_id] -= 1
            raise TransientError(f"catalog timeout for {product_id}")
        p = self.catalog.get(product_id)
        return None if p is None else dict(p)

    def sleep(self, ms: int):
        self.waited_ms += ms


FAILED = object()


def resolve_products(requests: list, catalog: dict, flaky: dict,
                     max_retries: int, base_ms: int, use_cache: bool = False) -> dict:
    """Without the cache: O(sum of chain lengths) calls. With it: every id is fetched
    successfully at most once and every definitive answer is memoized for every id on the
    walked path, so the whole run is O(len(requests) + len(catalog)) amortized."""
    api = CatalogAPI(catalog, flaky)
    fetched = {}        # id -> response (product dict or None); only used when use_cache
    answer = {}         # id -> final definitive result; only used when use_cache

    def fetch(pid):
        if use_cache and pid in fetched:
            return fetched[pid]
        for attempt in range(max_retries + 1):
            if attempt:
                api.sleep(base_ms * 2 ** (attempt - 1))
            try:
                resp = api.get(pid)
            except TransientError:
                continue
            if use_cache:
                fetched[pid] = resp
            return resp
        return FAILED

    def resolve(pid):
        path, visited, cur = [], set(), pid
        while True:
            if use_cache and cur in answer:
                result = answer[cur]
                break
            if cur in visited:
                result = "CYCLE"
                break
            visited.add(cur)
            path.append(cur)
            p = fetch(cur)
            if p is FAILED:
                return "FAILED"                       # never remembered
            if p is None:
                result = "NOT_FOUND"
                break
            if p["status"] == "active":
                result = cur
                break
            if p.get("replacement") is None:
                result = "UNAVAILABLE"
                break
            cur = p["replacement"]
        if use_cache:
            for q in path:
                answer[q] = result
        return result

    results = [resolve(pid) for pid in requests]
    return {"results": results, "calls": api.calls, "wait_ms": api.waited_ms}
