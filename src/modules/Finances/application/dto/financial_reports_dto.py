"""Advanced Financial Reports DTOs"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class SaleDetailDTO(BaseModel):
    """Detalle de una venta individual"""
    id: str
    order_number: str
    customer_name: str
    waiter_name: str
    payment_method: str
    items_count: int
    total_amount: float
    tax_amount: float
    discount_amount: float
    final_amount: float
    sale_date: str
    registered_at: datetime


class ItemBreakdownDTO(BaseModel):
    """Desglose de items en reportes"""
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    percentage_of_total: float


class SaleItemDetailDTO(BaseModel):
    """Detalle de venta con items"""
    id: str
    order_number: str
    customer_name: str
    waiter_name: str
    payment_method: str
    total_amount: float
    final_amount: float
    sale_date: str
    items: List[ItemBreakdownDTO] = []


class PaymentMethodSummary(BaseModel):
    """Resumen por método de pago"""
    method: str
    count: int
    total_amount: float
    average_amount: float
    percentage: float


class WaiterPerformanceDTO(BaseModel):
    """Performance de vendedor"""
    waiter_id: str
    waiter_name: str
    sales_count: int
    total_sales: float
    average_sale: float
    percentage_of_total: float


class FinancialMetricsDTO(BaseModel):
    """Métricas financieras agregadas"""
    period_start: str
    period_end: str
    total_sales: int
    total_revenue: float
    total_tax: float
    total_discount: float
    total_expenses: float
    net_profit: float
    profit_margin_percent: float
    average_ticket: float
    average_discount_percent: float


class ComparisonPeriodDTO(BaseModel):
    """Datos para comparación de periodos"""
    current_period: FinancialMetricsDTO
    previous_period: FinancialMetricsDTO
    growth_rate_percent: float
    revenue_change: float
    expense_change: float
    profit_change: float


class CategoryProductSummary(BaseModel):
    """Resumen por categoría de producto"""
    category: str
    items_sold: int
    total_quantity: int
    total_amount: float
    percentage: float
    most_sold_item: str
    least_sold_item: str


class DetailedFinancialReportDTO(BaseModel):
    """Reporte financiero detallado con filtros"""
    period_start: str
    period_end: str
    
    # Métricas principales
    metrics: FinancialMetricsDTO
    
    # Desgloses por método de pago
    by_payment_method: List[PaymentMethodSummary] = []
    
    # Performance de empleados
    by_waiter: List[WaiterPerformanceDTO] = []
    
    # Categorías de productos más vendidos
    by_product_category: List[CategoryProductSummary] = []
    
    # Listado de ventas individuales
    sales_detail: List[SaleItemDetailDTO] = []
    
    # Metadatos
    filters_applied: Dict[str, str] = {}


class FinancialComparisonReportDTO(BaseModel):
    """Reporte comparativo entre períodos"""
    comparison: ComparisonPeriodDTO
    insights: List[str] = []  # Insights automáticos del análisis
    recommendations: List[str] = []  # Recomendaciones basadas en datos


class FilteredSalesReportDTO(BaseModel):
    """Reporte de ventas filtrado"""
    period_start: str
    period_end: str
    total_sales: int
    total_amount: float
    average_amount: float
    sales_list: List[SaleItemDetailDTO] = []
    applied_filters: Dict[str, str] = {}
