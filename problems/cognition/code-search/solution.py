import heapq
import re
from collections import Counter

WORD = re.compile(r"[A-Za-z0-9]+")
SUB = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+")


def tokenize(text):
    return [s.lower() for w in WORD.findall(text) for s in SUB.findall(w)]


class CodeSearch:
    """Inverted index term -> {path: count}, plus each file's term counts for removal.
    add/remove: O(tokens in file). search: O(postings of the rarest term * #terms + m log k)."""

    def __init__(self):
        self.index = {}       # term -> {path: count}
        self.files = {}       # path -> Counter(term)

    def add_file(self, path, content):
        if path in self.files:
            self.remove_file(path)
        counts = Counter(tokenize(content))
        self.files[path] = counts
        for term, c in counts.items():
            self.index.setdefault(term, {})[path] = c

    def remove_file(self, path):
        counts = self.files.pop(path, None)
        if counts is None:
            return False
        for term in counts:
            postings = self.index[term]
            del postings[path]
            if not postings:
                del self.index[term]
        return True

    def search(self, query, k):
        terms = set(tokenize(query))
        if not terms or k <= 0:
            return []
        lists = []
        for t in terms:
            if t not in self.index:
                return []
            lists.append(self.index[t])
        lists.sort(key=len)
        scored = []
        for path, c in lists[0].items():
            total = c
            for other in lists[1:]:
                oc = other.get(path)
                if oc is None:
                    break
                total += oc
            else:
                scored.append((-total, path))
        return [p for _, p in heapq.nsmallest(k, scored)]
