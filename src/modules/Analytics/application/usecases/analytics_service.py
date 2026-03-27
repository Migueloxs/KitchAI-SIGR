"""Analytics business logic service."""

from typing import Optional
from datetime import datetime

from src.modules.Analytics.application.dto import (
    SalesDataResponseDTO,
    ProductSalesAggregateDTO,
    HourlySalesDTO,
    ServiceTypeSalesDTO,
    MetadataDTO,
    ComparativeAnalyticsResponseDTO,
    ComparisonPeriodDTO,
    AnalyticsSummaryDTO,
)
from src.modules.Analytics.infrastructure.repositories import AnalyticsRepository


class AnalyticsService:
    """Service for analytics operations."""
    
    def __init__(self):
        self.repository = AnalyticsRepository()
    
    def get_sales_analytics(
        self,
        start_date: str,
        end_date: str,
        service_type: Optional[str] = None,
        employee_id: Optional[str] = None,
        category_name: Optional[str] = None,
    ) -> SalesDataResponseDTO:
        """
        CA1: Get aggregated sales data by product, hour and category.
        CA2: Supports filters by date range, service type, and employee.
        CA3: Includes metadata with totals, percentages and comparatives.
        """
        
        # Get aggregated data
        products_data = self.repository.get_aggregated_by_product(
            start_date, end_date, service_type, employee_id
        )
        categories_data = self.repository.get_aggregated_by_category(
            start_date, end_date, service_type
        )
        hours_data = self.repository.get_aggregated_by_hour(
            start_date, end_date, service_type
        )
        service_types_data = self.repository.get_aggregated_by_service_type(
            start_date, end_date
        )
        
        # Get totals
        totals = self.repository.get_period_totals(
            start_date, end_date, service_type, employee_id
        )
        
        # Calculate percentages and metadata
        total_revenue = totals["total_revenue"]
        
        # Calculate profit margin
        profit_margin = 0.0
        if total_revenue > 0:
            profit_margin = (totals["total_profit"] / total_revenue) * 100
        
        # Calculate average ticket
        average_ticket = 0.0
        if totals["total_transactions"] > 0:
            average_ticket = total_revenue / totals["total_transactions"]
        
        # Build product DTOs with percentages
        sales_by_product = [
            ProductSalesAggregateDTO(
                product_id=item["product_id"],
                product_name=item["product_name"],
                category_name=item["category_name"],
                total_quantity=item["total_quantity"],
                total_revenue=item["total_revenue"],
                total_profit=item["total_profit"],
                total_discount=item["total_discount"],
                transaction_count=item["transaction_count"],
            )
            for item in products_data
        ]
        
        # Build hourly DTOs
        sales_by_hour = [
            HourlySalesDTO(
                hour=item["hour"],
                revenue=item["revenue"],
                quantity_sold=item["quantity_sold"],
                transaction_count=item["transaction_count"],
                average_price_per_item=item.get("avg_price_per_item"),
            )
            for item in hours_data
        ]
        
        # Build category DTOs
        sales_by_category = [
            ProductSalesAggregateDTO(
                product_id=item["category_name"],
                product_name=item["category_name"],
                category_name=item["category_name"],
                total_quantity=item["total_quantity"],
                total_revenue=item["total_revenue"],
                total_profit=item["total_profit"],
                total_discount=0.0,
                transaction_count=item["transaction_count"],
            )
            for item in categories_data
        ]
        
        # Build service type DTOs with percentages
        sales_by_service_type = []
        for item in service_types_data:
            percentage = 0.0
            if total_revenue > 0:
                percentage = (item["revenue"] / total_revenue) * 100
            
            sales_by_service_type.append(
                ServiceTypeSalesDTO(
                    service_type=item["service_type"],
                    revenue=item["revenue"],
                    transaction_count=item["transaction_count"],
                    percentage_of_total=round(percentage, 2),
                )
            )
        
        # Build metadata
        metadata = MetadataDTO(
            total_revenue=round(total_revenue, 2),
            total_cost=round(totals["total_cost"], 2),
            total_profit=round(totals["total_profit"], 2),
            total_discount=round(totals["total_discount"], 2),
            total_tax=round(totals["total_tax"], 2),
            total_transactions=totals["total_transactions"],
            average_ticket=round(average_ticket, 2),
            profit_margin=round(profit_margin, 2),
        )
        
        return SalesDataResponseDTO(
            date_range_start=start_date,
            date_range_end=end_date,
            sales_by_product=sales_by_product,
            sales_by_hour=sales_by_hour,
            sales_by_category=sales_by_category,
            sales_by_service_type=sales_by_service_type,
            metadata=metadata,
        )
    
    def get_comparative_analytics(
        self,
        start_date: str,
        end_date: str,
        period_type: str = "day",
        service_type: Optional[str] = None,
    ) -> ComparativeAnalyticsResponseDTO:
        """
        Get comparative analysis with previous period.
        Includes top products, peak hours, and employee performance.
        """
        
        # Get current period data
        current_data = self.get_sales_analytics(
            start_date, end_date, service_type
        )
        
        # Get comparison with previous period
        comparison_data = self.repository.get_period_comparison(
            period_type, start_date, end_date
        )
        
        # Get top products (top 10)
        top_products_data = self.repository.get_top_products(
            start_date, end_date, limit=10
        )
        top_products = [
            ProductSalesAggregateDTO(
                product_id=item["product_id"],
                product_name=item["product_name"],
                category_name=item["category_name"],
                total_quantity=item["total_quantity"],
                total_revenue=item["total_revenue"],
                total_profit=item["total_profit"],
                total_discount=0.0,
                transaction_count=item["transaction_count"],
            )
            for item in top_products_data
        ]
        
        # Get peak hours (top 5)
        peak_hours_data = self.repository.get_peak_hours(
            start_date, end_date, limit=5
        )
        peak_hours = [
            HourlySalesDTO(
                hour=item["hour"],
                revenue=item["revenue"],
                quantity_sold=item["quantity_sold"],
                transaction_count=item["transaction_count"],
                average_price_per_item=item.get("avg_price_per_item"),
            )
            for item in peak_hours_data
        ]
        
        # Get top employee
        employee_perf = self.repository.get_employee_performance(
            start_date, end_date
        )
        top_employee = None
        if employee_perf:
            best = employee_perf[0]
            top_employee = {
                "employee_id": best["employee_id"],
                "total_sales": best["total_sales"],
                "total_transactions": best["total_transactions"],
                "average_ticket": best["average_ticket"],
                "items_sold": best["items_sold"],
            }
        
        # Build comparison period DTO
        comparison_period = ComparisonPeriodDTO(
            period_type=period_type,
            current_period=comparison_data["current_period"],
            previous_period=comparison_data["previous_period"],
            changes={
                "revenue_change_percentage": comparison_data["revenue_change_percentage"],
                "profit_change_percentage": comparison_data["profit_change_percentage"],
                "transaction_growth_percentage": comparison_data["transaction_growth_percentage"],
            },
        )
        
        return ComparativeAnalyticsResponseDTO(
            current_sales_data=current_data,
            comparison_with_previous=comparison_period,
            top_products=top_products,
            top_employee=top_employee,
            peak_hours=peak_hours,
        )
    
    def get_dashboard_summary(
        self,
        date: Optional[str] = None,
    ) -> AnalyticsSummaryDTO:
        """Get dashboard summary for a specific date."""
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        totals = self.repository.get_period_totals(date, date)
        
        # Get service type breakdown
        service_types = self.repository.get_aggregated_by_service_type(date, date)
        service_dict = {item["service_type"]: item["revenue"] for item in service_types}
        
        # Get peak hour
        peak_hours = self.repository.get_peak_hours(date, date, limit=1)
        peak_hour = None
        peak_hour_revenue = 0.0
        if peak_hours:
            peak_hour = peak_hours[0]["hour"]
            peak_hour_revenue = peak_hours[0]["revenue"]
        
        # Calculate average ticket
        average_ticket = 0.0
        if totals["total_transactions"] > 0:
            average_ticket = totals["total_revenue"] / totals["total_transactions"]
        
        return AnalyticsSummaryDTO(
            date=date,
            total_revenue=round(totals["total_revenue"], 2),
            total_profit=round(totals["total_profit"], 2),
            total_transactions=totals["total_transactions"],
            average_ticket=round(average_ticket, 2),
            peak_hour=peak_hour,
            peak_hour_revenue=round(peak_hour_revenue, 2),
            dine_in_revenue=round(service_dict.get("dine-in", 0.0), 2),
            delivery_revenue=round(service_dict.get("delivery", 0.0), 2),
            takeaway_revenue=round(service_dict.get("takeaway", 0.0), 2),
        )
