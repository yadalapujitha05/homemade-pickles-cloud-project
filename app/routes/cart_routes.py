"""
Cart Routes
Session-based shopping cart: add, view, update, and clear cart items.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.services.product_service import get_product_by_id
from app.utils.auth_helpers import login_required

cart_bp = Blueprint("cart", __name__)


def get_cart():
    """Return the current user's cart from session."""
    return session.get("cart", [])


def save_cart(cart):
    """Persist the cart back into the session."""
    session["cart"] = cart
    session.modified = True


@cart_bp.route("/")
@login_required
def view_cart():
    """Display the cart with product details and total."""
    cart = get_cart()
    total = sum(float(item["Price"]) * int(item["Quantity"]) for item in cart)
    return render_template("cart/cart.html", cart=cart, total=round(total, 2))


@cart_bp.route("/add/<product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    """Add a product to the session cart."""
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products.catalog"))

    quantity = int(request.form.get("quantity", 1))
    stock = int(product.get("Stock", 0))

    if stock < quantity:
        flash(f"Only {stock} units available.", "warning")
        return redirect(url_for("products.detail", product_id=product_id))

    cart = get_cart()

    # If product already in cart, update quantity
    for item in cart:
        if item["ProductID"] == product_id:
            new_qty = item["Quantity"] + quantity
            if new_qty > stock:
                flash("Not enough stock.", "warning")
                return redirect(url_for("products.detail", product_id=product_id))
            item["Quantity"] = new_qty
            save_cart(cart)
            flash(f"Updated {product['Name']} quantity in cart.", "success")
            return redirect(url_for("cart.view_cart"))

    # New item in cart
    cart.append({
        "ProductID": product_id,
        "Name": product["Name"],
        "Price": str(product["Price"]),
        "Quantity": quantity,
        "ImageURL": product.get("ImageURL", ""),
    })
    save_cart(cart)
    flash(f"{product['Name']} added to cart!", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    """Remove a specific product from the cart."""
    cart = [item for item in get_cart() if item["ProductID"] != product_id]
    save_cart(cart)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/clear", methods=["POST"])
@login_required
def clear_cart():
    """Empty the entire cart."""
    save_cart([])
    flash("Cart cleared.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/count")
def cart_count():
    """API endpoint: return current cart item count as JSON."""
    cart = get_cart()
    count = sum(item["Quantity"] for item in cart)
    return jsonify({"count": count})
