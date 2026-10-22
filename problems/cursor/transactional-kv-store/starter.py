class KVStore:
    def __init__(self):
        pass

    def get(self, key: str):
        pass

    def set(self, key: str, value: str) -> None:
        pass

    def delete(self, key: str) -> bool:
        pass

    def begin(self) -> None:
        pass

    def commit(self) -> bool:
        pass

    def rollback(self) -> bool:
        pass


# ---- Follow-up ----
class OCCStore:
    def __init__(self):
        pass

    def begin(self) -> int:
        pass

    def get(self, txn: int, key: str):
        pass

    def set(self, txn: int, key: str, value: str) -> bool:
        pass

    def delete(self, txn: int, key: str) -> bool:
        pass

    def commit(self, txn: int) -> bool:
        pass

    def rollback(self, txn: int) -> bool:
        pass

    def read(self, key: str):
        pass
