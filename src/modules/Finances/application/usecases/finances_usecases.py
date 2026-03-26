"""Finances Service - Core Business Logic"""

from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from src.modules.Finances.domain.entities.expense import Expense
from src.modules.Finances.infrastructure.repositories.finances_repository import (
    FinancesRepository,
)
from src.modules.Finances.application.dto.finance_response import (
    ExpenseResponseDTO,
    DailyFinancialDTO,
    PeriodFinancialDTO,
    FinancialReportDTO,
    ExpenseByCategory,
    CreateExpenseRequestDTO,
)
from src.modules.Sales.infrastructure.repositories.sales_repository import SalesRepository
from src.shared.infrastructure.database.turso_connection import get_turso_client


class FinancesService:
    """Service for financial calculations and reporting"""

    def __init__(self):
        self.repo = FinancesRepository()
        self.sales_repo = SalesRepository()
        self.client = get_turso_client()

    # ==================== EXPENSE MANAGEMENT ====================

    def create_expense(
        self, request: CreateExpenseRequestDTO, user_id: str
    ) -> ExpenseResponseDTO:
        """Create a new expense record"""
        expense = Expense(
            id=str(uuid.uuid4()),
            category=request.category,
            description=request.description,
            amount=request.amount,
            vendor=request.vendor,
            notes=request.notes,
            expense_date=request.expense_date,
            registered_at=datetime.now(),
            registered_by=user_id,
        )

        created_expense = self.repo.create_expense(expense)
        return self._to_expense_response_dto(created_expense)

    def get_expense(self, expense_id: str) -> Optional[ExpenseResponseDTO]:
        """Get expense by ID"""
        expense = self.repo.get_expense_by_id(expense_id)
        return self._to_expense_response_dto(expense) if expense else None

    def get_all_expenses(self) -> List[ExpenseResponseDTO]:
        """Get all expenses"""
        expenses = self.repo.get_all_expenses()
        return [self._to_expense_response_dto(e) for e in expenses]

    # ==================== CA1: CALCULATE TOTAL INCOME ====================

    def get_total_income_by_date(self, date: str) -> float:
        """
        CA1: Calculate total income (sum of all sales) for a specific date
        """
        try:
            sales = self.sales_repo.get_sales_by_date_range(date, date)
            total = sum(sale.final_amount for sale in sales)
            return round(total, 2)
        except Exception as e:
            print(f"Error calculating income for {date}: {e}")
            return 0.0

    def get_total_income_by_period(self, start_date: str, end_date: str) -> float:
        """
        CA1: Calculate total income (sum of all sales) for a period
        """
        try:
            sales = self.sales_repo.get_sales_by_date_range(start_date, end_date)
            total = sum(sale.final_amount for sale in sales)
            return round(total, 2)
        except Exception as e:
            print(f"Error calculating income for period {start_date} to {end_date}: {e}")
            return 0.0

    # ==================== CA2: CALCULATE NET PROFIT ====================

    def get_net_profit_by_date(self, date: str) -> dict:
        """
        CA2: Calculate net profit = income - expenses for a specific date
        Returns: {income, expenses, net_profit}
        """
        income = self.get_total_income_by_date(date)
        expenses = self.repo.get_total_expenses_by_date(date)
        net_profit = income - expenses

        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_profit": round(net_profit, 2),
        }

    def get_net_profit_by_period(self, start_date: str, end_date: str) -> dict:
        """
        CA2: Calculate net profit = income - expenses for a period
        Returns: {income, expenses, net_profit, profit_margin}
        """
        income = self.get_total_income_by_period(start_date, end_date)
        expenses = self.repo.get_total_expenses_by_period(start_date, end_date)
        net_profit = income - expenses
        profit_margin = (
            (net_profit / income * 100) if income > 0 else 0
        )

        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin": round(profit_margin, 2),
        }

    # ==================== CA3: REAL-TIME FINANCIAL REPORTS ====================

    def get_daily_financial_summary(self, date: str) -> DailyFinancialDTO:
        """
        CA3: Get real-time daily financial summary
        """
        profit_data = self.get_net_profit_by_date(date)

        # Count transactions (sales + expenses)
        sales = self.sales_repo.get_sales_by_date_range(date, date)
        expenses = self.repo.get_expenses_by_date_range(date, date)
        transaction_count = len(sales) + len(expenses)

        return DailyFinancialDTO(
            date=date,
            total_income=profit_data["income"],
            total_expenses=profit_data["expenses"],
            net_profit=profit_data["net_profit"],
            transaction_count=transaction_count,
        )

    def get_period_financial_summary(
        self, start_date: str, end_date: str
    ) -> PeriodFinancialDTO:
        """
        CA3: Get real-time period financial summary
        """
        profit_data = self.get_net_profit_by_period(start_date, end_date)

        # Calculate daily averages
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1

        daily_avg_income = profit_data["income"] / days if days > 0 else 0
        daily_avg_expense = profit_data["expenses"] / days if days > 0 else 0
        daily_avg_profit = profit_data["net_profit"] / days if days > 0 else 0

        # Count transactions
        sales = self.sales_repo.get_sales_by_date_range(start_date, end_date)
        expenses = self.repo.get_expenses_by_date_range(start_date, end_date)
        transaction_count = len(sales) + len(expenses)

        return PeriodFinancialDTO(
            period_start=start_date,
            period_end=end_date,
            total_income=profit_data["income"],
            total_expenses=profit_data["expenses"],
            net_profit=profit_data["net_profit"],
            profit_margin=profit_data["profit_margin"],
            daily_average_income=round(daily_avg_income, 2),
            daily_average_expense=round(daily_avg_expense, 2),
            daily_average_profit=round(daily_avg_profit, 2),
            transaction_count=transaction_count,
        )

    def get_comprehensive_financial_report(
        self, start_date: str, end_date: str
    ) -> FinancialReportDTO:
        """
        CA3: Get comprehensive financial report with detailed breakdown
        """
        period_summary = self.get_period_financial_summary(start_date, end_date)

        # Generate daily summaries
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current = start

        daily_summaries = []
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            daily_summaries.append(self.get_daily_financial_summary(date_str))
            current += timedelta(days=1)

        # Get expense breakdown by category
        category_summary = self.repo.get_expense_summary_by_category(
            start_date, end_date
        )
        total_expenses = period_summary.total_expenses

        expenses_by_category = []
        top_category = None

        for cat_id, cat_data in category_summary.items():
            amount = cat_data["amount"]
            percentage = (
                (amount / total_expenses * 100) if total_expenses > 0 else 0
            )

            expense_by_cat = ExpenseByCategory(
                category_name=cat_data["name"],
                amount=round(amount, 2),
                percentage=round(percentage, 2),
                count=cat_data["count"],
            )

            expenses_by_category.append(expense_by_cat)

            # Track top category
            if top_category is None or amount > top_category.amount:
                top_category = expense_by_cat

        # Sort by amount descending
        expenses_by_category.sort(key=lambda x: x.amount, reverse=True)

        return FinancialReportDTO(
            period_start=start_date,
            period_end=end_date,
            total_income=period_summary.total_income,
            total_expenses=period_summary.total_expenses,
            net_profit=period_summary.net_profit,
            profit_margin=period_summary.profit_margin,
            daily_summary=daily_summaries,
            expenses_by_category=expenses_by_category,
            top_expense_category=top_category,
        )

    def _to_expense_response_dto(self, expense: Optional[Expense]) -> Optional[ExpenseResponseDTO]:
        """Convert Expense entity to DTO"""
        if not expense:
            return None

        return ExpenseResponseDTO(
            id=expense.id,
            category=expense.category,
            description=expense.description,
            amount=expense.amount,
            vendor=expense.vendor,
            notes=expense.notes,
            expense_date=expense.expense_date,
            registered_at=expense.registered_at,
            registered_by=expense.registered_by,
        )
