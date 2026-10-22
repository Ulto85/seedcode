class FileEditor:
    def __init__(self):
        pass

    def create(self, path: str, text: str) -> str:
        pass

    def view(self, path: str, start: int, end: int) -> str:
        pass

    def str_replace(self, path: str, old: str, new: str) -> str:
        pass

    def insert(self, path: str, line: int, text: str) -> str:
        pass

    # ---- Follow-up ----
    def undo(self, path: str) -> str:
        pass
