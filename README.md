# Place an Order for a Food Delivery Platform

## Problem Statement

You are building the backend for a food delivery platform (like Zomato or Swiggy). As a part of this system, you need to expose a functionality using which a customer can place an order from a restaurant.

## Requirements

1. The request to place an order will contain:
   - `customer_name` – The name of the customer placing the order.
   - `address` – The delivery address.
   - `restaurant` – The name of the restaurant to order from.
   - `items` – A list of items the customer wants to order. Each item has an `item_name` and a `quantity`.

2. The system should validate the order. The restaurant name and the item names are matched ignoring upper/lower case. The checks are done in this order, and the first failing check returns a FAILED response:
   - If the restaurant does not exist, return a FAILED response with message "Restaurant not found".
   - If the list of items is empty, return a FAILED response with message "No items in the order".
   - Then every item of the request is checked one by one, in the order of the list. For each item:
     - If the quantity is less than or equal to 0, return a FAILED response with message "Invalid quantity for {item_name}".
     - If the item does not exist in the restaurant's menu, return a FAILED response with message "Item not found: {item_name}".
     - If the item is present but is currently out of stock (i.e. `is_available` is `False`), return a FAILED response with message "{item_name} is out of stock".
   - `{item_name}` is the name exactly as written in the request.
   - If any check fails, no order should be saved.

3. If the order is valid, the system should:
   - Calculate the total amount: sum of (item price x quantity) for each ordered item. The total is a whole number: drop the decimals (for example 298.5 becomes 298).
   - Calculate estimated delivery time: max preparation time across all ordered items + 10 minutes.
   - Create and save an `Order` object with status "PLACED". Every order needs a unique string id.
   - Return a success `PlaceOrderResponse` with `status = "PLACED"`, `order_id`, `total_amount`, and `estimated_delivery_time_minutes`.

## How This System is Structured

This is a **plain Python project**, there is no database. Instead:
- `RestaurantRepository` and `OrderRepository` keep everything in memory. There is one shared object of each (use `RestaurantRepository.get_instance()` and `OrderRepository.get_instance()`).
- `OrderService` is the class where all the business logic lives, you need to implement the `place_order(request)` method.
- `OrderController` creates an `OrderService` with both repositories and calls `place_order`.

## Instructions (Expected Time: 25 - 30 minutes)

1. Look at `place_order_request.py` and `place_order_response.py` to understand the request and response format.
2. Look at `restaurant.py`, `menu_item.py`, `order.py`, and `order_item.py` to understand the data models.
3. Look at `restaurant_repository.py` and `order_repository.py` to understand how data is stored.
4. Implement the `place_order(request)` method inside `services/order_service.py`. The method skeleton with the steps is already provided in the file.
5. Use `PlaceOrderResponse.success(...)` to return a success response and `PlaceOrderResponse.failure(...)` for error cases.
