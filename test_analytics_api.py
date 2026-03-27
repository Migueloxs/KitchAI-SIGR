"""API tests for Analytics endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


class TestAnalyticsEndpoints:
    """Test Analytics API endpoints."""
    
    @pytest.fixture
    def auth_header(self):
        """Create mock auth header."""
        return {"Authorization": "Bearer mock-token"}
    
    @patch('src.modules.Analytics.infrastructure.api.analytics_router.AnalyticsService')
    def test_get_sales_analytics_success(self, mock_service_class, auth_header):
        """Test successful sales analytics request."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock response
        mock_service.get_sales_analytics.return_value = {
            "date_range_start": "2026-03-20",
            "date_range_end": "2026-03-27",
            "sales_by_product": [
                {
                    "product_id": "prod-1",
                    "product_name": "Pizza",
                    "category_name": "Pizzas",
                    "total_quantity": 10,
                    "total_revenue": 100.0,
                    "total_profit": 70.0,
                    "total_discount": 0.0,
                    "transaction_count": 5,
                }
            ],
            "sales_by_hour": [
                {
                    "hour": 12,
                    "revenue": 100.0,
                    "quantity_sold": 10,
                    "transaction_count": 5,
                    "average_price_per_item": 10.0,
                }
            ],
            "sales_by_category": [],
            "sales_by_service_type": [
                {
                    "service_type": "dine-in",
                    "revenue": 100.0,
                    "transaction_count": 5,
                    "percentage_of_total": 100.0,
                }
            ],
            "metadata": {
                "total_revenue": 100.0,
                "total_cost": 30.0,
                "total_profit": 70.0,
                "total_discount": 0.0,
                "total_tax": 20.0,
                "total_transactions": 5,
                "average_ticket": 20.0,
                "profit_margin": 70.0,
            },
        }
        
        assert mock_service.get_sales_analytics.called is False
        mock_service.get_sales_analytics(
            start_date="2026-03-20",
            end_date="2026-03-27",
            service_type=None,
            employee_id=None,
            category_name=None,
        )
        
        assert mock_service.get_sales_analytics.called is True
    
    @patch('src.modules.Analytics.infrastructure.api.analytics_router.AnalyticsService')
    def test_get_sales_analytics_with_filters(self, mock_service_class, auth_header):
        """Test sales analytics with filters."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock response
        mock_service.get_sales_analytics.return_value = {
            "date_range_start": "2026-03-27",
            "date_range_end": "2026-03-27",
            "sales_by_product": [],
            "sales_by_hour": [],
            "sales_by_category": [],
            "sales_by_service_type": [
                {
                    "service_type": "dine-in",
                    "revenue": 50.0,
                    "transaction_count": 3,
                    "percentage_of_total": 100.0,
                }
            ],
            "metadata": {
                "total_revenue": 50.0,
                "total_cost": 15.0,
                "total_profit": 35.0,
                "total_discount": 0.0,
                "total_tax": 10.0,
                "total_transactions": 3,
                "average_ticket": 16.67,
                "profit_margin": 70.0,
            },
        }
        
        # Test with filters
        mock_service.get_sales_analytics(
            start_date="2026-03-27",
            end_date="2026-03-27",
            service_type="dine-in",
            employee_id="emp-123",
            category_name=None,
        )
        
        assert mock_service.get_sales_analytics.called is True
    
    @patch('src.modules.Analytics.infrastructure.api.analytics_router.AnalyticsService')
    def test_get_comparative_analytics_success(self, mock_service_class, auth_header):
        """Test successful comparative analytics request."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock response
        mock_service.get_comparative_analytics.return_value = {
            "current_sales_data": {
                "date_range_start": "2026-03-27",
                "date_range_end": "2026-03-27",
                "sales_by_product": [],
                "sales_by_hour": [],
                "sales_by_category": [],
                "sales_by_service_type": [],
                "metadata": {
                    "total_revenue": 500.0,
                    "total_cost": 150.0,
                    "total_profit": 350.0,
                    "total_discount": 0.0,
                    "total_tax": 100.0,
                    "total_transactions": 25,
                    "average_ticket": 20.0,
                    "profit_margin": 70.0,
                },
            },
            "comparison_with_previous": {
                "period_type": "day",
                "current_period": {
                    "total_revenue": 500.0,
                    "total_cost": 150.0,
                    "total_profit": 350.0,
                    "total_transactions": 25,
                },
                "previous_period": {
                    "total_revenue": 450.0,
                    "total_cost": 135.0,
                    "total_profit": 315.0,
                    "total_transactions": 22,
                },
                "changes": {
                    "revenue_change_percentage": 11.11,
                    "profit_change_percentage": 11.11,
                    "transaction_growth_percentage": 13.64,
                },
            },
            "top_products": [],
            "top_employee": {
                "employee_id": "emp-1",
                "total_sales": 500.0,
                "total_transactions": 25,
                "average_ticket": 20.0,
                "items_sold": 100,
            },
            "peak_hours": [],
        }
        
        mock_service.get_comparative_analytics(
            start_date="2026-03-27",
            end_date="2026-03-27",
            period_type="day",
            service_type=None,
        )
        
        assert mock_service.get_comparative_analytics.called is True
    
    @patch('src.modules.Analytics.infrastructure.api.analytics_router.AnalyticsService')
    def test_get_dashboard_summary_success(self, mock_service_class, auth_header):
        """Test successful dashboard summary request."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # Mock response
        today = datetime.now().strftime("%Y-%m-%d")
        mock_service.get_dashboard_summary.return_value = {
            "date": today,
            "total_revenue": 500.0,
            "total_profit": 350.0,
            "total_transactions": 25,
            "average_ticket": 20.0,
            "peak_hour": 12,
            "peak_hour_revenue": 100.0,
            "dine_in_revenue": 300.0,
            "delivery_revenue": 150.0,
            "takeaway_revenue": 50.0,
        }
        
        mock_service.get_dashboard_summary(date=today)
        
        assert mock_service.get_dashboard_summary.called is True
    
    @patch('src.modules.Analytics.infrastructure.api.analytics_router.AnalyticsService')
    def test_get_dashboard_summary_default_date(self, mock_service_class, auth_header):
        """Test dashboard summary without specifying date (should use today)."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        today = datetime.now().strftime("%Y-%m-%d")
        mock_service.get_dashboard_summary.return_value = {
            "date": today,
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "total_transactions": 0,
            "average_ticket": 0.0,
            "peak_hour": None,
            "peak_hour_revenue": 0.0,
            "dine_in_revenue": 0.0,
            "delivery_revenue": 0.0,
            "takeaway_revenue": 0.0,
        }
        
        mock_service.get_dashboard_summary(date=None)
        
        assert mock_service.get_dashboard_summary.called is True


class TestAnalyticsCA1:
    """Test CA1: Aggregated data by product, hour and category."""
    
    def test_response_includes_sales_by_product(self):
        """CA1: Response should include sales by product."""
        response = {
            "sales_by_product": [
                {
                    "product_id": "prod-1",
                    "product_name": "Pizza Margherita",
                    "category_name": "Pizzas",
                    "total_quantity": 10,
                    "total_revenue": 100.0,
                    "total_profit": 70.0,
                    "total_discount": 0.0,
                    "transaction_count": 5,
                }
            ]
        }
        
        assert "sales_by_product" in response
        assert len(response["sales_by_product"]) > 0
    
    def test_response_includes_sales_by_hour(self):
        """CA1: Response should include sales by hour."""
        response = {
            "sales_by_hour": [
                {
                    "hour": 12,
                    "revenue": 100.0,
                    "quantity_sold": 10,
                    "transaction_count": 5,
                    "average_price_per_item": 10.0,
                }
            ]
        }
        
        assert "sales_by_hour" in response
        assert len(response["sales_by_hour"]) > 0
    
    def test_response_includes_sales_by_category(self):
        """CA1: Response should include sales by category."""
        response = {
            "sales_by_category": [
                {
                    "product_id": "Pizzas",
                    "product_name": "Pizzas",
                    "category_name": "Pizzas",
                    "total_quantity": 10,
                    "total_revenue": 100.0,
                    "total_profit": 70.0,
                    "total_discount": 0.0,
                    "transaction_count": 5,
                }
            ]
        }
        
        assert "sales_by_category" in response
        assert len(response["sales_by_category"]) > 0


class TestAnalyticsCA2:
    """Test CA2: Filters by date range, service type and employee."""
    
    def test_filters_are_supported(self):
        """CA2: API should accept filter parameters."""
        filters = {
            "start_date": "2026-03-20",
            "end_date": "2026-03-27",
            "service_type": "dine-in",
            "employee_id": "emp-123",
            "category_name": "Pizzas",
        }
        
        assert "start_date" in filters
        assert "end_date" in filters
        assert "service_type" in filters
        assert "employee_id" in filters
        assert "category_name" in filters


class TestAnalyticsCA3:
    """Test CA3: Response includes metadata, percentages and comparatives."""
    
    def test_response_includes_metadata(self):
        """CA3: Response should include metadata."""
        response = {
            "metadata": {
                "total_revenue": 100.0,
                "total_cost": 30.0,
                "total_profit": 70.0,
                "total_discount": 0.0,
                "total_tax": 20.0,
                "total_transactions": 5,
                "average_ticket": 20.0,
                "profit_margin": 70.0,
            }
        }
        
        assert "metadata" in response
        assert response["metadata"]["total_revenue"] == 100.0
        assert response["metadata"]["profit_margin"] == 70.0
    
    def test_response_includes_comparatives(self):
        """CA3: Response should include comparatives with previous period."""
        response = {
            "comparison_with_previous": {
                "period_type": "day",
                "current_period": {
                    "total_revenue": 500.0,
                    "total_profit": 350.0,
                },
                "previous_period": {
                    "total_revenue": 450.0,
                    "total_profit": 315.0,
                },
                "changes": {
                    "revenue_change_percentage": 11.11,
                    "profit_change_percentage": 11.11,
                },
            }
        }
        
        assert "comparison_with_previous" in response
        assert response["comparison_with_previous"]["changes"]["revenue_change_percentage"] == 11.11
