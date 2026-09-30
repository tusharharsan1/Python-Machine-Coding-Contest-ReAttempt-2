from repositories.restaurant_repository import RestaurantRepository


class RestaurantService:
    def __init__(self, restaurant_repository: RestaurantRepository):
        self.restaurant_repository = restaurant_repository

    def mark_item_out_of_stock(self, restaurant_name: str, item_name: str) -> bool:
        """Marks the item as out of stock. Returns False if the restaurant or the item does not exist."""
        return self._set_available(restaurant_name, item_name, False)

    def restock_item(self, restaurant_name: str, item_name: str) -> bool:
        """Marks the item as available again. Returns False if the restaurant or the item does not exist."""
        return self._set_available(restaurant_name, item_name, True)

    def _set_available(self, restaurant_name: str, item_name: str, available: bool) -> bool:
        restaurant = self.restaurant_repository.get_restaurant_by_name(restaurant_name)
        if restaurant is None:
            return False
        for item in restaurant.menu:
            if item.name.lower() == item_name.lower():
                item.is_available = available
                return True
        return False
