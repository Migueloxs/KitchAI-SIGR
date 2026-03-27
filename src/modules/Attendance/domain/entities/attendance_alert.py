"""
Attendance Alert Entity - Represents automatic alerts about attendance issues.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class AlertType(str, Enum):
    """Types of attendance alerts"""
    NO_CHECK_IN = "NO_CHECK_IN"
    LATE_ARRIVAL = "LATE_ARRIVAL"
    NO_CHECK_OUT = "NO_CHECK_OUT"
    EARLY_DEPARTURE = "EARLY_DEPARTURE"
    ABSENT = "ABSENT"


class AlertSeverity(str, Enum):
    """Severity levels for alerts"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class AttendanceAlert:
    """
    Entity that represents an automatic attendance alert.
    
    Attributes:
        id: Unique identifier for the alert (UUID)
        employee_id: ID of the employee this alert is for
        alert_type: Type of alert (NO_CHECK_IN, LATE_ARRIVAL, etc.)
        description: Human-readable description of the alert
        severity: Severity level (INFO, WARNING, CRITICAL)
        shift_assignment_id: ID of the shift assignment related to this alert
        referenced_attendance_id: ID of the attendance record that triggered this alert
        is_acknowledged: Whether a manager has acknowledged this alert
        acknowledged_by: ID of the user who acknowledged this alert
        acknowledged_at: When this alert was acknowledged
        auto_resolved: Whether this alert was auto-resolved (e.g., employee checked in before manual alert)
        resolved_at: When this alert was resolved
        created_at: When this alert was created
        updated_at: When this alert was last updated
    """
    id: str
    employee_id: str
    alert_type: AlertType
    description: str
    severity: AlertSeverity
    shift_assignment_id: Optional[str] = None
    referenced_attendance_id: Optional[str] = None
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    auto_resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validations after initialization."""
        if not isinstance(self.alert_type, AlertType):
            raise ValueError(f"Invalid alert_type: {self.alert_type}")
        
        if not isinstance(self.severity, AlertSeverity):
            raise ValueError(f"Invalid severity: {self.severity}")
        
        if self.is_acknowledged and self.acknowledged_at is None:
            raise ValueError("acknowledged_at must be set when is_acknowledged is True")
        
        if self.auto_resolved and self.resolved_at is None:
            raise ValueError("resolved_at must be set when auto_resolved is True")
    
    def acknowledge(self, acknowledged_by: str, acknowledged_at: Optional[datetime] = None) -> None:
        """
        Mark this alert as acknowledged by a manager.
        
        Args:
            acknowledged_by: ID of the user acknowledging this alert
            acknowledged_at: When the alert was acknowledged (defaults to now)
        """
        self.is_acknowledged = True
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = acknowledged_at or datetime.now()
        self.updated_at = datetime.now()
    
    def auto_resolve(self, resolved_at: Optional[datetime] = None) -> None:
        """
        Mark this alert as auto-resolved.
        
        Args:
            resolved_at: When the alert was resolved (defaults to now)
        """
        self.auto_resolved = True
        self.resolved_at = resolved_at or datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert the alert to a dictionary."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "alert_type": self.alert_type.value,
            "description": self.description,
            "severity": self.severity.value,
            "shift_assignment_id": self.shift_assignment_id,
            "referenced_attendance_id": self.referenced_attendance_id,
            "is_acknowledged": self.is_acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "auto_resolved": self.auto_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
