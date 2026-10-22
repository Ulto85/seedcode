class ReferralNetwork:
    """Referrals form a forest (each candidate has at most one referrer, no cycles).

    add_user / add_referral: O(α(n)) using union-find over trees; a referral creates a cycle exactly
        when the candidate is the root of the referrer's tree (the candidate has no referrer yet, so it
        is the root of its own tree).
    Queries: reach (subtree size) and depth are recomputed lazily in one O(n) pass after any change,
        then cached; the ranking is sorted once per change, O(n log n). Space O(n)."""

    def __init__(self):
        self.children = {}
        self.parent = {}
        self.dsu = {}          # user -> union-find parent; the DSU root of a tree is its referral root
        self.dirty = True
        self.reach = {}
        self.depth = {}
        self.ranking = []

    def _find(self, u):
        root = u
        while self.dsu[root] != root:
            root = self.dsu[root]
        while self.dsu[u] != root:
            self.dsu[u], u = root, self.dsu[u]
        return root

    def add_user(self, user_id):
        if user_id in self.children:
            return False
        self.children[user_id] = []
        self.dsu[user_id] = user_id
        self.dirty = True
        return True

    def add_referral(self, referrer, candidate):
        if referrer not in self.children or candidate not in self.children:
            return False
        if referrer == candidate or candidate in self.parent:
            return False
        if self._find(referrer) == candidate:
            return False
        self.parent[candidate] = referrer
        self.children[referrer].append(candidate)
        self.dsu[candidate] = self._find(referrer)   # keeps the referral root as DSU root
        self.dirty = True
        return True

    def get_direct_referrals(self, user_id):
        return sorted(self.children.get(user_id, []))

    def _refresh(self):
        if not self.dirty:
            return
        order = [u for u in self.children if u not in self.parent]
        depth = {u: 0 for u in order}
        i = 0
        while i < len(order):
            u = order[i]
            for c in self.children[u]:
                depth[c] = depth[u] + 1
                order.append(c)
            i += 1
        reach = {u: 0 for u in order}
        for u in reversed(order):
            p = self.parent.get(u)
            if p is not None:
                reach[p] += reach[u] + 1
        self.reach, self.depth = reach, depth
        self.ranking = sorted((u for u in reach if reach[u] > 0), key=lambda u: (-reach[u], u))
        self.dirty = False

    def total_referral_count(self, user_id):
        if user_id not in self.children:
            return 0
        self._refresh()
        return self.reach[user_id]

    def top_referrers_by_reach(self, k):
        if k <= 0:
            return []
        self._refresh()
        return [[u, self.reach[u]] for u in self.ranking[:k]]

    def flow_centrality(self, user_id):
        if user_id not in self.children:
            return 0
        self._refresh()
        return self.depth[user_id] * self.reach[user_id]
