class TransientError(Exception):
    """Raised by MockAPI.fetch when a call fails but would succeed if retried."""


class MockAPI:
    """Provided. Don't edit. Simulates a cursor-paginated data API."""

    def __init__(self, spec: dict):
        self.pages = spec["pages"]
        self.failures = dict(spec.get("failures", {}))
        self.calls = 0

    def fetch(self, cursor):
        """Returns (records, next_cursor), or raises TransientError."""
        self.calls += 1
        key = "" if cursor is None else cursor
        if self.failures.get(key, 0) > 0:
            self.failures[key] -= 1
            raise TransientError(f"temporary failure fetching {key!r}")
        page = self.pages.get(key, {"records": [], "next": None})
        return [dict(r) for r in page["records"]], page["next"]


MAX_RETRIES = 3


def fetch_all(api_spec: dict) -> dict:
    api = MockAPI(api_spec)
    # call api.fetch(cursor) ...
    pass


def compact(records: list, trigger: int, target: int, mode: str = "count") -> list:
    pass
