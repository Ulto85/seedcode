"""Directory tree of dicts. add_file is O(depth + name length) amortized: a per-(directory, stem, ext)
counter remembers where the last free-suffix search stopped (safe because names are never freed).
list_entries is O(c log c) for c children."""


class _Dir:
    __slots__ = ("children", "next_k")

    def __init__(self):
        self.children = {}     # name -> _Dir, or None for a file
        self.next_k = {}       # (stem, ext) -> smallest k not yet known to be taken


def _parse(path):
    """List of segments, or None if invalid. '/' -> []."""
    if not isinstance(path, str) or not path.startswith("/"):
        return None
    if path == "/":
        return []
    parts = path[1:].split("/")
    if any(p in ("", ".", "..") for p in parts):
        return None
    return parts


def _split_ext(name):
    dot = name.rfind(".")
    if dot <= 0:
        return name, ""
    return name[:dot], name[dot:]


class FileVault:
    def __init__(self, max_children=None):
        self.root = _Dir()
        self.cap = max_children

    def add_file(self, path: str) -> str:
        parts = _parse(path)
        if not parts:
            return ""
        *dirs, name = parts
        node, i = self.root, 0
        while i < len(dirs) and dirs[i] in node.children:     # walk the existing prefix
            child = node.children[dirs[i]]
            if child is None:
                return ""                                     # a directory segment is a file
            node, i = child, i + 1
        # node gets exactly one new child (a new dir, or the file); new dirs get one child each.
        if self.cap is not None and len(node.children) + 1 > self.cap:
            return ""
        for d in dirs[i:]:
            new = _Dir()
            node.children[d] = new
            node = new
        if name in node.children:
            stem, ext = _split_ext(name)
            k = node.next_k.get((stem, ext), 1)
            while f"{stem}({k}){ext}" in node.children:
                k += 1
            node.next_k[(stem, ext)] = k + 1
            name = f"{stem}({k}){ext}"
        node.children[name] = None
        return "/" + "/".join(dirs + [name])

    def list_entries(self, path: str) -> list:
        parts = _parse(path)
        if parts is None:
            return []
        node = self.root
        for p in parts:
            node = node.children.get(p)
            if node is None:
                return []
        return sorted(node.children)
