"""Domain Repository Interface - Finances Module"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.Finances.domain.entities.expense import Expense, ExpenseCategory


class FinancesRepositoryInterface(ABC):
    """Contract for Finances Repository"""

    @abstractmethod
    def create_expense(self, expense: Expense) -> Expense:
        """Create a new expense record"""
        pass

    @abstractmethod
    def get_expense_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get expense by ID"""
        pass

    @abstractmethod
    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses"""
        pass

    @abstractmethod
    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        """Get expenses within date range (YYYY-MM-DD)"""
        pass

    @abstractmethod
    def get_expenses_by_category(self, category_id: str) -> List[Expense]:
        """Get expenses by category"""
        pass

    @abstractmethod
    def get_total_expenses_by_date(self, date: str) -> float:
        """Get total expenses for a specific date"""
        pass

    @abstractmethod
    def get_total_expenses_by_period(self, start_date: str, end_date: str) -> float:
        """Get total expenses for a period"""
        pass

    @abstractmethod
    def get_categories(self) -> List[ExpenseCategory]:
        """Get all expense categories"""
        pass

    @abstractmethod
    def get_expense_summary_by_category(self, start_date: str, end_date: str) -> dict:
        """Get expense breakdown by category for a period"""
        pass
