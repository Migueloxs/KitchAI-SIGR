"""
Attendance Record Entity - Represents an employee's check-in and check-out record.
Encapsulates the business logic related to attendance tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    """Enum for attendance status"""
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    NO_CHECKOUT = "NO_CHECKOUT"
    LATE = "LATE"


@dataclass
class AttendanceRecord:
    """
    Entity that represents an attendance record for an employee.
    
    Attributes:
        id: Unique identifier for the attendance record (UUID)
        employee_id: ID of the employee who checked in
        shift_assignment_id: ID of the shift assignment for this day
        check_in_time: ISO 8601 datetime when employee checked in
        check_out_time: ISO 8601 datetime when employee checked out (optional)
        duration_minutes: Total duration in minutes (check_out - check_in)
        status: Current status of the attendance record
        is_late: Whether the check-in was late
        late_by_minutes: Number of minutes late (if late)
        notes: Additional notes about this attendance record
        created_at: When this record was created
        updated_at: When this record was last updated
    """
    id: str
    employee_id: str
    shift_assignment_id: Optional[str]
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: AttendanceStatus = AttendanceStatus.CHECKED_IN
    is_late: bool = False
    late_by_minutes: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validations after initialization."""
        if not isinstance(self.check_in_time, datetime):
            raise ValueError("check_in_time must be a datetime object")
        
        if self.check_out_time is not None:
            if not isinstance(self.check_out_time, datetime):
                raise ValueError("check_out_time must be a datetime object")
            
            if self.check_out_time <= self.check_in_time:
                raise ValueError("check_out_time must be after check_in_time")
            
            # Calculate duration
            delta = self.check_out_time - self.check_in_time
            self.duration_minutes = int(delta.total_seconds() / 60)
    
    def mark_checkout(self, checkout_time: datetime) -> None:
        """
        Mark the employee checkout time.
        
        Args:
            checkout_time: The datetime when the employee checked out
            
        Raises:
            ValueError: If checkout_time is invalid or before check_in_time
        """
        if checkout_time <= self.check_in_time:
            raise ValueError("Checkout time must be after check-in time")
        
        self.check_out_time = checkout_time
        self.status = AttendanceStatus.CHECKED_OUT
        
        # Calculate duration
        delta = checkout_time - self.check_in_time
        self.duration_minutes = int(delta.total_seconds() / 60)
        self.updated_at = datetime.now()
    
    def mark_late(self, late_minutes: int) -> None:
        """
        Mark this attendance record as late.
        
        Args:
            late_minutes: Number of minutes the employee was late
        """
        if late_minutes < 0:
            raise ValueError("late_minutes cannot be negative")
        
        self.is_late = True
        self.late_by_minutes = late_minutes
        self.status = AttendanceStatus.LATE
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert the attendance record to a dictionary."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "shift_assignment_id": self.shift_assignment_id,
            "check_in_time": self.check_in_time.isoformat(),
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "duration_minutes": self.duration_minutes,
            "status": self.status.value,
            "is_late": self.is_late,
            "late_by_minutes": self.late_by_minutes,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
