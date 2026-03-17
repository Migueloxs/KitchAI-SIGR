from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.modules.Order.domain.entities.order import ServiceType

class OrderItemResponseDTO(BaseModel):
    id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_notes: Optional[str] = None

class OrderResponseDTO(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_phone: Optional[str] = None
    table_number: Optional[int] = None
    status: str
    service_type: ServiceType
    total_amount: float
    tax_amount: float
    discount_amount: float
    final_amount: float
    payment_status: str
    payment_method: Optional[str] = None
    special_instructions: Optional[str] = None
    waiter_id: Optional[str] = None
    cancelled_by: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    preparation_started_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    preparation_time: Optional[int] = None
    total_time: Optional[int] = None
    items: List[OrderItemResponseDTO] = []