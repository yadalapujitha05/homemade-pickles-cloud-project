"""
Seed Products Script
Populates DynamoDB Products and Inventory tables with sample product data.

Usage:
    python aws/seed_products.py

Run AFTER dynamodb_setup.py has created the tables.
"""

import boto3
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-south-1",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

# ===== SAMPLE PRODUCT DATA =====
SAMPLE_PRODUCTS = [
    # --- Pickles ---
    {
        "ProductID": "prod-mango-001",
        "Name": "Traditional Mango Pickle",
        "Category": "Pickles",
        "Price": "149",
        "Stock": 50,
        "Description": "Classic South Indian raw mango pickle made with mustard oil, red chili, and secret family spices. Perfect with rice and roti.",
        "ImageURL": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400",
    },
    {
        "ProductID": "prod-lemon-002",
        "Name": "Spicy Lemon Pickle",
        "Category": "Pickles",
        "Price": "129",
        "Stock": 35,
        "Description": "Tangy whole lemon pickle with mustard seeds, asafoetida, and Kashmiri chili. A perfect balance of sour and spice.",
        "ImageURL": "https://images.unsplash.com/photo-1548943487-a2e4e43b4853?w=400",
    },
    {
        "ProductID": "prod-garlic-003",
        "Name": "Garlic Pickle",
        "Category": "Pickles",
        "Price": "179",
        "Stock": 28,
        "Description": "Bold and pungent garlic cloves pickled in sesame oil with fenugreek and black pepper. Great for health benefits too!",
        "ImageURL": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
    },
    {
        "ProductID": "prod-gongura-004",
        "Name": "Gongura Chutney Pickle",
        "Category": "Pickles",
        "Price": "159",
        "Stock": 40,
        "Description": "Andhra-style sorrel leaf pickle with red chilies and sesame. A fiery regional specialty with incredible depth of flavor.",
        "ImageURL": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400",
    },
    {
        "ProductID": "prod-mixed-005",
        "Name": "Mixed Vegetable Pickle",
        "Category": "Pickles",
        "Price": "139",
        "Stock": 60,
        "Description": "A colorful medley of carrot, cauliflower, raw mango, and green chili pickled together in a tangy mustard marinade.",
        "ImageURL": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400",
    },
    {
        "ProductID": "prod-tomato-006",
        "Name": "Tomato Pickle",
        "Category": "Pickles",
        "Price": "119",
        "Stock": 8,   # Low stock - triggers alert
        "Description": "Sun-ripened tomatoes cooked with tamarind, jaggery, and whole spices into a thick, smoky pickle.",
        "ImageURL": "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=400",
    },
    # --- Snacks ---
    {
        "ProductID": "prod-murukku-007",
        "Name": "Crispy Rice Murukku",
        "Category": "Snacks",
        "Price": "99",
        "Stock": 75,
        "Description": "Traditional spiral rice flour murukku fried to golden perfection. Light, crunchy, and mildly spiced with cumin.",
        "ImageURL": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
    },
    {
        "ProductID": "prod-chivda-008",
        "Name": "Spicy Poha Chivda",
        "Category": "Snacks",
        "Price": "89",
        "Stock": 90,
        "Description": "Lightly roasted flattened rice mixed with peanuts, curry leaves, dried coconut, and the perfect blend of spices.",
        "ImageURL": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400",
    },
    {
        "ProductID": "prod-chakli-009",
        "Name": "Wheat Chakli",
        "Category": "Snacks",
        "Price": "109",
        "Stock": 55,
        "Description": "Whole wheat spiral snack seasoned with sesame seeds, ajwain, and red chili. A healthier take on the classic chakli.",
        "ImageURL": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400",
    },
    {
        "ProductID": "prod-kodubale-010",
        "Name": "Karnataka Kodubale",
        "Category": "Snacks",
        "Price": "119",
        "Stock": 45,
        "Description": "Ring-shaped crispy snack from Karnataka made with rice flour and coconut. Mildly spiced with green chilies.",
        "ImageURL": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400",
    },
    {
        "ProductID": "prod-boondi-011",
        "Name": "Masala Boondi",
        "Category": "Snacks",
        "Price": "79",
        "Stock": 100,
        "Description": "Crispy chickpea flour balls seasoned with chaat masala, black salt, and roasted cumin. Perfect tea-time snack.",
        "ImageURL": "https://images.unsplash.com/photo-1606755456205-f699ad80ba77?w=400",
    },
    {
        "ProductID": "prod-namkeen-012",
        "Name": "Rajasthani Namkeen Mix",
        "Category": "Snacks",
        "Price": "129",
        "Stock": 0,   # Out of stock - shows badge
        "Description": "Authentic Rajasthani mixture with sev, boondi, peanuts, and flattened rice tossed in exotic desert spices.",
        "ImageURL": "https://images.unsplash.com/photo-1605333396915-47ed6b68a00e?w=400",
    },
]


def seed_products():
    """Insert all sample products into Products and Inventory tables."""
    products_table = dynamodb.Table("Products")
    inventory_table = dynamodb.Table("Inventory")
    now = datetime.utcnow().isoformat()

    print("\n=== Seeding Products & Inventory ===\n")

    for product in SAMPLE_PRODUCTS:
        # Insert into Products table
        products_table.put_item(Item=product)
        print(f"  ✅ Products: {product['Name']}")

        # Insert into Inventory table (mirrors stock)
        inventory_table.put_item(Item={
            "ProductID": product["ProductID"],
            "Stock": product["Stock"],
            "LastUpdated": now,
        })
        print(f"  ✅ Inventory: {product['ProductID']} → Stock: {product['Stock']}\n")

    print(f"=== Seeding complete! {len(SAMPLE_PRODUCTS)} products loaded. ===\n")
    print("Next step: Run the Flask app with 'gunicorn -c gunicorn_config.py run:app'\n")


def seed_admin_user():
    """Create a default admin user for testing the admin dashboard."""
    import hashlib
    users_table = dynamodb.Table("Users")
    salt = os.environ.get("PASSWORD_SALT", "pickles-salt-2024")

    admin_password = "admin123"
    hashed = hashlib.sha256(f"{salt}{admin_password}".encode()).hexdigest()

    users_table.put_item(Item={
        "UserID": "admin-user-001",
        "Name": "Admin User",
        "Email": "admin@homemadepickles.com",
        "Password": hashed,
        "Address": "Hyderabad, Telangana",
        "Role": "admin",
        "CreatedAt": datetime.utcnow().isoformat(),
        "BrowsingHistory": [],
        "OrderHistory": [],
    })
    print("  ✅ Admin user created: admin@homemadepickles.com / admin123\n")


if __name__ == "__main__":
    seed_products()
    seed_admin_user()
