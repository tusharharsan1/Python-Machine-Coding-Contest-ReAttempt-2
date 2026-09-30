from typing import List

from models.menu_item import MenuItem


class Restaurant:
    def __init__(self, id: str, name: str, location: str, is_open: bool):
        self.id = id
        self.name = name
        self.location = location
        self.is_open = is_open
        self.menu: List[MenuItem] = []

    def add_menu_item(self, item: MenuItem) -> None:
        self.menu.append(item)
