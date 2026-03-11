"""
User Service
Handles all business logic for user registration, login, and profile management.
Uses DynamoDB Users table via boto3.
"""

from boto3.dynamodb.conditions import Attr
from app.utils.dynamodb_client import get_table
from app.models.user_model import new_user
from app.utils.auth_helpers import hash_password, verify_password


TABLE_NAME = "Users"


def register_user(name: str, email: str, password: str, address: str = "") -> dict:
    """
    Register a new user.
    Returns {'success': True, 'user': {...}} or {'success': False, 'error': '...'}.
    """
    table = get_table(TABLE_NAME)

    # Check if email already exists
    existing = table.scan(FilterExpression=Attr("Email").eq(email))
    if existing.get("Items"):
        return {"success": False, "error": "Email already registered."}

    user = new_user(name, email, hash_password(password), address)
    table.put_item(Item=user)
    return {"success": True, "user": user}


def login_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email and password.
    Returns {'success': True, 'user': {...}} or {'success': False, 'error': '...'}.
    """
    table = get_table(TABLE_NAME)
    result = table.scan(FilterExpression=Attr("Email").eq(email))
    items = result.get("Items", [])

    if not items:
        return {"success": False, "error": "Invalid email or password."}

    user = items[0]
    if not verify_password(password, user["Password"]):
        return {"success": False, "error": "Invalid email or password."}

    return {"success": True, "user": user}


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a user record by UserID."""
    table = get_table(TABLE_NAME)
    result = table.get_item(Key={"UserID": user_id})
    return result.get("Item")


def update_browsing_history(user_id: str, product_id: str):
    """
    Append a product to user's browsing history (max 20 items).
    Used by the recommendation engine.
    """
    table = get_table(TABLE_NAME)
    user = get_user_by_id(user_id)
    if not user:
        return

    history = user.get("BrowsingHistory", [])
    # Avoid duplicates; keep most recent at front
    if product_id in history:
        history.remove(product_id)
    history.insert(0, product_id)
    history = history[:20]  # keep last 20

    table.update_item(
        Key={"UserID": user_id},
        UpdateExpression="SET BrowsingHistory = :h",
        ExpressionAttributeValues={":h": history},
    )


def append_order_to_user(user_id: str, order_id: str):
    """Add an OrderID to user's OrderHistory list."""
    table = get_table(TABLE_NAME)
    table.update_item(
        Key={"UserID": user_id},
        UpdateExpression="SET OrderHistory = list_append(if_not_exists(OrderHistory, :empty), :oid)",
        ExpressionAttributeValues={":oid": [order_id], ":empty": []},
    )
