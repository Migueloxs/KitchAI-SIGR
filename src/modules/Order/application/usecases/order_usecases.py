from src.modules.Order.infrastructure.repositories.order_repository import OrderRepository
from src.modules.Order.application.dto.order_request import OrderRequestDTO, OrderStatusUpdateRequestDTO
from src.modules.Order.application.dto.order_response import OrderResponseDTO, OrderItemResponseDTO
from src.modules.Order.domain.entities.order import Order, OrderStatus, ServiceType
from src.modules.Order.domain.entities.order_item import OrderItem
from src.modules.Order.domain.services.order_status_service import OrderStatusService
from src.modules.Inventory.application.usecases.inventory_order_sync_usecase import InventoryOrderSyncService
import uuid
from datetime import datetime
from typing import Optional

class OrderService:
    def __init__(self):
        self.repo = OrderRepository()
        self.inventory_sync_service = InventoryOrderSyncService()

    def create_order(self, waiter_id: str, request: OrderRequestDTO) -> OrderResponseDTO:
        order_id = str(uuid.uuid4())
        order_number = f"ORD-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

        items = []
        total_amount = 0.0

        for i in request.items:
            subtotal = i.quantity * i.unit_price
            total_amount += subtotal

            items.append(
                OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    menu_item_id=i.menu_item_id,
                    menu_item_name=i.menu_item_name,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                    subtotal=subtotal,
                    special_notes=i.special_notes,
                    created_at=datetime.now()
                )
            )

        tax_amount = total_amount * 0.18 # Example tax rate
        final_amount = total_amount + tax_amount

        order = Order(
            id=order_id,
            order_number=order_number,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            table_number=request.table_number,
            status=OrderStatus.PENDING,
            service_type=request.service_type,
            total_amount=total_amount,
            tax_amount=tax_amount,
            final_amount=final_amount,
            special_instructions=request.special_instructions,
            waiter_id=waiter_id,
            items=items,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        saved_order = self.repo.create(order)
        return self._to_response_dto(saved_order)

    def update_order_status(self, order_id: str, request: OrderStatusUpdateRequestDTO, user_id: str) -> OrderResponseDTO:
        # Obtener el pedido actual
        order = self.repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Pedido con ID {order_id} no encontrado")

        # Validar el nuevo estado
        try:
            new_status = OrderStatus(request.new_status.lower())
        except ValueError:
            raise ValueError(f"Estado '{request.new_status}' no válido. Estados permitidos: {[s.value for s in OrderStatus]}")

        # Validar transición
        is_valid, error_msg = OrderStatusService.validate_transition(order, new_status)
        if not is_valid:
            raise ValueError(error_msg)

        # Validar cancelación si aplica
        if new_status == OrderStatus.CANCELLED:
            can_cancel, cancel_error = OrderStatusService.can_cancel(order)
            if not can_cancel:
                raise ValueError(cancel_error)

        # Aplicar el cambio de estado
        updated_order = OrderStatusService.apply_status_change(
            order, new_status, user_id, request.cancellation_reason
        )

        # CA1 y CA3: al confirmar el pedido (pending -> preparing) descontar inventario inmediatamente.
        if order.status == OrderStatus.PENDING and new_status == OrderStatus.PREPARING:
            self.inventory_sync_service.apply_stock_discount_for_confirmed_order(
                updated_order, triggered_status=new_status.value
            )

        # Guardar en la base de datos
        saved_order = self.repo.update_status_with_details(updated_order)
        return self._to_response_dto(saved_order)

    def get_order_by_id(self, order_id: str) -> Optional[OrderResponseDTO]:
        order = self.repo.get_by_id(order_id)
        return self._to_response_dto(order) if order else None

    def get_orders_by_waiter(self, waiter_id: str) -> list[OrderResponseDTO]:
        orders = self.repo.get_all(waiter_id=waiter_id)
        return [self._to_response_dto(order) for order in orders]

    def _to_response_dto(self, order: Order) -> OrderResponseDTO:
        """Convierte entidad Order a DTO de respuesta"""
        return OrderResponseDTO(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            table_number=order.table_number,
            status=order.status.value,
            service_type=order.service_type,
            total_amount=order.total_amount,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            special_instructions=order.special_instructions,
            waiter_id=order.waiter_id,
            cancelled_by=order.cancelled_by,
            cancelled_at=order.cancelled_at,
            cancellation_reason=order.cancellation_reason,
            created_at=order.created_at,
            updated_at=order.updated_at,
            preparation_started_at=order.preparation_started_at,
            ready_at=order.ready_at,
            completed_at=order.completed_at,
            preparation_time=order.preparation_time,
            total_time=order.total_time,
            items=[
                OrderItemResponseDTO(
                    id=item.id,
                    menu_item_id=item.menu_item_id,
                    menu_item_name=item.menu_item_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                    special_notes=item.special_notes
                )
                for item in order.items
            ]
        )