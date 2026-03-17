#!/usr/bin/env python3
"""
Test E2E para actualizacion automatica de inventario tras confirmar pedidos.
Cubre CA1, CA2 y CA3.
"""

from datetime import datetime
import json
import os
import requests

from src.shared.infrastructure.database.turso_connection import get_turso_client

BASE_URL = os.getenv("KITCHAI_BASE_URL", "http://localhost:8000")


def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
    elif method.upper() == "PUT":
        response = requests.put(url, headers=headers, data=json.dumps(data) if data else None)
    else:
        raise ValueError(f"Metodo no soportado: {method}")

    body = None
    if response.content:
        try:
            body = response.json()
        except requests.exceptions.JSONDecodeError:
            body = {"raw": response.text}
    return response.status_code, body


def ensure_user(email, name, password, role):
    register_payload = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
    }
    make_request("POST", "/api/auth/register", register_payload)

    status, login_result = make_request(
        "POST",
        "/api/auth/login",
        {"email": email, "password": password},
    )
    if status != 200:
        raise RuntimeError(f"No se pudo autenticar usuario {email}: {login_result}")

    return login_result["access_token"]


def ensure_menu_item_exists(menu_item_id: str, name: str, price: float) -> None:
    client = get_turso_client()
    now = datetime.now().isoformat()
    client.execute(
        """
        INSERT OR IGNORE INTO menu_items (
            id, name, description, price, is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            menu_item_id,
            name,
            f"Auto generado para prueba de inventario {menu_item_id}",
            price,
            1,
            now,
            now,
        ],
    )


def test_inventory_auto_update():
    print("🧪 Test Inventory Auto Update")
    print("=" * 50)

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    admin_token = ensure_user(
        email=f"inventory.admin.{stamp}@test.com",
        name="Inventory Admin",
        password="AdminPass123!",
        role="admin",
    )
    waiter_token = ensure_user(
        email=f"inventory.waiter.{stamp}@test.com",
        name="Inventory Waiter",
        password="WaiterPass123!",
        role="waiter",
    )

    # Crear item de inventario que quedara en nivel minimo luego del descuento.
    status, inventory_item = make_request(
        "POST",
        "/api/inventory/",
        {
            "name": f"Queso Mozzarella {stamp}",
            "category": "Lacteos",
            "current_quantity": 5,
            "minimum_stock": 3,
            "unit": "kg",
        },
        admin_token,
    )
    assert status == 201, f"No se pudo crear item de inventario: {inventory_item}"

    item_id = inventory_item["id"]
    ensure_menu_item_exists(item_id, f"Menu Item {stamp}", 11.0)
    print(f"✅ Inventario inicial creado: {item_id} (stock: 5)")

    # Crear pedido usando menu_item_id igual al inventory_item.id
    status, order = make_request(
        "POST",
        "/api/orders/",
        {
            "customer_name": "Cliente Test AutoUpdate",
            "customer_phone": "+18095550000",
            "table_number": 7,
            "service_type": "dine_in",
            "items": [
                {
                    "menu_item_id": item_id,
                    "menu_item_name": "Pizza Margarita",
                    "quantity": 2,
                    "unit_price": 11.0,
                }
            ],
        },
        waiter_token,
    )
    assert status in (200, 201), f"No se pudo crear pedido: {order}"
    order_id = order["id"]
    print(f"✅ Pedido creado: {order_id}")

    # Confirmar pedido: pending -> preparing (debe descontar inventario).
    status, updated_order = make_request(
        "PUT",
        f"/api/orders/{order_id}/status",
        {"new_status": "preparing"},
        waiter_token,
    )
    assert status == 200, f"No se pudo confirmar pedido: {updated_order}"
    print("✅ Pedido confirmado en preparing")

    # CA1 + CA3: verificar descuento inmediato.
    status, updated_item = make_request("GET", f"/api/inventory/{item_id}", token=admin_token)
    assert status == 200, f"No se pudo leer inventario actualizado: {updated_item}"
    assert updated_item["current_quantity"] == 3, f"Stock esperado 3, obtenido {updated_item['current_quantity']}"
    print("✅ CA1/CA3 OK - Inventario descontado inmediatamente (5 -> 3)")

    # CA2: validar alerta interna por stock en minimo.
    status, alerts = make_request("GET", "/api/inventory/alerts", token=admin_token)
    assert status == 200, f"No se pudieron consultar alertas: {alerts}"

    alert_for_order = [
        a
        for a in alerts
        if a.get("order_id") == order_id and a.get("inventory_item_id") == item_id and a.get("alert_type") == "LOW_STOCK"
    ]
    assert alert_for_order, "No se encontro alerta de bajo stock para el pedido confirmado"
    print("✅ CA2 OK - Alerta interna LOW_STOCK registrada")

    # Mover estado para asegurar que no se vuelva a descontar en otras transiciones.
    status, _ = make_request(
        "PUT",
        f"/api/orders/{order_id}/status",
        {"new_status": "ready"},
        waiter_token,
    )
    assert status == 200, "No se pudo mover pedido a ready"

    status, final_item = make_request("GET", f"/api/inventory/{item_id}", token=admin_token)
    assert status == 200
    assert final_item["current_quantity"] == 3, "El inventario se desconto mas de una vez"
    print("✅ Idempotencia OK - No hay descuentos duplicados")

    print("\n🎉 Todo OK: actualizacion automatica de inventario validada")


if __name__ == "__main__":
    status, _ = make_request("GET", "/health")
    if status != 200:
        print("❌ Servidor no disponible. Ejecuta: python -m uvicorn main:app --reload")
    else:
        test_inventory_auto_update()
