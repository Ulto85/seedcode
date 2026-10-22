class FenceParser:
    """Line-buffered state machine. Each character is buffered once and each complete line is
    classified once, so a whole stream costs O(total input) no matter how it is chunked.
    Space: O(longest line) for the pending partial line."""

    def __init__(self):
        self.pending = []          # pieces of the current, not yet terminated line
        self.fence = None          # (char, length) of the open fence, or None outside code

    @staticmethod
    def _run(line, ch):
        n = 0
        while n < len(line) and line[n] == ch:
            n += 1
        return n

    def _line(self, line, out):
        if self.fence is None:
            for ch in "`~":
                n = self._run(line, ch)
                info = line[n:]
                if n >= 3 and not (ch == "`" and "`" in info):
                    parts = info.split()
                    out.append(["open", parts[0] if parts else ""])
                    self.fence = (ch, n)
                    return
            out.append(["text", line])
        else:
            ch, k = self.fence
            body = line.rstrip(" ")
            if len(body) >= k and self._run(body, ch) == len(body):
                out.append(["close"])
                self.fence = None
            else:
                out.append(["code", line])

    def feed(self, chunk: str) -> list:
        out = []
        start = 0
        while True:
            i = chunk.find("\n", start)
            if i < 0:
                break
            self.pending.append(chunk[start:i])
            line = "".join(self.pending)
            self.pending = []
            self._line(line, out)
            start = i + 1
        if start < len(chunk):
            self.pending.append(chunk[start:])
        return out

    def finish(self) -> list:
        out = []
        line = "".join(self.pending)
        self.pending = []
        if line:
            self._line(line, out)
        if self.fence is not None:
            out.append(["close"])
            self.fence = None
        return out
