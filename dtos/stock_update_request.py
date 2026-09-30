class StockUpdateRequest:
    """The request to mark an item of a restaurant as out of stock (or back in stock)."""

    def __init__(self, restaurant_name: str, item_name: str):
        self.restaurant_name = restaurant_name
        self.item_name = item_name
