from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from src.modules.Order.domain.entities.order_item import OrderItem

class OrderStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ServiceType(str, Enum):
    DINE_IN = "dine_in"
    TAKEOUT = "takeout"
    DELIVERY = "delivery"

class Order(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_phone: Optional[str] = None
    table_number: Optional[int] = None
    status: OrderStatus
    service_type: ServiceType
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
    cancellation_reason: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    preparation_started_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    preparation_time: Optional[int] = None  # in seconds
    total_time: Optional[int] = None  # in seconds
    items: List[OrderItem] = []

