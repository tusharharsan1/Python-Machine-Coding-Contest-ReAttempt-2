from dtos.place_order_request import PlaceOrderRequest
from dtos.place_order_response import PlaceOrderResponse
from models.order import Order
from models.order_item import OrderItem
from repositories.order_repository import OrderRepository
from repositories.restaurant_repository import RestaurantRepository


class OrderService:
    """This class contains all the business logic for placing an order.

    You need to implement the place_order(...) method.
    The repositories are given in the constructor, do NOT change the constructor.
    """

    def __init__(self, restaurant_repository: RestaurantRepository, order_repository: OrderRepository):
        self.restaurant_repository = restaurant_repository
        self.order_repository = order_repository
        self.order_id_counter = 1  # used to give every order its own id

    def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        """Places an order for a customer at a restaurant.

        Returns a PlaceOrderResponse: a success response with the order details, or a failure response
        with a message.
        """

        # TODO Step 1: Find the restaurant with self.restaurant_repository.get_restaurant_by_name(request.restaurant).
        #   If there is no such restaurant (you get None), return:
        #       PlaceOrderResponse.failure("Restaurant not found")
        #   If request.items is empty, return:
        #       PlaceOrderResponse.failure("No items in the order")

        # TODO Step 2: Validate every item of request.items and remember the MenuItem of each one.
        #   Loop over the items. For each item_request (it has item_name and quantity):
        #
        #   a) The quantity must be more than 0.
        #      If not, return: PlaceOrderResponse.failure("Invalid quantity for " + item_request.item_name)
        #
        #   b) Find the matching MenuItem in restaurant.menu. The names must match ignoring upper/lower case.
        #      Hint: compare menu_item.name.lower() with item_request.item_name.lower()
        #      If there is no match, return: PlaceOrderResponse.failure("Item not found: " + item_request.item_name)
        #
        #   c) The MenuItem must be available (menu_item.is_available is True).
        #      If not, return: PlaceOrderResponse.failure(item_request.item_name + " is out of stock")
        #
        #   Check the items one by one in the order of the list, and do NOT save anything yet.

        # TODO Step 3: Calculate the total amount and the estimated delivery time.
        #   - total_amount = sum of (menu_item.price * quantity) for all the items, then made a whole number
        #     with int(...)
        #   - max_prep_time = the biggest menu_item.prep_time among all the items
        #   - estimated_delivery_time = max_prep_time + 10

        # TODO Step 4: Create an Order and save it.
        #   Order(order_id, customer_name, address, restaurant, items, total_amount,
        #         estimated_delivery_time_minutes, status, assigned_delivery_partner)
        #   - order_id: a unique string, for example str(self.order_id_counter) and then add 1 to the counter
        #   - customer_name: request.customer_name
        #   - address: request.address
        #   - restaurant: request.restaurant
        #   - items: a list of OrderItem(item_name, quantity), one for every item of the request
        #   - total_amount and estimated_delivery_time_minutes: calculated in Step 3
        #   - status: "PLACED"
        #   - assigned_delivery_partner: None
        #   Save it with self.order_repository.save(order)

        # TODO Step 5: Return a success response:
        #   PlaceOrderResponse.success(order.order_id, total_amount, estimated_delivery_time)
        #   (and delete the line `return None` below)

        return None
