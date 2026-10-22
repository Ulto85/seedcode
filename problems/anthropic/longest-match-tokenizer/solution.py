def _build_trie(vocab):
    root = {}
    for word, tid in vocab.items():
        node = root
        for ch in word:
            node = node.setdefault(ch, {})
        node[None] = tid            # None key marks "a vocab word ends here"
    return root


def _spans(text, vocab, unk_id):
    """Yield (id, start, end) greedily. Walking the trie from each position costs at most
    L steps (L = longest vocab key): O(n * L) time, O(total vocab chars) space."""
    root = _build_trie(vocab)
    i, n = 0, len(text)
    while i < n:
        node, j = root, i
        best_id, best_end = None, i
        while j < n and text[j] in node:
            node = node[text[j]]
            j += 1
            if None in node:
                best_id, best_end = node[None], j
        if best_id is None:
            yield unk_id, i, i + 1
            i += 1
        else:
            yield best_id, i, best_end
            i = best_end


def tokenize(text, vocab, unk_id):
    return [tid for tid, _, _ in _spans(text, vocab, unk_id)]


def tokenize_spans(text, vocab, unk_id):
    out = []
    prev_unknown = False
    for tid, a, b in _spans(text, vocab, unk_id):
        unknown = tid == unk_id          # unk_id is never a vocab id
        if unknown and prev_unknown:
            out[-1][1] += text[a:b]
        else:
            out.append([tid, text[a:b]])
        prev_unknown = unknown
    return out
