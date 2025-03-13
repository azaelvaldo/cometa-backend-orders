from fastapi.testclient import TestClient
from app import app  # Importamos la app de FastAPI

client = TestClient(app)

def test_get_order():
    response = client.get("/order")
    assert response.status_code == 200
    data = response.json()

    assert "subtotal" in data
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)

def test_order_total_calculation():
    response = client.get("/order")
    data = response.json()

    expected_total = data["subtotal"] + data["taxes"] - data["discounts"]
    assert data["total"] == expected_total