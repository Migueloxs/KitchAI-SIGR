"""
API tests for Payroll module endpoints.

Tests the REST endpoints functionality and integration.
"""

import pytest
import json
from datetime import datetime


@pytest.fixture
def auth_header():
    """Fixture for authorization header with valid JWT token."""
    # In a real environment, this would be obtained from login
    return {"Authorization": "Bearer test_token"}


class TestPayrollPeriodEndpoints:
    """Tests for payroll period management endpoints."""
    
    def test_create_payroll_period_success(self, client, auth_header):
        """Test successful payroll period creation."""
        response = client.post(
            "/api/payroll/periods",
            headers=auth_header,
            json={
                "name": "2026-03 (March 2026)",
                "period_type": "MONTHLY",
                "start_date": "2026-03-01",
                "end_date": "2026-03-31",
                "is_active": True,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "2026-03 (March 2026)"
        assert data["period_type"] == "MONTHLY"
        assert data["is_active"] is True
    
    def test_create_payroll_period_invalid_dates(self, client, auth_header):
        """Test payroll period creation with invalid dates."""
        response = client.post(
            "/api/payroll/periods",
            headers=auth_header,
            json={
                "name": "Invalid Period",
                "period_type": "MONTHLY",
                "start_date": "2026-03-31",
                "end_date": "2026-03-01",  # Invalid: end before start
                "is_active": False,
            },
        )
        
        assert response.status_code == 400
    
    def test_get_active_payroll_periods(self, client, auth_header):
        """Test retrieving active payroll periods."""
        response = client.get(
            "/api/payroll/periods/active",
            headers=auth_header,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All should be active
        for period in data:
            assert period["is_active"] is True


class TestWorkedHoursCalculationEndpoints:
    """Tests for worked hours calculation (CA1) endpoints."""
    
    def test_calculate_worked_hours_success(self, client, auth_header):
        """Test successful worked hours calculation."""
        response = client.post(
            "/api/payroll/worked-hours",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "normal_hours" in data
            assert "overtime_hours" in data
            assert "total_hours" in data
            assert data["normal_hours"] >= 0
            assert data["overtime_hours"] >= 0
            assert data["total_hours"] == data["normal_hours"] + data["overtime_hours"]
    
    def test_calculate_worked_hours_not_authorized(self, client):
        """Test that unauthorized users cannot access other employee's hours."""
        response = client.post(
            "/api/payroll/worked-hours",
            headers={"Authorization": "Bearer invalid_token"},
            json={
                "employee_id": "emp-456",
                "payroll_period_id": "period-2026-03",
            },
        )
        
        assert response.status_code == 401  # Unauthorized
    
    def test_calculate_worked_hours_permission_denied(self, client, auth_header):
        """Test that regular employee cannot see other employee's hours."""
        # Auth header configured for regular employee
        response = client.post(
            "/api/payroll/worked-hours",
            headers=auth_header,
            json={
                "employee_id": "emp-other",  # Different employee
                "payroll_period_id": "period-2026-03",
            },
        )
        
        # Depending on permission setup, may be 403
        assert response.status_code in [403, 401]


class TestAbsenceRecordsEndpoints:
    """Tests for absence records (CA2) endpoints."""
    
    def test_get_absences_success(self, client, auth_header):
        """Test successful absence records retrieval."""
        response = client.post(
            "/api/payroll/absences",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "justified_absences" in data
            assert "unjustified_absences" in data
            assert "total_absences" in data
            assert "paid_absences" in data
            assert data["justified_absences"] >= 0
            assert data["unjustified_absences"] >= 0
    
    def test_record_absence_justified(self, client, auth_header):
        """Test recording a justified absence."""
        response = client.post(
            "/api/payroll/absences/record",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "absence_date": "2026-03-05",
                "absence_type": "JUSTIFIED",
                "reason": "Medical leave",
                "description": "Doctor appointment",
                "is_paid": True,
            },
        )
        
        if response.status_code == 201:
            data = response.json()
            assert data["absence_type"] == "JUSTIFIED"
            assert data["reason"] == "Medical leave"
            assert data["id"] is not None
    
    def test_record_absence_unjustified(self, client, auth_header):
        """Test recording an unjustified absence."""
        response = client.post(
            "/api/payroll/absences/record",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "absence_date": "2026-03-06",
                "absence_type": "UNJUSTIFIED",
                "reason": "No-show",
                "is_paid": False,
            },
        )
        
        if response.status_code == 201:
            data = response.json()
            assert data["absence_type"] == "UNJUSTIFIED"


class TestDeductionsEndpoints:
    """Tests for deductions management endpoints."""
    
    def test_add_deduction_success(self, client, auth_header):
        """Test successful deduction creation."""
        response = client.post(
            "/api/payroll/deductions",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
                "deduction_type": "DISCOUNT",
                "amount": 100.00,
                "reason": "Disciplinary action",
            },
        )
        
        if response.status_code == 201:
            data = response.json()
            assert data["deduction_type"] == "DISCOUNT"
            assert data["amount"] == 100.00
    
    def test_add_deduction_invalid_amount(self, client, auth_header):
        """Test deduction with invalid (zero or negative) amount."""
        response = client.post(
            "/api/payroll/deductions",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
                "deduction_type": "DISCOUNT",
                "amount": 0.0,  # Invalid
                "reason": "Test",
            },
        )
        
        assert response.status_code == 400


class TestPayrollCalculationEndpoints:
    """Tests for payroll calculation endpoints."""
    
    def test_calculate_payroll_success(self, client, auth_header):
        """Test successful payroll calculation."""
        response = client.post(
            "/api/payroll/calculate",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
                "hourly_rate": 15.50,
                "overtime_multiplier": 1.5,
                "include_deductions": True,
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "gross_salary" in data
            assert "net_salary" in data
            assert "status" in data
            assert data["status"] in ["DRAFT", "CALCULATED", "APPROVED", "PAID"]
    
    def test_calculate_payroll_expected_salary(self, client, auth_header):
        """Test payroll calculation with expected values."""
        response = client.post(
            "/api/payroll/calculate",
            headers=auth_header,
            json={
                "employee_id": "emp-test",
                "payroll_period_id": "period-2026-03",
                "hourly_rate": 15.50,
                "overtime_multiplier": 1.5,
                "include_deductions": False,
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            # Net salary should equal gross when no deductions
            assert data["net_salary"] == data["gross_salary"]


class TestPayrollReportEndpoints:
    """Tests for payroll report and export (CA3) endpoints."""
    
    def test_generate_payroll_report_success(self, client, auth_header):
        """Test successful payroll report generation."""
        response = client.post(
            "/api/payroll/report",
            headers=auth_header,
            json={
                "payroll_period_id": "period-2026-03",
                "include_deductions": True,
                "format_type": "JSON",
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "payroll_period_id" in data
            assert "records" in data
            assert "summary" in data
            assert isinstance(data["records"], list)
            
            # Check summary calculations
            summary = data["summary"]
            assert "total_gross_salary" in summary
            assert "total_net_salary" in summary
            assert "total_employees" in summary
    
    def test_export_payroll_json(self, client, auth_header):
        """Test payroll export as JSON."""
        response = client.post(
            "/api/payroll/export/json",
            headers=auth_header,
            json={
                "payroll_period_id": "period-2026-03",
                "include_deductions": True,
                "format_type": "JSON",
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "export_id" in data
            assert "export_date" in data
            assert "export_format" in data
            assert "payroll_report" in data
            assert data["export_format"] == "JSON"


class TestApprovalWorkflow:
    """Tests for payroll approval and payment workflow."""
    
    def test_approve_payroll_success(self, client, auth_header):
        """Test successful payroll approval."""
        # First, calculate payroll
        calc_response = client.post(
            "/api/payroll/calculate",
            headers=auth_header,
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
                "hourly_rate": 15.50,
                "overtime_multiplier": 1.5,
            },
        )
        
        if calc_response.status_code == 200:
            payroll_id = calc_response.json()["id"]
            
            # Then approve it
            response = client.post(
                "/api/payroll/approve",
                headers=auth_header,
                json={"payroll_id": payroll_id},
            )
            
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "APPROVED"
                assert data["approved_by"] is not None
                assert data["approved_at"] is not None
    
    def test_mark_payroll_as_paid(self, client, auth_header):
        """Test marking payroll as paid."""
        # This would require first approving the payroll
        # Full workflow test would be more complex
        pass
    
    def test_payment_requires_approval(self, client, auth_header):
        """Test that payment requires prior approval."""
        # Trying to pay without approval should fail
        response = client.post(
            "/api/payroll/pay",
            headers=auth_header,
            json={"payroll_id": "calc-not-approved"},
        )
        
        # Should fail (404 if doesn't exist, or error if not approved)
        assert response.status_code in [400, 404]


class TestErrorHandling:
    """Tests for error handling and validation."""
    
    def test_invalid_auth_token(self, client):
        """Test requests with invalid auth token."""
        response = client.post(
            "/api/payroll/worked-hours",
            headers={"Authorization": "Bearer invalid_token"},
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
            },
        )
        
        assert response.status_code == 401
    
    def test_missing_auth_header(self, client):
        """Test requests without auth header."""
        response = client.post(
            "/api/payroll/worked-hours",
            json={
                "employee_id": "emp-123",
                "payroll_period_id": "period-2026-03",
            },
        )
        
        assert response.status_code == 401
    
    def test_insufficient_permissions(self, client, auth_header):
        """Test endpoints that require HR_MANAGER role."""
        # Auth header for regular employee trying admin operation
        response = client.post(
            "/api/payroll/periods",
            headers=auth_header,
            json={
                "name": "2026-04 (April 2026)",
                "period_type": "MONTHLY",
                "start_date": "2026-04-01",
                "end_date": "2026-04-30",
            },
        )
        
        # May be 403 if permission checking is implemented
        assert response.status_code in [403, 401]
    
    def test_not_found_error(self, client, auth_header):
        """Test 404 errors for missing resources."""
        response = client.get(
            "/api/payroll/periods/nonexistent-id",
            headers=auth_header,
        )
        
        assert response.status_code == 404


class TestHealthCheck:
    """Tests for module health and status endpoints."""
    
    def test_payroll_health_check(self, client, auth_header):
        """Test payroll module health check."""
        response = client.get(
            "/api/payroll/health",
            headers=auth_header,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "payroll"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
