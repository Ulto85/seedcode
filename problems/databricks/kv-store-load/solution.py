from bisect import bisect_right


class KVStore:
    """Keeps every call's timestamp per operation in a sorted list (timestamps never decrease, so append keeps it
    sorted). A window count is two binary searches.
    put/get O(1), measure_* / average_qps O(log n), space O(n).
    (Part 1 alone can use a 300-slot ring buffer for O(1) memory.)"""

    WINDOW = 300

    def __init__(self):
        self.data = {}
        self.calls = {"put": [], "get": []}

    def put(self, key, value, timestamp):
        self.data[key] = value
        self.calls["put"].append(timestamp)

    def get(self, key, timestamp):
        self.calls["get"].append(timestamp)
        return self.data.get(key)

    def average_qps(self, op, timestamp, window):
        ts = self.calls[op]
        count = bisect_right(ts, timestamp) - bisect_right(ts, timestamp - window)
        return count / window

    def measure_put_load(self, timestamp):
        return self.average_qps("put", timestamp, self.WINDOW)

    def measure_get_load(self, timestamp):
        return self.average_qps("get", timestamp, self.WINDOW)
