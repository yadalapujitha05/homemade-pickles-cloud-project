"""
Order Model
Defines the data structure for DynamoDB Orders table.
"""

import uuid
from datetime import datetime


def new_order(user_id: str, products: list, total_amount: float) -> dict:
    """
    Create a new order document.

    Args:
        user_id: The ID of the user placing the order.
        products: List of dicts [{"ProductID": ..., "Quantity": ..., "Price": ...}]
        total_amount: Total price of the order.
    """
    return {
        "OrderID": str(uuid.uuid4()),
        "UserID": user_id,
        "Products": products,
        "TotalAmount": str(round(total_amount, 2)),
        "OrderStatus": "Confirmed",
        "OrderDate": datetime.utcnow().isoformat(),
    }
