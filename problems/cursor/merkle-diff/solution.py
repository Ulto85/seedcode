import hashlib


def _build(snapshot):
    """Nested dicts: directory -> {name: subdir dict | file contents str}."""
    root = {}
    for path, contents in snapshot.items():
        *dirs, leaf = path.split("/")
        node = root
        for d in dirs:
            node = node.setdefault(d, {})
        node[leaf] = contents
    return root


def _hash(node, memo):
    """Post-order hash. memo maps id(dir) -> hash so each directory is hashed once."""
    if isinstance(node, str):
        return hashlib.sha256(("blob\0" + node).encode()).hexdigest()
    key = id(node)
    if key not in memo:
        lines = []
        for name in sorted(node):
            child = node[name]
            kind = "blob" if isinstance(child, str) else "tree"
            lines.append(f"{kind} {name} {_hash(child, memo)}\n")
        memo[key] = hashlib.sha256(("tree\0" + "".join(lines)).encode()).hexdigest()
    return memo[key]


def _files(node, prefix, out):
    for name, child in node.items():
        path = prefix + name
        if isinstance(child, str):
            out.append(path)
        else:
            _files(child, path + "/", out)


def repo_diff(snapshot_a: dict, snapshot_b: dict) -> list:
    """Build a Merkle tree for each snapshot, then walk both trees together, skipping any pair of
    directories whose hashes match. Time O(S + N log N) for S bytes of content and N nodes;
    unchanged subtrees cost nothing after hashing. Space O(N)."""
    ta, tb = _build(snapshot_a), _build(snapshot_b)
    ma, mb = {}, {}
    out = []

    def walk(a, b, prefix):
        if _hash(a, ma) == _hash(b, mb):
            return
        for name in a.keys() | b.keys():
            path = prefix + name
            ca, cb = a.get(name), b.get(name)
            a_file, b_file = isinstance(ca, str), isinstance(cb, str)
            if isinstance(ca, dict) and isinstance(cb, dict):
                walk(ca, cb, path + "/")
                continue
            if a_file and b_file:
                if ca != cb:
                    out.append([path, "MODIFIED"])
                continue
            # one side missing, or a file on one side and a directory on the other
            if ca is not None:
                gone = []
                _files({name: ca}, prefix, gone)
                out.extend([p, "REMOVED"] for p in gone)
            if cb is not None:
                new = []
                _files({name: cb}, prefix, new)
                out.extend([p, "ADDED"] for p in new)

    walk(ta, tb, "")
    out.sort()
    return out


def tree_hash(snapshot: dict, path: str):
    """Hash of the file or directory at `path` ("" is the root); None if it doesn't exist.
    Time O(S + N log N) to build and hash the tree."""
    node = _build(snapshot)
    if path:
        for part in path.split("/"):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
    return _hash(node, {})
