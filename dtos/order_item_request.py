class OrderItemRequest:
    """One line of the order: which item and how many."""

    def __init__(self, item_name: str, quantity: int):
        self.item_name = item_name
        self.quantity = quantity
