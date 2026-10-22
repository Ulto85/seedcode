import re

NAME = re.compile(r"[A-Za-z0-9._-]+\Z")
ARGS = {"mkdir": 1, "touch": 1, "ls": 1, "rm": 1, "rmdir": 1, "cd": 1, "pwd": 0}


class Node:
    __slots__ = ("name", "parent", "children")

    def __init__(self, name, parent, is_dir):
        self.name = name
        self.parent = parent
        self.children = {} if is_dir else None   # None marks a file

    @property
    def is_dir(self):
        return self.children is not None


class FileSystem:
    """A tree of nodes; each directory maps child name -> node.

    Every operation is one path parse plus one walk: O(L) for a path with L components, plus
    O(k log k) for ls on a directory with k entries. pwd is O(depth). execute is the sum of its commands.
    """

    def __init__(self):
        self.root = Node("", None, True)
        self.root.parent = self.root          # ".." at the root stays at the root
        self.cwd = self.root

    # ---- path handling: one parser, one walker ----
    def _parse(self, path):
        """Return (start_node, components) or None if the path is syntactically invalid."""
        if not path:
            return None
        if path == "/":
            return self.root, []
        absolute = path.startswith("/")
        parts = path[1:].split("/") if absolute else path.split("/")
        if any(not NAME.match(p) for p in parts):
            return None
        return (self.root if absolute else self.cwd), parts

    def _step(self, node, comp):
        if comp == ".":
            return node
        if comp == "..":
            return node.parent
        return node.children.get(comp)

    def _walk(self, path):
        """Resolve all but the last component. Returns (error, parent_dir, last_component_or_None)."""
        parsed = self._parse(path)
        if parsed is None:
            return "error: invalid path", None, None
        node, parts = parsed
        if not parts:
            return None, None, None                  # the root itself
        for comp in parts[:-1]:
            nxt = self._step(node, comp)
            if nxt is None:
                return "error: not found", None, None
            if not nxt.is_dir:
                return "error: not a directory", None, None
            node = nxt
        return None, node, parts[-1]

    def _target(self, path):
        """Resolve the whole path. Returns (error, node); node is None if the last component is missing."""
        err, parent, last = self._walk(path)
        if err:
            return err, None
        if parent is None:
            return None, self.root
        return None, self._step(parent, last)

    # ---- Part 1 ----
    def _create(self, path, is_dir):
        err, parent, last = self._walk(path)
        if err:
            return err
        if parent is None or last in (".", "..") or last in parent.children:
            return "error: already exists"
        parent.children[last] = Node(last, parent, is_dir)
        return "ok"

    def mkdir(self, path: str) -> str:
        return self._create(path, True)

    def touch(self, path: str) -> str:
        return self._create(path, False)

    def ls(self, path: str):
        err, node = self._target(path)
        if err:
            return err
        if node is None:
            return "error: not found"
        return sorted(node.children) if node.is_dir else [node.name]

    # ---- Part 2 ----
    def _removable(self, path):
        if path.rsplit("/", 1)[-1] in (".", ".."):
            return "error: invalid path", None
        err, node = self._target(path)
        if err:
            return err, None
        if node is None:
            return "error: not found", None
        return None, node

    def rm(self, path: str) -> str:
        err, node = self._removable(path)
        if err:
            return err
        if node.is_dir:
            return "error: is a directory"
        del node.parent.children[node.name]
        return "ok"

    def rmdir(self, path: str) -> str:
        err, node = self._removable(path)
        if err:
            return err
        if node is self.root:
            return "error: cannot remove root"
        if not node.is_dir:
            return "error: not a directory"
        if node.children:
            return "error: not empty"
        if node is self.cwd:
            return "error: busy"
        del node.parent.children[node.name]
        return "ok"

    def execute(self, commands: list) -> list:
        out = []
        for line in commands:
            tokens = line.split()
            if not tokens or tokens[0] not in ARGS:
                out.append("error: unknown command")
            elif len(tokens) - 1 != ARGS[tokens[0]]:
                out.append("error: wrong number of arguments")
            else:
                res = getattr(self, tokens[0])(*tokens[1:])
                out.append(" ".join(res) if isinstance(res, list) else res)
        return out

    # ---- Follow-up ----
    def cd(self, path: str) -> str:
        err, node = self._target(path)
        if err:
            return err
        if node is None:
            return "error: not found"
        if not node.is_dir:
            return "error: not a directory"
        self.cwd = node
        return "ok"

    def pwd(self) -> str:
        names, node = [], self.cwd
        while node is not self.root:
            names.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(names))
