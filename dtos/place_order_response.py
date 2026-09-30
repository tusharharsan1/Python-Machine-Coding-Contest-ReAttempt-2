from typing import Optional


class PlaceOrderResponse:
    """The response of placing an order. Do not create it directly, use success(...) or failure(...)."""

    def __init__(self):
        self.status: Optional[str] = None
        self.order_id: Optional[str] = None
        self.total_amount: int = 0
        self.estimated_delivery_time_minutes: int = 0
        self.message: Optional[str] = None

    @classmethod
    def success(cls, order_id: str, total_amount: int, delivery_time: int) -> "PlaceOrderResponse":
        response = cls()
        response.status = "PLACED"
        response.order_id = order_id
        response.total_amount = total_amount
        response.estimated_delivery_time_minutes = delivery_time
        return response

    @classmethod
    def failure(cls, message: str) -> "PlaceOrderResponse":
        response = cls()
        response.status = "FAILED"
        response.message = message
        return response
