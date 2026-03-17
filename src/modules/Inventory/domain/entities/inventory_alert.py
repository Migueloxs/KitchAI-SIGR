from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InventoryAlert(BaseModel):
    id: str
    inventory_item_id: str
    order_id: Optional[str] = None
    alert_type: str
    message: str
    current_quantity: float
    minimum_stock: float
    is_resolved: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None
