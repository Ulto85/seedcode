class OrderManager:
    def __init__(self):
        pass

    def create(self, order_id: str, symbol: str, side: str, quantity: int) -> bool:
        pass

    def pause(self, order_id: str) -> bool:
        pass

    def resume(self, order_id: str) -> bool:
        pass

    def cancel(self, order_id: str) -> bool:
        pass

    def get(self, order_id: str):
        pass

    def count(self, state: str) -> int:
        pass

    # ---- Follow-up ----
    def cancel_all(self, symbol: str) -> int:
        pass

    def live_orders(self, symbol: str) -> list:
        pass
