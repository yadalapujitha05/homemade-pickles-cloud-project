"""
Main Routes
Home page and general landing views.
"""

from flask import Blueprint, render_template, session
from app.services.product_service import get_all_products, get_products_by_category
from app.services.recommendation_service import get_recommendations

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Home page: show featured products and recommendations."""
    pickles = get_products_by_category("Pickles")[:4]
    snacks = get_products_by_category("Snacks")[:4]

    recommendations = []
    if "user_id" in session:
        recommendations = get_recommendations(session["user_id"], limit=4)

    return render_template(
        "index.html",
        pickles=pickles,
        snacks=snacks,
        recommendations=recommendations,
    )
