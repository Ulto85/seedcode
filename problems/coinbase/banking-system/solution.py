import heapq


class Bank:
    """Hash maps for balances / spending. top_spenders: O(A log k) with heapq.nsmallest.
    Scheduled payments live in a min-heap keyed by (at, seq): process_until pops only due ones,
    O(log P) each. Cancelled payments are removed lazily."""

    def __init__(self):
        self.balance = {}
        self.spent = {}
        self.clock = 0
        self.seq = 0
        self.heap = []            # (at, seq, payment_id)
        self.pending = {}         # payment_id -> (from, to, amount)

    def create_account(self, account_id):
        if account_id in self.balance:
            return False
        self.balance[account_id] = 0
        self.spent[account_id] = 0
        return True

    def deposit(self, account_id, amount):
        if account_id not in self.balance or amount <= 0:
            return None
        self.balance[account_id] += amount
        return self.balance[account_id]

    def transfer(self, from_id, to_id, amount):
        b = self.balance
        if from_id not in b or to_id not in b or from_id == to_id or amount <= 0 or b[from_id] < amount:
            return None
        b[from_id] -= amount
        b[to_id] += amount
        self.spent[from_id] += amount
        return b[from_id]

    def get_balance(self, account_id):
        return self.balance.get(account_id)

    def top_spenders(self, k):
        if k <= 0:
            return []
        best = heapq.nsmallest(k, self.spent.items(), key=lambda kv: (-kv[1], kv[0]))
        return [[a, s] for a, s in best]

    def schedule_payment(self, from_id, to_id, amount, at):
        b = self.balance
        if from_id not in b or to_id not in b or from_id == to_id or amount <= 0 or at <= self.clock:
            return None
        self.seq += 1
        pid = f"p{self.seq}"
        self.pending[pid] = (from_id, to_id, amount)
        heapq.heappush(self.heap, (at, self.seq, pid))
        return pid

    def cancel_payment(self, payment_id):
        return self.pending.pop(payment_id, None) is not None

    def process_until(self, t):
        if t < self.clock:
            return None
        out = []
        while self.heap and self.heap[0][0] <= t:
            _, _, pid = heapq.heappop(self.heap)
            p = self.pending.pop(pid, None)
            if p is None:                     # cancelled
                continue
            ok = self.transfer(*p) is not None
            out.append([pid, "executed" if ok else "failed"])
        self.clock = t
        return out
