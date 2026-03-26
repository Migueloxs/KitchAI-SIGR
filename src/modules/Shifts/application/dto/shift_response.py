"""
Shift Response DTOs - Para enviar datos al cliente
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date


class ShiftResponseDTO(BaseModel):
    """DTO para responder con datos de un turno"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    day_of_week: int
    day_name: str  # ej: "Lunes"
    start_time: str  # ej: "08:00"
    end_time: str    # ej: "16:00"
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EmployeeShiftDTO(BaseModel):
    """DTO que combina datos de turno y empleado"""
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: str
    employee_name: str
    email: str
    shift_id: str
    shift_name: str
    day_of_week: int
    day_name: str
    start_time: str
    end_time: str


class ShiftAssignmentResponseDTO(BaseModel):
    """DTO para responder con datos de una asignación de turno"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    shift_id: str
    shift_name: str
    day_of_week: int
    day_name: str
    start_time: str
    end_time: str
    employee_id: str
    employee_name: str
    email: str
    start_date: date
    end_date: Optional[date]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EmployeeShiftsResponseDTO(BaseModel):
    """DTO para mostrar todos los turnos de un empleado (CA3 - Calendario)"""
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: str
    employee_name: str
    email: str
    shifts: List[ShiftAssignmentResponseDTO]
    total_hours_per_week: float  # Total de horas en la semana


class WeeklyCalendarDTO(BaseModel):
    """DTO para mostrar el calendario semanal de un empleado"""
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: str
    employee_name: str
    week_start: date
    week_end: date
    schedule: dict  # {day_name: [ShiftAssignmentResponseDTO]}


class ShiftConflictDTO(BaseModel):
    """DTO para reportar conflictos de turnos solapados (CA2)"""
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: str
    employee_name: str
    date: date
    conflicts: List[dict]  # [{"shift_id": "...", "name": "...", "time": "HH:MM-HH:MM"}]
    message: str


class BulkAssignmentResponseDTO(BaseModel):
    """DTO para responder a asignaciones masivas de turnos"""
    model_config = ConfigDict(from_attributes=True)
    
    successful: int
    failed: int
    errors: List[dict]  # [{"employee_id": "...", "error": "..."}]
    assigned_shifts: List[ShiftAssignmentResponseDTO]


class ShiftStatsDTO(BaseModel):
    """DTO para mostrar estadísticas de turnos"""
    model_config = ConfigDict(from_attributes=True)
    
    total_shifts: int
    active_shifts: int
    total_assignments: int
    active_assignments: int
    employees_covered: int
    average_shift_duration: float  # en horas
