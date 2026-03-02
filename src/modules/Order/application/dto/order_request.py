from pydantic import BaseModel
from typing import List, Optional

class OrderItemRequestDTO(BaseModel):
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    special_notes: Optional[str] = None

class OrderRequestDTO(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    table_number: Optional[int] = None
    special_instructions: Optional[str] = None
    items: List[OrderItemRequestDTO]

