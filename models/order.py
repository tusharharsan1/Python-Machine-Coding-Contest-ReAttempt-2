from typing import List, Optional

from models.order_item import OrderItem


class Order:
    def __init__(self, order_id: str, customer_name: str, address: str, restaurant: str,
                 items: List[OrderItem], total_amount: int, estimated_delivery_time_minutes: int,
                 status: str, assigned_delivery_partner: Optional[str] = None):
        self.order_id = order_id
        self.customer_name = customer_name
        self.address = address
        self.restaurant = restaurant
        self.items = items
        self.total_amount = total_amount
        self.estimated_delivery_time_minutes = estimated_delivery_time_minutes
        self.status = status
        self.assigned_delivery_partner = assigned_delivery_partner
