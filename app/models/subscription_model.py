"""
Subscription Model
Defines the data structure for DynamoDB Subscriptions table.
"""

import uuid
from datetime import datetime, timedelta


def new_subscription(user_id: str, product_id: str, frequency: str) -> dict:
    """
    Create a new subscription document.

    Args:
        user_id: The subscribing user's ID.
        product_id: The product to subscribe to.
        frequency: 'weekly' or 'monthly'.
    """
    days = 7 if frequency == "weekly" else 30
    next_delivery = (datetime.utcnow() + timedelta(days=days)).isoformat()

    return {
        "SubscriptionID": str(uuid.uuid4()),
        "UserID": user_id,
        "ProductID": product_id,
        "Frequency": frequency,
        "NextDelivery": next_delivery,
        "Status": "Active",
        "CreatedAt": datetime.utcnow().isoformat(),
    }
