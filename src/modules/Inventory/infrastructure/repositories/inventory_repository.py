from datetime import datetime
from typing import List, Optional

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
