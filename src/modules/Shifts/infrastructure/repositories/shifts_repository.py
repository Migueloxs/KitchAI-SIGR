"""
Shifts Repository - Data access layer for shifts and assignments
"""
from datetime import datetime, date
from typing import List, Optional
import uuid

from src.modules.Shifts.domain.entities.shift import Shift, DayOfWeek
from src.modules.Shifts.domain.entities.shift_assignment import ShiftAssignment
from src.shared.infrastructure.database.turso_connection import get_turso_client


class ShiftsRepository:
    """Repository for Shifts and ShiftAssignments"""
    
    def __init__(self):
        self.client = get_turso_connection()
    
    # ============= SHIFT OPERATIONS =============
    
    def create_shift(self, shift: Shift) -> Shift:
        """Create a new shift"""
        self.client.execute(
            """
            INSERT INTO shifts (id, name, day_of_week, start_time, end_time, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                shift.id,
                shift.name,
                shift.day_of_week,
                shift.start_time,
                shift.end_time,
                1 if shift.is_active else 0,
                shift.created_at.isoformat(),
                shift.updated_at.isoformat(),
            ],
        )
        return shift
    
    def get_shift_by_id(self, shift_id: str) -> Optional[Shift]:
        """Get a shift by ID"""
        result = self.client.execute(
            """
            SELECT id, name, day_of_week, start_time, end_time, is_active, created_at, updated_at
            FROM shifts
            WHERE id = ?
            """,
            [shift_id],
        )
        
        if not result.rows:
            return None
        
        return self._map_to_shift_entity(result.rows[0])
    
    def get_all_shifts(self, active_only: bool = False) -> List[Shift]:
        """Get all shifts, optionally filter by active status"""
        query = "SELECT id, name, day_of_week, start_time, end_time, is_active, created_at, updated_at FROM shifts"
        params = []
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY day_of_week, start_time"
        
        result = self.client.execute(query, params)
        
        return [self._map_to_shift_entity(row) for row in result.rows]
    
    def get_shifts_by_day(self, day_of_week: int, active_only: bool = False) -> List[Shift]:
        """Get all shifts for a specific day of the week"""
        query = "SELECT id, name, day_of_week, start_time, end_time, is_active, created_at, updated_at FROM shifts WHERE day_of_week = ?"
        params = [day_of_week]
        
        if active_only:
            query += " AND is_active = 1"
        
        query += " ORDER BY start_time"
        
        result = self.client.execute(query, params)
        
        return [self._map_to_shift_entity(row) for row in result.rows]
    
    def update_shift(self, shift: Shift) -> Shift:
        """Update an existing shift"""
        shift.updated_at = datetime.now()
        
        self.client.execute(
            """
            UPDATE shifts
            SET name = ?, day_of_week = ?, start_time = ?, end_time = ?, is_active = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                shift.name,
                shift.day_of_week,
                shift.start_time,
                shift.end_time,
                1 if shift.is_active else 0,
                shift.updated_at.isoformat(),
                shift.id,
            ],
        )
        return shift
    
    def delete_shift(self, shift_id: str) -> bool:
        """Soft delete: deactivate a shift"""
        result = self.client.execute(
            "UPDATE shifts SET is_active = 0, updated_at = ? WHERE id = ?",
            [datetime.now().isoformat(), shift_id],
        )
        return result.rows_affected > 0 if hasattr(result, 'rows_affected') else True
    
    # ============= SHIFT ASSIGNMENT OPERATIONS =============
    
    def create_assignment(self, assignment: ShiftAssignment) -> ShiftAssignment:
        """Create a new shift assignment"""
        self.client.execute(
            """
            INSERT INTO shift_assignments (id, shift_id, employee_id, start_date, end_date, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                assignment.id,
                assignment.shift_id,
                assignment.employee_id,
                assignment.start_date.isoformat() if isinstance(assignment.start_date, date) else assignment.start_date,
                assignment.end_date.isoformat() if assignment.end_date and isinstance(assignment.end_date, date) else assignment.end_date,
                assignment.notes,
                assignment.created_at.isoformat(),
                assignment.updated_at.isoformat(),
            ],
        )
        return assignment
    
    def get_assignment_by_id(self, assignment_id: str) -> Optional[ShiftAssignment]:
        """Get an assignment by ID"""
        result = self.client.execute(
            """
            SELECT sa.id, sa.shift_id, sa.employee_id, sa.start_date, sa.end_date, sa.notes, sa.created_at, sa.updated_at
            FROM shift_assignments sa
            WHERE sa.id = ?
            """,
            [assignment_id],
        )
        
        if not result.rows:
            return None
        
        return self._map_to_assignment_entity(result.rows[0])
    
    def get_employee_assignments(self, employee_id: str, active_only: bool = True) -> List[ShiftAssignment]:
        """Get all assignments for an employee"""
        query = """
            SELECT sa.id, sa.shift_id, sa.employee_id, sa.start_date, sa.end_date, sa.notes, sa.created_at, sa.updated_at
            FROM shift_assignments sa
            WHERE sa.employee_id = ?
        """
        params = [employee_id]
        
        if active_only:
            query += " AND sa.end_date IS NULL OR sa.end_date >= ?"
            params.append(date.today().isoformat())
        
        query += " ORDER BY sa.start_date DESC"
        
        result = self.client.execute(query, params)
        
        return [self._map_to_assignment_entity(row) for row in result.rows]
    
    def get_shift_assignments(self, shift_id: str, active_only: bool = True) -> List[ShiftAssignment]:
        """Get all employees assigned to a specific shift"""
        query = """
            SELECT sa.id, sa.shift_id, sa.employee_id, sa.start_date, sa.end_date, sa.notes, sa.created_at, sa.updated_at
            FROM shift_assignments sa
            WHERE sa.shift_id = ?
        """
        params = [shift_id]
        
        if active_only:
            query += " AND (sa.end_date IS NULL OR sa.end_date >= ?)"
            params.append(date.today().isoformat())
        
        query += " ORDER BY sa.start_date DESC"
        
        result = self.client.execute(query, params)
        
        return [self._map_to_assignment_entity(row) for row in result.rows]
    
    def get_employee_shifts_for_date_range(self, employee_id: str, start_date: date, end_date: date) -> List[dict]:
        """Get all shifts for an employee within a date range (CA3 - Calendar)"""
        query = """
            SELECT 
                sa.id, sa.shift_id, s.name, s.day_of_week, s.start_time, s.end_time,
                u.name as employee_name, u.email,
                sa.start_date, sa.end_date, sa.notes
            FROM active_shift_assignments asa
            JOIN shift_assignments sa ON asa.id = sa.id
            JOIN shifts s ON asa.shift_id = s.id
            JOIN users u ON asa.employee_id = u.id
            WHERE sa.employee_id = ? AND sa.start_date <= ? AND (sa.end_date IS NULL OR sa.end_date >= ?)
            ORDER BY sa.start_date ASC
        """
        
        result = self.client.execute(
            query,
            [
                employee_id,
                end_date.isoformat(),
                start_date.isoformat(),
            ],
        )
        
        return [self._map_to_calendar_record(row) for row in result.rows]
    
    def check_shift_overlap(self, employee_id: str, target_date: date) -> List[dict]:
        """
        Check if an employee has overlapping shifts on a specific date (CA2)
        Returns list of overlapping shifts if any
        """
        # Get the day of week for the target date
        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
        
        query = """
            SELECT 
                s.id, s.name, s.day_of_week, s.start_time, s.end_time,
                sa.id as assignment_id, sa.start_date, sa.end_date
            FROM shift_assignments sa
            JOIN shifts s ON sa.shift_id = s.id
            WHERE sa.employee_id = ? 
            AND sa.start_date <= ? 
            AND (sa.end_date IS NULL OR sa.end_date >= ?)
            AND s.day_of_week = ?
        """
        
        result = self.client.execute(
            query,
            [employee_id, target_date.isoformat(), target_date.isoformat(), day_of_week],
        )
        
        return [
            {
                "shift_id": row[0],
                "name": row[1],
                "start_time": row[3],
                "end_time": row[4],
                "assignment_id": row[5],
                "start_date": row[6],
                "end_date": row[7],
            }
            for row in result.rows
        ]
    
    def get_employee_weekly_schedule(self, employee_id: str, as_of: Optional[date] = None) -> dict:
        """Get the weekly schedule for an employee (CA3 - Calendar view)"""
        if as_of is None:
            as_of = date.today()
        
        query = """
            SELECT 
                asa.employee_id,
                u.name as employee_name,
                u.email,
                asa.shift_id,
                asa.name as shift_name,
                asa.day_of_week,
                asa.start_time,
                asa.end_time,
                asa.start_date,
                asa.end_date
            FROM active_shift_assignments asa
            JOIN users u ON asa.employee_id = u.id
            WHERE asa.employee_id = ? AND asa.start_date <= ? AND (asa.end_date IS NULL OR asa.end_date >= ?)
            ORDER BY asa.day_of_week, asa.start_time
        """
        
        result = self.client.execute(
            query,
            [employee_id, as_of.isoformat(), as_of.isoformat()],
        )
        
        schedule = {}
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for row in result.rows:
            day_name = days[row[5]]
            if day_name not in schedule:
                schedule[day_name] = []
            
            schedule[day_name].append({
                'shift_id': row[3],
                'name': row[4],
                'start_time': row[6],
                'end_time': row[7],
            })
        
        return {
            'employee_id': employee_id,
            'schedule': schedule,
        }
    
    def update_assignment(self, assignment: ShiftAssignment) -> ShiftAssignment:
        """Update an existing assignment"""
        assignment.updated_at = datetime.now()
        
        self.client.execute(
            """
            UPDATE shift_assignments
            SET end_date = ?, notes = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                assignment.end_date.isoformat() if assignment.end_date and isinstance(assignment.end_date, date) else assignment.end_date,
                assignment.notes,
                assignment.updated_at.isoformat(),
                assignment.id,
            ],
        )
        return assignment
    
    def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        result = self.client.execute(
            "DELETE FROM shift_assignments WHERE id = ?",
            [assignment_id],
        )
        return result.rows_affected > 0 if hasattr(result, 'rows_affected') else True
    
    def bulk_assign_shift(self, shift_id: str, employee_ids: List[str], start_date: date, end_date: Optional[date] = None) -> List[ShiftAssignment]:
        """Assign a shift to multiple employees"""
        assignments = []
        
        for employee_id in employee_ids:
            assignment = ShiftAssignment(
                id=str(uuid.uuid4()),
                shift_id=shift_id,
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.create_assignment(assignment)
            assignments.append(assignment)
        
        return assignments
    
    # ============= MAPPING METHODS =============
    
    def _map_to_shift_entity(self, row: tuple) -> Shift:
        """Map database row to Shift entity"""
        return Shift(
            id=row[0],
            name=row[1],
            day_of_week=row[2],
            start_time=row[3],
            end_time=row[4],
            is_active=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )
    
    def _map_to_assignment_entity(self, row: tuple) -> ShiftAssignment:
        """Map database row to ShiftAssignment entity"""
        return ShiftAssignment(
            id=row[0],
            shift_id=row[1],
            employee_id=row[2],
            start_date=row[3] if isinstance(row[3], date) else datetime.fromisoformat(row[3]).date(),
            end_date=row[4] if row[4] is None else (row[4] if isinstance(row[4], date) else datetime.fromisoformat(row[4]).date()),
            notes=row[5],
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )
    
    def _map_to_calendar_record(self, row: tuple) -> dict:
        """Map database row to calendar record"""
        return {
            'assignment_id': row[0],
            'shift_id': row[1],
            'shift_name': row[2],
            'day_of_week': row[3],
            'start_time': row[4],
            'end_time': row[5],
            'employee_name': row[6],
            'email': row[7],
            'start_date': row[8],
            'end_date': row[9],
            'notes': row[10],
        }


def get_turso_connection():
    """Get Turso database connection"""
    return get_turso_client()
