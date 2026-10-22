class FileEditor:
    """Files are stored as strings; each file keeps a stack of reverse edits (position, inserted_len,
    removed_text) instead of full snapshots, so undo memory is O(size of the edits).
    Every operation is O(file size) for the scan/rebuild; undo is O(file size)."""

    def __init__(self):
        self.files = {}
        self.history = {}

    def create(self, path, text):
        if path in self.files:
            return "ERROR: file exists"
        self.files[path] = text
        self.history[path] = []
        return "OK"

    def view(self, path, start, end):
        if path not in self.files:
            return "ERROR: no such file"
        lines = self.files[path].split("\n")
        if start < 1 or start > len(lines) or (end != -1 and end < start):
            return "ERROR: invalid range"
        stop = len(lines) if end == -1 else min(end, len(lines))
        return "\n".join(f"{i}|{lines[i - 1]}" for i in range(start, stop + 1))

    def _splice(self, path, pos, remove_len, insert_text):
        text = self.files[path]
        removed = text[pos:pos + remove_len]
        self.files[path] = text[:pos] + insert_text + text[pos + remove_len:]
        self.history[path].append((pos, len(insert_text), removed))

    def str_replace(self, path, old, new):
        if path not in self.files:
            return "ERROR: no such file"
        if old == "":
            return "ERROR: old is empty"
        text = self.files[path]
        n = text.count(old)
        if n == 0:
            return "ERROR: old not found"
        if n > 1:
            return f"ERROR: old found {n} times"
        pos = text.find(old)
        line = text.count("\n", 0, pos) + 1
        self._splice(path, pos, len(old), new)
        return f"OK: line {line}"

    def insert(self, path, line, text):
        if path not in self.files:
            return "ERROR: no such file"
        content = self.files[path]
        lines = content.split("\n")
        if not 0 <= line <= len(lines):
            return "ERROR: invalid line"
        # Same result as lines[:line] + text.split("\n") + lines[line:], expressed as a splice.
        if line == 0:
            self._splice(path, 0, 0, text + "\n")
        else:
            pos = -1
            for _ in range(line):
                pos = content.find("\n", pos + 1)
                if pos == -1:
                    pos = len(content)
                    break
            self._splice(path, pos, 0, "\n" + text)
        return "OK"

    def undo(self, path):
        if path not in self.files:
            return "ERROR: no such file"
        if not self.history[path]:
            return "ERROR: nothing to undo"
        pos, ins_len, removed = self.history[path].pop()
        text = self.files[path]
        self.files[path] = text[:pos] + removed + text[pos + ins_len:]
        return "OK"
