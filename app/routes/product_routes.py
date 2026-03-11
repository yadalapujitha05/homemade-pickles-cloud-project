"""
Product Routes
Product catalog, category browsing, and product detail pages.
"""

from flask import Blueprint, render_template, session
from app.services.product_service import (
    get_all_products, get_products_by_category, get_product_by_id
)
from app.services.user_service import update_browsing_history

product_bp = Blueprint("products", __name__)


@product_bp.route("/")
def catalog():
    """Display full product catalog."""
    products = get_all_products()
    return render_template("products/catalog.html", products=products)


@product_bp.route("/category/<category>")
def by_category(category):
    """Display products filtered by category."""
    products = get_products_by_category(category)
    return render_template("products/catalog.html", products=products, category=category)


@product_bp.route("/<product_id>")
def detail(product_id):
    """Product detail page. Also records browsing history for recommendations."""
    product = get_product_by_id(product_id)
    if not product:
        return render_template("404.html"), 404

    # Track browsing history for logged-in users
    if "user_id" in session:
        update_browsing_history(session["user_id"], product_id)

    return render_template("products/detail.html", product=product)
