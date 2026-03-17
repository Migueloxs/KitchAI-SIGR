from datetime import datetime
from typing import List, Optional
import uuid

from src.modules.Inventory.application.dto.inventory_request import (
    CreateInventoryItemRequestDTO,
    UpdateInventoryItemRequestDTO,
)
from src.modules.Inventory.application.dto.inventory_response import InventoryItemResponseDTO
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
