"""Unit tests for Analytics module."""

import pytest
from unittest.mock import MagicMock, patch
from src.modules.Analytics.application.usecases.analytics_service import AnalyticsService
from src.modules.Analytics.domain.entities import (
    SalesAggregate,
    DailySummary,
    PeriodComparison,
)


class TestSalesAggregate:
    """Test SalesAggregate entity."""
    
    def test_create_sales_aggregate(self):
        """Test creating a sales aggregate."""
        agg = SalesAggregate(
            id="agg-1",
            date="2026-03-27",
            product_id="prod-1",
            product_name="Pizza Margherita",
            category_id="cat-1",
            category_name="Pizzas",
            hour=12,
            service_type="dine-in",
            employee_id="emp-1",
            quantity_sold=5,
            revenue=50.0,
            cost=15.0,
            profit=35.0,
            discount_applied=0.0,
            tax_collected=10.0,
            transaction_count=1,
        )
        
        assert agg.id == "agg-1"
        assert agg.product_name == "Pizza Margherita"
        assert agg.revenue == 50.0
        assert agg.profit == 35.0
        assert agg.service_type == "dine-in"


class TestDailySummary:
    """Test DailySummary entity."""
    
    def test_create_daily_summary(self):
        """Test creating a daily summary."""
        summary = DailySummary(
            id="summary-1",
            date="2026-03-27",
            total_revenue=1000.0,
            total_cost=300.0,
            total_profit=700.0,
            total_discount=50.0,
            total_tax=200.0,
            total_transactions=50,
            total_items_sold=120,
            average_ticket=20.0,
            dine_in_revenue=600.0,
            dine_in_transactions=30,
            delivery_revenue=300.0,
            delivery_transactions=15,
            takeaway_revenue=100.0,
            takeaway_transactions=5,
            peak_hour=12,
            peak_hour_revenue=200.0,
        )
        
        assert summary.total_revenue == 1000.0
        assert summary.total_profit == 700.0
        assert summary.total_transactions == 50
        assert summary.average_ticket == 20.0


class TestPeriodComparison:
    """Test PeriodComparison entity."""
    
    def test_create_period_comparison(self):
        """Test creating a period comparison."""
        comp = PeriodComparison(
            id="comp-1",
            period_start_date="2026-03-20",
            period_end_date="2026-03-27",
            period_type="week",
            current_revenue=5000.0,
            current_cost=1500.0,
            current_profit=3500.0,
            current_transactions=250,
            previous_period_start_date="2026-03-13",
            previous_period_end_date="2026-03-20",
            previous_revenue=4500.0,
            previous_cost=1350.0,
            previous_profit=3150.0,
            previous_transactions=225,
            revenue_change_percentage=11.11,
            profit_change_percentage=11.11,
            transaction_growth_percentage=11.11,
        )
        
        assert comp.current_revenue == 5000.0
        assert comp.previous_revenue == 4500.0
        assert comp.revenue_change_percentage == 11.11


class TestAnalyticsService:
    """Test Analytics Service."""
    
    @patch('src.modules.Analytics.application.usecases.analytics_service.AnalyticsRepository')
    def test_get_sales_analytics(self, mock_repo_class):
        """Test getting sales analytics."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.get_aggregated_by_product.return_value = [
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
        ]
        
        mock_repo.get_aggregated_by_category.return_value = [
            {
                "category_name": "Pizzas",
                "total_quantity": 10,
                "total_revenue": 100.0,
                "total_profit": 70.0,
                "transaction_count": 5,
                "product_count": 1,
            }
        ]
        
        mock_repo.get_aggregated_by_hour.return_value = [
            {
                "hour": 12,
                "revenue": 100.0,
                "quantity_sold": 10,
                "transaction_count": 5,
                "avg_price_per_item": 10.0,
            }
        ]
        
        mock_repo.get_aggregated_by_service_type.return_value = [
            {
                "service_type": "dine-in",
                "revenue": 100.0,
                "transaction_count": 5,
            }
        ]
        
        mock_repo.get_period_totals.return_value = {
            "total_revenue": 100.0,
            "total_cost": 30.0,
            "total_profit": 70.0,
            "total_discount": 0.0,
            "total_tax": 20.0,
            "total_transactions": 5,
            "total_quantity": 10,
        }
        
        service = AnalyticsService()
        result = service.get_sales_analytics(
            start_date="2026-03-27",
            end_date="2026-03-27",
        )
        
        assert result.date_range_start == "2026-03-27"
        assert result.date_range_end == "2026-03-27"
        assert len(result.sales_by_product) > 0
        assert result.metadata.total_revenue == 100.0
        assert result.metadata.profit_margin == 70.0
    
    @patch('src.modules.Analytics.application.usecases.analytics_service.AnalyticsRepository')
    def test_get_comparative_analytics(self, mock_repo_class):
        """Test getting comparative analytics."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.get_aggregated_by_product.return_value = []
        mock_repo.get_aggregated_by_category.return_value = []
        mock_repo.get_aggregated_by_hour.return_value = []
        mock_repo.get_aggregated_by_service_type.return_value = []
        mock_repo.get_period_totals.return_value = {
            "total_revenue": 1000.0,
            "total_cost": 300.0,
            "total_profit": 700.0,
            "total_discount": 0.0,
            "total_tax": 200.0,
            "total_transactions": 50,
            "total_quantity": 100,
        }
        
        mock_repo.get_period_comparison.return_value = {
            "current_period": {
                "total_revenue": 1000.0,
                "total_cost": 300.0,
                "total_profit": 700.0,
                "total_transactions": 50,
            },
            "previous_period": {
                "total_revenue": 900.0,
                "total_cost": 270.0,
                "total_profit": 630.0,
                "total_transactions": 45,
            },
            "revenue_change_percentage": 11.11,
            "profit_change_percentage": 11.11,
            "transaction_growth_percentage": 11.11,
        }
        
        mock_repo.get_top_products.return_value = []
        mock_repo.get_peak_hours.return_value = []
        mock_repo.get_employee_performance.return_value = []
        
        service = AnalyticsService()
        result = service.get_comparative_analytics(
            start_date="2026-03-27",
            end_date="2026-03-27",
            period_type="day",
        )
        
        assert result.current_sales_data is not None
        assert result.comparison_with_previous is not None
        assert result.comparison_with_previous.period_type == "day"
    
    @patch('src.modules.Analytics.application.usecases.analytics_service.AnalyticsRepository')
    def test_get_dashboard_summary(self, mock_repo_class):
        """Test getting dashboard summary."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        mock_repo.get_period_totals.return_value = {
            "total_revenue": 500.0,
            "total_cost": 150.0,
            "total_profit": 350.0,
            "total_discount": 0.0,
            "total_tax": 100.0,
            "total_transactions": 25,
            "total_quantity": 50,
        }
        
        mock_repo.get_aggregated_by_service_type.return_value = [
            {"service_type": "dine-in", "revenue": 300.0, "transaction_count": 15},
            {"service_type": "delivery", "revenue": 150.0, "transaction_count": 10},
            {"service_type": "takeaway", "revenue": 50.0, "transaction_count": 0},
        ]
        
        mock_repo.get_peak_hours.return_value = [
            {"hour": 12, "revenue": 200.0, "quantity_sold": 20, "transaction_count": 10}
        ]
        
        service = AnalyticsService()
        result = service.get_dashboard_summary(date="2026-03-27")
        
        assert result.date == "2026-03-27"
        assert result.total_revenue == 500.0
        assert result.average_ticket == 20.0
        assert result.peak_hour == 12
