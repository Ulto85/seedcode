def _parse(pattern):
    """'a.b.c.d[/p]' -> (masked 32-bit int, prefix length)."""
    addr, _, plen = pattern.partition("/")
    p = int(plen) if plen else 32
    a, b, c, d = (int(x) for x in addr.split("."))
    value = (a << 24) | (b << 16) | (c << 8) | d
    mask = ((1 << 32) - 1) ^ ((1 << (32 - p)) - 1)
    return value & mask, p


INF = float("inf")


class Firewall:
    """Binary trie over prefix bits. Each node keeps the earliest rule ending there (`rule`) and the
    earliest rule anywhere in its subtree (`best`).
    check: O(32).  check_block: O(32 + nodes visited inside the block), pruning subtrees whose
    rules can't beat the rule already covering them.  Build: O(32 * R)."""

    def __init__(self, rules):
        self.actions = [a for a, _ in rules]
        # node = [child0, child1, rule_idx, best_idx]
        self.root = [None, None, INF, INF]
        for i, (_, pat) in enumerate(rules):
            value, p = _parse(pat)
            node = self.root
            node[3] = min(node[3], i)
            for k in range(p):
                bit = (value >> (31 - k)) & 1
                if node[bit] is None:
                    node[bit] = [None, None, INF, INF]
                node = node[bit]
                node[3] = min(node[3], i)
            node[2] = min(node[2], i)

    def _action(self, idx):
        return "DENY" if idx == INF else self.actions[idx]

    def check(self, ip):
        value, _ = _parse(ip)
        node, best = self.root, self.root[2]
        for k in range(32):
            node = node[(value >> (31 - k)) & 1]
            if node is None:
                break
            best = min(best, node[2])
        return self._action(best)

    def check_block(self, cidr):
        value, p = _parse(cidr)
        node, best = self.root, self.root[2]
        for k in range(p):
            node = node[(value >> (31 - k)) & 1]
            if node is None:
                return self._action(best)
            best = min(best, node[2])
        return self._block(node, best)

    def _block(self, node, best):
        # `best` already includes node's own rule. Only rules earlier than `best` can change anything.
        if node is None or node[3] >= best:
            return self._action(best)
        results = set()
        for child in (node[0], node[1]):
            b = min(best, child[2]) if child is not None else best
            results.add(self._block(child, b))
            if len(results) > 1 or "MIXED" in results:
                return "MIXED"
        return results.pop()
