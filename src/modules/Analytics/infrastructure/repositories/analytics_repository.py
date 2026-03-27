"""Analytics repository for database access."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.modules.Analytics.domain.entities import (
    SalesAggregate,
    DailySummary,
    PeriodComparison,
    EmployeePerformance,
)
from src.shared.infrastructure.database.turso_connection import get_turso_client
import uuid


class AnalyticsRepository:
    """Repository for analytics data access."""
    
    def __init__(self):
        self.client = get_turso_client()
    
    def get_sales_aggregates_by_date_range(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
        employee_id: Optional[str] = None,
        category_name: Optional[str] = None,
    ) -> List[SalesAggregate]:
        """Get sales aggregates for a date range with optional filters."""
        
        query = """
        SELECT 
            id, date, product_id, product_name, category_id, category_name,
            hour, service_type, employee_id, quantity_sold, revenue, cost,
            profit, discount_applied, tax_collected, transaction_count,
            created_at, updated_at
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        if service_type and service_type.lower() != "all":
            query += " AND service_type = ?"
            params.append(service_type)
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if category_name:
            query += " AND category_name = ?"
            params.append(category_name)
        
        query += " ORDER BY date DESC, hour DESC"
        
        result = self.client.execute(query, params)
        
        return [self._map_row_to_sales_aggregate(row) for row in result.rows]
    
    def get_aggregated_by_product(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated sales data grouped by product."""
        
        query = """
        SELECT 
            product_id,
            product_name,
            category_name,
            SUM(quantity_sold) as total_quantity,
            SUM(revenue) as total_revenue,
            SUM(profit) as total_profit,
            SUM(discount_applied) as total_discount,
            SUM(transaction_count) as transaction_count,
            COUNT(DISTINCT date, hour) as periods_sold
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        if service_type and service_type.lower() != "all":
            query += " AND service_type = ?"
            params.append(service_type)
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        query += " GROUP BY product_id, product_name, category_name ORDER BY total_revenue DESC"
        
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_aggregated_by_category(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated sales data grouped by category."""
        
        query = """
        SELECT 
            category_name,
            SUM(quantity_sold) as total_quantity,
            SUM(revenue) as total_revenue,
            SUM(profit) as total_profit,
            SUM(transaction_count) as transaction_count,
            COUNT(DISTINCT product_id) as product_count
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        if service_type and service_type.lower() != "all":
            query += " AND service_type = ?"
            params.append(service_type)
        
        query += " GROUP BY category_name ORDER BY total_revenue DESC"
        
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_aggregated_by_hour(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated sales data grouped by hour."""
        
        query = """
        SELECT 
            hour,
            SUM(revenue) as revenue,
            SUM(quantity_sold) as quantity_sold,
            SUM(transaction_count) as transaction_count,
            ROUND(SUM(revenue) / NULLIF(SUM(quantity_sold), 0), 2) as avg_price_per_item
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ? AND hour IS NOT NULL
        """
        
        params = [start_date, end_date]
        
        if service_type and service_type.lower() != "all":
            query += " AND service_type = ?"
            params.append(service_type)
        
        query += " GROUP BY hour ORDER BY hour ASC"
        
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_aggregated_by_service_type(
        self,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Get aggregated sales data grouped by service type."""
        
        query = """
        SELECT 
            service_type,
            SUM(revenue) as revenue,
            SUM(transaction_count) as transaction_count
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        GROUP BY service_type
        ORDER BY revenue DESC
        """
        
        params = [start_date, end_date]
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_period_totals(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get total metrics for a period."""
        
        query = """
        SELECT 
            SUM(revenue) as total_revenue,
            SUM(cost) as total_cost,
            SUM(profit) as total_profit,
            SUM(discount_applied) as total_discount,
            SUM(tax_collected) as total_tax,
            SUM(transaction_count) as total_transactions,
            SUM(quantity_sold) as total_quantity
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        if service_type and service_type.lower() != "all":
            query += " AND service_type = ?"
            params.append(service_type)
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        result = self.client.execute(query, params)
        
        if result.rows:
            row = result.rows[0]
            return {
                "total_revenue": row[0] or 0.0,
                "total_cost": row[1] or 0.0,
                "total_profit": row[2] or 0.0,
                "total_discount": row[3] or 0.0,
                "total_tax": row[4] or 0.0,
                "total_transactions": row[5] or 0,
                "total_quantity": row[6] or 0,
            }
        
        return {
            "total_revenue": 0.0,
            "total_cost": 0.0,
            "total_profit": 0.0,
            "total_discount": 0.0,
            "total_tax": 0.0,
            "total_transactions": 0,
            "total_quantity": 0,
        }
    
    def get_period_comparison(
        self,
        period_type: str,  # 'day', 'week', 'month', 'quarter', 'year'
        current_start: str,
        current_end: str,
    ) -> Dict[str, Any]:
        """Get comparison with previous period."""
        
        from datetime import datetime, timedelta
        
        current_start_dt = datetime.strptime(current_start, "%Y-%m-%d")
        current_end_dt = datetime.strptime(current_end, "%Y-%m-%d")
        
        # Calculate previous period dates based on period_type
        if period_type == "day":
            period_delta = timedelta(days=1)
        elif period_type == "week":
            period_delta = timedelta(weeks=1)
        elif period_type == "month":
            period_delta = timedelta(days=30)
        elif period_type == "quarter":
            period_delta = timedelta(days=90)
        elif period_type == "year":
            period_delta = timedelta(days=365)
        else:
            period_delta = timedelta(days=1)
        
        previous_start_dt = current_start_dt - period_delta
        previous_end_dt = current_end_dt - period_delta
        
        current_data = self.get_period_totals(current_start, current_end)
        previous_data = self.get_period_totals(
            previous_start_dt.strftime("%Y-%m-%d"),
            previous_end_dt.strftime("%Y-%m-%d"),
        )
        
        # Calculate percentage changes
        revenue_change = 0.0
        if previous_data["total_revenue"] > 0:
            revenue_change = (
                (current_data["total_revenue"] - previous_data["total_revenue"]) 
                / previous_data["total_revenue"] * 100
            )
        
        profit_change = 0.0
        if previous_data["total_profit"] != 0:
            profit_change = (
                (current_data["total_profit"] - previous_data["total_profit"]) 
                / abs(previous_data["total_profit"]) * 100
            )
        
        transaction_growth = 0.0
        if previous_data["total_transactions"] > 0:
            transaction_growth = (
                (current_data["total_transactions"] - previous_data["total_transactions"]) 
                / previous_data["total_transactions"] * 100
            )
        
        return {
            "current_period": current_data,
            "previous_period": previous_data,
            "revenue_change_percentage": round(revenue_change, 2),
            "profit_change_percentage": round(profit_change, 2),
            "transaction_growth_percentage": round(transaction_growth, 2),
        }
    
    def get_employee_performance(
        self,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Get employee performance metrics."""
        
        query = """
        SELECT 
            employee_id,
            SUM(revenue) as total_sales,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(revenue) / NULLIF(SUM(transaction_count), 0), 2) as average_ticket,
            SUM(quantity_sold) as items_sold
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ? AND employee_id IS NOT NULL
        GROUP BY employee_id
        ORDER BY total_sales DESC
        """
        
        params = [start_date, end_date]
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_peak_hours(
        self,
        start_date: str,
        end_date: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get peak sales hours."""
        
        query = """
        SELECT 
            hour,
            SUM(revenue) as revenue,
            SUM(quantity_sold) as quantity_sold,
            SUM(transaction_count) as transaction_count,
            ROUND(SUM(revenue) / NULLIF(SUM(quantity_sold), 0), 2) as avg_price_per_item
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ? AND hour IS NOT NULL
        GROUP BY hour
        ORDER BY revenue DESC
        LIMIT ?
        """
        
        params = [start_date, end_date, limit]
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def get_top_products(
        self,
        start_date: str,
        end_date: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top performing products."""
        
        query = """
        SELECT 
            product_id,
            product_name,
            category_name,
            SUM(quantity_sold) as total_quantity,
            SUM(revenue) as total_revenue,
            SUM(profit) as total_profit,
            SUM(transaction_count) as transaction_count
        FROM analytics_sales_aggregates
        WHERE date BETWEEN ? AND ?
        GROUP BY product_id, product_name, category_name
        ORDER BY total_revenue DESC
        LIMIT ?
        """
        
        params = [start_date, end_date, limit]
        result = self.client.execute(query, params)
        
        return [dict(row) for row in result.rows]
    
    def _map_row_to_sales_aggregate(self, row: tuple) -> SalesAggregate:
        """Map database row to SalesAggregate entity."""
        return SalesAggregate(
            id=row[0],
            date=row[1],
            product_id=row[2],
            product_name=row[3],
            category_id=row[4],
            category_name=row[5],
            hour=row[6],
            service_type=row[7],
            employee_id=row[8],
            quantity_sold=row[9],
            revenue=row[10],
            cost=row[11],
            profit=row[12],
            discount_applied=row[13],
            tax_collected=row[14],
            transaction_count=row[15],
            created_at=row[16],
            updated_at=row[17],
        )
