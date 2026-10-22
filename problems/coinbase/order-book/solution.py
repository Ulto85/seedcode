import bisect
from collections import deque


class _Side:
    """One side of the book: price -> FIFO of order ids, price -> total qty,
    and a sorted list of active prices (best price at the END for both sides)."""

    def __init__(self, is_bid):
        self.is_bid = is_bid
        self.queues = {}
        self.totals = {}
        self.prices = []          # sorted so that prices[-1] is the best

    def _key(self, p):
        return p if self.is_bid else -p

    def add(self, price, oid, qty):
        if price not in self.queues:
            self.queues[price] = deque()
            self.totals[price] = 0
            bisect.insort(self.prices, self._key(price))
        self.queues[price].append(oid)
        self.totals[price] += qty

    def drop_level(self, price):
        del self.queues[price], self.totals[price]
        k = self._key(price)
        i = bisect.bisect_left(self.prices, k)
        self.prices.pop(i)

    def best(self):
        if not self.prices:
            return None
        k = self.prices[-1]
        return k if self.is_bid else -k


class OrderBook:
    """Price-time priority book.
    Fills: O(1) each (plus amortised skipping of cancelled ids). New/emptied price level: O(log L)
    search + list shift. cancel: O(1) (lazy: the id stays in its FIFO and is skipped later, unless
    the level becomes empty, which drops it). depth(k): O(k)."""

    def __init__(self):
        self.sides = {"buy": _Side(True), "sell": _Side(False)}
        self.remaining = {}       # resting order id -> remaining qty (only live resting orders)
        self.info = {}            # resting order id -> (side, price)
        self.used = set()

    def _match(self, side, price, qty):
        book = self.sides["sell" if side == "buy" else "buy"]
        fills = []
        while qty > 0:
            best = book.best()
            if best is None or (price is not None and (best > price if side == "buy" else best < price)):
                break
            q = book.queues[best]
            while q and qty > 0:
                oid = q[0]
                rem = self.remaining.get(oid)
                if rem is None:              # cancelled earlier, lazily removed
                    q.popleft()
                    continue
                take = min(qty, rem)
                fills.append([oid, best, take])
                qty -= take
                book.totals[best] -= take
                if take == rem:
                    q.popleft()
                    del self.remaining[oid], self.info[oid]
                else:
                    self.remaining[oid] = rem - take
            if book.totals[best] == 0:
                book.drop_level(best)
        return fills, qty

    def _valid(self, order_id, side, qty):
        return side in self.sides and qty > 0 and order_id not in self.used

    def place(self, order_id, side, price, qty):
        if not self._valid(order_id, side, qty) or price <= 0:
            return None
        self.used.add(order_id)
        fills, left = self._match(side, price, qty)
        if left:
            self.sides[side].add(price, order_id, left)
            self.remaining[order_id] = left
            self.info[order_id] = (side, price)
        return fills

    def place_market(self, order_id, side, qty):
        if not self._valid(order_id, side, qty):
            return None
        self.used.add(order_id)
        return self._match(side, None, qty)[0]

    def cancel(self, order_id):
        if order_id not in self.remaining:
            return False
        side, price = self.info.pop(order_id)
        book = self.sides[side]
        book.totals[price] -= self.remaining.pop(order_id)
        if book.totals[price] == 0:
            book.drop_level(price)
        return True

    def _top(self, side):
        b = self.sides[side].best()
        return None if b is None else [b, self.sides[side].totals[b]]

    def best_bid(self):
        return self._top("buy")

    def best_ask(self):
        return self._top("sell")

    def depth(self, side, levels):
        if side not in self.sides or levels <= 0:
            return []
        book = self.sides[side]
        out = []
        for k in reversed(book.prices[-levels:]):
            p = k if book.is_bid else -k
            out.append([p, book.totals[p]])
        return out
