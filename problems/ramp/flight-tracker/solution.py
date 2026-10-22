from bisect import bisect_right
from collections import defaultdict


class FlightLog:
    """Groups flights per user and sorts each group by departure once: O(n log n) build.
    most_flights is O(1) after build; location is O(log k) for a user with k flights."""

    def __init__(self, flights):
        by_user = defaultdict(list)
        for dep, dep_t, arr, arr_t, user in flights:
            by_user[user].append((dep_t, arr_t, dep, arr))
        self.flights = {}
        self.starts = {}
        for user, fl in by_user.items():
            fl.sort()
            self.flights[user] = fl
            self.starts[user] = [f[0] for f in fl]
        self.top = None
        if by_user:
            self.top = min(by_user, key=lambda u: (-len(by_user[u]), u))

    def most_flights(self):
        return self.top

    def location(self, user_id, t):
        if user_id not in self.flights:
            return None
        i = bisect_right(self.starts[user_id], t) - 1   # last flight departing at or before t
        if i < 0:
            return "unknown"
        dep_t, arr_t, dep, arr = self.flights[user_id][i]
        if t < arr_t:
            return ["in_transit", dep, arr]
        return arr
