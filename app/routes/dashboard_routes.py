"""
Dashboard Routes
User dashboard: profile, order history, subscriptions, recommendations.
"""

from flask import Blueprint, render_template, session
from app.services.order_service import get_orders_by_user
from app.services.subscription_service import get_subscriptions_by_user
from app.services.recommendation_service import get_recommendations
from app.services.user_service import get_user_by_id
from app.services.product_service import get_product_by_id
from app.utils.auth_helpers import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    """User dashboard: aggregates orders, subscriptions, and recommendations."""
    user_id = session["user_id"]

    user = get_user_by_id(user_id)
    orders = get_orders_by_user(user_id)[:5]   # Show last 5 orders
    subs = get_subscriptions_by_user(user_id)
    recommendations = get_recommendations(user_id, limit=4)

    # Enrich subscriptions with product details
    for sub in subs:
        sub["product"] = get_product_by_id(sub["ProductID"])

    return render_template(
        "dashboard/home.html",
        user=user,
        orders=orders,
        subscriptions=subs,
        recommendations=recommendations,
    )
