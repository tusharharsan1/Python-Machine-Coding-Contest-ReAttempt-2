class MenuItem:
    def __init__(self, name: str, price: float, is_available: bool, prep_time: int):
        self.name = name
        self.price = price
        self.is_available = is_available  # False = out of stock
        self.prep_time = prep_time        # minutes needed to prepare this item
