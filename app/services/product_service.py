"""
Product Service
Handles all product catalog operations: listing, searching, and detail fetching.
Reads from DynamoDB Products table.
"""

from boto3.dynamodb.conditions import Attr
from app.utils.dynamodb_client import get_table

TABLE_NAME = "Products"


def get_all_products() -> list:
    """Return all products from the catalog."""
    table = get_table(TABLE_NAME)
    result = table.scan()
    return result.get("Items", [])


def get_products_by_category(category: str) -> list:
    """Return products filtered by category (e.g., 'Pickles', 'Snacks')."""
    table = get_table(TABLE_NAME)
    result = table.scan(FilterExpression=Attr("Category").eq(category))
    return result.get("Items", [])


def get_product_by_id(product_id: str) -> dict | None:
    """Fetch a single product by its ProductID."""
    table = get_table(TABLE_NAME)
    result = table.get_item(Key={"ProductID": product_id})
    return result.get("Item")


def get_products_by_ids(product_ids: list) -> list:
    """Fetch multiple products given a list of ProductIDs."""
    return [p for pid in product_ids if (p := get_product_by_id(pid)) is not None]


def get_popular_products(limit: int = 5) -> list:
    """
    Return products sorted by popularity (low stock = high demand proxy).
    In a production system this would use order frequency data.
    """
    products = get_all_products()
    # Sort: products with stock > 0 first, then by lowest stock (most ordered proxy)
    in_stock = [p for p in products if int(p.get("Stock", 0)) > 0]
    in_stock.sort(key=lambda x: int(x.get("Stock", 0)))
    return in_stock[:limit]
