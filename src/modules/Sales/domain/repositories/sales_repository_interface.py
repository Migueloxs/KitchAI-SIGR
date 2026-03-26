from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from src.modules.Sales.domain.entities.sale import Sale


class SalesRepositoryInterface(ABC):
    @abstractmethod
    def create(self, sale: Sale) -> Sale:
        pass

    @abstractmethod
    def get_by_id(self, sale_id: str) -> Optional[Sale]:
        pass

    @abstractmethod
    def get_by_order_id(self, order_id: str) -> Optional[Sale]:
        pass

    @abstractmethod
    def get_all(self) -> List[Sale]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        pass

    @abstractmethod
    def get_by_waiter(self, waiter_id: str) -> List[Sale]:
        pass

    @abstractmethod
    def get_summary_by_date(self, date: str) -> dict:
        pass

    @abstractmethod
    def get_summary_by_waiter(self, start_date: str, end_date: str) -> List[dict]:
        pass

    @abstractmethod
    def get_summary_by_payment_method(self, start_date: str, end_date: str) -> List[dict]:
        pass

    @abstractmethod
    def exists_for_order(self, order_id: str) -> bool:
        pass
