class Bank:
    def __init__(self):
        pass

    def create_account(self, account_id: str) -> bool:
        pass

    def deposit(self, account_id: str, amount: int):
        pass

    def transfer(self, from_id: str, to_id: str, amount: int):
        pass

    def get_balance(self, account_id: str):
        pass

    # ---- Part 2 ----
    def top_spenders(self, k: int) -> list:
        pass

    # ---- Follow-up ----
    def schedule_payment(self, from_id: str, to_id: str, amount: int, at: int):
        pass

    def cancel_payment(self, payment_id: str) -> bool:
        pass

    def process_until(self, t: int):
        pass
