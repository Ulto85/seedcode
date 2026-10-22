class VersionedKV:
    def __init__(self):
        pass

    def set(self, key: str, value, ts: int) -> None:
        pass

    def delete(self, key: str, ts: int) -> None:
        pass

    def get(self, key: str, ts: int):
        pass

    # ---- Part 2 ----
    def get_range(self, key: str, start: int, end: int) -> list:
        pass

    # ---- Follow-up ----
    def restore(self, ts: int) -> None:
        pass
