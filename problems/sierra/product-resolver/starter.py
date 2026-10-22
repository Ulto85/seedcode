class TransientError(Exception):
    """Raised by CatalogAPI.get when a call fails but may succeed if retried."""


class CatalogAPI:
    """Provided. Don't edit. Simulates a flaky product-catalog service."""

    def __init__(self, catalog: dict, flaky: dict):
        self.catalog = catalog
        self.flaky = dict(flaky)
        self.calls = 0
        self.waited_ms = 0

    def get(self, product_id: str):
        """Returns a copy of the product dict, or None if it doesn't exist. May raise TransientError."""
        self.calls += 1
        if self.flaky.get(product_id, 0) > 0:
            self.flaky[product_id] -= 1
            raise TransientError(f"catalog timeout for {product_id}")
        p = self.catalog.get(product_id)
        return None if p is None else dict(p)

    def sleep(self, ms: int):
        """Pretend to wait (nothing actually sleeps)."""
        self.waited_ms += ms


def resolve_products(requests: list, catalog: dict, flaky: dict,
                     max_retries: int, base_ms: int, use_cache: bool = False) -> dict:
    api = CatalogAPI(catalog, flaky)
    # ...
    return {"results": [], "calls": api.calls, "wait_ms": api.waited_ms}
