"""Repository Implementation - Finances Module"""

from datetime import datetime
from typing import List, Optional, Dict
import uuid

from src.modules.Finances.domain.entities.expense import Expense, ExpenseCategory
from src.modules.Finances.domain.repositories.finances_repository_interface import (
    FinancesRepositoryInterface,
)
from src.shared.infrastructure.database.turso_connection import get_turso_client


class FinancesRepository(FinancesRepositoryInterface):
    def __init__(self):
        self.client = get_turso_client()

    def create_expense(self, expense: Expense) -> Expense:
        """Create a new expense record"""
        expense_id = expense.id or str(uuid.uuid4())

        self.client.execute(
            """
            INSERT INTO expenses (
                id, category, description, amount, vendor, notes,
                expense_date, registered_at, registered_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                expense_id,
                expense.category,
                expense.description,
                expense.amount,
                expense.vendor,
                expense.notes,
                expense.expense_date,
                expense.registered_at.isoformat(),
                expense.registered_by,
            ],
        )

        expense.id = expense_id
        return expense

    def get_expense_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get expense by ID"""
        result = self.client.execute(
            "SELECT * FROM expenses WHERE id = ?",
            [expense_id],
        )

        if not result.rows:
            return None

        return self._map_to_expense(result.rows[0])

    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses"""
        result = self.client.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, registered_at DESC"
        )

        return [self._map_to_expense(row) for row in result.rows]

    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        """Get expenses within date range (YYYY-MM-DD)"""
        result = self.client.execute(
            """
            SELECT * FROM expenses
            WHERE expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC, registered_at DESC
            """,
            [start_date, end_date],
        )

        return [self._map_to_expense(row) for row in result.rows]

    def get_expenses_by_category(self, category_id: str) -> List[Expense]:
        """Get expenses by category"""
        result = self.client.execute(
            """
            SELECT * FROM expenses
            WHERE category = ?
            ORDER BY expense_date DESC
            """,
            [category_id],
        )

        return [self._map_to_expense(row) for row in result.rows]

    def get_total_expenses_by_date(self, date: str) -> float:
        """Get total expenses for a specific date"""
        result = self.client.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE expense_date = ?",
            [date],
        )

        if result.rows and result.rows[0][0]:
            return float(result.rows[0][0])
        return 0.0

    def get_total_expenses_by_period(self, start_date: str, end_date: str) -> float:
        """Get total expenses for a period"""
        result = self.client.execute(
            """
            SELECT SUM(amount) as total FROM expenses
            WHERE expense_date BETWEEN ? AND ?
            """,
            [start_date, end_date],
        )

        if result.rows and result.rows[0][0]:
            return float(result.rows[0][0])
        return 0.0

    def get_categories(self) -> List[ExpenseCategory]:
        """Get all expense categories"""
        result = self.client.execute("SELECT * FROM expense_categories ORDER BY name")

        categories = []
        for row in result.rows:
            categories.append(
                ExpenseCategory(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                )
            )

        return categories

    def get_expense_summary_by_category(
        self, start_date: str, end_date: str
    ) -> dict:
        """Get expense breakdown by category for a period"""
        result = self.client.execute(
            """
            SELECT ec.id, ec.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN expense_categories ec ON e.category = ec.id
            WHERE e.expense_date BETWEEN ? AND ?
            GROUP BY ec.id, ec.name
            ORDER BY total DESC
            """,
            [start_date, end_date],
        )

        summary = {}
        for row in result.rows:
            summary[row[0]] = {
                "name": row[1],
                "amount": float(row[2]) if row[2] else 0.0,
                "count": row[3],
            }

        return summary

    def _map_to_expense(self, row: tuple) -> Expense:
        """Map database row to Expense entity"""
        return Expense(
            id=row[0],
            category=row[1],
            description=row[2],
            amount=float(row[3]),
            vendor=row[4],
            notes=row[5],
            expense_date=row[6],
            registered_at=datetime.fromisoformat(row[7]),
            registered_by=row[8],
        )
