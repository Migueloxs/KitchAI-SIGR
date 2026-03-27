"""Analytics DTOs for API requests and responses."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ProductSalesAggregateDTO(BaseModel):
    """DTO for aggregated sales data by product."""
    
    product_id: str
    product_name: str
    category_name: str
    total_quantity: int
    total_revenue: float
    total_profit: float
    total_discount: float
    transaction_count: int
    
    class Config:
        from_attributes = True


class HourlySalesDTO(BaseModel):
    """DTO for hourly sales breakdown."""
    
    hour: int
    revenue: float
    quantity_sold: int
    transaction_count: int
    average_price_per_item: Optional[float] = None
    
    class Config:
        from_attributes = True


class ServiceTypeSalesDTO(BaseModel):
    """DTO for sales breakdown by service type."""
    
    service_type: str  # 'dine-in', 'delivery', 'takeaway'
    revenue: float
    transaction_count: int
    percentage_of_total: float
    
    class Config:
        from_attributes = True


class MetadataDTO(BaseModel):
    """DTO for metadata in responses (totals, percentages, comparatives)."""
    
    total_revenue: float
    total_cost: float
    total_profit: float
    total_discount: float
    total_tax: float
    total_transactions: int
    average_ticket: float
    profit_margin: float  # profit / revenue * 100
    
    class Config:
        from_attributes = True


class SalesDataResponseDTO(BaseModel):
    """DTO for CA1: Aggregated sales data response."""
    
    date_range_start: str
    date_range_end: str
    
    # Sales by product
    sales_by_product: List[ProductSalesAggregateDTO]
    
    # Sales by hour
    sales_by_hour: List[HourlySalesDTO]
    
    # Sales by category
    sales_by_category: List[ProductSalesAggregateDTO]
    
    # Sales by service type
    sales_by_service_type: List[ServiceTypeSalesDTO]
    
    # Metadata with totals and percentages
    metadata: MetadataDTO
    
    class Config:
        from_attributes = True


class FilteredAnalyticsRequestDTO(BaseModel):
    """DTO for CA2: Filters for analytics queries."""
    
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    service_type: Optional[str] = None  # 'dine-in', 'delivery', 'takeaway' or all
    employee_id: Optional[str] = None
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ComparisonPeriodDTO(BaseModel):
    """DTO for period comparison data."""
    
    period_type: str  # 'day', 'week', 'month', 'quarter', 'year'
    current_period: dict  # Contains revenue, cost, profit, transactions
    previous_period: dict  # Contains same fields
    changes: dict  # Contains percentage changes
    
    class Config:
        from_attributes = True


class ComparativeAnalyticsResponseDTO(BaseModel):
    """DTO for CA3: Response with comparative data."""
    
    current_sales_data: SalesDataResponseDTO
    
    # Comparison with previous period
    comparison_with_previous: ComparisonPeriodDTO
    
    # Top performing products
    top_products: List[ProductSalesAggregateDTO]
    
    # Best performing employee
    top_employee: Optional[dict] = None
    
    # Peak hours analysis
    peak_hours: List[HourlySalesDTO]
    
    class Config:
        from_attributes = True


class AnalyticsSummaryDTO(BaseModel):
    """DTO for dashboard summary data."""
    
    date: str
    total_revenue: float
    total_profit: float
    total_transactions: int
    average_ticket: float
    peak_hour: Optional[int] = None
    peak_hour_revenue: float
    
    # By service type
    dine_in_revenue: float
    delivery_revenue: float
    takeaway_revenue: float
    
    class Config:
        from_attributes = True
