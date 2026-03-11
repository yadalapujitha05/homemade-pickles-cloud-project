"""
Flask Application Factory
Creates and configures the Flask app with all blueprints registered.
"""

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Secret key for session management
    app.secret_key = os.environ.get("SECRET_KEY", "homemade-pickles-secret-2024")

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.order_routes import order_bp
    from app.routes.subscription_routes import subscription_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(subscription_bp, url_prefix="/subscriptions")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # Home route registered on main app
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app
