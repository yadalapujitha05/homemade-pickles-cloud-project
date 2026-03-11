"""
Subscription Service
Handles monthly/weekly delivery subscriptions for users.
"""

from boto3.dynamodb.conditions import Attr
from app.utils.dynamodb_client import get_table
from app.models.subscription_model import new_subscription

TABLE_NAME = "Subscriptions"


def create_subscription(user_id: str, product_id: str, frequency: str) -> dict:
    """
    Create a new subscription.
    Returns the created subscription item.
    """
    table = get_table(TABLE_NAME)
    sub = new_subscription(user_id, product_id, frequency)
    table.put_item(Item=sub)
    return sub


def get_subscriptions_by_user(user_id: str) -> list:
    """Return all active subscriptions for a user."""
    table = get_table(TABLE_NAME)
    result = table.scan(FilterExpression=Attr("UserID").eq(user_id))
    return result.get("Items", [])


def cancel_subscription(subscription_id: str, user_id: str) -> dict:
    """
    Cancel a subscription by setting its status to 'Cancelled'.
    Verifies ownership before updating.
    """
    table = get_table(TABLE_NAME)
    result = table.get_item(Key={"SubscriptionID": subscription_id})
    sub = result.get("Item")

    if not sub or sub["UserID"] != user_id:
        return {"success": False, "error": "Subscription not found."}

    table.update_item(
        Key={"SubscriptionID": subscription_id},
        UpdateExpression="SET #s = :cancelled",
        ExpressionAttributeNames={"#s": "Status"},
        ExpressionAttributeValues={":cancelled": "Cancelled"},
    )
    return {"success": True}
