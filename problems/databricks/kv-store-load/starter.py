class KVStore:
    def __init__(self):
        pass

    def put(self, key: str, value: str, timestamp: int) -> None:
        pass

    def get(self, key: str, timestamp: int):
        pass

    def measure_put_load(self, timestamp: int) -> float:
        pass

    def measure_get_load(self, timestamp: int) -> float:
        pass

    # ---- Follow-up ----
    def average_qps(self, op: str, timestamp: int, window: int) -> float:
        pass
