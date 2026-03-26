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
from src.modules.Finances.infrastructure.repositories.financial_reports_repository import (
    FinancialReportsRepository,
)
from src.modules.Finances.application.dto.financial_reports_dto import (
    DetailedFinancialReportDTO,
    FinancialMetricsDTO,
    PaymentMethodSummary,
    WaiterPerformanceDTO,
    SaleItemDetailDTO,
    ItemBreakdownDTO,
    FilteredSalesReportDTO,
    CategoryProductSummary,
    FinancialComparisonReportDTO,
    ComparisonPeriodDTO,
)
from src.shared.infrastructure.database.turso_connection import get_turso_client


class FinancesService:
    """Service for financial calculations and reporting"""

    def __init__(self):
        self.repo = FinancesRepository()
        self.sales_repo = SalesRepository()
        self.reports_repo = FinancialReportsRepository()
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

    # ==================== CA1: Detailed Sales Reports ====================

    def get_sales_report_by_period(
        self, start_date: str, end_date: str
    ) -> FilteredSalesReportDTO:
        """CA1: Get detailed sales report filtered by date"""
        sales_data = self.reports_repo.get_sales_with_items(start_date, end_date)
        
        total_sales = len(sales_data)
        total_amount = sum(s["final_amount"] for s in sales_data)
        average_amount = total_amount / total_sales if total_sales > 0 else 0.0

        sales_detail = [
            SaleItemDetailDTO(
                id=s["id"],
                order_number=s["order_number"],
                customer_name=s["customer_name"],
                waiter_name=s["waiter_name"],
                payment_method=s["payment_method"],
                total_amount=s["total_amount"],
                final_amount=s["final_amount"],
                sale_date=s["sale_date"],
                items=[
                    ItemBreakdownDTO(
                        menu_item_name=item["menu_item_name"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        subtotal=item["subtotal"],
                        percentage_of_total=round((item["subtotal"] / s["final_amount"]) * 100, 2) if s["final_amount"] > 0 else 0.0,
                    )
                    for item in s["items"]
                ],
            )
            for s in sales_data
        ]

        return FilteredSalesReportDTO(
            period_start=start_date,
            period_end=end_date,
            total_sales=total_sales,
            total_amount=round(total_amount, 2),
            average_amount=round(average_amount, 2),
            sales_list=sales_detail,
            applied_filters={"date_range": f"{start_date} to {end_date}"},
        )

    # ==================== CA2: Filtered Reports ====================

    def get_sales_report_by_payment_method(
        self, start_date: str, end_date: str, payment_method: str
    ) -> FilteredSalesReportDTO:
        """CA2: Get sales report filtered by payment method"""
        sales_data = self.reports_repo.get_sales_by_payment_method(
            start_date, end_date, payment_method
        )

        total_sales = len(sales_data)
        total_amount = sum(s["final_amount"] for s in sales_data)
        average_amount = total_amount / total_sales if total_sales > 0 else 0.0

        sales_detail = [
            SaleItemDetailDTO(
                id=s["id"],
                order_number=s["order_number"],
                customer_name=s["customer_name"],
                waiter_name=self.reports_repo._get_waiter_name(s["waiter_id"]),
                payment_method=s["payment_method"],
                total_amount=s["total_amount"],
                final_amount=s["final_amount"],
                sale_date=s["sale_date"],
            )
            for s in sales_data
        ]

        return FilteredSalesReportDTO(
            period_start=start_date,
            period_end=end_date,
            total_sales=total_sales,
            total_amount=round(total_amount, 2),
            average_amount=round(average_amount, 2),
            sales_list=sales_detail,
            applied_filters={"payment_method": payment_method},
        )

    def get_sales_report_by_waiter(
        self, start_date: str, end_date: str, waiter_id: str
    ) -> FilteredSalesReportDTO:
        """CA2: Get sales report filtered by employee"""
        sales_data = self.reports_repo.get_sales_by_waiter(start_date, end_date, waiter_id)

        total_sales = len(sales_data)
        total_amount = sum(s["final_amount"] for s in sales_data)
        average_amount = total_amount / total_sales if total_sales > 0 else 0.0
        waiter_name = self.reports_repo._get_waiter_name(waiter_id)

        sales_detail = [
            SaleItemDetailDTO(
                id=s["id"],
                order_number=s["order_number"],
                customer_name=s["customer_name"],
                waiter_name=waiter_name,
                payment_method=s["payment_method"],
                total_amount=s["total_amount"],
                final_amount=s["final_amount"],
                sale_date=s["sale_date"],
            )
            for s in sales_data
        ]

        return FilteredSalesReportDTO(
            period_start=start_date,
            period_end=end_date,
            total_sales=total_sales,
            total_amount=round(total_amount, 2),
            average_amount=round(average_amount, 2),
            sales_list=sales_detail,
            applied_filters={"waiter_id": waiter_id, "waiter_name": waiter_name},
        )

    # ==================== CA3: Comprehensive Reports with Metadata ====================

    def get_detailed_financial_report(
        self, start_date: str, end_date: str
    ) -> DetailedFinancialReportDTO:
        """CA3: Get comprehensive financial report with metrics and breakdowns"""
        
        # Get base metrics
        metrics_data = self.reports_repo.get_financial_metrics(start_date, end_date)
        expenses = self.repo.get_total_expenses_by_period(start_date, end_date)
        net_profit = metrics_data["total_revenue"] - expenses

        metrics = FinancialMetricsDTO(
            period_start=start_date,
            period_end=end_date,
            total_sales=metrics_data["total_sales"],
            total_revenue=round(metrics_data["total_revenue"], 2),
            total_tax=round(metrics_data["total_tax"], 2),
            total_discount=round(metrics_data["total_discount"], 2),
            total_expenses=round(expenses, 2),
            net_profit=round(net_profit, 2),
            profit_margin_percent=round((net_profit / metrics_data["total_revenue"] * 100) if metrics_data["total_revenue"] > 0 else 0, 2),
            average_ticket=round(metrics_data["average_ticket"], 2),
            average_discount_percent=round(metrics_data["average_discount_percent"], 2),
        )

        # Payment method summary
        payment_methods_data = self.reports_repo.get_payment_method_summary(start_date, end_date)
        by_payment_method = [
            PaymentMethodSummary(
                method=data["method"],
                count=data["count"],
                total_amount=round(data["total_amount"], 2),
                average_amount=round(data["average_amount"], 2),
                percentage=round((data["total_amount"] / metrics_data["total_revenue"] * 100) if metrics_data["total_revenue"] > 0 else 0, 2),
            )
            for data in payment_methods_data.values()
        ]

        # Waiter performance
        waiters_data = self.reports_repo.get_waiter_performance_summary(start_date, end_date)
        by_waiter = [
            WaiterPerformanceDTO(
                waiter_id=data["waiter_id"],
                waiter_name=data["waiter_name"],
                sales_count=data["sales_count"],
                total_sales=round(data["total_sales"], 2),
                average_sale=round(data["average_sale"], 2),
                percentage_of_total=round((data["total_sales"] / metrics_data["total_revenue"] * 100) if metrics_data["total_revenue"] > 0 else 0, 2),
            )
            for data in waiters_data.values()
        ]

        # Product category summary
        products_data = self.reports_repo.get_product_category_summary(start_date, end_date)
        by_product_category = [
            CategoryProductSummary(
                category=data["menu_item_name"],
                items_sold=data["quantity"],
                total_quantity=data["quantity"],
                total_amount=round(data["total_amount"], 2),
                percentage=round((data["total_amount"] / metrics_data["total_revenue"] * 100) if metrics_data["total_revenue"] > 0 else 0, 2),
                most_sold_item=data["menu_item_name"],
                least_sold_item=data["menu_item_name"],
            )
            for data in products_data.values()
        ]

        # Sales detail
        sales_data = self.reports_repo.get_sales_with_items(start_date, end_date)
        sales_detail = [
            SaleItemDetailDTO(
                id=s["id"],
                order_number=s["order_number"],
                customer_name=s["customer_name"],
                waiter_name=s["waiter_name"],
                payment_method=s["payment_method"],
                total_amount=s["total_amount"],
                final_amount=s["final_amount"],
                sale_date=s["sale_date"],
                items=[
                    ItemBreakdownDTO(
                        menu_item_name=item["menu_item_name"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        subtotal=item["subtotal"],
                        percentage_of_total=round((item["subtotal"] / s["final_amount"]) * 100, 2) if s["final_amount"] > 0 else 0.0,
                    )
                    for item in s["items"]
                ],
            )
            for s in sales_data
        ]

        return DetailedFinancialReportDTO(
            period_start=start_date,
            period_end=end_date,
            metrics=metrics,
            by_payment_method=by_payment_method,
            by_waiter=by_waiter,
            by_product_category=by_product_category,
            sales_detail=sales_detail,
            filters_applied={"date_range": f"{start_date} to {end_date}"},
        )

    def get_financial_comparison_report(
        self, current_start: str, current_end: str, 
        previous_start: str, previous_end: str
    ) -> FinancialComparisonReportDTO:
        """CA3: Get comparative financial report between two periods"""
        
        # Current period
        current_metrics_data = self.reports_repo.get_financial_metrics(current_start, current_end)
        current_expenses = self.repo.get_total_expenses_by_period(current_start, current_end)
        current_profit = current_metrics_data["total_revenue"] - current_expenses

        current_metrics = FinancialMetricsDTO(
            period_start=current_start,
            period_end=current_end,
            total_sales=current_metrics_data["total_sales"],
            total_revenue=round(current_metrics_data["total_revenue"], 2),
            total_tax=round(current_metrics_data["total_tax"], 2),
            total_discount=round(current_metrics_data["total_discount"], 2),
            total_expenses=round(current_expenses, 2),
            net_profit=round(current_profit, 2),
            profit_margin_percent=round((current_profit / current_metrics_data["total_revenue"] * 100) if current_metrics_data["total_revenue"] > 0 else 0, 2),
            average_ticket=round(current_metrics_data["average_ticket"], 2),
            average_discount_percent=round(current_metrics_data["average_discount_percent"], 2),
        )

        # Previous period
        previous_metrics_data = self.reports_repo.get_financial_metrics(previous_start, previous_end)
        previous_expenses = self.repo.get_total_expenses_by_period(previous_start, previous_end)
        previous_profit = previous_metrics_data["total_revenue"] - previous_expenses

        previous_metrics = FinancialMetricsDTO(
            period_start=previous_start,
            period_end=previous_end,
            total_sales=previous_metrics_data["total_sales"],
            total_revenue=round(previous_metrics_data["total_revenue"], 2),
            total_tax=round(previous_metrics_data["total_tax"], 2),
            total_discount=round(previous_metrics_data["total_discount"], 2),
            total_expenses=round(previous_expenses, 2),
            net_profit=round(previous_profit, 2),
            profit_margin_percent=round((previous_profit / previous_metrics_data["total_revenue"] * 100) if previous_metrics_data["total_revenue"] > 0 else 0, 2),
            average_ticket=round(previous_metrics_data["average_ticket"], 2),
            average_discount_percent=round(previous_metrics_data["average_discount_percent"], 2),
        )

        # Calculate growth rates
        revenue_change = current_metrics_data["total_revenue"] - previous_metrics_data["total_revenue"]
        expense_change = current_expenses - previous_expenses
        profit_change = current_profit - previous_profit
        growth_rate = (revenue_change / previous_metrics_data["total_revenue"] * 100) if previous_metrics_data["total_revenue"] > 0 else 0

        comparison = ComparisonPeriodDTO(
            current_period=current_metrics,
            previous_period=previous_metrics,
            growth_rate_percent=round(growth_rate, 2),
            revenue_change=round(revenue_change, 2),
            expense_change=round(expense_change, 2),
            profit_change=round(profit_change, 2),
        )

        # Generate insights
        insights = self._generate_insights(comparison)

        return FinancialComparisonReportDTO(
            comparison=comparison,
            insights=insights,
        )

    def _generate_insights(self, comparison: ComparisonPeriodDTO) -> List[str]:
        """Generate automatic insights from comparison"""
        insights = []

        if comparison.growth_rate_percent > 10:
            insights.append(f"📈 Crecimiento fuerte: ingresos aumentaron {comparison.growth_rate_percent}%")
        elif comparison.growth_rate_percent > 0:
            insights.append(f"📊 Crecimiento moderado: ingresos aumentaron {comparison.growth_rate_percent}%")
        elif comparison.growth_rate_percent < -10:
            insights.append(f"📉 Caída significativa: ingresos disminuyeron {abs(comparison.growth_rate_percent)}%")
        else:
            insights.append(f"➡️ Ingresos estables con cambio de {comparison.growth_rate_percent}%")

        if comparison.current_period.profit_margin_percent > comparison.previous_period.profit_margin_percent:
            margin_diff = comparison.current_period.profit_margin_percent - comparison.previous_period.profit_margin_percent
            insights.append(f"💰 Margen de ganancia mejoró: +{margin_diff}% (ahora {comparison.current_period.profit_margin_percent}%)")
        else:
            margin_diff = comparison.previous_period.profit_margin_percent - comparison.current_period.profit_margin_percent
            insights.append(f"⚠️ Margen de ganancia disminuyó: -{margin_diff}% (ahora {comparison.current_period.profit_margin_percent}%)")

        if comparison.expense_change > 0:
            insights.append(f"💸 Gastos aumentaron: +${abs(comparison.expense_change)}")
        else:
            insights.append(f"✅ Gastos reducidos: ${abs(comparison.expense_change)}")

        return insights

