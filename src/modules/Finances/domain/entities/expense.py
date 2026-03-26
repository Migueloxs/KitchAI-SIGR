"""Domain Entities - Finances Module"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExpenseCategory(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime


class Expense(BaseModel):
    id: str
    category: str  # FK to expense_categories.id
    description: str
    amount: float
    vendor: Optional[str] = None
    notes: Optional[str] = None
    expense_date: str  # YYYY-MM-DD
    registered_at: datetime
    registered_by: Optional[str] = None  # User ID who registered the expense
