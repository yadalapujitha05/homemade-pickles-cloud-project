"""
Recommendation Service
Generates personalized product recommendations based on:
  1. User's past order history (collaborative signal)
  2. User's browsing history
  3. Popular products (fallback for new users)
"""

from app.services.product_service import get_products_by_ids, get_popular_products, get_all_products
from app.services.order_service import get_orders_by_user
from app.services.user_service import get_user_by_id


def get_recommendations(user_id: str, limit: int = 6) -> list:
    """
    Return a personalized list of recommended products for a user.

    Strategy:
    - Collect product IDs from past orders + browsing history
    - Exclude already-browsed/ordered items (to show new products)
    - Fill remaining slots with popular products
    - Always return in-stock items only
    """
    seen_product_ids = set()
    recommended_ids = []

    # --- Signal 1: Past Orders ---
    orders = get_orders_by_user(user_id)
    for order in orders:
        for item in order.get("Products", []):
            seen_product_ids.add(item["ProductID"])

    # --- Signal 2: Browsing History ---
    user = get_user_by_id(user_id)
    browsing = user.get("BrowsingHistory", []) if user else []
    for pid in browsing:
        seen_product_ids.add(pid)

    # --- Find related products (same category as ordered items) ---
    if seen_product_ids:
        ordered_products = get_products_by_ids(list(seen_product_ids))
        ordered_categories = {p["Category"] for p in ordered_products if p}

        all_products = get_all_products()
        for product in all_products:
            if (
                product["ProductID"] not in seen_product_ids
                and product["Category"] in ordered_categories
                and int(product.get("Stock", 0)) > 0
            ):
                recommended_ids.append(product["ProductID"])
                if len(recommended_ids) >= limit:
                    break

    # --- Fallback: Popular Products ---
    if len(recommended_ids) < limit:
        popular = get_popular_products(limit=limit * 2)
        for p in popular:
            pid = p["ProductID"]
            if pid not in seen_product_ids and pid not in recommended_ids:
                recommended_ids.append(pid)
                if len(recommended_ids) >= limit:
                    break

    return get_products_by_ids(recommended_ids[:limit])
