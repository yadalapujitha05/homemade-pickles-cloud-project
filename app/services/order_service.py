"""
Order Service
Handles order creation, stock deduction, and order history retrieval.
Orchestrates between inventory, user, and order DynamoDB tables.
"""

from boto3.dynamodb.conditions import Attr
from app.utils.dynamodb_client import get_table
from app.models.order_model import new_order
from app.services.inventory_service import deduct_stock
from app.services.user_service import append_order_to_user

TABLE_NAME = "Orders"


def place_order(user_id: str, cart_items: list) -> dict:
    """
    Place an order for the given cart items.

    Args:
        user_id: The user placing the order.
        cart_items: List of {"ProductID": str, "Name": str, "Price": float, "Quantity": int}

    Returns:
        {'success': True, 'order': {...}} or {'success': False, 'error': str}
    """
    table = get_table(TABLE_NAME)

    # Step 1: Deduct inventory for each item
    deducted = []
    for item in cart_items:
        result = deduct_stock(item["ProductID"], item["Quantity"])
        if not result["success"]:
            # Rollback any already-deducted items
            from app.services.inventory_service import restock_product
            for d in deducted:
                restock_product(d["ProductID"], d["Quantity"])
            return {"success": False, "error": f"{item['Name']}: {result['error']}"}
        deducted.append(item)

    # Step 2: Calculate total
    total = sum(float(i["Price"]) * int(i["Quantity"]) for i in cart_items)

    # Step 3: Create order record
    products_snapshot = [
        {"ProductID": i["ProductID"], "Name": i["Name"],
         "Quantity": i["Quantity"], "Price": str(i["Price"])}
        for i in cart_items
    ]
    order = new_order(user_id, products_snapshot, total)
    table.put_item(Item=order)

    # Step 4: Link order to user history
    append_order_to_user(user_id, order["OrderID"])

    return {"success": True, "order": order}


def get_orders_by_user(user_id: str) -> list:
    """Fetch all orders placed by a specific user."""
    table = get_table(TABLE_NAME)
    result = table.scan(FilterExpression=Attr("UserID").eq(user_id))
    items = result.get("Items", [])
    items.sort(key=lambda x: x.get("OrderDate", ""), reverse=True)
    return items


def get_all_orders() -> list:
    """Fetch all orders (admin use)."""
    table = get_table(TABLE_NAME)
    result = table.scan()
    items = result.get("Items", [])
    items.sort(key=lambda x: x.get("OrderDate", ""), reverse=True)
    return items


def get_order_by_id(order_id: str) -> dict | None:
    """Fetch a single order by OrderID."""
    table = get_table(TABLE_NAME)
    result = table.get_item(Key={"OrderID": order_id})
    return result.get("Item")
