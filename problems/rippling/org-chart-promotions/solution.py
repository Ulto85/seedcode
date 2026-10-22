def _tree(n, manager, reportee):
    """Children lists + BFS order and depths (CEO = 1 at level 1). Iterative: chains can be 10^5 deep."""
    children = [[] for _ in range(n + 1)]
    parent = [0] * (n + 1)
    for m, r in zip(manager, reportee):
        children[m].append(r)
        parent[r] = m
    depth = [0] * (n + 1)
    depth[1] = 1
    order = [1]
    for v in order:                       # BFS: order grows while we iterate
        for c in children[v]:
            depth[c] = depth[v] + 1
            order.append(c)
    return children, parent, depth, order


def org_height(n, manager, reportee):
    """BFS from the CEO. O(n) time and space."""
    _, _, depth, _ = _tree(n, manager, reportee)
    return max(depth[1:n + 1])


def min_promotions(n, manager, reportee, h):
    """Greedy, deepest first. Take the deepest employee v not yet fixed; if its level is > h, some promotion on
    v's path must happen, and promoting the ancestor u exactly h-2 levels above v is best: it puts v at level h
    and moves the largest possible subtree (everything in it is no deeper than v, so all of it ends up within h).
    Mark u's subtree fixed and continue. Ancestors via a DFS path stack; O(n) time and space."""
    if h == 1:
        return 0 if n == 1 else -1
    children, parent, depth, order = _tree(n, manager, reportee)
    k = h - 2
    # target[v] = ancestor k levels above v (only needed when depth[v] > h, so it always exists below the CEO)
    target = [0] * (n + 1)
    path = []
    stack = [(1, False)]
    while stack:
        v, done = stack.pop()
        if done:
            path.pop()
            continue
        path.append(v)
        if depth[v] > h:
            target[v] = path[-1 - k]
        stack.append((v, True))
        for c in children[v]:
            stack.append((c, False))
    fixed = [False] * (n + 1)
    moves = 0
    for v in reversed(order):             # BFS order reversed = non-increasing depth
        if depth[v] <= h:
            break
        if fixed[v]:
            continue
        u = target[v]
        moves += 1
        todo = [u]
        while todo:                       # mark u's subtree; stop at parts already marked
            x = todo.pop()
            if fixed[x]:
                continue
            fixed[x] = True
            todo.extend(children[x])
    return moves
