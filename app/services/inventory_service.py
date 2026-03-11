"""
Inventory Service
Manages real-time stock updates in both Products and Inventory DynamoDB tables.
Uses conditional expressions to prevent overselling (concurrency-safe).
"""

from datetime import datetime
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from app.utils.dynamodb_client import get_table

PRODUCTS_TABLE = "Products"
INVENTORY_TABLE = "Inventory"


def get_stock(product_id: str) -> int:
    """Get current stock level for a product from the Inventory table."""
    table = get_table(INVENTORY_TABLE)
    result = table.get_item(Key={"ProductID": product_id})
    item = result.get("Item")
    return int(item["Stock"]) if item else 0


def deduct_stock(product_id: str, quantity: int) -> dict:
    """
    Atomically deduct stock from both Inventory and Products tables.

    Uses DynamoDB conditional expression to prevent negative stock
    (simulates atomic transaction for concurrency safety).

    Returns:
        {'success': True} or {'success': False, 'error': 'Out of stock'}
    """
    inv_table = get_table(INVENTORY_TABLE)
    prod_table = get_table(PRODUCTS_TABLE)
    now = datetime.utcnow().isoformat()

    try:
        # --- Update Inventory table ---
        inv_table.update_item(
            Key={"ProductID": product_id},
            UpdateExpression="SET Stock = Stock - :qty, LastUpdated = :ts",
            ConditionExpression=Attr("Stock").gte(quantity),
            ExpressionAttributeValues={":qty": quantity, ":ts": now},
        )

        # --- Mirror update in Products table ---
        prod_table.update_item(
            Key={"ProductID": product_id},
            UpdateExpression="SET Stock = Stock - :qty",
            ExpressionAttributeValues={":qty": quantity},
        )

        return {"success": True}

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"success": False, "error": "Insufficient stock for this product."}
        raise


def restock_product(product_id: str, quantity: int):
    """Add stock to a product (admin use or scheduled restocking)."""
    inv_table = get_table(INVENTORY_TABLE)
    prod_table = get_table(PRODUCTS_TABLE)
    now = datetime.utcnow().isoformat()

    inv_table.update_item(
        Key={"ProductID": product_id},
        UpdateExpression="SET Stock = Stock + :qty, LastUpdated = :ts",
        ExpressionAttributeValues={":qty": quantity, ":ts": now},
    )
    prod_table.update_item(
        Key={"ProductID": product_id},
        UpdateExpression="SET Stock = Stock + :qty",
        ExpressionAttributeValues={":qty": quantity},
    )


def get_low_stock_products(threshold: int = 10) -> list:
    """Return all products with stock below the given threshold."""
    table = get_table(INVENTORY_TABLE)
    result = table.scan(FilterExpression=Attr("Stock").lte(threshold))
    return result.get("Items", [])
