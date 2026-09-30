from typing import Dict

from dtos.stock_update_request import StockUpdateRequest
from repositories.restaurant_repository import RestaurantRepository
from services.restaurant_service import RestaurantService


class RestaurantStockController:
    def __init__(self):
        self.restaurant_service = RestaurantService(RestaurantRepository.get_instance())

    def mark_out_of_stock(self, request: StockUpdateRequest) -> Dict[str, str]:
        success = self.restaurant_service.mark_item_out_of_stock(request.restaurant_name, request.item_name)
        return {"status": "SUCCESS" if success else "FAILED"}

    def restock_item(self, request: StockUpdateRequest) -> Dict[str, str]:
        success = self.restaurant_service.restock_item(request.restaurant_name, request.item_name)
        return {"status": "SUCCESS" if success else "FAILED"}
