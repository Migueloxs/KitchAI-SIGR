from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SaleItem(BaseModel):
    id: str
    sale_id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float


class Sale(BaseModel):
    id: str
    order_id: str
    order_number: str
    customer_name: str
    waiter_id: str
    payment_method: Optional[str] = None
    total_amount: float = 0.0
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    final_amount: float = 0.0
    items_count: int = 0
    sale_date: str
    registered_at: datetime
    items: List[SaleItem] = []
