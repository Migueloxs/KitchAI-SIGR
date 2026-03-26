from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class SaleItemResponseDTO(BaseModel):
    id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float


class SaleResponseDTO(BaseModel):
    id: str
    order_id: str
    order_number: str
    customer_name: str
    waiter_id: str
    payment_method: Optional[str] = None
    total_amount: float
    tax_amount: float
    discount_amount: float
    final_amount: float
    items_count: int
    sale_date: str
    registered_at: datetime
    items: List[SaleItemResponseDTO] = []


class SalesReportDTO(BaseModel):
    total_sales: int
    total_revenue: float
    total_tax: float
    total_discount: float
    period_from: str
    period_to: str
    by_waiter: dict = {}
    by_payment_method: dict = {}


class SalesByWaiterDTO(BaseModel):
    waiter_id: str
    sales_count: int
    total_revenue: float


class SalesByDateDTO(BaseModel):
    date: str
    sales_count: int
    total_revenue: float
