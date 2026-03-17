from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.Inventory.domain.entities.inventory_item import InventoryItem


class IInventoryRepository(ABC):
    @abstractmethod
    def create(self, item: InventoryItem) -> InventoryItem:
        pass

    @abstractmethod
    def get_by_id(self, item_id: str) -> Optional[InventoryItem]:
        pass

    @abstractmethod
    def get_all(self) -> List[InventoryItem]:
        pass

    @abstractmethod
    def update(self, item: InventoryItem) -> InventoryItem:
        pass

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def exists_by_name(self, name: str, excluding_id: Optional[str] = None) -> bool:
        pass
