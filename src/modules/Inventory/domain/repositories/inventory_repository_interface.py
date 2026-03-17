from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.Inventory.domain.entities.inventory_alert import InventoryAlert
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

    @abstractmethod
    def deduct_stock(self, item_id: str, quantity: float) -> InventoryItem:
        pass

    @abstractmethod
    def create_alert(self, alert: InventoryAlert) -> InventoryAlert:
        pass

    @abstractmethod
    def get_active_alerts(self) -> List[InventoryAlert]:
        pass

    @abstractmethod
    def get_all_alerts(self) -> List[InventoryAlert]:
        pass

    @abstractmethod
    def mark_alert_as_viewed(self, alert_id: str) -> Optional[InventoryAlert]:
        pass

    @abstractmethod
    def mark_alert_as_resolved(self, alert_id: str) -> Optional[InventoryAlert]:
        pass

    @abstractmethod
    def create_daily_low_stock_alerts(self, check_date: str) -> int:
        pass

    @abstractmethod
    def is_order_inventory_processed(self, order_id: str) -> bool:
        pass

    @abstractmethod
    def mark_order_inventory_processed(self, order_id: str, triggered_status: str) -> None:
        pass
