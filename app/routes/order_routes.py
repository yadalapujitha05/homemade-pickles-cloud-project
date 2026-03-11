"""
Order Routes
Checkout process, order confirmation, and order history.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.services.order_service import place_order, get_orders_by_user, get_order_by_id
from app.utils.auth_helpers import login_required

order_bp = Blueprint("orders", __name__)


@order_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    """
    Process the checkout:
    1. Read cart from session
    2. Place order (deduct inventory)
    3. Clear cart on success
    4. Show confirmation
    """
    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view_cart"))

    result = place_order(session["user_id"], cart)

    if result["success"]:
        session["cart"] = []   # Clear cart after successful order
        session.modified = True
        order = result["order"]
        flash(f"Order #{order['OrderID'][:8]} placed successfully!", "success")
        return redirect(url_for("orders.confirmation", order_id=order["OrderID"]))
    else:
        flash(f"Order failed: {result['error']}", "danger")
        return redirect(url_for("cart.view_cart"))


@order_bp.route("/confirmation/<order_id>")
@login_required
def confirmation(order_id):
    """Order confirmation page."""
    order = get_order_by_id(order_id)
    if not order or order["UserID"] != session["user_id"]:
        flash("Order not found.", "danger")
        return redirect(url_for("main.home"))
    return render_template("orders/confirmation.html", order=order)


@order_bp.route("/history")
@login_required
def history():
    """Show all past orders for the logged-in user."""
    orders = get_orders_by_user(session["user_id"])
    return render_template("orders/history.html", orders=orders)
