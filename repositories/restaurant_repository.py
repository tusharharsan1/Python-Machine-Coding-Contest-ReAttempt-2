from typing import List, Optional

from models.restaurant import Restaurant


class RestaurantRepository:
    """Keeps all the restaurants in memory."""

    _instance: Optional["RestaurantRepository"] = None

    def __init__(self):
        self.restaurants: List[Restaurant] = []

    @classmethod
    def get_instance(cls) -> "RestaurantRepository":
        """Returns the one shared RestaurantRepository (it is created the first time it is asked for)."""
        if cls._instance is None:
            cls._instance = RestaurantRepository()
        return cls._instance

    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.restaurants.append(restaurant)

    def get_restaurant_by_name(self, name: str) -> Optional[Restaurant]:
        """Returns the restaurant with this name (upper/lower case does not matter), or None."""
        for restaurant in self.restaurants:
            if restaurant.name.lower() == name.lower():
                return restaurant
        return None

    def clear(self) -> None:
        self.restaurants.clear()
