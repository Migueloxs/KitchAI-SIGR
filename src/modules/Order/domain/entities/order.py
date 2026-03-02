from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.modules.Order.domain.entities.order_item import OrderItem

class Order(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_phone: Optional[str] = None
    table_number: Optional[int] = None
    status: str
    total_amount: float = 0.0
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    final_amount: float = 0.0
    payment_status: str = "PENDING"
    payment_method: Optional[str] = None
    special_instructions: Optional[str] = None
    waiter_id: Optional[str] = None
    cancelled_by: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    items: List[OrderItem] = []

