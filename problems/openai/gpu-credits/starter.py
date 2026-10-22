class GPUCredits:
    def __init__(self):
        pass

    def add_credit(self, amount: int, timestamp: int, expiration: int) -> None:
        pass

    def subtract(self, amount: int, timestamp: int) -> None:
        pass

    def get_balance(self, timestamp: int):
        """Return the live balance at `timestamp`, or None after an overdraft."""
        pass
