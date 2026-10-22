class ChunkCache:
    def __init__(self, capacity: int):
        pass

    def read(self, chunk_hash: str, size: int) -> bool:
        pass

    def used(self) -> int:
        pass

    def stats(self) -> list:
        """Return [hits, misses, bytes_fetched]."""
        pass

    # Follow-up
    def mount(self, container_id: str, chunks: list) -> int:
        pass

    def unmount(self, container_id: str) -> bool:
        pass
