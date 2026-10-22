from collections import defaultdict

STATES = ("LIVE", "PAUSED", "CANCELLED")


class OrderManager:
    """Hash map id -> [symbol, state, seq] plus a running count per state.
    Per symbol, a dict of still-open (LIVE/PAUSED) ids keyed in creation order.
    Transitions, get, count: O(1). cancel_all / live_orders: O(open orders of that symbol).
    Paused orders stay in the symbol's dict, so a resumed order keeps its creation position."""

    def __init__(self):
        self.orders = {}                       # id -> [symbol, state, seq]
        self.counts = {s: 0 for s in STATES}
        self.open = defaultdict(dict)          # symbol -> {id: seq} for LIVE/PAUSED orders
        self.seq = 0

    def _move(self, oid, new):
        o = self.orders[oid]
        self.counts[o[1]] -= 1
        self.counts[new] += 1
        o[1] = new
        if new == "CANCELLED":
            del self.open[o[0]][oid]

    def create(self, order_id, symbol, side, quantity):
        if order_id in self.orders or side not in ("buy", "sell"):
            return False
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            return False
        self.orders[order_id] = [symbol, "LIVE", self.seq]
        self.open[symbol][order_id] = self.seq
        self.seq += 1
        self.counts["LIVE"] += 1
        return True

    def _transition(self, oid, allowed, new):
        o = self.orders.get(oid)
        if o is None or o[1] not in allowed:
            return False
        self._move(oid, new)
        return True

    def pause(self, order_id):
        return self._transition(order_id, ("LIVE",), "PAUSED")

    def resume(self, order_id):
        return self._transition(order_id, ("PAUSED",), "LIVE")

    def cancel(self, order_id):
        return self._transition(order_id, ("LIVE", "PAUSED"), "CANCELLED")

    def get(self, order_id):
        o = self.orders.get(order_id)
        return o[1] if o else None

    def count(self, state):
        return self.counts.get(state, 0)

    def cancel_all(self, symbol):
        ids = list(self.open.get(symbol, {}))
        for oid in ids:
            self._move(oid, "CANCELLED")
        return len(ids)

    def live_orders(self, symbol):
        # open[symbol] is insertion-ordered by creation, and ids only leave it on cancel
        return [oid for oid in self.open.get(symbol, {}) if self.orders[oid][1] == "LIVE"]
