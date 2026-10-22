def synonym_groups(sentences):
    """Hash each 4-word context to the first word seen there and union every later word with it.
    O(W * alpha) for the unions plus O(W log W) to sort the output; O(W) space."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    first_at = {}
    for s in sentences:
        w = s.split(" ")
        for i in range(2, len(w) - 2):
            word = w[i]
            parent.setdefault(word, word)
            ctx = (w[i - 2], w[i - 1], w[i + 1], w[i + 2])
            other = first_at.setdefault(ctx, word)
            ra, rb = find(word), find(other)
            if ra != rb:
                parent[ra] = rb

    groups = {}
    for word in parent:
        groups.setdefault(find(word), []).append(word)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)
