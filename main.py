"""A small demo of the food delivery platform. Run it with:  python main.py
Nothing to change in this file.
"""
from controllers.order_controller import OrderController
from controllers.restaurant_stock_controller import RestaurantStockController
from dtos.order_item_request import OrderItemRequest
from dtos.place_order_request import PlaceOrderRequest
from dtos.stock_update_request import StockUpdateRequest
from models.menu_item import MenuItem
from models.restaurant import Restaurant
from repositories.restaurant_repository import RestaurantRepository


def main():
    # a restaurant with a small menu
    restaurant = Restaurant("r1", "Pizza Palace", "Bangalore", True)
    restaurant.add_menu_item(MenuItem("Margherita", 250.0, True, 15))
    restaurant.add_menu_item(MenuItem("Garlic Bread", 120.5, True, 8))
    restaurant.add_menu_item(MenuItem("Tiramisu", 180.0, False, 5))  # out of stock
    RestaurantRepository.get_instance().add_restaurant(restaurant)

    order_controller = OrderController()
    stock_controller = RestaurantStockController()

    request = PlaceOrderRequest("Asha", "12 MG Road", "Pizza Palace",
                                [OrderItemRequest("Margherita", 2), OrderItemRequest("Garlic Bread", 1)])
    response = order_controller.place_order(request)
    print("Status:", response.status)
    if response.status == "PLACED":
        print("Order id:", response.order_id, "| total:", response.total_amount,
              "| delivery in", response.estimated_delivery_time_minutes, "minutes")

    request = PlaceOrderRequest("Asha", "12 MG Road", "Pizza Palace", [OrderItemRequest("Tiramisu", 1)])
    print("Ordering an item which is out of stock:", order_controller.place_order(request).status)

    print("Restocking Tiramisu:", stock_controller.restock_item(StockUpdateRequest("Pizza Palace", "Tiramisu")))


if __name__ == "__main__":
    main()
