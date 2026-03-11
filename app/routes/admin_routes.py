"""
Admin Routes
Admin monitoring dashboard: orders, inventory, low-stock alerts.
Access restricted to users with role='admin'.
"""

from flask import Blueprint, render_template
from app.services.order_service import get_all_orders
from app.services.product_service import get_all_products
from app.services.inventory_service import get_low_stock_products
from app.utils.auth_helpers import login_required, admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """
    Admin monitoring dashboard.
    Shows: total orders, inventory summary, low-stock alerts, recent orders.
    Demonstrates real-time cloud data from DynamoDB.
    """
    orders = get_all_orders()
    products = get_all_products()
    low_stock = get_low_stock_products(threshold=10)

    # Summary statistics
    total_orders = len(orders)
    total_revenue = sum(float(o.get("TotalAmount", 0)) for o in orders)
    recent_orders = orders[:10]  # Most recent 10

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        products=products,
        low_stock=low_stock,
        recent_orders=recent_orders,
    )
