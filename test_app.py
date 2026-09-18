"""
Automated Test Suite for Verdant Heritage Organic Farm Application
Validates all page routes, REST APIs, cart, orders, CSA, bookings, and error handling.
"""

import pytest
from app import app, USERS_DB

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    with app.test_client() as client:
        yield client

def test_homepage_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Verdant Heritage" in response.data
    assert b"Fresh From Our Fields" in response.data
    assert b"Shop Fresh Produce" in response.data
    assert b"Join Our CSA" in response.data
    assert b"Visit Our Farm" in response.data

def test_shop_page_route(client):
    response = client.get("/shop")
    assert response.status_code == 200
    assert b"Shop Fresh Organic Harvest" in response.data

def test_shop_filter_by_category(client):
    response = client.get("/shop?category=Vegetables")
    assert response.status_code == 200
    assert b"Heirloom Cherokee Purple Tomatoes" in response.data

def test_product_detail_route(client):
    response = client.get("/product/1")
    assert response.status_code == 200
    assert b"Heirloom Cherokee Purple Tomatoes" in response.data
    assert b"Harvest Location" in response.data

def test_product_not_found_404(client):
    response = client.get("/product/9999")
    assert response.status_code == 404

def test_csa_page_route(client):
    response = client.get("/csa")
    assert response.status_code == 200
    assert b"Weekly Harvest Box" in response.data
    assert b"Community Supported Agriculture" in response.data

def test_visits_page_route(client):
    response = client.get("/visits")
    assert response.status_code == 200
    assert b"Guided Regenerative Farm Walk" in response.data
    assert b"Book Your Farm Visit" in response.data

def test_about_page_route(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"78 Years of Earth Stewardship" in response.data
    assert b"Meet the Stewards" in response.data

def test_blog_overview_and_single_route(client):
    res_list = client.get("/blog")
    assert res_list.status_code == 200
    assert b"The Farm Journal" in res_list.data

    res_single = client.get("/blog/1")
    assert res_single.status_code == 200
    assert b"The Secret Life of Soil" in res_single.data

def test_contact_page_route(client):
    response = client.get("/contact")
    assert response.status_code == 200
    assert b"4820 Valley Meadow Road" in response.data
    assert b"Send Us a Message" in response.data

def test_checkout_page_route(client):
    response = client.get("/checkout")
    assert response.status_code == 200
    assert b"Farm Harvest Checkout" in response.data

def test_account_page_route(client):
    response = client.get("/account")
    assert response.status_code == 200

# --- REST API TESTS ---

def test_api_products_list(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["products"]) >= 10

def test_api_products_filter_category(client):
    res = client.get("/api/products?category=Fruits")
    assert res.status_code == 200
    data = res.get_json()
    for p in data["products"]:
        assert p["category"] == "Fruits"

def test_api_product_by_id(client):
    res = client.get("/api/products/2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["product"]["id"] == 2

def test_api_auth_registration_and_login(client):
    test_email = "testuser@verdantfarm.com"
    reg_payload = {
        "name": "Sarah Connor",
        "email": test_email,
        "phone": "(555) 999-1234",
        "password": "securepassword",
        "address": "123 Farm Way, Eugene, OR"
    }

    # Register
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "Sarah" in data["message"]

    # Duplicate registration should return 409
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 409

    # Current user check
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 200
    me_data = res_me.get_json()
    assert me_data["user"]["email"] == test_email

    # Logout
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 200

    # Login
    res_login = client.post("/api/auth/login", json={"email": test_email, "password": "securepassword"})
    assert res_login.status_code == 200
    assert res_login.get_json()["success"] is True

def test_api_auth_invalid_login(client):
    res = client.post("/api/auth/login", json={"email": "nonexistent@farm.com", "password": "wrong"})
    assert res.status_code == 401
    assert res.get_json()["success"] is False

def test_api_forgot_password(client):
    res = client.post("/api/auth/forgot-password", json={"email": "demo@verdantfarm.com"})
    assert res.status_code == 200
    assert res.get_json()["success"] is True

def test_api_order_submission(client):
    # Log in as demo user
    client.post("/api/auth/login", json={"email": "demo@verdantfarm.com", "password": "password123"})

    order_payload = {
        "name": "Eleanor Vance",
        "email": "demo@verdantfarm.com",
        "phone": "(555) 234-5678",
        "delivery_type": "Home Delivery",
        "address": "742 Evergreen Terrace, Springfield, OR",
        "payment_method": "Credit/Debit Card",
        "items": [
            {"id": 1, "name": "Heirloom Cherokee Purple Tomatoes", "price": 5.75, "quantity": 4},
            {"id": 2, "name": "Crisp Mountain Honeycrisp Apples", "price": 4.50, "quantity": 3}
        ]
    }

    res = client.post("/api/orders", json=order_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "VHF-" in data["order"]["order_id"]
    assert data["order"]["total"] == round((5.75 * 4) + (4.50 * 3), 2)  # Over $35, free delivery!

def test_api_csa_subscription(client):
    client.post("/api/auth/login", json={"email": "demo@verdantfarm.com", "password": "password123"})

    res = client.post("/api/csa/subscribe", json={"plan_id": "family-box"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["subscription"]["plan_name"] == "Family Bounty Box"

    res_cancel = client.post("/api/csa/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.get_json()["success"] is True

def test_api_farm_tour_booking(client):
    booking_payload = {
        "tour_id": "sunset-tasting",
        "name": "Jonathan Archer",
        "email": "archer@starfleet.org",
        "phone": "(555) 301-4450",
        "visitors": 3,
        "date": "2026-10-15",
        "time_slot": "05:30 PM"
    }

    res = client.post("/api/visits/book", json=booking_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "VBK-" in data["booking"]["booking_id"]
    assert data["booking"]["total_price"] == 45.00 * 3

def test_api_newsletter_and_contact(client):
    res_news = client.post("/api/newsletter", json={"email": "organiclover@green.org"})
    assert res_news.status_code == 200
    assert res_news.get_json()["success"] is True

    res_contact = client.post("/api/contact", json={
        "name": "Maya Lin",
        "email": "maya@valley.org",
        "subject": "Farm Tour",
        "message": "We have a group of 12 looking for an autumn apple tour."
    })
    assert res_contact.status_code == 200
    assert res_contact.get_json()["success"] is True
