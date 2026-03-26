"""
Shifts Service - Business logic for shifts management
Implements CA1, CA2, CA3 requirements
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import uuid

from src.modules.Shifts.domain.entities.shift import Shift, DayOfWeek
from src.modules.Shifts.domain.entities.shift_assignment import ShiftAssignment
from src.modules.Shifts.infrastructure.repositories.shifts_repository import ShiftsRepository
from src.modules.Shifts.application.dto import (
    CreateShiftRequestDTO,
    UpdateShiftRequestDTO,
    AssignShiftRequestDTO,
    UpdateShiftAssignmentRequestDTO,
    BulkAssignShiftRequestDTO,
    ShiftResponseDTO,
    ShiftAssignmentResponseDTO,
    EmployeeShiftsResponseDTO,
    WeeklyCalendarDTO,
    ShiftConflictDTO,
    BulkAssignmentResponseDTO,
)


class ShiftsService:
    """Service for managing shifts and assignments"""
    
    def __init__(self):
        self.repository = ShiftsRepository()
    
    # ============= SHIFT MANAGEMENT (CA1) =============
    
    def create_shift(self, request: CreateShiftRequestDTO) -> ShiftResponseDTO:
        """Create a new shift (CA1: Define weekly shifts)"""
        # Validate that shift doesn't already exist
        existing_shifts = self.repository.get_shifts_by_day(request.day_of_week)
        for existing in existing_shifts:
            if existing.name.lower() == request.name.lower():
                raise ValueError(f"Ya existe un turno llamado '{request.name}' para el {existing.get_day_name()}")
        
        # Create shift entity with validation
        shift = Shift(
            id=str(uuid.uuid4()),
            name=request.name,
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # Save to database
        saved_shift = self.repository.create_shift(shift)
        return self._map_shift_to_response(saved_shift)
    
    def get_shift(self, shift_id: str) -> ShiftResponseDTO:
        """Get a specific shift"""
        shift = self.repository.get_shift_by_id(shift_id)
        if not shift:
            raise ValueError(f"Turno con ID {shift_id} no encontrado")
        return self._map_shift_to_response(shift)
    
    def get_all_shifts(self, active_only: bool = True) -> List[ShiftResponseDTO]:
        """Get all shifts"""
        shifts = self.repository.get_all_shifts(active_only=active_only)
        return [self._map_shift_to_response(shift) for shift in shifts]
    
    def get_shifts_by_day(self, day_of_week: int) -> List[ShiftResponseDTO]:
        """Get shifts for a specific day"""
        if not (0 <= day_of_week <= 6):
            raise ValueError("day_of_week debe estar entre 0 (Lunes) y 6 (Domingo)")
        
        shifts = self.repository.get_shifts_by_day(day_of_week)
        return [self._map_shift_to_response(shift) for shift in shifts]
    
    def update_shift(self, shift_id: str, request: UpdateShiftRequestDTO) -> ShiftResponseDTO:
        """Update a shift"""
        shift = self.repository.get_shift_by_id(shift_id)
        if not shift:
            raise ValueError(f"Turno con ID {shift_id} no encontrado")
        
        # Update fields if provided
        if request.name is not None:
            shift.name = request.name
        if request.day_of_week is not None:
            shift.day_of_week = request.day_of_week
        if request.start_time is not None:
            shift.start_time = request.start_time
        if request.end_time is not None:
            shift.end_time = request.end_time
        if request.is_active is not None:
            shift.is_active = request.is_active
        
        shift.updated_at = datetime.now()
        
        # Validate the updated shift
        try:
            Shift(
                id=shift.id,
                name=shift.name,
                day_of_week=shift.day_of_week,
                start_time=shift.start_time,
                end_time=shift.end_time,
                is_active=shift.is_active,
            )
        except ValueError as e:
            raise ValueError(f"Datos de turno inválidos: {str(e)}")
        
        updated_shift = self.repository.update_shift(shift)
        return self._map_shift_to_response(updated_shift)
    
    def delete_shift(self, shift_id: str) -> bool:
        """Delete (deactivate) a shift"""
        shift = self.repository.get_shift_by_id(shift_id)
        if not shift:
            raise ValueError(f"Turno con ID {shift_id} no encontrado")
        
        # Check if shift has active assignments
        assignments = self.repository.get_shift_assignments(shift_id, active_only=True)
        if assignments:
            raise ValueError(f"No se puede eliminar un turno que tiene {len(assignments)} asignaciones activas")
        
        return self.repository.delete_shift(shift_id)
    
    # ============= SHIFT ASSIGNMENT (CA1, CA2) =============
    
    def assign_shift(self, request: AssignShiftRequestDTO) -> ShiftAssignmentResponseDTO:
        """
        Assign a shift to an employee (CA1: Assign shifts to employees)
        Validates CA2: No overlapping shifts on the same day
        """
        # Verify shift exists
        shift = self.repository.get_shift_by_id(request.shift_id)
        if not shift:
            raise ValueError(f"Turno con ID {request.shift_id} no encontrado")
        
        # CA2: Check for overlapping shifts
        conflicts = self.repository.check_shift_overlap(request.employee_id, request.start_date)
        if conflicts:
            conflict_times = ", ".join(
                [f"{c['name']} ({c['start_time']}-{c['end_time']})" for c in conflicts]
            )
            raise ValueError(
                f"El empleado ya tiene turnos asignados en esa fecha: {conflict_times}. No pueden solaparse."
            )
        
        # Create assignment
        assignment = ShiftAssignment(
            id=str(uuid.uuid4()),
            shift_id=request.shift_id,
            employee_id=request.employee_id,
            start_date=request.start_date,
            end_date=request.end_date,
            notes=request.notes,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        saved_assignment = self.repository.create_assignment(assignment)
        return self._map_assignment_to_response_dto(saved_assignment, shift)
    
    def bulk_assign_shift(self, request: BulkAssignShiftRequestDTO) -> BulkAssignmentResponseDTO:
        """
        Assign a shift to multiple employees (CA1: Multiple employees)
        With CA2 validation for each employee
        """
        shift = self.repository.get_shift_by_id(request.shift_id)
        if not shift:
            raise ValueError(f"Turno con ID {request.shift_id} no encontrado")
        
        successful = 0
        failed = 0
        errors = []
        assignments = []
        
        for employee_id in request.employee_ids:
            try:
                # Check for overlaps (CA2)
                conflicts = self.repository.check_shift_overlap(employee_id, request.start_date)
                if conflicts:
                    raise ValueError("Turnos solapados detectados")
                
                # Create assignment
                assignment = ShiftAssignment(
                    id=str(uuid.uuid4()),
                    shift_id=request.shift_id,
                    employee_id=employee_id,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    notes=request.notes,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                
                saved = self.repository.create_assignment(assignment)
                assignments.append(self._map_assignment_to_response_dto(saved, shift))
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append({
                    "employee_id": employee_id,
                    "error": str(e)
                })
        
        return BulkAssignmentResponseDTO(
            successful=successful,
            failed=failed,
            errors=errors,
            assigned_shifts=assignments,
        )
    
    def get_employee_assignments(self, employee_id: str) -> List[ShiftAssignmentResponseDTO]:
        """Get all assignments for an employee"""
        assignments = self.repository.get_employee_assignments(employee_id, active_only=False)
        result = []
        
        for assignment in assignments:
            shift = self.repository.get_shift_by_id(assignment.shift_id)
            if shift:
                result.append(self._map_assignment_to_response_dto(assignment, shift))
        
        return result
    
    def update_assignment(self, assignment_id: str, request: UpdateShiftAssignmentRequestDTO) -> ShiftAssignmentResponseDTO:
        """Update an assignment (extend or end)"""
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación con ID {assignment_id} no encontrada")
        
        if request.end_date is not None:
            if request.end_date < assignment.start_date:
                raise ValueError("end_date debe ser posterior o igual a start_date")
            assignment.end_date = request.end_date
        
        if request.notes is not None:
            assignment.notes = request.notes
        
        assignment.updated_at = datetime.now()
        updated = self.repository.update_assignment(assignment)
        
        shift = self.repository.get_shift_by_id(assignment.shift_id)
        return self._map_assignment_to_response_dto(updated, shift)
    
    def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        assignment = self.repository.get_assignment_by_id(assignment_id)
        if not assignment:
            raise ValueError(f"Asignación con ID {assignment_id} no encontrada")
        
        return self.repository.delete_assignment(assignment_id)
    
    # ============= CALENDAR VIEW (CA3) =============
    
    def get_employee_calendar(self, employee_id: str, week_start: Optional[date] = None) -> WeeklyCalendarDTO:
        """
        Get employee's calendar view for a specific week (CA3: Shared calendar)
        Shows all assigned shifts in calendar format
        """
        if week_start is None:
            # Find the Monday of the current week
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        # Get the end of the week (Sunday)
        week_end = week_start + timedelta(days=6)
        
        # Get all shifts for the employee in that week
        shifts_data = self.repository.get_employee_shifts_for_date_range(employee_id, week_start, week_end)
        
        # Organize by day
        schedule = {}
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for record in shifts_data:
            day_name = days[record['day_of_week']]
            if day_name not in schedule:
                schedule[day_name] = []
            
            schedule[day_name].append(record)
        
        # Get employee name
        from src.modules.User.infrastructure.repositories.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_id(employee_id)
        
        return WeeklyCalendarDTO(
            employee_id=employee_id,
            employee_name=user.name if user else "Unknown",
            week_start=week_start,
            week_end=week_end,
            schedule=schedule,
        )
    
    def get_team_calendar(self, employee_ids: List[str], week_start: Optional[date] = None) -> List[WeeklyCalendarDTO]:
        """Get calendars for multiple employees (CA3: Team view)"""
        return [self.get_employee_calendar(emp_id, week_start) for emp_id in employee_ids]
    
    # ============= CONFLICT DETECTION (CA2) =============
    
    def check_conflicts_for_employee(self, employee_id: str, target_date: date) -> Optional[ShiftConflictDTO]:
        """
        Check if employee has conflicting shifts on a specific date (CA2 validation)
        """
        conflicts = self.repository.check_shift_overlap(employee_id, target_date)
        
        if len(conflicts) <= 1:
            # 0 or 1 shift is not a conflict
            return None
        
        # Multiple shifts on same day = conflict
        from src.modules.User.infrastructure.repositories.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_id(employee_id)
        
        return ShiftConflictDTO(
            employee_id=employee_id,
            employee_name=user.name if user else "Unknown",
            date=target_date,
            conflicts=[
                {
                    "shift_id": c['shift_id'],
                    "name": c['name'],
                    "time": f"{c['start_time']}-{c['end_time']}",
                }
                for c in conflicts
            ],
            message=f"El empleado tiene {len(conflicts)} turnos solapados el {target_date.strftime('%Y-%m-%d')}",
        )
    
    # ============= MAPPING METHODS =============
    
    def _map_shift_to_response(self, shift: Shift) -> ShiftResponseDTO:
        """Map Shift entity to response DTO"""
        return ShiftResponseDTO(
            id=shift.id,
            name=shift.name,
            day_of_week=shift.day_of_week,
            day_name=shift.get_day_name(),
            start_time=shift.start_time,
            end_time=shift.end_time,
            is_active=shift.is_active,
            created_at=shift.created_at,
            updated_at=shift.updated_at,
        )
    
    def _map_assignment_to_response_dto(self, assignment: ShiftAssignment, shift: Shift) -> ShiftAssignmentResponseDTO:
        """Map assignment to response DTO"""
        from src.modules.User.infrastructure.repositories.user_repository import UserRepository
        user_repo = UserRepository()
        user = user_repo.get_by_id(assignment.employee_id)
        
        return ShiftAssignmentResponseDTO(
            id=assignment.id,
            shift_id=assignment.shift_id,
            shift_name=shift.name,
            day_of_week=shift.day_of_week,
            day_name=shift.get_day_name(),
            start_time=shift.start_time,
            end_time=shift.end_time,
            employee_id=assignment.employee_id,
            employee_name=user.name if user else "Unknown",
            email=user.email if user else "",
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            notes=assignment.notes,
            is_active=assignment.is_active(),
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )
