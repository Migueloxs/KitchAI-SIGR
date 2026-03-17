from datetime import datetime
from typing import List, Optional
import uuid

from src.modules.Inventory.domain.entities.inventory_alert import InventoryAlert
from src.modules.Inventory.domain.entities.inventory_item import InventoryItem
from src.modules.Inventory.domain.repositories.inventory_repository_interface import (
    IInventoryRepository,
)
from src.shared.infrastructure.database.turso_connection import get_turso_client


class InventoryRepository(IInventoryRepository):
    def __init__(self):
        self.client = get_turso_client()

    def create(self, item: InventoryItem) -> InventoryItem:
        self.client.execute(
            """
            INSERT INTO inventory_items (
                id, name, category, current_quantity, minimum_stock, unit, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                item.id,
                item.name,
                item.category,
                item.current_quantity,
                item.minimum_stock,
                item.unit,
                item.created_at.isoformat(),
                item.updated_at.isoformat(),
            ],
        )
        return item

    def get_by_id(self, item_id: str) -> Optional[InventoryItem]:
        result = self.client.execute(
            """
            SELECT id, name, category, current_quantity, minimum_stock, unit, created_at, updated_at
            FROM inventory_items
            WHERE id = ?
            """,
            [item_id],
        )

        if not result.rows:
            return None

        return self._map_to_entity(result.rows[0])

    def get_all(self) -> List[InventoryItem]:
        result = self.client.execute(
            """
            SELECT id, name, category, current_quantity, minimum_stock, unit, created_at, updated_at
            FROM inventory_items
            ORDER BY name
            """
        )

        return [self._map_to_entity(row) for row in result.rows]

    def update(self, item: InventoryItem) -> InventoryItem:
        self.client.execute(
            """
            UPDATE inventory_items SET
                name = ?,
                category = ?,
                current_quantity = ?,
                minimum_stock = ?,
                unit = ?,
                updated_at = ?
            WHERE id = ?
            """,
            [
                item.name,
                item.category,
                item.current_quantity,
                item.minimum_stock,
                item.unit,
                item.updated_at.isoformat(),
                item.id,
            ],
        )
        return item

    def delete(self, item_id: str) -> bool:
        self.client.execute("DELETE FROM inventory_items WHERE id = ?", [item_id])
        return True

    def exists_by_name(self, name: str, excluding_id: Optional[str] = None) -> bool:
        query = "SELECT COUNT(*) FROM inventory_items WHERE LOWER(name) = LOWER(?)"
        params = [name]

        if excluding_id:
            query += " AND id <> ?"
            params.append(excluding_id)

        result = self.client.execute(query, params)
        return result.rows[0][0] > 0

    def deduct_stock(self, item_id: str, quantity: float) -> InventoryItem:
        item = self.get_by_id(item_id)
        if not item:
            raise ValueError(f"Articulo de inventario con ID {item_id} no encontrado")

        if quantity <= 0:
            raise ValueError("La cantidad a descontar debe ser mayor que cero")

        if item.current_quantity < quantity:
            raise ValueError(
                f"Stock insuficiente para '{item.name}'. Disponible: {item.current_quantity}, requerido: {quantity}"
            )

        updated_item = InventoryItem(
            id=item.id,
            name=item.name,
            category=item.category,
            current_quantity=item.current_quantity - quantity,
            minimum_stock=item.minimum_stock,
            unit=item.unit,
            created_at=item.created_at,
            updated_at=datetime.now(),
        )
        return self.update(updated_item)

    def create_alert(self, alert: InventoryAlert) -> InventoryAlert:
        alert_id = alert.id or str(uuid.uuid4())
        self.client.execute(
            """
            INSERT INTO inventory_alerts (
                id, inventory_item_id, order_id, alert_type, message,
                current_quantity, minimum_stock, is_resolved, created_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                alert_id,
                alert.inventory_item_id,
                alert.order_id,
                alert.alert_type,
                alert.message,
                alert.current_quantity,
                alert.minimum_stock,
                1 if alert.is_resolved else 0,
                alert.created_at.isoformat(),
                alert.resolved_at.isoformat() if alert.resolved_at else None,
            ],
        )
        return alert.model_copy(update={"id": alert_id})

    def get_active_alerts(self) -> List[InventoryAlert]:
        result = self.client.execute(
            """
            SELECT id, inventory_item_id, order_id, alert_type, message,
                   current_quantity, minimum_stock, is_resolved, created_at, resolved_at
            FROM inventory_alerts
            WHERE is_resolved = 0
            ORDER BY created_at DESC
            """
        )
        return [self._map_alert_entity(row) for row in result.rows]

    def is_order_inventory_processed(self, order_id: str) -> bool:
        result = self.client.execute(
            "SELECT COUNT(*) FROM order_inventory_updates WHERE order_id = ?",
            [order_id],
        )
        return result.rows[0][0] > 0

    def mark_order_inventory_processed(self, order_id: str, triggered_status: str) -> None:
        self.client.execute(
            """
            INSERT OR IGNORE INTO order_inventory_updates (order_id, triggered_status, processed_at)
            VALUES (?, ?, ?)
            """,
            [order_id, triggered_status, datetime.now().isoformat()],
        )

    def _map_to_entity(self, row) -> InventoryItem:
        return InventoryItem(
            id=row[0],
            name=row[1],
            category=row[2],
            current_quantity=row[3],
            minimum_stock=row[4],
            unit=row[5],
            created_at=datetime.fromisoformat(row[6]) if isinstance(row[6], str) else row[6],
            updated_at=datetime.fromisoformat(row[7]) if isinstance(row[7], str) else row[7],
        )

    def _map_alert_entity(self, row) -> InventoryAlert:
        return InventoryAlert(
            id=row[0],
            inventory_item_id=row[1],
            order_id=row[2],
            alert_type=row[3],
            message=row[4],
            current_quantity=row[5],
            minimum_stock=row[6],
            is_resolved=bool(row[7]),
            created_at=datetime.fromisoformat(row[8]) if isinstance(row[8], str) else row[8],
            resolved_at=datetime.fromisoformat(row[9]) if isinstance(row[9], str) and row[9] else row[9],
        )
