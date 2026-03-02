from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.Order.domain.entities.order import Order

class IOrderRepository(ABC):
    @abstractmethod
    def create(self, order: Order) -> Order: pass
    
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]: pass
    
    @abstractmethod
    def get_all(self, waiter_id: Optional[str] = None) -> List[Order]: pass
    
    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool: pass