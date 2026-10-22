"""Forward edges (cell -> referenced cells, with multiplicity) and reverse edges (cell -> dependents).
A set checks for a cycle by searching the dependents of the target, then recomputes only the target's
dependent closure in topological order. get is O(1). set is O(terms + size of the affected subgraph)."""
import re
from collections import Counter

_TOKEN = re.compile(r"\s*([A-Z]+[1-9][0-9]*|[0-9]+|[+-])\s*")


def _parse_formula(body):
    """'A1 + 3 - B2' -> (constant, Counter{cell: coefficient})."""
    toks = _TOKEN.findall(body)
    const, coef, sign = 0, Counter(), 1
    for tok in toks:
        if tok == "+":
            sign = 1
        elif tok == "-":
            sign = -1
        elif tok[0].isdigit():
            const += sign * int(tok)
        else:
            coef[tok] += sign
    return const, coef


def eager_sheet(operations: list) -> list:
    value = {}         # cell -> int (missing = 0)
    formula = {}       # cell -> (const, Counter refs); literals are (n, empty)
    dependents = {}    # cell -> set of cells whose formula references it
    out = []

    def deps_closure_topo(start):
        """Cells reachable from start via dependents, in topological order (start first)."""
        order, seen = [], set()
        stack = [(start, iter(dependents.get(start, ())))]
        seen.add(start)
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                stack.pop()
                order.append(node)
            elif nxt not in seen:
                seen.add(nxt)
                stack.append((nxt, iter(dependents.get(nxt, ()))))
        order.reverse()
        return order, seen

    for op in operations:
        if op[0] == "get":
            out.append(str(value.get(op[1], 0)))
            continue
        _, cell, raw = op
        raw = raw.strip()
        if raw.startswith("="):
            const, coef = _parse_formula(raw[1:])
        else:
            const, coef = int(raw), Counter()
        refs = set(coef)
        _, reach = deps_closure_topo(cell)        # cell and everything depending on it
        if refs & reach:
            out.append("CYCLE")
            continue
        for r in formula.get(cell, (0, Counter()))[1]:
            dependents[r].discard(cell)
        for r in refs:
            dependents.setdefault(r, set()).add(cell)
        formula[cell] = (const, coef)
        order, _ = deps_closure_topo(cell)
        for c in order:
            k, cf = formula[c]
            value[c] = k + sum(m * value.get(r, 0) for r, m in cf.items())
        out.append("OK")
    return out
