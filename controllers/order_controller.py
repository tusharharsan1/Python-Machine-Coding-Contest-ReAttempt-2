from dtos.place_order_request import PlaceOrderRequest
from dtos.place_order_response import PlaceOrderResponse
from repositories.order_repository import OrderRepository
from repositories.restaurant_repository import RestaurantRepository
from services.order_service import OrderService


class OrderController:
    def __init__(self):
        self.order_service = OrderService(RestaurantRepository.get_instance(), OrderRepository.get_instance())

    def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        return self.order_service.place_order(request)
