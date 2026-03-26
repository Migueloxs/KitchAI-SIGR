"""
Shift Request DTOs - Para recibir datos de entrada del cliente
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class CreateShiftRequestDTO(BaseModel):
    """DTO para crear un nuevo turno (CA1)"""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre del turno (ej: Mañana, Tarde, Noche)")
    day_of_week: int = Field(..., ge=0, le=6, description="Día de la semana (0=Lunes, 6=Domingo)")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora de inicio en formato HH:MM")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora de cierre en formato HH:MM")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        normalized = " ".join(v.split())
        if not normalized:
            raise ValueError("El nombre del turno no puede estar vacío")
        return normalized


class UpdateShiftRequestDTO(BaseModel):
    """DTO para actualizar un turno existente"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    is_active: Optional[bool] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v is not None:
            normalized = " ".join(v.split())
            if not normalized:
                raise ValueError("El nombre del turno no puede estar vacío")
            return normalized
        return v


class AssignShiftRequestDTO(BaseModel):
    """DTO para asignar un turno a un empleado (CA1)"""
    shift_id: str = Field(..., description="ID del turno a asignar")
    employee_id: str = Field(..., description="ID del empleado")
    start_date: date = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    end_date: Optional[date] = Field(None, description="Fecha de fin en formato YYYY-MM-DD (opcional, None para indefinido)")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales sobre la asignación")


class UpdateShiftAssignmentRequestDTO(BaseModel):
    """DTO para actualizar una asignación de turno"""
    end_date: Optional[date] = Field(None, description="Nueva fecha de fin")
    notes: Optional[str] = Field(None, max_length=500)


class BulkAssignShiftRequestDTO(BaseModel):
    """DTO para asignar un turno a múltiples empleados"""
    shift_id: str = Field(..., description="ID del turno")
    employee_ids: list[str] = Field(..., min_length=1, description="Lista de IDs de empleados")
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: Optional[date] = Field(None, description="Fecha de fin (opcional)")
    notes: Optional[str] = Field(None, max_length=500)
