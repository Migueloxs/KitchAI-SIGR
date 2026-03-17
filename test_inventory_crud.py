#!/usr/bin/env python3
"""
Test script para CRUD de inventario.
Valida criterios CA1, CA2 y persistencia de CA3.
"""

import json
import requests

BASE_URL = "http://localhost:8000"


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
    elif method.upper() == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Metodo no soportado: {method}")

    body = response.json() if response.content else None
    return response.status_code, body


def get_admin_token():
    register_payload = {
        "name": "Inventory Admin",
        "email": "inventory.admin@test.com",
        "password": "AdminPass123!",
        "role": "admin",
    }
    make_request("POST", "/api/auth/register", register_payload)

    status, login_result = make_request(
        "POST",
        "/api/auth/login",
        {
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )

    if status != 200:
        raise RuntimeError(f"No se pudo autenticar admin: {login_result}")

    return login_result["access_token"]


def test_inventory_crud():
    print("🧪 Test Inventory CRUD")
    print("=" * 50)

    token = get_admin_token()
    print("✅ Admin autenticado")

    # CA1: Crear articulo con nombre, categoria, cantidad y stock minimo
    create_payload = {
        "name": "Tomate Fresco",
        "category": "Vegetales",
        "current_quantity": 30,
        "minimum_stock": 10,
        "unit": "kg",
    }
    status, created = make_request("POST", "/api/inventory/", create_payload, token)
    assert status == 201, f"Error creando articulo: {created}"
    item_id = created["id"]
    print(f"✅ CA1 OK - Articulo creado: {item_id}")

    # Verificar lectura y persistencia inmediata
    status, fetched = make_request("GET", f"/api/inventory/{item_id}", token=token)
    assert status == 200, f"Error consultando articulo creado: {fetched}"
    assert fetched["name"] == create_payload["name"]
    print("✅ CA3 OK - Persistencia confirmada en lectura inmediata")

    # CA2: Actualizar articulo
    update_payload = {
        "name": "Tomate Fresco Premium",
        "category": "Vegetales",
        "current_quantity": 22,
        "minimum_stock": 12,
        "unit": "kg",
    }
    status, updated = make_request("PUT", f"/api/inventory/{item_id}", update_payload, token)
    assert status == 200, f"Error actualizando articulo: {updated}"
    assert updated["name"] == update_payload["name"]
    assert updated["is_below_minimum_stock"] is False
    print("✅ CA2 OK - Articulo actualizado")

    # Verificar listado
    status, listed = make_request("GET", "/api/inventory/", token=token)
    assert status == 200, f"Error listando articulos: {listed}"
    assert any(i["id"] == item_id for i in listed), "No se encontro articulo en listado"
    print("✅ Listado de inventario funcionando")

    # CA2: Eliminar articulo
    status, deleted = make_request("DELETE", f"/api/inventory/{item_id}", token=token)
    assert status == 200, f"Error eliminando articulo: {deleted}"
    print("✅ CA2 OK - Articulo eliminado")

    status, not_found = make_request("GET", f"/api/inventory/{item_id}", token=token)
    assert status == 404, "El articulo deberia no existir luego de eliminarse"
    print("✅ CA3 OK - Eliminacion persistida")

    print("\n🎉 Inventory CRUD listo y validado")


if __name__ == "__main__":
    try:
        health_status, _ = make_request("GET", "/health")
        if health_status != 200:
            print("❌ El servidor no esta listo. Ejecuta: python -m uvicorn main:app --reload")
        else:
            test_inventory_crud()
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
