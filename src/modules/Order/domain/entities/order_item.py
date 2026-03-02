from pydantic import BaseModel
from typing import Optional

class OrderItem(BaseModel):
    id: str
    order_id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_notes: Optional[str] = None

    class Config:
        from_attributes = True
from typing import Optional

class OrderItem(BaseModel):
    id: str
    order_id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_notes: Optional[str] = None

    class Config:
        from_attributes = True
