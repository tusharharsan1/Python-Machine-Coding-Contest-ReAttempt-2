from typing import Dict, Optional

from models.order import Order


class OrderRepository:
    """Keeps all the orders in memory, by order id."""

    _instance: Optional["OrderRepository"] = None

    def __init__(self):
        self.orders: Dict[str, Order] = {}

    @classmethod
    def get_instance(cls) -> "OrderRepository":
        """Returns the one shared OrderRepository (it is created the first time it is asked for)."""
        if cls._instance is None:
            cls._instance = OrderRepository()
        return cls._instance

    def save(self, order: Order) -> None:
        self.orders[order.order_id] = order

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

    def get_all_orders(self) -> Dict[str, Order]:
        return self.orders

    def clear(self) -> None:
        self.orders.clear()
