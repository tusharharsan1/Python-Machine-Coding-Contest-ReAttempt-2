from typing import List

from dtos.order_item_request import OrderItemRequest


class PlaceOrderRequest:
    """The request to place an order."""

    def __init__(self, customer_name: str, address: str, restaurant: str, items: List[OrderItemRequest]):
        self.customer_name = customer_name
        self.address = address
        self.restaurant = restaurant
        self.items = items
