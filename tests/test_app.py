"""
Test Suite for HomeMade Pickles & Snacks
Tests cover: user auth, product catalog, cart, orders, subscriptions, recommendations.

Usage:
    python -m pytest tests/ -v

Note: These tests use mocking to avoid real AWS DynamoDB calls.
      For integration testing against real DynamoDB, set USE_REAL_DB=1 in env.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from app import create_app


# ===== TEST FIXTURES =====

@pytest.fixture
def app():
    """Create a test Flask app instance."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def mock_product():
    """Sample product data matching DynamoDB schema."""
    return {
        "ProductID": "prod-test-001",
        "Name": "Test Mango Pickle",
        "Category": "Pickles",
        "Price": "149",
        "Stock": 25,
        "Description": "Test pickle description for unit testing.",
        "ImageURL": "https://example.com/test.jpg",
    }


@pytest.fixture
def mock_user():
    """Sample user data."""
    return {
        "UserID": "user-test-001",
        "Name": "Test User",
        "Email": "test@example.com",
        "Password": "hashed_password",
        "Role": "customer",
        "BrowsingHistory": [],
        "OrderHistory": [],
    }


# ===== 1. HOME PAGE TEST =====

def test_home_page_loads(client):
    """Test that the home page returns HTTP 200."""
    with patch("app.routes.main_routes.get_products_by_category", return_value=[]):
        with patch("app.routes.main_routes.get_recommendations", return_value=[]):
            response = client.get("/")
            assert response.status_code == 200
            assert b"HomeMade Pickles" in response.data


# ===== 2. USER REGISTRATION TEST =====

def test_register_page_loads(client):
    """Registration form page should load correctly."""
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_register_new_user(client):
    """Successful registration should redirect to login."""
    with patch("app.routes.auth_routes.register_user") as mock_reg:
        mock_reg.return_value = {
            "success": True,
            "user": {"UserID": "new-001", "Name": "Alice", "Email": "alice@test.com"}
        }
        response = client.post("/auth/register", data={
            "name": "Alice",
            "email": "alice@test.com",
            "password": "password123",
            "address": "Hyderabad",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Registration successful" in response.data


def test_register_duplicate_email(client):
    """Duplicate email registration should show error."""
    with patch("app.routes.auth_routes.register_user") as mock_reg:
        mock_reg.return_value = {"success": False, "error": "Email already registered."}
        response = client.post("/auth/register", data={
            "name": "Bob",
            "email": "existing@test.com",
            "password": "password123",
            "address": "",
        })
        assert b"Email already registered" in response.data


# ===== 3. LOGIN TEST =====

def test_login_page_loads(client):
    """Login page should load."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_success(client, mock_user):
    """Valid credentials should log in and redirect to home."""
    with patch("app.routes.auth_routes.login_user") as mock_login:
        mock_login.return_value = {"success": True, "user": mock_user}
        response = client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Welcome back" in response.data


def test_login_invalid_credentials(client):
    """Invalid credentials should show error."""
    with patch("app.routes.auth_routes.login_user") as mock_login:
        mock_login.return_value = {"success": False, "error": "Invalid email or password."}
        response = client.post("/auth/login", data={
            "email": "wrong@test.com",
            "password": "wrongpass",
        })
        assert b"Invalid email or password" in response.data


# ===== 4. PRODUCT CATALOG TEST =====

def test_product_catalog_loads(client, mock_product):
    """Catalog page should display products."""
    with patch("app.routes.product_routes.get_all_products", return_value=[mock_product]):
        response = client.get("/products/")
        assert response.status_code == 200
        assert b"Test Mango Pickle" in response.data


def test_product_detail_loads(client, mock_product):
    """Product detail page should display product information."""
    with patch("app.routes.product_routes.get_product_by_id", return_value=mock_product):
        with patch("app.routes.product_routes.update_browsing_history"):
            response = client.get("/products/prod-test-001")
            assert response.status_code == 200
            assert b"Test Mango Pickle" in response.data


def test_product_not_found(client):
    """Non-existent product should return 404."""
    with patch("app.routes.product_routes.get_product_by_id", return_value=None):
        response = client.get("/products/nonexistent-id")
        assert response.status_code == 404


def test_category_filter(client, mock_product):
    """Category filter should return only matching products."""
    with patch("app.routes.product_routes.get_products_by_category", return_value=[mock_product]):
        response = client.get("/products/category/Pickles")
        assert response.status_code == 200
        assert b"Test Mango Pickle" in response.data


# ===== 5. CART TESTS =====

def test_cart_requires_login(client):
    """Cart page should redirect unauthenticated users."""
    response = client.get("/cart/")
    assert response.status_code == 302  # Redirect to login


def test_add_to_cart(client, mock_product):
    """Logged-in user should be able to add items to cart."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["user_name"] = "Test User"
        sess["role"] = "customer"

    with patch("app.routes.cart_routes.get_product_by_id", return_value=mock_product):
        response = client.post(
            "/cart/add/prod-test-001",
            data={"quantity": "2"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"added to cart" in response.data


def test_cart_shows_items(client, mock_product):
    """Cart page should display items added to session cart."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["user_name"] = "Test User"
        sess["role"] = "customer"
        sess["cart"] = [{
            "ProductID": "prod-test-001",
            "Name": "Test Mango Pickle",
            "Price": "149",
            "Quantity": 2,
            "ImageURL": "",
        }]

    response = client.get("/cart/")
    assert response.status_code == 200
    assert b"Test Mango Pickle" in response.data
    assert b"298" in response.data  # 149 * 2


# ===== 6. CHECKOUT & INVENTORY DEDUCTION TEST =====

def test_checkout_deducts_inventory(client):
    """Placing an order should call place_order which deducts inventory."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["user_name"] = "Test User"
        sess["role"] = "customer"
        sess["cart"] = [{
            "ProductID": "prod-test-001",
            "Name": "Test Mango Pickle",
            "Price": "149",
            "Quantity": 1,
        }]

    with patch("app.routes.order_routes.place_order") as mock_order:
        mock_order.return_value = {
            "success": True,
            "order": {
                "OrderID": "order-test-001",
                "UserID": "user-test-001",
                "Products": [{"ProductID": "prod-test-001", "Name": "Test Mango Pickle", "Quantity": 1, "Price": "149"}],
                "TotalAmount": "149.00",
                "OrderStatus": "Confirmed",
                "OrderDate": "2024-01-01T00:00:00",
            }
        }
        response = client.post("/orders/checkout", follow_redirects=False)
        assert response.status_code == 302  # Redirect to confirmation
        mock_order.assert_called_once()  # Verify order was placed


def test_checkout_out_of_stock(client):
    """Checkout should fail if product is out of stock."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["cart"] = [{"ProductID": "prod-out", "Name": "Out Item", "Price": "100", "Quantity": 5}]

    with patch("app.routes.order_routes.place_order") as mock_order:
        mock_order.return_value = {"success": False, "error": "Insufficient stock"}
        response = client.post("/orders/checkout", follow_redirects=True)
        assert b"Insufficient stock" in response.data or b"failed" in response.data.lower()


# ===== 7. SUBSCRIPTION TEST =====

def test_create_subscription(client, mock_product):
    """User should be able to create a subscription."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["user_name"] = "Test User"
        sess["role"] = "customer"

    with patch("app.routes.subscription_routes.create_subscription") as mock_sub:
        mock_sub.return_value = {
            "SubscriptionID": "sub-001",
            "ProductID": "prod-test-001",
            "Frequency": "monthly",
            "NextDelivery": "2024-02-01",
            "Status": "Active",
        }
        with patch("app.routes.subscription_routes.get_all_products", return_value=[mock_product]):
            response = client.post("/subscriptions/new", data={
                "product_id": "prod-test-001",
                "frequency": "monthly",
            }, follow_redirects=True)
            assert response.status_code == 200
            mock_sub.assert_called_once()


# ===== 8. RECOMMENDATION TEST =====

def test_recommendations_shown_on_home(client, mock_product):
    """Logged-in users should see recommendations on the home page."""
    with client.session_transaction() as sess:
        sess["user_id"] = "user-test-001"
        sess["user_name"] = "Test User"
        sess["role"] = "customer"

    with patch("app.routes.main_routes.get_products_by_category", return_value=[mock_product]):
        with patch("app.routes.main_routes.get_recommendations", return_value=[mock_product]):
            response = client.get("/")
            assert response.status_code == 200
            assert b"Recommended for You" in response.data


# ===== 9. INVENTORY SERVICE UNIT TEST =====

def test_deduct_stock_success():
    """Inventory deduction should succeed when stock is sufficient."""
    with patch("app.services.inventory_service.get_table") as mock_table_fn:
        mock_table = MagicMock()
        mock_table_fn.return_value = mock_table
        mock_table.update_item.return_value = {}

        from app.services.inventory_service import deduct_stock
        result = deduct_stock("prod-test-001", 5)
        assert result["success"] is True


def test_deduct_stock_insufficient():
    """Inventory deduction should fail with ConditionalCheckFailedException."""
    from botocore.exceptions import ClientError

    with patch("app.services.inventory_service.get_table") as mock_table_fn:
        mock_table = MagicMock()
        mock_table_fn.return_value = mock_table

        error_response = {"Error": {"Code": "ConditionalCheckFailedException", "Message": "Condition failed"}}
        mock_table.update_item.side_effect = ClientError(error_response, "UpdateItem")

        from app.services.inventory_service import deduct_stock
        result = deduct_stock("prod-test-001", 999)
        assert result["success"] is False
        assert "stock" in result["error"].lower()


# ===== 10. PASSWORD HASHING TEST =====

def test_password_hashing():
    """Password hash should be deterministic and verifiable."""
    from app.utils.auth_helpers import hash_password, verify_password
    pw = "MySecurePassword123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
