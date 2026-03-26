"""Data Transfer Objects - Finances Module"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class ExpenseResponseDTO(BaseModel):
    id: str
    category: str
    description: str
    amount: float
    vendor: Optional[str] = None
    notes: Optional[str] = None
    expense_date: str
    registered_at: datetime
    registered_by: Optional[str] = None


class ExpenseCategoryDTO(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class DailyFinancialDTO(BaseModel):
    """Daily financial summary"""
    date: str
    total_income: float
    total_expenses: float
    net_profit: float
    transaction_count: int


class PeriodFinancialDTO(BaseModel):
    """Period (week/month) financial summary"""
    period_start: str
    period_end: str
    total_income: float
    total_expenses: float
    net_profit: float
    profit_margin: float  # (net_profit / total_income) * 100
    daily_average_income: float
    daily_average_expense: float
    daily_average_profit: float
    transaction_count: int


class ExpenseByCategory(BaseModel):
    category_name: str
    amount: float
    percentage: float
    count: int


class FinancialReportDTO(BaseModel):
    """Comprehensive financial report"""
    period_start: str
    period_end: str
    total_income: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    daily_summary: List[DailyFinancialDTO]
    expenses_by_category: List[ExpenseByCategory]
    top_expense_category: Optional[ExpenseByCategory] = None


class CreateExpenseRequestDTO(BaseModel):
    category: str
    description: str
    amount: float
    vendor: Optional[str] = None
    notes: Optional[str] = None
    expense_date: str  # YYYY-MM-DD
