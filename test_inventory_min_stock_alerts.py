#!/usr/bin/env python3
"""
Test E2E para alertas de stock minimo y dashboard de notificaciones internas.
Cubre:
- CA1: verificacion diaria y creacion de alerta interna
- CA2: consulta de dashboard de alertas
- CA3: marcado de alertas como vistas y resueltas
"""

from datetime import datetime
import json
import os
import uuid
import requests

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


def ensure_admin_token():
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique = uuid.uuid4().hex[:8]
    register_payload = {
        "name": "Inventory Admin Alerts",
        "email": f"inventory.alerts.admin.{stamp}.{unique}@test.com",
        "password": "AdminPass123!",
        "role": "admin",
    }
    register_status, register_result = make_request("POST", "/api/auth/register", register_payload)
    if register_status not in (200, 201):
        raise RuntimeError(f"No se pudo registrar admin: {register_result}")

    status, login_result = make_request(
        "POST",
        "/api/auth/login",
        {"email": register_payload["email"], "password": register_payload["password"]},
    )
    if status != 200:
        raise RuntimeError(f"No se pudo autenticar admin: {login_result}")

    return login_result["access_token"]


def test_inventory_min_stock_alerts_dashboard():
    print("🧪 Test Inventory Min Stock Alerts")
    print("=" * 50)

    token = ensure_admin_token()
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    status, created_item = make_request(
        "POST",
        "/api/inventory/",
        {
            "name": f"Aceite Alerta Diaria {stamp}",
            "category": "Insumos",
            "current_quantity": 4,
            "minimum_stock": 4,
            "unit": "litros",
        },
        token,
    )
    assert status == 201, f"No se pudo crear item de inventario: {created_item}"
    item_id = created_item["id"]
    print("✅ Item con stock minimo creado")

    # CA1: ejecutar verificacion diaria (el scheduler tambien lo hace automaticamente en startup).
    status, daily_check_result = make_request("POST", "/api/inventory/alerts/daily-check", token=token)
    assert status == 200, f"No se pudo ejecutar verificacion diaria: {daily_check_result}"
    assert daily_check_result["alerts_created"] >= 1, "La verificacion diaria no creo alertas"
    print("✅ CA1 OK - Verificacion diaria genera notificaciones internas")

    # CA2: dashboard de alertas con la alerta diaria.
    status, dashboard_alerts = make_request("GET", "/api/inventory/alerts/dashboard", token=token)
    assert status == 200, f"No se pudo consultar dashboard de alertas: {dashboard_alerts}"

    matching_alerts = [
        alert
        for alert in dashboard_alerts
        if alert.get("inventory_item_id") == item_id and alert.get("alert_type") == "DAILY_MIN_STOCK"
    ]
    assert matching_alerts, "No se encontro alerta DAILY_MIN_STOCK en dashboard"
    alert = matching_alerts[0]
    alert_id = alert["id"]
    print("✅ CA2 OK - Dashboard muestra alerta de stock minimo")

    # CA3 parte 1: marcar como vista.
    status, viewed_alert = make_request("PUT", f"/api/inventory/alerts/{alert_id}/view", token=token)
    assert status == 200, f"No se pudo marcar alerta como vista: {viewed_alert}"
    assert viewed_alert["is_viewed"] is True
    print("✅ CA3 OK - Alerta marcada como vista")

    # CA3 parte 2: marcar como resuelta.
    status, resolved_alert = make_request("PUT", f"/api/inventory/alerts/{alert_id}/resolve", token=token)
    assert status == 200, f"No se pudo marcar alerta como resuelta: {resolved_alert}"
    assert resolved_alert["is_resolved"] is True
    assert resolved_alert["is_viewed"] is True
    print("✅ CA3 OK - Alerta marcada como resuelta")

    # La alerta resuelta no debe salir en activas.
    status, active_alerts = make_request("GET", "/api/inventory/alerts", token=token)
    assert status == 200
    assert all(a["id"] != alert_id for a in active_alerts), "Una alerta resuelta sigue apareciendo como activa"
    print("✅ Dashboard activo limpio de alertas resueltas")

    print("\n🎉 Alertas de stock minimo listas y validadas")


if __name__ == "__main__":
    status, _ = make_request("GET", "/health")
    if status != 200:
        print("❌ Servidor no disponible. Ejecuta: python -m uvicorn main:app --reload")
    else:
        test_inventory_min_stock_alerts_dashboard()
