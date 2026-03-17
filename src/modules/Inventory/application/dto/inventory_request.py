from pydantic import BaseModel, Field, field_validator


class CreateInventoryItemRequestDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=80)
    current_quantity: float = Field(..., ge=0)
    minimum_stock: float = Field(..., ge=0)
    unit: str = Field(default="unit", min_length=1, max_length=20)

    @field_validator("name", "category", "unit")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("El valor no puede estar vacio")
        return normalized


class UpdateInventoryItemRequestDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=80)
    current_quantity: float = Field(..., ge=0)
    minimum_stock: float = Field(..., ge=0)
    unit: str = Field(default="unit", min_length=1, max_length=20)

    @field_validator("name", "category", "unit")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("El valor no puede estar vacio")
        return normalized
