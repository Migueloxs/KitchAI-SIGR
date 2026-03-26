"""
Shift Entity - Representa un turno semanal del sistema.
Encapsula la lógica de negocio relacionada con turnos.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import IntEnum


class DayOfWeek(IntEnum):
    """Enum para días de la semana"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class Shift:
    """
    Entidad que representa un turno semanal.
    
    Attributes:
        id: Identificador único del turno (UUID)
        name: Nombre del turno (ej: Mañana, Tarde, Noche)
        day_of_week: Día de la semana (0=Lunes, 6=Domingo)
        start_time: Hora de inicio en formato HH:MM
        end_time: Hora de cierre en formato HH:MM
        is_active: Si el turno está activo
        created_at: Fecha de creación del turno
        updated_at: Fecha de última actualización
    """
    id: str
    name: str
    day_of_week: int
    start_time: str
    end_time: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not (0 <= self.day_of_week <= 6):
            raise ValueError("day_of_week debe estar entre 0 (Lunes) y 6 (Domingo)")
        
        if not self._is_valid_time_format(self.start_time):
            raise ValueError("start_time debe estar en formato HH:MM")
        
        if not self._is_valid_time_format(self.end_time):
            raise ValueError("end_time debe estar en formato HH:MM")
        
        if self._compare_times(self.start_time, self.end_time) >= 0:
            raise ValueError("start_time debe ser anterior a end_time")
    
    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        """Valida que el tiempo esté en formato HH:MM (2 dígitos cada uno)"""
        try:
            if not isinstance(time_str, str) or len(time_str) != 5:
                return False
            if time_str[2] != ':':
                return False
            hour_str, minute_str = time_str[:2], time_str[3:]
            if not hour_str.isdigit() or not minute_str.isdigit():
                return False
            hour, minute = int(hour_str), int(minute_str)
            return 0 <= hour < 24 and 0 <= minute < 60
        except (ValueError, AttributeError, TypeError):
            return False
    
    @staticmethod
    def _compare_times(time1: str, time2: str) -> int:
        """Compara dos tiempos. Retorna -1 si time1 < time2, 0 si son iguales, 1 si time1 > time2"""
        h1, m1 = map(int, time1.split(':'))
        h2, m2 = map(int, time2.split(':'))
        t1 = h1 * 60 + m1
        t2 = h2 * 60 + m2
        return -1 if t1 < t2 else (0 if t1 == t2 else 1)
    
    def overlaps_with(self, other: 'Shift') -> bool:
        """
        Verifica si dos turnos se solapan.
        Retorna True si ambos turnos están el mismo día y sus horarios se solapan.
        """
        if self.day_of_week != other.day_of_week:
            return False
        
        # Convertir tiempos a minutos
        self_start = int(self.start_time.split(':')[0]) * 60 + int(self.start_time.split(':')[1])
        self_end = int(self.end_time.split(':')[0]) * 60 + int(self.end_time.split(':')[1])
        other_start = int(other.start_time.split(':')[0]) * 60 + int(other.start_time.split(':')[1])
        other_end = int(other.end_time.split(':')[0]) * 60 + int(other.end_time.split(':')[1])
        
        # Verificar solapamiento
        return self_start < other_end and other_start < self_end
    
    def get_day_name(self) -> str:
        """Retorna el nombre en español del día de la semana"""
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return days[self.day_of_week]
