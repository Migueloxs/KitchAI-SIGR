from datetime import datetime
import uuid

from src.modules.Inventory.domain.entities.inventory_alert import InventoryAlert
from src.modules.Inventory.infrastructure.repositories.inventory_repository import InventoryRepository
from src.modules.Order.domain.entities.order import Order


class InventoryOrderSyncService:
    def __init__(self):
        self.repo = InventoryRepository()

    def apply_stock_discount_for_confirmed_order(self, order: Order, triggered_status: str) -> None:
        if self.repo.is_order_inventory_processed(order.id):
            return

        # Validacion previa de stock para evitar descuentos parciales.
        for order_item in order.items:
            inventory_item = self.repo.get_by_id(order_item.menu_item_id)
            if not inventory_item:
                raise ValueError(
                    f"No existe articulo de inventario para el item del pedido '{order_item.menu_item_name}' ({order_item.menu_item_id})"
                )
            if inventory_item.current_quantity < order_item.quantity:
                raise ValueError(
                    f"Stock insuficiente para '{inventory_item.name}'. Disponible: {inventory_item.current_quantity}, requerido: {order_item.quantity}"
                )

        for order_item in order.items:
            updated_item = self.repo.deduct_stock(order_item.menu_item_id, order_item.quantity)

            if updated_item.current_quantity <= updated_item.minimum_stock:
                alert = InventoryAlert(
                    id=str(uuid.uuid4()),
                    inventory_item_id=updated_item.id,
                    order_id=order.id,
                    alert_type="LOW_STOCK",
                    message=(
                        f"Articulo '{updated_item.name}' en stock minimo o por debajo "
                        f"(actual: {updated_item.current_quantity} {updated_item.unit}, minimo: {updated_item.minimum_stock} {updated_item.unit})"
                    ),
                    current_quantity=updated_item.current_quantity,
                    minimum_stock=updated_item.minimum_stock,
                    is_viewed=False,
                    is_resolved=False,
                    check_date=None,
                    created_at=datetime.now(),
                    viewed_at=None,
                    resolved_at=None,
                )
                self.repo.create_alert(alert)

        self.repo.mark_order_inventory_processed(order.id, triggered_status)
