class DeliveryTracker:
    def __init__(self):
        pass

    def add_driver(self, driver_id: int, rate: int) -> bool:
        pass

    def record_delivery(self, driver_id: int, start: int, end: int) -> bool:
        pass

    def get_total_cost(self) -> int:
        pass

    # ---- Part 2 ----
    def pay_up_to(self, time: int) -> int:
        pass

    def get_unpaid_cost(self) -> int:
        pass

    # ---- Follow-up ----
    def max_active_drivers(self, time: int) -> int:
        pass
