class OrderBook:
    def __init__(self):
        pass

    def place(self, order_id: str, side: str, price: int, qty: int):
        pass

    def cancel(self, order_id: str) -> bool:
        pass

    def best_bid(self):
        pass

    def best_ask(self):
        pass

    # ---- Follow-up ----
    def place_market(self, order_id: str, side: str, qty: int):
        pass

    def depth(self, side: str, levels: int) -> list:
        pass
