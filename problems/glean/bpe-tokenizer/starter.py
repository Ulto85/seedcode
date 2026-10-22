class BPETokenizer:
    def __init__(self):
        pass

    def train(self, text: str, threshold: int) -> list:
        """Return the merge rules learned, in order, each as [left, right]."""
        pass

    # ---- Part 2 ----
    def encode(self, text: str) -> list:
        pass

    def decode(self, ids: list):
        """Return the decoded string, or None if any id is unknown."""
        pass
