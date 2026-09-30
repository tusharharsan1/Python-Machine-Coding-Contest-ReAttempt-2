import unittest

from controllers.order_controller import OrderController
from controllers.restaurant_stock_controller import RestaurantStockController
from dtos.order_item_request import OrderItemRequest
from dtos.place_order_request import PlaceOrderRequest
from dtos.stock_update_request import StockUpdateRequest
from models.menu_item import MenuItem
from models.restaurant import Restaurant
from repositories.order_repository import OrderRepository
from repositories.restaurant_repository import RestaurantRepository
from services.order_service import OrderService


class OrderTestBase(unittest.TestCase):
    """Common setup used by every test class below.

    Before EVERY test we build brand new, empty repositories with these restaurants:

      "Pizza Palace"                                      price   prep time   in stock
          Margherita                                      250.0     15 min       yes
          Garlic Bread                                    120.5      8 min       yes
          Coke                                             60.0      1 min       yes
          Burger                                           99.5     12 min       yes
          Tiramisu                                        180.0      5 min       NO  (out of stock)
      "Burger Barn"
          Burger                                          150.0     20 min       yes
          Fries                                            70.0      6 min       yes
    """

    def setUp(self):
        self.restaurant_repository = RestaurantRepository()
        self.order_repository = OrderRepository()
        self.service = OrderService(self.restaurant_repository, self.order_repository)

        pizza = Restaurant("r1", "Pizza Palace", "Bangalore", True)
        pizza.add_menu_item(MenuItem("Margherita", 250.0, True, 15))
        pizza.add_menu_item(MenuItem("Garlic Bread", 120.5, True, 8))
        pizza.add_menu_item(MenuItem("Coke", 60.0, True, 1))
        pizza.add_menu_item(MenuItem("Burger", 99.5, True, 12))
        pizza.add_menu_item(MenuItem("Tiramisu", 180.0, False, 5))
        self.restaurant_repository.add_restaurant(pizza)

        barn = Restaurant("r2", "Burger Barn", "Bangalore", True)
        barn.add_menu_item(MenuItem("Burger", 150.0, True, 20))
        barn.add_menu_item(MenuItem("Fries", 70.0, True, 6))
        self.restaurant_repository.add_restaurant(barn)

    # ---------- helpers ----------
    def _request(self, items, restaurant="Pizza Palace", customer="Asha", address="12 MG Road"):
        """items = list of (item name, quantity)"""
        return PlaceOrderRequest(customer, address, restaurant,
                                 [OrderItemRequest(name, quantity) for name, quantity in items])

    def _place(self, items, **changes):
        return self.service.place_order(self._request(items, **changes))

    def _saved_orders(self):
        return list(self.order_repository.get_all_orders().values())

    def assert_placed(self, response):
        self.assertEqual("PLACED", response.status)

    def assert_failed(self, response, message):
        """A failed order: FAILED status, the exact message, and NOTHING saved."""
        self.assertEqual("FAILED", response.status)
        self.assertEqual(message, response.message)
        self.assertEqual([], self._saved_orders(), "no order should have been saved")


# ======================================================================================
# 1. Step 1: the restaurant (and the list of items)
# ======================================================================================
class RestaurantCheckTest(OrderTestBase):

    def test_unknown_restaurant_fails(self):
        self.assert_failed(self._place([("Margherita", 1)], restaurant="Nowhere Cafe"), "Restaurant not found")

    def test_restaurant_which_is_not_in_the_repository_at_all(self):
        service = OrderService(RestaurantRepository(), self.order_repository)
        response = service.place_order(self._request([("Margherita", 1)]))
        self.assert_failed(response, "Restaurant not found")

    def test_restaurant_name_ignores_upper_and_lower_case(self):
        for name in ("pizza palace", "PIZZA PALACE", "pIzZa PaLaCe"):
            with self.subTest(name=name):
                self.assert_placed(self._place([("Margherita", 1)], restaurant=name))

    def test_part_of_a_restaurant_name_is_not_enough(self):
        self.assert_failed(self._place([("Margherita", 1)], restaurant="Pizza"), "Restaurant not found")

    def test_the_restaurant_is_checked_before_the_items(self):
        response = self._place([("Nothing", 0), ("Tiramisu", -1)], restaurant="Nowhere Cafe")
        self.assert_failed(response, "Restaurant not found")

    def test_empty_list_of_items_fails(self):
        self.assert_failed(self._place([]), "No items in the order")

    def test_an_item_of_another_restaurant_is_not_found(self):
        # Fries exist only in Burger Barn
        self.assert_failed(self._place([("Fries", 1)], restaurant="Pizza Palace"), "Item not found: Fries")

    def test_the_menu_of_the_chosen_restaurant_is_used(self):
        self.assert_placed(self._place([("Fries", 1)], restaurant="Burger Barn"))


# ======================================================================================
# 2. Step 2: checking every item
# ======================================================================================
class ItemCheckTest(OrderTestBase):

    # ---------- quantity ----------
    def test_quantity_zero_fails(self):
        self.assert_failed(self._place([("Margherita", 0)]), "Invalid quantity for Margherita")

    def test_negative_quantity_fails(self):
        self.assert_failed(self._place([("Coke", -3)]), "Invalid quantity for Coke")

    def test_quantity_one_is_fine(self):
        self.assert_placed(self._place([("Coke", 1)]))

    def test_quantity_message_uses_the_name_as_written_in_the_request(self):
        self.assert_failed(self._place([("mArGhErItA", 0)]), "Invalid quantity for mArGhErItA")

    # ---------- item not on the menu ----------
    def test_unknown_item_fails(self):
        self.assert_failed(self._place([("Sushi", 1)]), "Item not found: Sushi")

    def test_item_name_ignores_upper_and_lower_case(self):
        for name in ("margherita", "MARGHERITA", "gArLiC bReAd"):
            with self.subTest(name=name):
                self.assert_placed(self._place([(name, 1)]))

    def test_not_found_message_uses_the_name_as_written_in_the_request(self):
        self.assert_failed(self._place([("SUSHI roll", 2)]), "Item not found: SUSHI roll")

    def test_part_of_an_item_name_is_not_enough(self):
        self.assert_failed(self._place([("Garlic", 1)]), "Item not found: Garlic")

    # ---------- out of stock ----------
    def test_item_out_of_stock_fails(self):
        self.assert_failed(self._place([("Tiramisu", 1)]), "Tiramisu is out of stock")

    def test_out_of_stock_message_uses_the_name_as_written_in_the_request(self):
        self.assert_failed(self._place([("tiRAmisu", 1)]), "tiRAmisu is out of stock")

    def test_an_item_which_becomes_out_of_stock_cannot_be_ordered(self):
        self.restaurant_repository.get_restaurant_by_name("Pizza Palace").menu[0].is_available = False
        self.assert_failed(self._place([("Margherita", 1)]), "Margherita is out of stock")

    def test_an_item_which_is_back_in_stock_can_be_ordered_again(self):
        item = self.restaurant_repository.get_restaurant_by_name("Pizza Palace").menu[4]  # Tiramisu
        item.is_available = True
        self.assert_placed(self._place([("Tiramisu", 1)]))

    # ---------- several items ----------
    def test_the_first_bad_item_is_reported(self):
        response = self._place([("Margherita", 1), ("Sushi", 1), ("Tiramisu", 1)])
        self.assert_failed(response, "Item not found: Sushi")

    def test_a_bad_item_at_the_end_fails_the_whole_order(self):
        response = self._place([("Margherita", 1), ("Coke", 2), ("Tiramisu", 1)])
        self.assert_failed(response, "Tiramisu is out of stock")

    def test_a_bad_first_item_is_reported_even_if_the_next_one_is_bad_too(self):
        response = self._place([("Tiramisu", 1), ("Sushi", 1)])
        self.assert_failed(response, "Tiramisu is out of stock")

    def test_items_are_checked_one_by_one_in_the_order_of_the_list(self):
        # the first item has a bad quantity, the second one does not exist: the FIRST problem is reported
        self.assert_failed(self._place([("Coke", 0), ("Sushi", 1)]), "Invalid quantity for Coke")
        self.assert_failed(self._place([("Sushi", 1), ("Coke", 0)]), "Item not found: Sushi")

    # ---------- order of the checks for ONE item ----------
    def test_quantity_is_checked_before_the_item_exists(self):
        self.assert_failed(self._place([("Sushi", 0)]), "Invalid quantity for Sushi")

    def test_quantity_is_checked_before_the_stock(self):
        self.assert_failed(self._place([("Tiramisu", 0)]), "Invalid quantity for Tiramisu")

    def test_the_item_is_looked_up_before_the_stock_is_checked(self):
        self.assert_failed(self._place([("Sushi", 1)]), "Item not found: Sushi")


# ======================================================================================
# 3. Step 3: total amount and delivery time
# ======================================================================================
class TotalAndTimeTest(OrderTestBase):

    def test_total_of_a_single_item(self):
        self.assertEqual(250, self._place([("Margherita", 1)]).total_amount)

    def test_total_is_price_times_quantity(self):
        self.assertEqual(750, self._place([("Margherita", 3)]).total_amount)

    def test_total_of_several_items(self):
        response = self._place([("Margherita", 2), ("Coke", 3)])  # 500 + 180
        self.assertEqual(680, response.total_amount)

    def test_total_uses_the_price_of_the_chosen_restaurant(self):
        self.assertEqual(99, self._place([("Burger", 1)], restaurant="Pizza Palace").total_amount)
        self.assertEqual(150, self._place([("Burger", 1)], restaurant="Burger Barn").total_amount)

    def test_the_same_item_in_two_lines_is_counted_twice(self):
        response = self._place([("Coke", 1), ("coke", 2)])
        self.assertEqual(180, response.total_amount)

    def test_decimals_are_dropped_not_rounded(self):
        self.assertEqual(120, self._place([("Garlic Bread", 1)]).total_amount)   # 120.5
        self.assertEqual(99, self._place([("Burger", 1)]).total_amount)          # 99.5

    def test_decimals_are_dropped_only_once_from_the_final_total(self):
        # 99.5 + 120.5 = 220.0. Dropping the decimals of every item first would give 99 + 120 = 219
        self.assertEqual(220, self._place([("Burger", 1), ("Garlic Bread", 1)]).total_amount)

    def test_total_with_decimals_and_quantities(self):
        self.assertEqual(361, self._place([("Garlic Bread", 3)]).total_amount)   # 361.5

    def test_total_is_a_whole_number(self):
        response = self._place([("Garlic Bread", 1)])
        self.assertIs(int, type(response.total_amount))

    def test_delivery_time_of_a_single_item(self):
        self.assertEqual(25, self._place([("Margherita", 1)]).estimated_delivery_time_minutes)  # 15 + 10

    def test_delivery_time_of_a_quick_item(self):
        self.assertEqual(11, self._place([("Coke", 1)]).estimated_delivery_time_minutes)        # 1 + 10

    def test_delivery_time_is_the_longest_preparation_time_plus_ten(self):
        response = self._place([("Coke", 1), ("Margherita", 1), ("Garlic Bread", 1)])
        self.assertEqual(25, response.estimated_delivery_time_minutes)

    def test_delivery_time_does_not_depend_on_the_order_of_the_items(self):
        first = self._place([("Margherita", 1), ("Coke", 1)])
        second = self._place([("Coke", 1), ("Margherita", 1)])
        self.assertEqual(25, first.estimated_delivery_time_minutes)
        self.assertEqual(25, second.estimated_delivery_time_minutes)

    def test_delivery_time_is_not_the_sum_of_the_preparation_times(self):
        response = self._place([("Garlic Bread", 1), ("Burger", 1)])  # 8 and 12
        self.assertEqual(22, response.estimated_delivery_time_minutes)

    def test_delivery_time_does_not_depend_on_the_quantity(self):
        self.assertEqual(25, self._place([("Margherita", 7)]).estimated_delivery_time_minutes)

    def test_delivery_time_uses_the_menu_of_the_chosen_restaurant(self):
        self.assertEqual(22, self._place([("Burger", 1)], restaurant="Pizza Palace").estimated_delivery_time_minutes)
        self.assertEqual(30, self._place([("Burger", 1)], restaurant="Burger Barn").estimated_delivery_time_minutes)


# ======================================================================================
# 4. Step 4 and 5: the saved order and the response
# ======================================================================================
class SavedOrderAndResponseTest(OrderTestBase):

    # ---------- the response ----------
    def test_successful_response(self):
        response = self._place([("Margherita", 2), ("Coke", 1)])
        self.assertEqual("PLACED", response.status)
        self.assertEqual(560, response.total_amount)
        self.assertEqual(25, response.estimated_delivery_time_minutes)

    def test_successful_response_has_an_order_id_and_no_message(self):
        response = self._place([("Margherita", 1)])
        self.assertIsInstance(response.order_id, str)
        self.assertNotEqual("", response.order_id)
        self.assertIsNone(response.message)

    def test_failure_response_has_a_message_no_order_id_and_no_amounts(self):
        response = self._place([("Sushi", 1)])
        self.assertEqual("FAILED", response.status)
        self.assertIsInstance(response.message, str)
        self.assertIsNone(response.order_id)
        self.assertEqual(0, response.total_amount)
        self.assertEqual(0, response.estimated_delivery_time_minutes)

    # ---------- the saved order ----------
    def test_the_order_is_saved(self):
        response = self._place([("Margherita", 1)])
        self.assertEqual(1, len(self._saved_orders()))
        self.assertIsNotNone(self.order_repository.get_order_by_id(response.order_id))

    def test_saved_order_has_the_customer_address_and_restaurant(self):
        response = self._place([("Margherita", 1)], customer="Bala", address="7 Park Street")
        order = self.order_repository.get_order_by_id(response.order_id)
        self.assertEqual("Bala", order.customer_name)
        self.assertEqual("7 Park Street", order.address)
        self.assertEqual("Pizza Palace", order.restaurant)

    def test_saved_order_keeps_the_restaurant_name_as_written_in_the_request(self):
        response = self._place([("Margherita", 1)], restaurant="pizza PALACE")
        self.assertEqual("pizza PALACE", self.order_repository.get_order_by_id(response.order_id).restaurant)

    def test_saved_order_is_for_the_other_restaurant_when_asked(self):
        response = self._place([("Fries", 1)], restaurant="Burger Barn")
        self.assertEqual("Burger Barn", self.order_repository.get_order_by_id(response.order_id).restaurant)

    def test_saved_order_status_is_placed(self):
        response = self._place([("Margherita", 1)])
        self.assertEqual("PLACED", self.order_repository.get_order_by_id(response.order_id).status)

    def test_saved_order_has_the_same_amounts_as_the_response(self):
        response = self._place([("Garlic Bread", 3), ("Coke", 1)])
        order = self.order_repository.get_order_by_id(response.order_id)
        self.assertEqual(response.order_id, order.order_id)
        self.assertEqual(response.total_amount, order.total_amount)
        self.assertEqual(response.estimated_delivery_time_minutes, order.estimated_delivery_time_minutes)
        self.assertEqual(421, order.total_amount)  # 361.5 + 60

    def test_saved_order_has_no_delivery_partner(self):
        response = self._place([("Margherita", 1)])
        self.assertIsNone(self.order_repository.get_order_by_id(response.order_id).assigned_delivery_partner)

    def test_saved_order_has_one_order_item_for_every_line_of_the_request(self):
        response = self._place([("Margherita", 2), ("Coke", 5), ("Burger", 1)])
        items = self.order_repository.get_order_by_id(response.order_id).items
        self.assertEqual([("Margherita", 2), ("Coke", 5), ("Burger", 1)],
                         [(item.item_name, item.quantity) for item in items])

    def test_saved_order_items_keep_the_names_as_written_in_the_request(self):
        response = self._place([("margherita", 1), ("COKE", 2)])
        items = self.order_repository.get_order_by_id(response.order_id).items
        self.assertEqual(["margherita", "COKE"], [item.item_name for item in items])

    def test_two_orders_are_two_saved_orders_with_different_ids(self):
        first = self._place([("Margherita", 1)], customer="Asha")
        second = self._place([("Coke", 2)], customer="Bala")
        self.assertNotEqual(first.order_id, second.order_id)
        self.assertEqual(2, len(self._saved_orders()))
        self.assertEqual("Asha", self.order_repository.get_order_by_id(first.order_id).customer_name)
        self.assertEqual("Bala", self.order_repository.get_order_by_id(second.order_id).customer_name)
        self.assertEqual(250, self.order_repository.get_order_by_id(first.order_id).total_amount)
        self.assertEqual(120, self.order_repository.get_order_by_id(second.order_id).total_amount)

    def test_many_orders_all_get_different_ids(self):
        ids = [self._place([("Coke", 1)]).order_id for _ in range(12)]
        self.assertEqual(12, len(set(ids)))
        self.assertEqual(12, len(self._saved_orders()))

    def test_a_failed_order_does_not_save_anything_and_the_next_order_works(self):
        self.assertEqual("FAILED", self._place([("Sushi", 1)]).status)
        self.assertEqual([], self._saved_orders())
        response = self._place([("Coke", 1)])
        self.assert_placed(response)
        self.assertEqual(1, len(self._saved_orders()))

    def test_failed_orders_between_good_ones_are_not_saved(self):
        first = self._place([("Coke", 1)])
        self._place([("Coke", 1), ("Tiramisu", 1)])
        second = self._place([("Coke", 2)])
        self.assertEqual(2, len(self._saved_orders()))
        self.assertNotEqual(first.order_id, second.order_id)

    # ---------- what must NOT change ----------
    def test_placing_an_order_does_not_change_the_menu(self):
        menu = self.restaurant_repository.get_restaurant_by_name("Pizza Palace").menu
        before = [(m.name, m.price, m.is_available, m.prep_time) for m in menu]
        self.assert_placed(self._place([("Margherita", 2), ("Coke", 1)]))
        self.assertEqual(before, [(m.name, m.price, m.is_available, m.prep_time) for m in menu])

    def test_placing_an_order_does_not_change_the_request(self):
        request = self._request([("Margherita", 2), ("Coke", 1)])
        self.assert_placed(self.service.place_order(request))
        self.assertEqual([("Margherita", 2), ("Coke", 1)], [(i.item_name, i.quantity) for i in request.items])

    def test_the_service_uses_the_repositories_it_was_given(self):
        # a service which reads or writes the shared repositories instead of its own would fail here
        RestaurantRepository.get_instance().clear()
        OrderRepository.get_instance().clear()
        response = self._place([("Margherita", 1)])
        self.assert_placed(response)
        self.assertEqual(1, len(self.order_repository.get_all_orders()))
        self.assertEqual(0, len(OrderRepository.get_instance().get_all_orders()))


# ======================================================================================
# 5. The whole flow through the controllers (they use the shared repositories)
# ======================================================================================
class ControllerFlowTest(unittest.TestCase):

    def setUp(self):
        self.restaurants = RestaurantRepository.get_instance()
        self.orders = OrderRepository.get_instance()
        self.restaurants.clear()
        self.orders.clear()
        pizza = Restaurant("r1", "Pizza Palace", "Bangalore", True)
        pizza.add_menu_item(MenuItem("Margherita", 250.0, True, 15))
        pizza.add_menu_item(MenuItem("Coke", 60.0, True, 1))
        self.restaurants.add_restaurant(pizza)
        self.order_controller = OrderController()
        self.stock_controller = RestaurantStockController()

    def tearDown(self):
        self.restaurants.clear()
        self.orders.clear()

    def _request(self, items):
        return PlaceOrderRequest("Asha", "12 MG Road", "Pizza Palace",
                                 [OrderItemRequest(name, quantity) for name, quantity in items])

    def test_controller_places_an_order(self):
        response = self.order_controller.place_order(self._request([("Margherita", 2), ("Coke", 1)]))
        self.assertEqual("PLACED", response.status)
        self.assertEqual(560, response.total_amount)
        self.assertEqual(25, response.estimated_delivery_time_minutes)

    def test_controller_saves_the_order_in_the_shared_repository(self):
        response = self.order_controller.place_order(self._request([("Coke", 1)]))
        order = self.orders.get_order_by_id(response.order_id)
        self.assertIsNotNone(order)
        self.assertEqual("Asha", order.customer_name)

    def test_controller_returns_the_failure_response(self):
        response = self.order_controller.place_order(self._request([("Sushi", 1)]))
        self.assertEqual("FAILED", response.status)
        self.assertEqual("Item not found: Sushi", response.message)
        self.assertEqual(0, len(self.orders.get_all_orders()))

    def test_controller_fails_for_an_unknown_restaurant(self):
        request = PlaceOrderRequest("Asha", "12 MG Road", "Nowhere", [OrderItemRequest("Coke", 1)])
        response = self.order_controller.place_order(request)
        self.assertEqual("Restaurant not found", response.message)

    def test_an_item_marked_out_of_stock_cannot_be_ordered_until_it_is_restocked(self):
        stock = StockUpdateRequest("Pizza Palace", "margherita")
        self.assertEqual({"status": "SUCCESS"}, self.stock_controller.mark_out_of_stock(stock))
        blocked = self.order_controller.place_order(self._request([("Margherita", 1)]))
        self.assertEqual("FAILED", blocked.status)
        self.assertEqual("Margherita is out of stock", blocked.message)

        self.assertEqual({"status": "SUCCESS"}, self.stock_controller.restock_item(stock))
        allowed = self.order_controller.place_order(self._request([("Margherita", 1)]))
        self.assertEqual("PLACED", allowed.status)


if __name__ == "__main__":
    unittest.main()
