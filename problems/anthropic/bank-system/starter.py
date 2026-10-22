class Bank:
    def __init__(self):
        pass

    # ---- Level 1 ----
    def create_account(self, timestamp: int, account_id: str) -> bool:
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int):
        pass

    def pay(self, timestamp: int, account_id: str, amount: int):
        pass

    # ---- Level 2 ----
    def top_activity(self, timestamp: int, k: int) -> list:
        pass

    # ---- Level 3 ----
    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int):
        pass

    def accept_transfer(self, timestamp: int, account_id: str, transfer_id: str) -> bool:
        pass

    # ---- Level 4 ----
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        pass

    def get_balance(self, timestamp: int, account_id: str, time_at: int):
        pass
