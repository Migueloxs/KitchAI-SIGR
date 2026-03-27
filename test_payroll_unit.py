"""
Unit tests for Payroll module.

Tests for domain entities, service logic, and repository operations.
"""

import pytest
from datetime import datetime, timedelta
from src.modules.Payroll.domain.entities import (
    PayrollPeriod,
    WorkHours,
    PayrollAbsence,
    PayrollDeduction,
    PayrollCalculation,
    PeriodType,
    AbsenceType,
    DeductionType,
    PayrollStatus,
)
from src.modules.Payroll.application.dto import (
    PayrollPeriodCreateDTO,
    WorkedHoursRequestDTO,
    AbsenceRecordsRequestDTO,
    CalculatePayrollDTO,
)


class TestPayrollPeriod:
    """Tests for PayrollPeriod entity."""
    
    def test_create_valid_period(self):
        """Test creating a valid payroll period."""
        period = PayrollPeriod(
            id="period-1",
            name="2026-03 (March 2026)",
            period_type=PeriodType.MONTHLY,
            start_date="2026-03-01",
            end_date="2026-03-31",
        )
        
        assert period.id == "period-1"
        assert period.name == "2026-03 (March 2026)"
        assert period.period_type == PeriodType.MONTHLY
        assert period.start_date == "2026-03-01"
        assert period.end_date == "2026-03-31"
        assert period.is_active is True
    
    def test_create_period_invalid_dates(self):
        """Test that invalid date range raises error."""
        with pytest.raises(ValueError):
            PayrollPeriod(
                id="period-1",
                name="Invalid Period",
                period_type=PeriodType.MONTHLY,
                start_date="2026-03-31",
                end_date="2026-03-01",  # End before start
            )
    
    def test_create_period_same_dates(self):
        """Test that same start/end dates raise error."""
        with pytest.raises(ValueError):
            PayrollPeriod(
                id="period-1",
                name="Invalid Period",
                period_type=PeriodType.MONTHLY,
                start_date="2026-03-01",
                end_date="2026-03-01",  # Same date
            )
    
    def test_period_types(self):
        """Test all valid period types."""
        for period_type in [PeriodType.WEEKLY, PeriodType.BIWEEKLY, 
                           PeriodType.MONTHLY, PeriodType.CUSTOM]:
            period = PayrollPeriod(
                id="period-1",
                name="Test Period",
                period_type=period_type,
                start_date="2026-03-01",
                end_date="2026-03-31",
            )
            assert period.period_type == period_type


class TestWorkHours:
    """Tests for WorkHours entity."""
    
    def test_create_work_hours(self):
        """Test creating work hours."""
        wh = WorkHours(
            id="wh-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
        )
        
        assert wh.id == "wh-1"
        assert wh.normal_hours == 160.0
        assert wh.overtime_hours == 10.0
        assert wh.total_hours == 170.0  # Auto-calculated
    
    def test_negative_hours_raises_error(self):
        """Test that negative hours raise error."""
        with pytest.raises(ValueError):
            WorkHours(
                id="wh-1",
                employee_id="emp-1",
                payroll_period_id="period-1",
                normal_hours=-1.0,
                overtime_hours=10.0,
            )
    
    def test_total_hours_calculation(self):
        """Test total hours calculation."""
        wh = WorkHours(
            id="wh-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=5.5,
        )
        
        assert wh.total_hours == 165.5
    
    def test_lateness_validation(self):
        """Test lateness validation logic."""
        wh = WorkHours(
            id="wh-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=0.0,
            times_late=3,
            minutes_late=45,
        )
        
        assert wh.times_late == 3
        assert wh.minutes_late == 45
    
    def test_times_late_without_minutes_raises_error(self):
        """Test that times_late without minutes_late raises error."""
        with pytest.raises(ValueError):
            WorkHours(
                id="wh-1",
                employee_id="emp-1",
                payroll_period_id="period-1",
                normal_hours=160.0,
                overtime_hours=0.0,
                times_late=3,
                minutes_late=0,  # Invalid: times_late > 0 but minutes_late = 0
            )


class TestPayrollAbsence:
    """Tests for PayrollAbsence entity."""
    
    def test_create_justified_absence(self):
        """Test creating a justified absence."""
        absence = PayrollAbsence(
            id="abs-1",
            employee_id="emp-1",
            absence_date="2026-03-05",
            absence_type=AbsenceType.JUSTIFIED,
            reason="Medical leave",
            is_paid=True,
        )
        
        assert absence.absence_type == AbsenceType.JUSTIFIED
        assert absence.is_paid is True
    
    def test_create_unjustified_absence(self):
        """Test creating an unjustified absence."""
        absence = PayrollAbsence(
            id="abs-2",
            employee_id="emp-1",
            absence_date="2026-03-06",
            absence_type=AbsenceType.UNJUSTIFIED,
            reason="No-show",
            is_paid=False,
        )
        
        assert absence.absence_type == AbsenceType.UNJUSTIFIED
        assert absence.is_paid is False
    
    def test_invalid_date_format(self):
        """Test that invalid date format raises error."""
        with pytest.raises(ValueError):
            PayrollAbsence(
                id="abs-1",
                employee_id="emp-1",
                absence_date="03/05/2026",  # Wrong format
                absence_type=AbsenceType.JUSTIFIED,
                reason="Medical leave",
            )


class TestPayrollDeduction:
    """Tests for PayrollDeduction entity."""
    
    def test_create_absence_deduction(self):
        """Test creating an absence deduction."""
        deduction = PayrollDeduction(
            id="ded-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            deduction_type=DeductionType.ABSENCE,
            amount=100.0,
            reason="Unjustified absence",
        )
        
        assert deduction.deduction_type == DeductionType.ABSENCE
        assert deduction.amount == 100.0
    
    def test_create_discount_deduction(self):
        """Test creating a discount deduction."""
        deduction = PayrollDeduction(
            id="ded-2",
            employee_id="emp-1",
            payroll_period_id="period-1",
            deduction_type=DeductionType.DISCOUNT,
            amount=50.0,
            reason="Uniform cost",
        )
        
        assert deduction.deduction_type == DeductionType.DISCOUNT
        assert deduction.amount == 50.0
    
    def test_zero_or_negative_amount_raises_error(self):
        """Test that zero or negative amounts raise error."""
        with pytest.raises(ValueError):
            PayrollDeduction(
                id="ded-1",
                employee_id="emp-1",
                payroll_period_id="period-1",
                deduction_type=DeductionType.ABSENCE,
                amount=0.0,  # Invalid
                reason="Test",
            )
        
        with pytest.raises(ValueError):
            PayrollDeduction(
                id="ded-2",
                employee_id="emp-1",
                payroll_period_id="period-1",
                deduction_type=DeductionType.ABSENCE,
                amount=-50.0,  # Invalid
                reason="Test",
            )


class TestPayrollCalculation:
    """Tests for PayrollCalculation entity."""
    
    def test_create_payroll_calculation(self):
        """Test creating a payroll calculation."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=2480.0,
            overtime_salary=232.5,
            gross_salary=2712.5,
        )
        
        assert calc.net_salary == 2712.5  # No deductions
        assert calc.status == PayrollStatus.DRAFT
    
    def test_payroll_calculation_with_deductions(self):
        """Test payroll calculation with deductions."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=2480.0,
            overtime_salary=232.5,
            gross_salary=2712.5,
            total_deductions=150.0,
            net_salary=2562.5,
        )
        
        assert calc.gross_salary == 2712.5
        assert calc.total_deductions == 150.0
        assert calc.net_salary == 2562.5
    
    def test_salary_calculations(self):
        """Test automatic salary calculations."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=0.0,  # Will be calculated
            overtime_salary=0.0,  # Will be calculated
            gross_salary=0.0,  # Will be calculated
        )
        
        # After __post_init__, should be calculated
        assert calc.base_salary == 160.0 * 15.50  # 2480.0
        assert calc.overtime_salary == 10.0 * 15.50 * 1.5  # 232.5
        assert calc.gross_salary == 2712.5
    
    def test_approval_workflow(self):
        """Test approval workflow."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=2480.0,
            overtime_salary=232.5,
            gross_salary=2712.5,
        )
        
        assert calc.status == PayrollStatus.DRAFT
        
        calc.set_approved("user-manager-1")
        assert calc.status == PayrollStatus.APPROVED
        assert calc.approved_by == "user-manager-1"
        assert calc.approved_at is not None
    
    def test_payment_workflow(self):
        """Test payment workflow."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=2480.0,
            overtime_salary=232.5,
            gross_salary=2712.5,
            status=PayrollStatus.APPROVED,
            approved_by="user-manager-1",
        )
        
        calc.set_paid()
        assert calc.status == PayrollStatus.PAID
        assert calc.paid_at is not None
    
    def test_cannot_mark_as_paid_if_not_approved(self):
        """Test that payroll cannot be marked as paid if not approved."""
        calc = PayrollCalculation(
            id="calc-1",
            employee_id="emp-1",
            payroll_period_id="period-1",
            normal_hours=160.0,
            overtime_hours=10.0,
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            base_salary=2480.0,
            overtime_salary=232.5,
            gross_salary=2712.5,
        )
        
        with pytest.raises(ValueError):
            calc.set_paid()
    
    def test_invalid_hourly_rate(self):
        """Test that zero or negative hourly rate raises error."""
        with pytest.raises(ValueError):
            PayrollCalculation(
                id="calc-1",
                employee_id="emp-1",
                payroll_period_id="period-1",
                normal_hours=160.0,
                overtime_hours=10.0,
                hourly_rate=0.0,  # Invalid
                overtime_multiplier=1.5,
                base_salary=0.0,
                overtime_salary=0.0,
                gross_salary=0.0,
            )
    
    def test_negative_net_salary_raises_error(self):
        """Test that negative net salary raises error."""
        with pytest.raises(ValueError):
            PayrollCalculation(
                id="calc-1",
                employee_id="emp-1",
                payroll_period_id="period-1",
                normal_hours=5.0,  # Low hours
                overtime_hours=0.0,
                hourly_rate=20.0,  # Calculated: 5 * 20 = 100
                overtime_multiplier=1.5,
                base_salary=100.0,  # Will be recalculated
                overtime_salary=0.0,  # Will be recalculated
                gross_salary=100.0,  # Will be recalculated
                total_deductions=500.0,  # More than gross
                net_salary=-400.0,  # Will be recalculated to negative
            )


class TestPayrollDTOs:
    """Tests for Payroll DTOs."""
    
    def test_payroll_period_create_dto(self):
        """Test PayrollPeriodCreateDTO validation."""
        dto = PayrollPeriodCreateDTO(
            name="2026-03 (March 2026)",
            period_type="MONTHLY",
            start_date="2026-03-01",
            end_date="2026-03-31",
            is_active=True,
        )
        
        assert dto.name == "2026-03 (March 2026)"
        assert dto.period_type == "MONTHLY"
        assert dto.is_active is True
    
    def test_worked_hours_request_dto(self):
        """Test WorkedHoursRequestDTO."""
        dto = WorkedHoursRequestDTO(
            employee_id="emp-1",
            payroll_period_id="period-1",
        )
        
        assert dto.employee_id == "emp-1"
        assert dto.payroll_period_id == "period-1"
    
    def test_calculate_payroll_dto(self):
        """Test CalculatePayrollDTO."""
        dto = CalculatePayrollDTO(
            employee_id="emp-1",
            payroll_period_id="period-1",
            hourly_rate=15.50,
            overtime_multiplier=1.5,
            include_deductions=True,
        )
        
        assert dto.hourly_rate == 15.50
        assert dto.overtime_multiplier == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
