#!/usr/bin/env python3
"""
Test de servicio para actualizacion automatica de inventario al confirmar pedidos.
Valida la logica de negocio contra Turso DB sin depender del transporte HTTP.
"""

from datetime import datetime
import uuid

from src.modules.Inventory.application.dto.inventory_request import CreateInventoryItemRequestDTO
from src.modules.Inventory.application.usecases.inventory_order_sync_usecase import InventoryOrderSyncService
from src.modules.Inventory.application.usecases.inventory_usecases import InventoryService
from src.modules.Order.domain.entities.order import Order, OrderStatus, ServiceType
from src.modules.Order.domain.entities.order_item import OrderItem


def test_inventory_auto_update_service():
    print("🧪 Test Inventory Auto Update (Service)")
    print("=" * 50)

    inventory_service = InventoryService()
    sync_service = InventoryOrderSyncService()

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    created_item = inventory_service.create_item(
        CreateInventoryItemRequestDTO(
            name=f"Harina Test Sync {stamp}",
            category="Secos",
            current_quantity=10,
            minimum_stock=8,
            unit="kg",
        )
    )
    print(f"✅ Item creado: {created_item.id} (stock inicial: {created_item.current_quantity})")

    order_id = str(uuid.uuid4())
    order_item = OrderItem(
        id=str(uuid.uuid4()),
        order_id=order_id,
        menu_item_id=created_item.id,
        menu_item_name="Pizza Test",
        quantity=2,
        unit_price=20,
        subtotal=40,
        special_notes=None,
        created_at=datetime.now(),
    )

    order = Order(
        id=order_id,
        order_number=f"ORD-SYNC-{stamp}",
        customer_name="Cliente Test",
        customer_phone="+18095550000",
        table_number=4,
        status=OrderStatus.PREPARING,
        service_type=ServiceType.DINE_IN,
        total_amount=40,
        tax_amount=7.2,
        discount_amount=0,
        final_amount=47.2,
        payment_status="PENDING",
        payment_method=None,
        special_instructions=None,
        waiter_id="waiter-sync-test",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        items=[order_item],
    )

    sync_service.apply_stock_discount_for_confirmed_order(order, triggered_status="preparing")

    updated_item = inventory_service.get_item_by_id(created_item.id)
    assert updated_item is not None
    assert updated_item.current_quantity == 8, f"Stock esperado 8, obtenido {updated_item.current_quantity}"
    print("✅ CA1/CA3 OK - Stock descontado inmediatamente (10 -> 8)")

    alerts = inventory_service.get_active_alerts()
    relevant_alerts = [a for a in alerts if a.order_id == order_id and a.inventory_item_id == created_item.id]
    assert relevant_alerts, "No se genero alerta al quedar en stock minimo"
    print("✅ CA2 OK - Alerta interna generada en stock minimo")

    # Idempotencia: misma orden no debe descontar una segunda vez.
    sync_service.apply_stock_discount_for_confirmed_order(order, triggered_status="preparing")
    final_item = inventory_service.get_item_by_id(created_item.id)
    assert final_item is not None
    assert final_item.current_quantity == 8, "Se desconto stock mas de una vez para la misma orden"
    print("✅ Idempotencia OK - No hay descuentos duplicados por orden")

    print("\n🎉 Logica de auto-actualizacion de inventario validada")


if __name__ == "__main__":
    test_inventory_auto_update_service()
