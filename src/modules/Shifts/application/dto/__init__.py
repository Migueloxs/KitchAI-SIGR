"""DTOs for Shifts module"""

from .shift_request import (
    CreateShiftRequestDTO,
    UpdateShiftRequestDTO,
    AssignShiftRequestDTO,
    UpdateShiftAssignmentRequestDTO,
    BulkAssignShiftRequestDTO,
)
from .shift_response import (
    ShiftResponseDTO,
    EmployeeShiftDTO,
    ShiftAssignmentResponseDTO,
    EmployeeShiftsResponseDTO,
    WeeklyCalendarDTO,
    ShiftConflictDTO,
    BulkAssignmentResponseDTO,
    ShiftStatsDTO,
)

__all__ = [
    "CreateShiftRequestDTO",
    "UpdateShiftRequestDTO",
    "AssignShiftRequestDTO",
    "UpdateShiftAssignmentRequestDTO",
    "BulkAssignShiftRequestDTO",
    "ShiftResponseDTO",
    "EmployeeShiftDTO",
    "ShiftAssignmentResponseDTO",
    "EmployeeShiftsResponseDTO",
    "WeeklyCalendarDTO",
    "ShiftConflictDTO",
    "BulkAssignmentResponseDTO",
    "ShiftStatsDTO",
]
