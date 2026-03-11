"""
Auth Routes
Handles user registration, login, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.user_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        address = request.form.get("address", "").strip()

        if not all([name, email, password]):
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        result = register_user(name, email, password, address)
        if result["success"]:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(result["error"], "danger")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        result = login_user(email, password)
        if result["success"]:
            user = result["user"]
            session["user_id"] = user["UserID"]
            session["user_name"] = user["Name"]
            session["role"] = user.get("Role", "customer")
            flash(f"Welcome back, {user['Name']}!", "success")
            return redirect(url_for("main.home"))
        else:
            flash(result["error"], "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and redirect to home."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
