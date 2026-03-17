from pydantic import BaseModel
from datetime import datetime


class InventoryItem(BaseModel):
    id: str
    name: str
    category: str
    current_quantity: float
    minimum_stock: float
    unit: str = "unit"
    created_at: datetime
    updated_at: datetime
