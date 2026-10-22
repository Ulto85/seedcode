import re
from collections import defaultdict, deque

TERM = re.compile(r"([+-]?)([A-Z]+[0-9]+|[0-9]+)")


def parse(value):
    """-> (constant, [(sign, cell), ...])"""
    if not value.startswith("="):
        return int(value), []
    const, refs = 0, []
    for sign, tok in TERM.findall(value[1:]):
        s = -1 if sign == "-" else 1
        if tok[0].isdigit():
            const += s * int(tok)
        else:
            refs.append((s, tok))
    return const, refs


class Spreadsheet:
    """Caches every value and keeps a reverse dependency graph.
    get_cell: O(1).  set_cell: O(A + E_A) where A is the set of cells downstream of the changed cell:
    one BFS finds A (and detects cycles), then Kahn's algorithm re-evaluates A in topological order."""

    def __init__(self):
        self.formula = {}                     # cell -> (const, [(sign, ref)])
        self.users = defaultdict(set)         # cell -> cells whose formula references it
        self.value = {}

    def _downstream(self, cell):
        seen, q = {cell}, deque([cell])
        while q:
            for u in self.users[q.popleft()]:
                if u not in seen:
                    seen.add(u)
                    q.append(u)
        return seen

    def set_cell(self, cell, value):
        const, refs = parse(value)
        affected = self._downstream(cell)
        if any(r in affected for _, r in refs):
            return False
        for _, r in self.formula.get(cell, (0, []))[1]:
            self.users[r].discard(cell)
        for _, r in refs:
            self.users[r].add(cell)
        self.formula[cell] = (const, refs)

        indeg = {c: 0 for c in affected}
        for c in affected:
            for r in {r for _, r in self.formula.get(c, (0, []))[1]}:
                if r in affected:
                    indeg[c] += 1
        q = deque(c for c in affected if indeg[c] == 0)
        while q:
            c = q.popleft()
            k, rs = self.formula.get(c, (0, []))
            self.value[c] = k + sum(s * self.value.get(r, 0) for s, r in rs)
            for u in self.users[c]:
                indeg[u] -= 1
                if indeg[u] == 0:
                    q.append(u)
        return True

    def get_cell(self, cell):
        return self.value.get(cell, 0)
