from datetime import datetime
from typing import Optional, Tuple
from src.modules.Order.domain.entities.order import Order, OrderStatus, ServiceType

class OrderStatusService:
    """Servicio de dominio para manejar la lógica de estados de pedidos"""

    # Flujo válido de estados según modalidad de servicio
    VALID_TRANSITIONS = {
        ServiceType.DINE_IN: {
            OrderStatus.PENDING: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.SERVED, OrderStatus.CANCELLED],
            OrderStatus.SERVED: [],  # Estado final, no se puede cambiar
            OrderStatus.CANCELLED: []  # Estado final, no se puede cambiar
        },
        ServiceType.TAKEOUT: {
            OrderStatus.PENDING: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Estado final, no se puede cambiar
            OrderStatus.CANCELLED: []  # Estado final, no se puede cambiar
        },
        ServiceType.DELIVERY: {
            OrderStatus.PENDING: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Estado final, no se puede cambiar
            OrderStatus.CANCELLED: []  # Estado final, no se puede cambiar
        }
    }

    @staticmethod
    def validate_transition(order: Order, new_status: OrderStatus) -> Tuple[bool, str]:
        """
        Valida si una transición de estado es permitida según la modalidad de servicio
        Returns: (is_valid, error_message)
        """
        if order.status == new_status:
            return False, "El pedido ya está en ese estado"

        valid_transitions = OrderStatusService.VALID_TRANSITIONS[order.service_type]
        if new_status not in valid_transitions[order.status]:
            return False, f"No se puede cambiar de {order.status.value} a {new_status.value} para {order.service_type.value}"

        return True, ""

    @staticmethod
    def can_cancel(order: Order) -> Tuple[bool, str]:
        """Valida si un pedido puede ser cancelado"""
        final_states = [OrderStatus.SERVED, OrderStatus.DELIVERED]
        if order.status in final_states:
            status_text = "servido" if order.status == OrderStatus.SERVED else "entregado"
            return False, f"No se puede cancelar un pedido que ya fue {status_text}"
        if order.status == OrderStatus.CANCELLED:
            return False, "El pedido ya está cancelado"
        return True, ""

    @staticmethod
    def get_final_status_for_service_type(service_type: ServiceType) -> OrderStatus:
        """Retorna el estado final según la modalidad de servicio"""
        if service_type == ServiceType.DINE_IN:
            return OrderStatus.SERVED
        else:  # TAKEOUT or DELIVERY
            return OrderStatus.DELIVERED

    @staticmethod
    def apply_status_change(order: Order, new_status: OrderStatus, user_id: str,
                          cancellation_reason: Optional[str] = None) -> Order:
        """
        Aplica el cambio de estado con toda la lógica de negocio
        """
        now = datetime.now()
        updated_order = order.model_copy()  # Crear copia para no modificar el original
        updated_order.status = new_status
        updated_order.updated_at = now

        if new_status == OrderStatus.PREPARING:
            # CA3: Al cambiar a 'preparing'
            updated_order.preparation_started_at = now
            # Validar que tenga items
            if not order.items:
                raise ValueError("No se puede iniciar preparación: el pedido no tiene items")
            print(f"🔔 Notificación a cocina: Pedido {updated_order.order_number} ({updated_order.service_type.value}) iniciado preparación")

        elif new_status == OrderStatus.READY:
            # CA4: Al cambiar a 'ready'
            if not updated_order.preparation_started_at:
                raise ValueError("No se puede marcar como listo sin pasar por preparación")
            updated_order.ready_at = now
            updated_order.preparation_time = int((now - updated_order.preparation_started_at).total_seconds())

            if updated_order.service_type == ServiceType.DINE_IN:
                print(f"🔔 Notificación a mesero: Pedido {updated_order.order_number} listo para servir en mesa {updated_order.table_number}")
            else:  # TAKEOUT or DELIVERY
                action = "recoger" if updated_order.service_type == ServiceType.TAKEOUT else "entregar"
                print(f"🔔 Notificación: Pedido {updated_order.order_number} listo para {action}")

        elif new_status in [OrderStatus.SERVED, OrderStatus.DELIVERED]:
            # CA5: Al cambiar a estado final
            if not updated_order.ready_at:
                raise ValueError("No se puede marcar como completado sin estar listo")
            updated_order.completed_at = now
            updated_order.total_time = int((now - updated_order.created_at).total_seconds())
            # Marcar pago como completado si estaba pendiente
            if updated_order.payment_status == "PENDING":
                updated_order.payment_status = "PAID"

            status_text = "servido" if new_status == OrderStatus.SERVED else "entregado"
            print(f"✅ Pedido {updated_order.order_number} {status_text}")

        elif new_status == OrderStatus.CANCELLED:
            # CA6: Al cambiar a 'cancelled'
            if not cancellation_reason:
                raise ValueError("Se requiere motivo de cancelación")
            updated_order.cancelled_at = now
            updated_order.cancelled_by = user_id
            updated_order.cancellation_reason = cancellation_reason
            print(f"❌ Pedido {updated_order.order_number} cancelado por {user_id}: {cancellation_reason}")

        return updated_order
        """
        Aplica el cambio de estado con toda la lógica de negocio
        """
        now = datetime.now()
        updated_order = order.model_copy()  # Crear copia para no modificar el original
        updated_order.status = new_status
        updated_order.updated_at = now

        if new_status == OrderStatus.PREPARING:
            # CA3: Al cambiar a 'preparing'
            updated_order.preparation_started_at = now
            # Validar que tenga items
            if not order.items:
                raise ValueError("No se puede iniciar preparación: el pedido no tiene items")
            print(f"🔔 Notificación a cocina: Pedido {updated_order.order_number} iniciado preparación")

        elif new_status == OrderStatus.READY:
            # CA4: Al cambiar a 'ready'
            if not updated_order.preparation_started_at:
                raise ValueError("No se puede marcar como listo sin pasar por preparación")
            updated_order.ready_at = now
            updated_order.preparation_time = int((now - updated_order.preparation_started_at).total_seconds())
            print(f"🔔 Notificación a mesero: Pedido {updated_order.order_number} listo para servir")

        elif new_status == OrderStatus.SERVED:
            # CA5: Al cambiar a 'served'
            if not updated_order.ready_at:
                raise ValueError("No se puede marcar como servido sin estar listo")
            updated_order.completed_at = now
            updated_order.total_time = int((now - updated_order.created_at).total_seconds())
            # Marcar pago como completado si estaba pendiente
            if updated_order.payment_status == "PENDING":
                updated_order.payment_status = "PAID"
            print(f"✅ Pedido {updated_order.order_number} completado")

        elif new_status == OrderStatus.CANCELLED:
            # CA6: Al cambiar a 'cancelled'
            if not cancellation_reason:
                raise ValueError("Se requiere motivo de cancelación")
            updated_order.cancelled_at = now
            updated_order.cancelled_by = user_id
            updated_order.cancellation_reason = cancellation_reason
            print(f"❌ Pedido {updated_order.order_number} cancelado por {user_id}: {cancellation_reason}")

        return updated_order