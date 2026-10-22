import heapq


class _Seq:
    """Tokens in a doubly linked list over their original positions, plus pair -> set of left positions.
    Positions never move, so sorting a pair's positions gives its left-to-right order."""

    def __init__(self, tokens):
        n = len(tokens)
        self.tok = list(tokens)
        self.nxt = list(range(1, n)) + [-1] if n else []
        self.prv = list(range(-1, n - 1))
        self.pos = {}
        for i in range(n - 1):
            self.pos.setdefault((tokens[i], tokens[i + 1]), set()).add(i)

    def _drop(self, pair, i, touched):
        s = self.pos.get(pair)
        if s is not None and i in s:
            s.discard(i)
            touched.add(pair)

    def _add(self, pair, i, touched):
        self.pos.setdefault(pair, set()).add(i)
        touched.add(pair)

    def merge(self, pair):
        """Merge every non-overlapping occurrence of pair, left to right.
        Returns (pairs whose counts changed, left positions that were merged)."""
        a, b = pair
        new = a + b
        tok, nxt, prv = self.tok, self.nxt, self.prv
        here = self.pos.get(pair, set())
        touched, merged = {pair}, []
        for i in sorted(here):
            if i not in here:            # consumed by the previous merge (overlap)
                continue
            j = nxt[i]
            p, k = prv[i], nxt[j]
            here.discard(i)
            merged.append(i)
            if p != -1:
                self._drop((tok[p], a), p, touched)
            if k != -1:
                self._drop((b, tok[k]), j, touched)
            tok[i], tok[j] = new, None
            nxt[i] = k
            if k != -1:
                prv[k] = i
            if p != -1:
                self._add((tok[p], new), p, touched)
            if k != -1:
                self._add((new, tok[k]), i, touched)
        return touched, merged

    def order(self):
        """Live positions, left to right."""
        out, i = [], 0 if self.tok else -1
        while i != -1:
            out.append(i)
            i = self.nxt[i]
        return out


class BPETokenizer:
    """train: O(L log L + merges * log) amortised: every merge only touches the neighbours of the merged
    occurrences, and a max-heap of (count, pair) with lazy deletion finds the next best pair.
    encode: the same incremental merge per rule, O(rules + L log L). decode: O(output)."""

    def __init__(self):
        self.merges = []
        self.vocab = []          # id -> string
        self.char_id = {}

    def train(self, text, threshold):
        chars = sorted(set(text))
        self.char_id = {c: i for i, c in enumerate(chars)}
        self.vocab = list(chars)
        self.merges = []
        seq = _Seq(list(text))
        heap = [(-len(s), a, b) for (a, b), s in seq.pos.items()]
        heapq.heapify(heap)
        while heap:
            negc, a, b = heapq.heappop(heap)
            cur = len(seq.pos.get((a, b), ()))
            if cur != -negc or cur == 0:
                continue                 # stale entry
            if cur < threshold:
                break
            self.merges.append([a, b])
            self.vocab.append(a + b)
            for pr in seq.merge((a, b))[0]:
                c = len(seq.pos.get(pr, ()))
                if c:
                    heapq.heappush(heap, (-c, pr[0], pr[1]))
        return [list(m) for m in self.merges]

    def encode(self, text):
        C = len(self.char_id)
        seq = _Seq(list(text))
        tid = [self.char_id.get(c, -1) for c in text]
        for r, (a, b) in enumerate(self.merges):
            if seq.pos.get((a, b)):
                _, merged = seq.merge((a, b))
                for i in merged:
                    tid[i] = C + r
        return [tid[i] for i in seq.order()]

    def decode(self, ids):
        out = []
        for x in ids:
            if not isinstance(x, int) or not 0 <= x < len(self.vocab):
                return None
            out.append(self.vocab[x])
        return "".join(out)
