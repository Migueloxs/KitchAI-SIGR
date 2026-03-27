"""Analytics domain entities."""

from datetime import datetime
from typing import Optional, List


class SalesAggregate:
    """Represents aggregated sales data by product, hour, category and service type."""
    
    def __init__(
        self,
        id: str,
        date: str,
        product_id: str,
        product_name: str,
        category_id: str,
        category_name: str,
        hour: Optional[int],
        service_type: str,
        employee_id: Optional[str],
        quantity_sold: int,
        revenue: float,
        cost: float,
        profit: float,
        discount_applied: float,
        tax_collected: float,
        transaction_count: int,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.date = date
        self.product_id = product_id
        self.product_name = product_name
        self.category_id = category_id
        self.category_name = category_name
        self.hour = hour
        self.service_type = service_type  # 'dine-in', 'delivery', 'takeaway'
        self.employee_id = employee_id
        self.quantity_sold = quantity_sold
        self.revenue = revenue
        self.cost = cost
        self.profit = profit
        self.discount_applied = discount_applied
        self.tax_collected = tax_collected
        self.transaction_count = transaction_count
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


class DailySummary:
    """Represents daily aggregated summary of all sales."""
    
    def __init__(
        self,
        id: str,
        date: str,
        total_revenue: float,
        total_cost: float,
        total_profit: float,
        total_discount: float,
        total_tax: float,
        total_transactions: int,
        total_items_sold: int,
        average_ticket: float,
        dine_in_revenue: float,
        dine_in_transactions: int,
        delivery_revenue: float,
        delivery_transactions: int,
        takeaway_revenue: float,
        takeaway_transactions: int,
        peak_hour: Optional[int] = None,
        peak_hour_revenue: float = 0.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.date = date
        self.total_revenue = total_revenue
        self.total_cost = total_cost
        self.total_profit = total_profit
        self.total_discount = total_discount
        self.total_tax = total_tax
        self.total_transactions = total_transactions
        self.total_items_sold = total_items_sold
        self.average_ticket = average_ticket
        self.dine_in_revenue = dine_in_revenue
        self.dine_in_transactions = dine_in_transactions
        self.delivery_revenue = delivery_revenue
        self.delivery_transactions = delivery_transactions
        self.takeaway_revenue = takeaway_revenue
        self.takeaway_transactions = takeaway_transactions
        self.peak_hour = peak_hour
        self.peak_hour_revenue = peak_hour_revenue
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


class PeriodComparison:
    """Represents comparison data between two periods."""
    
    def __init__(
        self,
        id: str,
        period_start_date: str,
        period_end_date: str,
        period_type: str,
        current_revenue: float,
        current_cost: float,
        current_profit: float,
        current_transactions: int,
        previous_period_start_date: str,
        previous_period_end_date: str,
        previous_revenue: float,
        previous_cost: float,
        previous_profit: float,
        previous_transactions: int,
        revenue_change_percentage: Optional[float] = None,
        profit_change_percentage: Optional[float] = None,
        transaction_growth_percentage: Optional[float] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.period_start_date = period_start_date
        self.period_end_date = period_end_date
        self.period_type = period_type  # 'day', 'week', 'month', 'quarter', 'year'
        self.current_revenue = current_revenue
        self.current_cost = current_cost
        self.current_profit = current_profit
        self.current_transactions = current_transactions
        self.previous_period_start_date = previous_period_start_date
        self.previous_period_end_date = previous_period_end_date
        self.previous_revenue = previous_revenue
        self.previous_cost = previous_cost
        self.previous_profit = previous_profit
        self.previous_transactions = previous_transactions
        self.revenue_change_percentage = revenue_change_percentage
        self.profit_change_percentage = profit_change_percentage
        self.transaction_growth_percentage = transaction_growth_percentage
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()


class EmployeePerformance:
    """Represents employee performance metrics."""
    
    def __init__(
        self,
        id: str,
        employee_id: str,
        date: str,
        total_sales: float,
        total_transactions: int,
        average_ticket: float,
        items_sold: int,
        rating: Optional[float] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.employee_id = employee_id
        self.date = date
        self.total_sales = total_sales
        self.total_transactions = total_transactions
        self.average_ticket = average_ticket
        self.items_sold = items_sold
        self.rating = rating
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
