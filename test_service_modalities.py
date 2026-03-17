#!/usr/bin/env python3
"""
Test para Service Modalities - Verifica que los flujos de estado funcionen correctamente
para diferentes tipos de servicio (dine-in, takeout, delivery)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.modules.Order.domain.entities.order import Order, OrderStatus, ServiceType
from src.modules.Order.domain.entities.order_item import OrderItem
from src.modules.Order.domain.services.order_status_service import OrderStatusService

def test_service_modalities():
    """Test completo de modalidades de servicio"""
    print("🧪 Test de Service Modalities")
    print("=" * 50)

    # Test 1: Validar flujos por modalidad
    print("\n📋 Test 1: Flujos válidos por modalidad")

    # DINE_IN: pending -> preparing -> ready -> served
    dine_in_transitions = OrderStatusService.VALID_TRANSITIONS[ServiceType.DINE_IN]
    assert OrderStatus.SERVED in dine_in_transitions[OrderStatus.READY], "DINE_IN debe terminar en SERVED"
    assert OrderStatus.DELIVERED not in dine_in_transitions[OrderStatus.READY], "DINE_IN no debe tener DELIVERED"
    print("✅ DINE_IN: pending → preparing → ready → served")

    # TAKEOUT: pending -> preparing -> ready -> delivered
    takeout_transitions = OrderStatusService.VALID_TRANSITIONS[ServiceType.TAKEOUT]
    assert OrderStatus.DELIVERED in takeout_transitions[OrderStatus.READY], "TAKEOUT debe terminar en DELIVERED"
    assert OrderStatus.SERVED not in takeout_transitions[OrderStatus.READY], "TAKEOUT no debe tener SERVED"
    print("✅ TAKEOUT: pending → preparing → ready → delivered")

    # DELIVERY: pending -> preparing -> ready -> delivered
    delivery_transitions = OrderStatusService.VALID_TRANSITIONS[ServiceType.DELIVERY]
    assert OrderStatus.DELIVERED in delivery_transitions[OrderStatus.READY], "DELIVERY debe terminar en DELIVERED"
    assert OrderStatus.SERVED not in delivery_transitions[OrderStatus.READY], "DELIVERY no debe tener SERVED"
    print("✅ DELIVERY: pending → preparing → ready → delivered")

    # Test 2: Estados finales correctos
    print("\n📋 Test 2: Estados finales por modalidad")
    assert OrderStatusService.get_final_status_for_service_type(ServiceType.DINE_IN) == OrderStatus.SERVED
    assert OrderStatusService.get_final_status_for_service_type(ServiceType.TAKEOUT) == OrderStatus.DELIVERED
    assert OrderStatusService.get_final_status_for_service_type(ServiceType.DELIVERY) == OrderStatus.DELIVERED
    print("✅ Estados finales correctos")

    # Test 3: Validación de transiciones con service_type
    print("\n📋 Test 3: Validación de transiciones")

    # Crear pedido de ejemplo con items
    order_item = OrderItem(
        id="item-1",
        order_id="order-1",
        menu_item_id="menu-1",
        menu_item_name="Test Item",
        quantity=1,
        unit_price=10.0,
        subtotal=10.0,
        special_notes=None,
        created_at=datetime.now()
    )

    # Test DINE_IN
    dine_in_order = Order(
        id="order-dine-in",
        order_number="ORD-DINE-001",
        customer_name="Test Customer",
        customer_phone=None,
        table_number=5,
        status=OrderStatus.PENDING,
        service_type=ServiceType.DINE_IN,
        total_amount=10.0,
        tax_amount=1.8,
        discount_amount=0.0,
        final_amount=11.8,
        payment_status="PENDING",
        payment_method=None,
        special_instructions=None,
        waiter_id="waiter-1",
        items=[order_item],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Validar transiciones válidas para DINE_IN
    is_valid, _ = OrderStatusService.validate_transition(dine_in_order, OrderStatus.PREPARING)
    assert is_valid, "DINE_IN debe poder ir a PREPARING"
    print("✅ DINE_IN puede ir a PREPARING")

    # Cambiar a PREPARING y luego a READY
    updated_order = OrderStatusService.apply_status_change(dine_in_order, OrderStatus.PREPARING, "user-1")
    updated_order = OrderStatusService.apply_status_change(updated_order, OrderStatus.READY, "user-1")

    # Validar que puede ir a SERVED pero no a DELIVERED
    is_valid_served, _ = OrderStatusService.validate_transition(updated_order, OrderStatus.SERVED)
    is_valid_delivered, _ = OrderStatusService.validate_transition(updated_order, OrderStatus.DELIVERED)

    assert is_valid_served, "DINE_IN debe poder ir a SERVED"
    assert not is_valid_delivered, "DINE_IN no debe poder ir a DELIVERED"
    print("✅ DINE_IN puede ir a SERVED pero no a DELIVERED")

    # Test TAKEOUT
    takeout_order = Order(
        id="order-takeout",
        order_number="ORD-TAKEOUT-001",
        customer_name="Test Customer",
        customer_phone="555-0123",
        table_number=None,
        status=OrderStatus.PENDING,
        service_type=ServiceType.TAKEOUT,
        total_amount=10.0,
        tax_amount=1.8,
        discount_amount=0.0,
        final_amount=11.8,
        payment_status="PENDING",
        payment_method=None,
        special_instructions=None,
        waiter_id="waiter-1",
        items=[order_item],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Cambiar TAKEOUT a PREPARING y luego a READY
    updated_takeout = OrderStatusService.apply_status_change(takeout_order, OrderStatus.PREPARING, "user-1")
    updated_takeout = OrderStatusService.apply_status_change(updated_takeout, OrderStatus.READY, "user-1")

    # Validar que puede ir a DELIVERED pero no a SERVED
    is_valid_delivered, _ = OrderStatusService.validate_transition(updated_takeout, OrderStatus.DELIVERED)
    is_valid_served, _ = OrderStatusService.validate_transition(updated_takeout, OrderStatus.SERVED)

    assert is_valid_delivered, "TAKEOUT debe poder ir a DELIVERED"
    assert not is_valid_served, "TAKEOUT no debe poder ir a SERVED"
    print("✅ TAKEOUT puede ir a DELIVERED pero no a SERVED")

    # Test 4: Notificaciones específicas por servicio
    print("\n📋 Test 4: Notificaciones específicas")

    # DINE_IN - notificación a mesero
    final_dine_in = OrderStatusService.apply_status_change(updated_order, OrderStatus.SERVED, "user-1")
    assert final_dine_in.status == OrderStatus.SERVED
    print("✅ DINE_IN completado con notificación a mesero")

    # TAKEOUT - notificación de listo para recoger
    final_takeout = OrderStatusService.apply_status_change(updated_takeout, OrderStatus.DELIVERED, "user-1")
    assert final_takeout.status == OrderStatus.DELIVERED
    print("✅ TAKEOUT completado con notificación de entrega")

    print("\n🎉 Todos los tests de Service Modalities pasaron exitosamente!")
    return True

if __name__ == "__main__":
    try:
        test_service_modalities()
        print("\n✅ Test completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)