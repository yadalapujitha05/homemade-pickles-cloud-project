"""
Authentication Utility Helpers
Provides password hashing, session checks, and login decorators.
"""

import hashlib
import os
from functools import wraps
from flask import session, redirect, url_for, flash


def hash_password(password: str) -> str:
    """Hash a plain-text password using SHA-256 with a salt."""
    salt = os.environ.get("PASSWORD_SALT", "pickles-salt-2024")
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(plain_password: str, hashed: str) -> bool:
    """Verify a plain-text password against its hash."""
    return hash_password(plain_password) == hashed


def login_required(f):
    """Decorator: redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: restrict access to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated
