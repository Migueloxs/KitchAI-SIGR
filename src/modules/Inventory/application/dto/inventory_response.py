from datetime import datetime

from pydantic import BaseModel


class InventoryItemResponseDTO(BaseModel):
    id: str
    name: str
    category: str
    current_quantity: float
    minimum_stock: float
    unit: str
    is_below_minimum_stock: bool
    created_at: datetime
    updated_at: datetime
