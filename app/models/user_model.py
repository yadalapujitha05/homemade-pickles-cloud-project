"""
User Model
Defines the data structure for DynamoDB Users table operations.
"""

import uuid
from datetime import datetime


def new_user(name: str, email: str, hashed_password: str, address: str = "", role: str = "customer") -> dict:
    """Create a new user document for DynamoDB."""
    return {
        "UserID": str(uuid.uuid4()),
        "Name": name,
        "Email": email,
        "Password": hashed_password,
        "Address": address,
        "Role": role,
        "CreatedAt": datetime.utcnow().isoformat(),
        "BrowsingHistory": [],   # List of ProductIDs viewed
        "OrderHistory": [],      # List of OrderIDs placed
    }
