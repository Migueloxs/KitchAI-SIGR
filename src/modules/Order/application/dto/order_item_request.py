"""
DTOs relacionados a los ítems de un pedido.
"""
from pydantic import BaseModel, Field
from typing import Optional


class OrderItemCreateRequest(BaseModel):
    menu_item_id: str = Field(..., description="ID del producto del menú")
    quantity: int = Field(..., gt=0, description="Cantidad del producto (mínimo 1)")
    special_notes: Optional[str] = Field(
        None,
        description="Notas especiales para el ítem, e.g. 'sin cebolla'"
    )

    class Config:
        schema_extra = {
            "examples": [
                {"menu_item_id": "item-123", "quantity": 2, "special_notes": "sin sal"},
                {"menu_item_id": "item-456", "quantity": 1}
            ]
        }


class OrderItemUpdateRequest(BaseModel):
    item_id: str = Field(..., description="ID del ítem existente")
    quantity: int = Field(..., gt=0, description="Nueva cantidad (mínimo 1)")

    class Config:
        schema_extra = {
            "examples": [
                {"item_id": "oi-789", "quantity": 3}
            ]
        }
