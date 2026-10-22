import re

REF = re.compile(r"[A-Z][0-9]+")


def run_sheet(ops):
    """Stores parsed contents; each get runs an iterative DFS with a per-read memo and an on-path set.
    get: O(R + L) for R reachable cells/references and L = output length. set: O(len(raw))."""
    cells = {}                     # cell -> ("lit", text) | ("ref", [cells])

    def evaluate(root):
        memo, on_path = {}, set()
        stack = [(root, 0)]
        on_path.add(root)
        while stack:
            cell, i = stack[-1]
            kind, body = cells.get(cell, ("lit", ""))
            if kind == "lit":
                memo[cell] = body
            elif i < len(body):
                stack[-1] = (cell, i + 1)
                nxt = body[i]
                if nxt in on_path:
                    return None
                if nxt not in memo:
                    on_path.add(nxt)
                    stack.append((nxt, 0))
                continue
            else:
                memo[cell] = "".join(memo[r] for r in body)
            on_path.discard(cell)
            stack.pop()
        return memo[root]

    out = []
    for op in ops:
        if op[0] == "set":
            _, cell, raw = op
            cells[cell] = ("ref", REF.findall(raw)) if raw.startswith("=") else ("lit", raw)
            out.append("OK")
        else:
            v = evaluate(op[1])
            out.append("CYCLE" if v is None else "VALUE:" + v)
    return out
