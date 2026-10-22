import heapq
from collections import defaultdict

DAY = 86400


def _cents(numerator):
    """numerator is exact cost in cent-seconds-per-hour units (cents * 3600). Round half up."""
    return (numerator + 1800) // 3600


class DeliveryTracker:
    """Money is kept exact as an integer numerator: sum(rate * seconds); divide by 3600 only when reporting.
    add_driver / get_total_cost / get_unpaid_cost: O(1)
    record_delivery: O(log n)       pay_up_to: O(k log n) for k deliveries settled (amortized O(log n))
    max_active_drivers: O(n log n)  (scan, clip to the window, merge per driver, sweep)
    Space: O(n)."""

    def __init__(self):
        self.rates = {}
        self.deliveries = []      # (driver_id, start, end)
        self.total_num = 0        # exact cost * 3600 of all deliveries
        self.unpaid_num = 0       # exact cost * 3600 of unpaid deliveries
        self.unpaid = []          # min-heap of (end, numerator)

    def add_driver(self, driver_id: int, rate: int) -> bool:
        if driver_id in self.rates:
            return False
        self.rates[driver_id] = rate
        return True

    def record_delivery(self, driver_id: int, start: int, end: int) -> bool:
        if driver_id not in self.rates or end < start:
            return False
        num = self.rates[driver_id] * (end - start)
        self.deliveries.append((driver_id, start, end))
        self.total_num += num
        self.unpaid_num += num
        heapq.heappush(self.unpaid, (end, num))
        return True

    def get_total_cost(self) -> int:
        return _cents(self.total_num)

    def pay_up_to(self, time: int) -> int:
        settled = 0
        while self.unpaid and self.unpaid[0][0] <= time:
            _, num = heapq.heappop(self.unpaid)
            self.unpaid_num -= num
            settled += 1
        return settled

    def get_unpaid_cost(self) -> int:
        return _cents(self.unpaid_num)

    def max_active_drivers(self, time: int) -> int:
        lo, hi = time - DAY, time
        per_driver = defaultdict(list)
        for d, s, e in self.deliveries:
            s, e = max(s, lo), min(e, hi)
            if s < e:
                per_driver[d].append((s, e))
        events = []
        for ivs in per_driver.values():
            ivs.sort()
            cs, ce = ivs[0]
            for s, e in ivs[1:]:
                if s <= ce:
                    ce = max(ce, e)
                else:
                    events += [(cs, 1), (ce, -1)]
                    cs, ce = s, e
            events += [(cs, 1), (ce, -1)]
        events.sort()             # at equal times, -1 (end) sorts before +1 (start)
        best = cur = 0
        for _, delta in events:
            cur += delta
            best = max(best, cur)
        return best
