import heapq
from bisect import bisect_right

TTL = 1000


class Bank:
    """balance/activity: dicts over live accounts.
    history[id]: ([times], [balance or None]) appended in time order -> get_balance is a binary search.
    Pending transfers expire lazily via a min-heap on expiry time, processed before each call.
    Most ops O(1) amortized (+ O(log T) heap); top_activity O(A log k); merge O(#pending); get_balance O(log H)."""

    def __init__(self):
        self.balance = {}
        self.activity = {}
        self.history = {}
        self.pending = {}          # transfer_id -> [source, target, amount]
        self.expiry = []           # heap of (expires_at, transfer_id)
        self.count = 0

    # ---------- helpers ----------
    def _record(self, ts, acc, value):
        times, vals = self.history.setdefault(acc, ([], []))
        if times and times[-1] == ts:
            vals[-1] = value
        else:
            times.append(ts)
            vals.append(value)

    def _set_balance(self, ts, acc, value):
        self.balance[acc] = value
        self._record(ts, acc, value)

    def _expire(self, ts):
        while self.expiry and self.expiry[0][0] <= ts:
            at, tid = heapq.heappop(self.expiry)
            if tid in self.pending:
                src, _, amount = self.pending.pop(tid)
                self._set_balance(at, src, self.balance[src] + amount)

    # ---------- Level 1 ----------
    def create_account(self, timestamp, account_id):
        self._expire(timestamp)
        if account_id in self.balance:
            return False
        self.activity[account_id] = 0
        self._set_balance(timestamp, account_id, 0)
        return True

    def deposit(self, timestamp, account_id, amount):
        self._expire(timestamp)
        if account_id not in self.balance:
            return None
        self.activity[account_id] += amount
        self._set_balance(timestamp, account_id, self.balance[account_id] + amount)
        return self.balance[account_id]

    def pay(self, timestamp, account_id, amount):
        self._expire(timestamp)
        if account_id not in self.balance or self.balance[account_id] < amount:
            return None
        self.activity[account_id] += amount
        self._set_balance(timestamp, account_id, self.balance[account_id] - amount)
        return self.balance[account_id]

    # ---------- Level 2 ----------
    def top_activity(self, timestamp, k):
        self._expire(timestamp)
        best = heapq.nsmallest(k, self.activity.items(), key=lambda kv: (-kv[1], kv[0]))
        return [f"{acc}({act})" for acc, act in best]

    # ---------- Level 3 ----------
    def transfer(self, timestamp, source_id, target_id, amount):
        self._expire(timestamp)
        if (source_id == target_id or source_id not in self.balance
                or target_id not in self.balance or self.balance[source_id] < amount):
            return None
        self._set_balance(timestamp, source_id, self.balance[source_id] - amount)
        self.count += 1
        tid = f"transfer{self.count}"
        self.pending[tid] = [source_id, target_id, amount]
        heapq.heappush(self.expiry, (timestamp + TTL, tid))
        return tid

    def accept_transfer(self, timestamp, account_id, transfer_id):
        self._expire(timestamp)
        t = self.pending.get(transfer_id)
        if t is None or t[1] != account_id:
            return False
        src, dst, amount = self.pending.pop(transfer_id)
        self._set_balance(timestamp, dst, self.balance[dst] + amount)
        self.activity[src] += amount
        self.activity[dst] += amount
        return True

    # ---------- Level 4 ----------
    def merge_accounts(self, timestamp, account_id_1, account_id_2):
        self._expire(timestamp)
        a, b = account_id_1, account_id_2
        if a == b or a not in self.balance or b not in self.balance:
            return False
        new_balance = self.balance[a] + self.balance[b]
        for tid in list(self.pending):
            t = self.pending[tid]
            if t[0] == b:
                t[0] = a
            if t[1] == b:
                t[1] = a
            if t[0] == t[1]:                      # transfer between the two: cancel + refund
                new_balance += t[2]
                del self.pending[tid]
        self.activity[a] += self.activity.pop(b)
        del self.balance[b]
        self._record(timestamp, b, None)
        self._set_balance(timestamp, a, new_balance)
        return True

    def get_balance(self, timestamp, account_id, time_at):
        self._expire(timestamp)
        if account_id not in self.history:
            return None
        times, vals = self.history[account_id]
        i = bisect_right(times, time_at) - 1
        return vals[i] if i >= 0 else None
