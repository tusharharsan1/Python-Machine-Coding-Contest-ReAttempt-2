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

        # Step 1: the restaurant must exist and the order must have items
        restaurant = self.restaurant_repository.get_restaurant_by_name(request.restaurant)
        if restaurant is None:
            return PlaceOrderResponse.failure("Restaurant not found")
        if len(request.items) == 0:
            return PlaceOrderResponse.failure("No items in the order")

        # Step 2 and 3: check every item, and calculate the total amount and the longest preparation time
        total = 0
        max_prep_time = 0
        order_items = []
        for item_request in request.items:
            item_name = item_request.item_name

            # a) the quantity must be more than 0
            if item_request.quantity <= 0:
                return PlaceOrderResponse.failure("Invalid quantity for " + item_name)

            # b) the item must be on the menu (upper/lower case does not matter)
            menu_item = None
            for item_on_menu in restaurant.menu:
                if item_on_menu.name.lower() == item_name.lower():
                    menu_item = item_on_menu
                    break
            if menu_item is None:
                return PlaceOrderResponse.failure("Item not found: " + item_name)

            # c) the item must not be out of stock
            if not menu_item.is_available:
                return PlaceOrderResponse.failure(item_name + " is out of stock")

            total = total + menu_item.price * item_request.quantity
            if menu_item.prep_time > max_prep_time:
                max_prep_time = menu_item.prep_time
            order_items.append(OrderItem(item_name, item_request.quantity))

        total_amount = int(total)  # drop the decimals only once, at the end
        estimated_delivery_time = max_prep_time + 10

        # Step 4: create the order and save it
        order = Order(
            order_id=str(self.order_id_counter),
            customer_name=request.customer_name,
            address=request.address,
            restaurant=request.restaurant,
            items=order_items,
            total_amount=total_amount,
            estimated_delivery_time_minutes=estimated_delivery_time,
            status="PLACED",
            assigned_delivery_partner=None,
        )
        self.order_id_counter = self.order_id_counter + 1
        self.order_repository.save(order)

        # Step 5: return the success response
        return PlaceOrderResponse.success(order.order_id, total_amount, estimated_delivery_time)
