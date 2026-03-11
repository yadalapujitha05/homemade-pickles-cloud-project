"""
Subscription Routes
Create and manage product delivery subscriptions.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.subscription_service import (
    create_subscription, get_subscriptions_by_user, cancel_subscription
)
from app.services.product_service import get_all_products, get_product_by_id
from app.utils.auth_helpers import login_required

subscription_bp = Blueprint("subscriptions", __name__)


@subscription_bp.route("/")
@login_required
def list_subscriptions():
    """View all subscriptions for the current user."""
    subs = get_subscriptions_by_user(session["user_id"])

    # Enrich with product details
    for sub in subs:
        sub["product"] = get_product_by_id(sub["ProductID"])

    return render_template("subscriptions/list.html", subscriptions=subs)


@subscription_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_subscription():
    """Create a new subscription."""
    products = get_all_products()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        frequency = request.form.get("frequency", "monthly")

        if frequency not in ["weekly", "monthly"]:
            flash("Invalid delivery frequency.", "danger")
            return render_template("subscriptions/new.html", products=products)

        sub = create_subscription(session["user_id"], product_id, frequency)
        flash(f"Subscription created! Next delivery: {sub['NextDelivery'][:10]}", "success")
        return redirect(url_for("subscriptions.list_subscriptions"))

    return render_template("subscriptions/new.html", products=products)


@subscription_bp.route("/cancel/<subscription_id>", methods=["POST"])
@login_required
def cancel(subscription_id):
    """Cancel a subscription."""
    result = cancel_subscription(subscription_id, session["user_id"])
    if result["success"]:
        flash("Subscription cancelled.", "info")
    else:
        flash(result["error"], "danger")
    return redirect(url_for("subscriptions.list_subscriptions"))
