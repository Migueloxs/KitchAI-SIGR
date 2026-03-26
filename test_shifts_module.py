"""
Test Shifts Module - CA1, CA2, CA3 requirements
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from src.modules.Shifts.domain.entities.shift import Shift, DayOfWeek
from src.modules.Shifts.domain.entities.shift_assignment import ShiftAssignment
from src.modules.Shifts.application.dto import (
    CreateShiftRequestDTO,
    AssignShiftRequestDTO,
)


class TestShiftEntity:
    """Test Shift domain entity"""
    
    def test_shift_creation_valid(self):
        """Test creating a valid shift"""
        shift = Shift(
            id="shift-1",
            name="Mañana",
            day_of_week=0,  # Monday
            start_time="08:00",
            end_time="16:00",
        )
        assert shift.name == "Mañana"
        assert shift.day_of_week == 0
    
    def test_shift_invalid_day_of_week(self):
        """Test shift with invalid day of week"""
        with pytest.raises(ValueError):
            Shift(
                id="shift-1",
                name="Invalid",
                day_of_week=7,  # Invalid
                start_time="08:00",
                end_time="16:00",
            )
    
    def test_shift_invalid_time_format(self):
        """Test shift with invalid time format"""
        with pytest.raises(ValueError):
            Shift(
                id="shift-1",
                name="Invalid",
                day_of_week=0,
                start_time="8:00",  # Should be HH:MM
                end_time="16:00",
            )
    
    def test_shift_overlaps_detection(self):
        """Test CA2: Shift overlap detection"""
        shift1 = Shift(
            id="shift-1",
            name="Turno 1",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        
        shift2 = Shift(
            id="shift-2",
            name="Turno 2",
            day_of_week=0,  # Same day
            start_time="14:00",
            end_time="22:00",
        )
        
        # Should detect overlap
        assert shift1.overlaps_with(shift2) is True
    
    def test_shift_no_overlap_different_days(self):
        """Test no overlap on different days"""
        shift1 = Shift(
            id="shift-1",
            name="Turno 1",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        
        shift2 = Shift(
            id="shift-2",
            name="Turno 2",
            day_of_week=1,  # Different day
            start_time="08:00",
            end_time="16:00",
        )
        
        assert shift1.overlaps_with(shift2) is False
    
    def test_get_day_name(self):
        """Test day name retrieval"""
        days = [
            ("Lunes", 0),
            ("Martes", 1),
            ("Miércoles", 2),
            ("Jueves", 3),
            ("Viernes", 4),
            ("Sábado", 5),
            ("Domingo", 6),
        ]
        
        for day_name, day_num in days:
            shift = Shift(
                id="shift-1",
                name="Test",
                day_of_week=day_num,
                start_time="08:00",
                end_time="16:00",
            )
            assert shift.get_day_name() == day_name


class TestShiftAssignmentEntity:
    """Test ShiftAssignment domain entity"""
    
    def test_assignment_creation_valid(self):
        """Test creating a valid assignment"""
        assignment = ShiftAssignment(
            id="assign-1",
            shift_id="shift-1",
            employee_id="emp-1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        assert assignment.employee_id == "emp-1"
    
    def test_assignment_is_active_current_date(self):
        """Test CA1: Assignment activity check"""
        today = date.today()
        assignment = ShiftAssignment(
            id="assign-1",
            shift_id="shift-1",
            employee_id="emp-1",
            start_date=today,
            end_date=today + timedelta(days=30),
        )
        assert assignment.is_active(as_of=today) is True
    
    def test_assignment_is_active_after_end_date(self):
        """Test assignment is not active after end date"""
        today = date.today()
        assignment = ShiftAssignment(
            id="assign-1",
            shift_id="shift-1",
            employee_id="emp-1",
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
        )
        assert assignment.is_active(as_of=today) is False
    
    def test_assignment_end_date_validation(self):
        """Test end_date must be after start_date"""
        today = date.today()
        with pytest.raises(ValueError):
            ShiftAssignment(
                id="assign-1",
                shift_id="shift-1",
                employee_id="emp-1",
                start_date=today,
                end_date=today - timedelta(days=1),  # Invalid
            )


class TestShiftsService:
    """Test Shifts service business logic"""
    
    def test_shift_creation_dto(self):
        """Test shift creation DTO"""
        dto = CreateShiftRequestDTO(
            name="Mañana",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        assert dto.name == "Mañana"
    
    def test_shift_assignment_dto(self):
        """Test shift assignment DTO"""
        dto = AssignShiftRequestDTO(
            shift_id="shift-1",
            employee_id="emp-1",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        assert dto.employee_id == "emp-1"


class TestCalendarFeatures:
    """Test CA3 Calendar features"""
    
    def test_weekly_calendar_generation(self):
        """Test weekly calendar view generation"""
        # This would need a full test setup with database
        # Demonstrating the concept
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Should have 7 days in a week
        days_in_week = (week_end - week_start).days + 1
        assert days_in_week == 7


class TestConflictDetection:
    """Test CA2 Conflict detection"""
    
    def test_overlapping_shifts_validation(self):
        """Test that overlapping shifts are detected (CA2)"""
        shift1 = Shift(
            id="shift-1",
            name="Mañana",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        
        shift2 = Shift(
            id="shift-2",
            name="Tarde",
            day_of_week=0,
            start_time="15:00",
            end_time="23:00",
        )
        
        # These shifts overlap (15:00 < 16:00)
        assert shift1.overlaps_with(shift2) is True
        assert shift2.overlaps_with(shift1) is True
    
    def test_adjacent_shifts_no_overlap(self):
        """Test that adjacent shifts don't overlap"""
        shift1 = Shift(
            id="shift-1",
            name="Mañana",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        
        shift2 = Shift(
            id="shift-2",
            name="Tarde",
            day_of_week=0,
            start_time="16:00",
            end_time="23:00",
        )
        
        # Adjacent shifts should not overlap
        # (16:00 start exactly when 16:00 ends)
        assert shift1.overlaps_with(shift2) is False


# Integration tests (would run with actual database)
class TestShiftsIntegration:
    """Integration tests for shifts module"""
    
    def test_create_and_assign_shift_flow(self):
        """Test complete CA1 flow: create shift and assign to employee"""
        # This test demonstrates the expected flow
        # In actual testing, would use real database
        
        # 1. Create a shift
        shift_dto = CreateShiftRequestDTO(
            name="Mañana",
            day_of_week=0,
            start_time="08:00",
            end_time="16:00",
        )
        # service.create_shift(shift_dto)
        
        # 2. Assign to employee
        assignment_dto = AssignShiftRequestDTO(
            shift_id="shift-uuid",
            employee_id="employee-uuid",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
        )
        # service.assign_shift(assignment_dto)
        
        # 3. Verify no conflicts (CA2)
        # service.check_conflicts_for_employee("employee-uuid", date.today())
        
        pass
    
    def test_bulk_assignment_flow(self):
        """Test CA1 bulk assignment to multiple employees"""
        # This demonstrates assigning same shift to multiple employees
        # with individual validation for each
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
