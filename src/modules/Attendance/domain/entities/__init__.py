"""Domain entities for Attendance module"""

from .attendance_record import AttendanceRecord, AttendanceStatus
from .attendance_alert import AttendanceAlert, AlertType, AlertSeverity

__all__ = [
    "AttendanceRecord",
    "AttendanceStatus",
    "AttendanceAlert",
    "AlertType",
    "AlertSeverity",
]
