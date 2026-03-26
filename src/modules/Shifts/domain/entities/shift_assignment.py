"""
ShiftAssignment Entity - Representa la asignación de un turno a un empleado.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class ShiftAssignment:
    """
    Entidad que representa la asignación de un turno a un empleado.
    
    Attributes:
        id: Identificador único de la asignación (UUID)
        shift_id: ID del turno asignado
        employee_id: ID del empleado asignado al turno
        start_date: Fecha de inicio de la asignación (YYYY-MM-DD)
        end_date: Fecha de fin de la asignación o None para indefinido
        notes: Notas adicionales sobre la asignación
        created_at: Fecha de creación de la asignación
        updated_at: Fecha de última actualización
    """
    id: str
    shift_id: str
    employee_id: str
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        # Convertir strings a date si es necesario
        if isinstance(self.start_date, str):
            self.start_date = datetime.fromisoformat(self.start_date).date()
        
        if isinstance(self.end_date, str):
            self.end_date = datetime.fromisoformat(self.end_date).date()
        
        # Validar que end_date > start_date
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date debe ser posterior o igual a start_date")
    
    def is_active(self, as_of: Optional[date] = None) -> bool:
        """
        Verifica si la asignación está activa en una fecha específica.
        Si as_of es None, usa la fecha actual.
        """
        if as_of is None:
            as_of = date.today()
        
        if isinstance(as_of, str):
            as_of = datetime.fromisoformat(as_of).date()
        
        return self.start_date <= as_of and (self.end_date is None or as_of <= self.end_date)
    
    def get_duration_days(self) -> int:
        """Retorna la cantidad de días que dura la asignación"""
        if self.end_date is None:
            # Si no tiene fecha fin, retorna None o algún valor especial
            return -1
        return (self.end_date - self.start_date).days + 1
    
    def has_ended(self, as_of: Optional[date] = None) -> bool:
        """Verifica si la asignación ha terminado"""
        if as_of is None:
            as_of = date.today()
        
        if isinstance(as_of, str):
            as_of = datetime.fromisoformat(as_of).date()
        
        return self.end_date is not None and as_of > self.end_date
    
    def is_pending(self, as_of: Optional[date] = None) -> bool:
        """Verifica si la asignación aún no ha comenzado"""
        if as_of is None:
            as_of = date.today()
        
        if isinstance(as_of, str):
            as_of = datetime.fromisoformat(as_of).date()
        
        return as_of < self.start_date
