from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InventoryAlertResponseDTO(BaseModel):
    id: str
    inventory_item_id: str
    order_id: Optional[str] = None
    alert_type: str
    message: str
    current_quantity: float
    minimum_stock: float
    is_viewed: bool
    is_resolved: bool
    check_date: Optional[str] = None
    created_at: datetime
    viewed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
