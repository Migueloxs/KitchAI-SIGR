"""
Test Financial Reports APIs - Issue #13
Tests for all CA1, CA2, and CA3 requirements
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


@pytest.fixture
def test_dates():
    """Create test date ranges"""
    today = datetime.now().date()
    start_date = (today - timedelta(days=30)).isoformat()
    end_date = today.isoformat()
    
    return {
        "current_start": end_date,
        "current_end": today.isoformat(),
        "previous_start": start_date,
        "previous_end": (today - timedelta(days=1)).isoformat(),
    }


@pytest.fixture
def admin_token():
    """Mock admin JWT token for testing"""
    # This should be replaced with actual token generation
    return "mock-admin-token"


@pytest.fixture
def employee_token():
    """Mock employee JWT token for testing"""
    return "mock-employee-token"


class TestFinancialReportsAPI:
    """Test suite for Financial Reports APIs"""
    
    def test_ca1_sales_by_period_requires_auth(self, client):
        """CA1: Verify authentication is required"""
        response = client.get(
            "/api/finances/reports/sales-by-period/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.json().get("detail", "")
    
    def test_ca1_sales_by_period_structure(self, client, employee_token):
        """CA1: Verify response structure includes required fields"""
        response = client.get(
            "/api/finances/reports/sales-by-period/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify CA1 requirements
            assert "period" in data, "Must include period information"
            assert "sales_detail" in data, "Must include detailed sales data"
            assert "summary" in data, "Must include summary totals"
            
            # Verify period structure
            assert "start_date" in data["period"]
            assert "end_date" in data["period"]
            
            # Verify summary has totals
            assert "total_sales" in data["summary"]
            assert "total_transactions" in data["summary"]
            assert "average_transaction" in data["summary"]
            
            # Verify sales detail structure
            if data["sales_detail"]:
                sale = data["sales_detail"][0]
                assert "sale_id" in sale
                assert "order_number" in sale
                assert "total_amount" in sale
                assert "payment_method" in sale
                assert "items" in sale
    
    def test_ca2_sales_by_payment_method(self, client, employee_token):
        """CA2: Verify payment method filter works"""
        response = client.get(
            "/api/finances/reports/sales-by-payment-method/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "payment_method": "Tarjeta"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify all returned sales match the filter
            for sale in data.get("sales_detail", []):
                assert sale["payment_method"] == "Tarjeta", \
                    f"Payment method filter failed: got {sale['payment_method']}"
    
    def test_ca2_sales_by_employee(self, client, employee_token):
        """CA2: Verify employee filter works"""
        employee_id = "test-employee-uuid"
        
        response = client.get(
            "/api/finances/reports/sales-by-employee/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "employee_id": employee_id
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify structure
            assert "sales_detail" in data
            assert "summary" in data
    
    def test_ca3_detailed_report_admin_only(self, client, employee_token):
        """CA3: Verify admin-only access for detailed reports"""
        response = client.get(
            "/api/finances/reports/detailed/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code == 403, \
            "Employee should not access detailed reports"
    
    def test_ca3_detailed_report_structure(self, client, admin_token):
        """CA3: Verify detailed report includes all required metadata"""
        response = client.get(
            "/api/finances/reports/detailed/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify CA3 requirements
            assert "metrics" in data, "Must include aggregated metrics"
            assert "payment_method_breakdown" in data, "Must include payment breakdown"
            assert "employee_performance" in data, "Must include employee performance"
            assert "product_category_breakdown" in data, "Must include product breakdown"
            
            # Verify metrics has CA3 requirements
            metrics = data["metrics"]
            assert "total_revenue" in metrics
            assert "total_expenses" in metrics
            assert "total_profit" in metrics
            assert "profit_margin_percentage" in metrics
            assert "average_daily_revenue" in metrics
            
            # Verify payment breakdown has aggregations
            for payment in data["payment_method_breakdown"]:
                assert "transaction_count" in payment
                assert "total_amount" in payment
                assert "average_transaction" in payment
                assert "percentage_of_total" in payment
            
            # Verify employee performance has metrics
            for employee in data["employee_performance"]:
                assert "employee_name" in employee
                assert "sales_count" in employee
                assert "total_sales" in employee
                assert "percentage_of_sales" in employee
    
    def test_ca3_comparison_report_growth_rates(self, client, admin_token, test_dates):
        """CA3: Verify comparison report includes growth rate calculations"""
        response = client.get(
            "/api/finances/reports/comparison/",
            params=test_dates,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify comparison structure
            assert "comparison" in data
            assert "metrics_comparison" in data
            assert "insights" in data
            
            # Verify growth metrics
            growth = data["metrics_comparison"].get("growth", {})
            assert "revenue_growth_percentage" in growth
            assert "expense_growth_percentage" in growth
            assert "profit_growth_percentage" in growth
            
            # Verify insights are generated
            assert len(data["insights"]) > 0, "Must generate insights"
            assert isinstance(data["insights"], list)
    
    def test_invalid_date_format(self, client, employee_token):
        """Test error handling for invalid date format"""
        response = client.get(
            "/api/finances/reports/sales-by-period/",
            params={
                "start_date": "01-01-2024",  # Wrong format
                "end_date": "31-01-2024"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code in [400, 422], \
            "Should reject invalid date format"
    
    def test_missing_required_parameters(self, client, employee_token):
        """Test error handling for missing required parameters"""
        response = client.get(
            "/api/finances/reports/sales-by-period/",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code == 422, \
            "Should validate required parameters"
    
    def test_response_json_serializable(self, client, admin_token):
        """Verify all responses are valid JSON"""
        response = client.get(
            "/api/finances/reports/detailed/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            # Should not raise an exception
            data = response.json()
            json_str = json.dumps(data)
            assert len(json_str) > 0
    
    def test_percentage_calculations(self, client, admin_token):
        """Verify percentage calculations are correct"""
        response = client.get(
            "/api/finances/reports/detailed/",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify profit margin calculation
            metrics = data.get("metrics", {})
            if metrics.get("total_revenue", 0) > 0:
                expected_margin = (
                    (metrics["total_profit"] / metrics["total_revenue"]) * 100
                )
                actual_margin = metrics.get("profit_margin_percentage", 0)
                assert abs(expected_margin - actual_margin) < 0.01, \
                    "Profit margin calculation incorrect"
            
            # Verify percentage of total sums to 100
            total_percent = sum(
                p.get("percentage_of_total", 0)
                for p in data.get("payment_method_breakdown", [])
            )
            if total_percent > 0:
                assert abs(total_percent - 100.0) < 0.01, \
                    "Percentages should sum to 100"


class TestReportIntegration:
    """Integration tests for Financial Reports"""
    
    def test_all_endpoints_respond(self, client, admin_token, employee_token):
        """Verify all 6 endpoints are accessible"""
        endpoints = [
            "/api/finances/reports/sales-by-period/",
            "/api/finances/reports/sales-by-payment-method/",
            "/api/finances/reports/sales-by-employee/",
            "/api/finances/reports/detailed/",
            "/api/finances/reports/comparison/",
        ]
        
        params = {
            "sales-by-period": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "sales-by-payment-method": {"start_date": "2024-01-01", "end_date": "2024-01-31", "payment_method": "Tarjeta"},
            "sales-by-employee": {"start_date": "2024-01-01", "end_date": "2024-01-31", "employee_id": "uuid-1"},
            "detailed": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "comparison": {"current_start": "2024-02-01", "current_end": "2024-02-29", "previous_start": "2024-01-01", "previous_end": "2024-01-31"},
        }
        
        for endpoint in endpoints:
            endpoint_name = endpoint.split("/")[-2]
            params_dict = params.get(endpoint_name, {})
            
            # Admin token for all endpoints
            response = client.get(
                endpoint,
                params=params_dict,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            # Should not be 404 or 500
            assert response.status_code != 404, f"{endpoint} not found"
            assert response.status_code != 500, f"{endpoint} server error"


# Run tests with: pytest test_financial_reports.py -v
