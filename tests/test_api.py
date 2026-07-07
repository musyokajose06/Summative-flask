import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app
from storage import storage


@pytest.fixture(autouse=True)
def reset_storage():
    """Ensure each test starts with a clean, empty inventory."""
    storage._items.clear()
    storage._next_id = 1
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_items_empty(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_item_manual(client):
    payload = {"product_name": "Test Soda", "price": 1.99, "stock": 10}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Test Soda"
    assert data["price"] == 1.99
    assert data["stock"] == 10
    assert data["id"] == 1


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"price": 1.0})
    assert response.status_code == 400


def test_add_item_bad_json(client):
    response = client.post("/inventory", data="not json",
                            content_type="application/json")
    assert response.status_code == 400


def test_get_single_item(client):
    client.post("/inventory", json={"product_name": "Chips", "price": 2.5, "stock": 5})
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Chips"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_update_item_price_and_stock(client):
    client.post("/inventory", json={"product_name": "Crackers", "price": 3.0, "stock": 8})
    response = client.patch("/inventory/1", json={"price": 3.5, "stock": 20})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 3.5
    assert data["stock"] == 20
    assert data["product_name"] == "Crackers"  # unchanged fields stay intact


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404


def test_update_item_bad_price_type(client):
    client.post("/inventory", json={"product_name": "Juice", "price": 2.0, "stock": 4})
    response = client.patch("/inventory/1", json={"price": "not-a-number"})
    assert response.status_code == 400


def test_delete_item(client):
    client.post("/inventory", json={"product_name": "Gum", "price": 0.99, "stock": 50})
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    # confirm it's actually gone
    follow_up = client.get("/inventory/1")
    assert follow_up.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_lookup_missing_params(client):
    response = client.get("/inventory/lookup")
    assert response.status_code == 400


@pytest.mark.network
def test_lookup_by_barcode_live(client):
    """Hits the real OpenFoodFacts API - requires internet access."""
    response = client.get("/inventory/lookup", query_string={"barcode": "3017620422003"})
    assert response.status_code in (200, 502)  # 502 if API is unreachable in CI