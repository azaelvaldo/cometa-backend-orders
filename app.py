from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permite solicitudes desde Next.js
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

stock = {
    "last_updated": "2024-09-10 12:00:00",
    "beers": [
        {"name": "Corona", "price": 115, "quantity": 2},
        {"name": "Quilmes", "price": 120, "quantity": 0},
        {"name": "Club Colombia", "price": 110, "quantity": 3}
    ]
}

order = {
    "created": "2024-09-10 12:00:00",
    "paid": False,
    "rounds": [
        {
            "created": "2024-09-10 12:00:30",
            "items": [
                {"name": "Corona", "quantity": 2},
                {"name": "Club Colombia", "quantity": 1}
            ]
        },
        {
            "created": "2024-09-10 12:20:31",
            "items": [
                {"name": "Club Colombia", "quantity": 1},
                {"name": "Quilmes", "quantity": 2}
            ]
        },
        {
            "created": "2024-09-10 12:43:21",
            "items": [
                {"name": "Quilmes", "quantity": 3}
            ]
        }
    ]
}

class BeerItem(BaseModel):
    name: str
    quantity: int

class OrderRound(BaseModel):
    created: str
    items: List[BeerItem]

class OrderItem(BaseModel):
    name: str
    price_per_unit: float
    total: float

class OrderStatus(BaseModel):
    created: str
    paid: bool
    subtotal: float
    taxes: float
    discounts: float
    total: float
    items: List[OrderItem]
    rounds: List[OrderRound]

def calculate_order():
    items_summary = {}
    subtotal = 0

    price_lookup = {beer["name"]: beer["price"] for beer in stock["beers"]}

    for order_round in order["rounds"]:
        for item in order_round["items"]:
            name = item["name"]
            quantity = item["quantity"]
            price_per_unit = price_lookup.get(name, 0)

            if name not in items_summary:
                items_summary[name] = {"quantity": 0, "price_per_unit": price_per_unit}
            
            items_summary[name]["quantity"] += quantity

    items_list = []
    for name, data in items_summary.items():
        total_price = data["quantity"] * data["price_per_unit"]
        subtotal += total_price
        items_list.append({
            "name": name,
            "price_per_unit": data["price_per_unit"],
            "total": total_price
        })

    taxes = subtotal * 0.16  # 16% de impuestos
    discounts = subtotal * 0.05  # 5% de descuento
    total = subtotal + taxes - discounts

    return {
        "created": order["created"],
        "paid": order["paid"],
        "subtotal": subtotal,
        "taxes": taxes,
        "discounts": discounts,
        "total": total,
        "items": items_list,
        "rounds": order["rounds"]
    }

@app.get("/order", response_model=OrderStatus)
async def get_order_status():
    return calculate_order()
