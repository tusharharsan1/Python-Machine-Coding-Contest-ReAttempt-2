class OrderItem:
    """One line of a saved order."""

    def __init__(self, item_name: str, quantity: int):
        self.item_name = item_name
        self.quantity = quantity
