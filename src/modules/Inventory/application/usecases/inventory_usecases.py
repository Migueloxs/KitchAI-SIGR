from datetime import datetime
from typing import List, Optional
import uuid

from src.modules.Inventory.application.dto.inventory_request import (
    CreateInventoryItemRequestDTO,
    UpdateInventoryItemRequestDTO,
)
from src.modules.Inventory.application.dto.inventory_alert_response import InventoryAlertResponseDTO
from src.modules.Inventory.application.dto.inventory_response import InventoryItemResponseDTO
from src.modules.Inventory.domain.entities.inventory_alert import InventoryAlert
from src.modules.Inventory.domain.entities.inventory_item import InventoryItem
from src.modules.Inventory.infrastructure.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self):
        self.repo = InventoryRepository()

    def create_item(self, request: CreateInventoryItemRequestDTO) -> InventoryItemResponseDTO:
        if self.repo.exists_by_name(request.name):
            raise ValueError(f"Ya existe un articulo con el nombre '{request.name}'")

        now = datetime.now()
        item = InventoryItem(
            id=str(uuid.uuid4()),
            name=request.name,
            category=request.category,
            current_quantity=request.current_quantity,
            minimum_stock=request.minimum_stock,
            unit=request.unit,
            created_at=now,
            updated_at=now,
        )

        saved_item = self.repo.create(item)
        return self._to_response_dto(saved_item)

    def get_item_by_id(self, item_id: str) -> Optional[InventoryItemResponseDTO]:
        item = self.repo.get_by_id(item_id)
        return self._to_response_dto(item) if item else None

    def get_items(self) -> List[InventoryItemResponseDTO]:
        items = self.repo.get_all()
        return [self._to_response_dto(item) for item in items]

    def update_item(self, item_id: str, request: UpdateInventoryItemRequestDTO) -> InventoryItemResponseDTO:
        existing = self.repo.get_by_id(item_id)
        if not existing:
            raise ValueError(f"Articulo con ID {item_id} no encontrado")

        if self.repo.exists_by_name(request.name, excluding_id=item_id):
            raise ValueError(f"Ya existe otro articulo con el nombre '{request.name}'")

        updated_item = InventoryItem(
            id=existing.id,
            name=request.name,
            category=request.category,
            current_quantity=request.current_quantity,
            minimum_stock=request.minimum_stock,
            unit=request.unit,
            created_at=existing.created_at,
            updated_at=datetime.now(),
        )

        saved_item = self.repo.update(updated_item)
        return self._to_response_dto(saved_item)

    def delete_item(self, item_id: str) -> bool:
        existing = self.repo.get_by_id(item_id)
        if not existing:
            raise ValueError(f"Articulo con ID {item_id} no encontrado")

        return self.repo.delete(item_id)

    def get_active_alerts(self) -> List[InventoryAlertResponseDTO]:
        alerts = self.repo.get_active_alerts()
        return [self._to_alert_response_dto(alert) for alert in alerts]

    def _to_response_dto(self, item: InventoryItem) -> InventoryItemResponseDTO:
        return InventoryItemResponseDTO(
            id=item.id,
            name=item.name,
            category=item.category,
            current_quantity=item.current_quantity,
            minimum_stock=item.minimum_stock,
            unit=item.unit,
            is_below_minimum_stock=item.current_quantity <= item.minimum_stock,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def _to_alert_response_dto(self, alert: InventoryAlert) -> InventoryAlertResponseDTO:
        return InventoryAlertResponseDTO(
            id=alert.id,
            inventory_item_id=alert.inventory_item_id,
            order_id=alert.order_id,
            alert_type=alert.alert_type,
            message=alert.message,
            current_quantity=alert.current_quantity,
            minimum_stock=alert.minimum_stock,
            is_resolved=alert.is_resolved,
            created_at=alert.created_at,
            resolved_at=alert.resolved_at,
        )
