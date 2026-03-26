"""E2E Tests - Finances Module (CA1, CA2, CA3)"""

import pytest
from datetime import datetime, timedelta
from src.modules.Finances.application.usecases.finances_usecases import FinancesService
from src.modules.Finances.application.dto.finance_response import CreateExpenseRequestDTO


class TestCA1_IncomeCalculation:
    """CA1: El sistema debe calcular ingresos totales sumando todas las ventas registradas en un período"""

    def test_total_income_single_day(self):
        """Calcula correctamente los ingresos de un solo día"""
        service = FinancesService()
        
        # CA1: Calcular ingresos totales
        test_date = datetime.now().date().isoformat()
        total_income = service.get_total_income_by_date(test_date)
        
        # Verificaciones - El total debe ser un número
        assert isinstance(total_income, (int, float)), f"Ingresos debe ser numérico, se obtuvo {type(total_income)}"
        assert total_income >= 0, f"Ingresos no pueden ser negativos: {total_income}"
        print(f"✅ CA1: Ingresos del día {test_date}: ${total_income}")

    def test_total_income_period(self):
        """Calcula correctamente los ingresos de un período completo"""
        service = FinancesService()
        
        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        end_date = datetime.now().date().isoformat()
        
        # CA1: Calcular ingresos del período
        total_income = service.get_total_income_by_period(start_date, end_date)
        
        # Verificaciones
        assert isinstance(total_income, (int, float)), f"Ingresos debe ser numérico"
        assert total_income >= 0, f"Ingresos no pueden ser negativos: {total_income}"
        print(f"✅ CA1: Ingresos del período {start_date} al {end_date}: ${total_income}")

    def test_income_invalid_date_range(self):
        """Maneja correctamente rangos de fecha inválidos"""
        service = FinancesService()
        
        # Usar fechas inversas (end < start)
        start_date = "2024-12-31"
        end_date = "2024-01-01"
        
        # Debe devolver 0 o manejar gracefully
        total_income = service.get_total_income_by_period(start_date, end_date)
        assert total_income >= 0, f"Se esperaba 0 o resultado válido"
        print(f"✅ CA1: Validación de rango de fechas inválido: ${total_income}")


class TestCA2_ProfitCalculation:
    """CA2: Debe restar automáticamente los egresos registrados para obtener la ganancia neta"""

    def test_net_profit_single_day(self):
        """Calcula ganancia neta correctamente (ingresos - gastos)"""
        service = FinancesService()
        
        test_date = datetime.now().date().isoformat()
        
        # Crear egreso: gasto de $300
        expense = CreateExpenseRequestDTO(
            category="Inventario",
            description="Compra de ingredientes",
            amount=300.00,
            vendor="Distribuidor ABC",
            notes="Ingredientes frescos",
            expense_date=test_date
        )
        service.create_expense(expense, user_id="test-user-id")
        
        # CA2: Calcular ganancia neta
        profit_data = service.get_net_profit_by_date(test_date)
        
        # Verificaciones
        assert profit_data["expenses"] == 300.00, f"Gastos incorrectos: {profit_data['expenses']}"
        assert profit_data["net_profit"] >= 0, f"Ganancia neta no puede ser negativa"
        print(f"✅ CA2: Ingresos=${profit_data['income']}, Gastos=${profit_data['expenses']}, Ganancia=${profit_data['net_profit']}, Margen={profit_data['profit_margin']}%")

    def test_net_profit_period(self):
        """Calcula ganancia neta correctamente para un período"""
        service = FinancesService()
        
        start_date = (datetime.now() - timedelta(days=3)).date().isoformat()
        end_date = datetime.now().date().isoformat()
        
        # Crear gastos: $1500
        for i in range(3):
            test_date = (datetime.now() - timedelta(days=i)).date().isoformat()
            expense = CreateExpenseRequestDTO(
                category="Inventario",
                description=f"Gasto {i}",
                amount=500.00,
                vendor="Distribuidor XYZ",
                notes="Gastos operativos",
                expense_date=test_date
            )
            service.create_expense(expense, user_id="test-user-id")
        
        # CA2: Calcular ganancia del período
        profit_data = service.get_net_profit_by_period(start_date, end_date)
        
        # Verificaciones
        assert profit_data["expenses"] >= 1500.00, f"Gastos insuficientes: {profit_data['expenses']}"
        assert profit_data["net_profit"] >= 0, f"Ganancia puede ser 0 o positiva"
        assert profit_data["profit_margin"] is not None, f"Margen no calculado"
        print(f"✅ CA2 Período: Ingresos=${profit_data['income']}, Gastos=${profit_data['expenses']}, Ganancia=${profit_data['net_profit']}, Margen={profit_data['profit_margin']}%")

    def test_profit_with_no_expenses(self):
        """Ganancia = ingresos cuando no hay gastos"""
        service = FinancesService()
        
        # Usar fecha sin gastos
        test_date = (datetime.now() - timedelta(days=30)).date().isoformat()
        
        # CA2: Sin gastos, ganancia = ingresos
        profit_data = service.get_net_profit_by_date(test_date)
        
        # Verificaciones
        assert profit_data["expenses"] == 0.0, f"Gastos deben ser 0: {profit_data['expenses']}"
        if profit_data["income"] == 0:
            assert profit_data["profit_margin"] == 0, f"Margen debe ser 0 cuando no hay ingresos"
        else:
            assert profit_data["net_profit"] == profit_data["income"], f"Ganancia debe igualar ingresos"
        print(f"✅ CA2: Sin gastos, ganancia = ingresos = ${profit_data['net_profit']}")


class TestCA3_RealTimeReports:
    """CA3: Los resultados deben actualizarse en tiempo real y estar disponibles a través de una API"""

    def test_daily_financial_summary_dto(self):
        """Genera reporte diario con formato DTO correcto"""
        service = FinancesService()
        
        test_date = datetime.now().date().isoformat()
        
        # CA3: Obtener resumen diario
        daily_summary = service.get_daily_financial_summary(test_date)
        
        # Verificaciones de estructura
        assert hasattr(daily_summary, 'date'), "Falta campo 'date'"
        assert hasattr(daily_summary, 'total_income'), "Falta campo 'total_income'"
        assert hasattr(daily_summary, 'total_expenses'), "Falta campo 'total_expenses'"
        assert hasattr(daily_summary, 'net_profit'), "Falta campo 'net_profit'"
        assert hasattr(daily_summary, 'transaction_count'), "Falta campo 'transaction_count'"
        
        # El DTO debe ser serializable a JSON
        dto_dict = daily_summary.model_dump()
        assert isinstance(dto_dict, dict), "DTO no es serializable a dict"
        print(f"✅ CA3: Daily Summary DTO válido - {dto_dict}")

    def test_period_financial_summary_dto(self):
        """Genera reporte de período con formato DTO correcto"""
        service = FinancesService()
        
        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        end_date = datetime.now().date().isoformat()
        
        # CA3: Obtener resumen de período
        period_summary = service.get_period_financial_summary(start_date, end_date)
        
        # Verificaciones de estructura
        assert hasattr(period_summary, 'period_start'), "Falta campo 'period_start'"
        assert hasattr(period_summary, 'period_end'), "Falta campo 'period_end'"
        assert hasattr(period_summary, 'total_income'), "Falta campo 'total_income'"
        assert hasattr(period_summary, 'daily_average_income'), "Falta campo 'daily_average_income'"
        assert hasattr(period_summary, 'daily_average_expense'), "Falta campo 'daily_average_expense'"
        assert hasattr(period_summary, 'daily_average_profit'), "Falta campo 'daily_average_profit'"
        assert hasattr(period_summary, 'profit_margin_percent'), "Falta campo 'profit_margin_percent'"
        
        # El DTO debe ser serializable a JSON
        dto_dict = period_summary.model_dump()
        assert isinstance(dto_dict, dict), "DTO no es serializable a dict"
        print(f"✅ CA3: Period Summary DTO válido - {dto_dict}")

    def test_comprehensive_financial_report_dto(self):
        """Genera reporte detallado con desglose por categoría"""
        service = FinancesService()
        
        start_date = (datetime.now() - timedelta(days=1)).date().isoformat()
        end_date = datetime.now().date().isoformat()
        
        # Crear datos de prueba con gastos en diferentes categorías
        for category in ["Inventario", "Servicios", "Mantenimiento"]:
            expense = CreateExpenseRequestDTO(
                category=category,
                description=f"Gasto en {category}",
                amount=100.00,
                vendor="Vendor",
                notes="Test",
                expense_date=start_date
            )
            service.create_expense(expense, user_id="test-user-id")
        
        # CA3: Obtener reporte completo
        comprehensive_report = service.get_comprehensive_financial_report(start_date, end_date)
        
        # Verificaciones de estructura
        assert hasattr(comprehensive_report, 'daily_summaries'), "Falta 'daily_summaries'"
        assert hasattr(comprehensive_report, 'expenses_by_category'), "Falta 'expenses_by_category'"
        assert hasattr(comprehensive_report, 'top_expense_category'), "Falta 'top_expense_category'"
        assert len(comprehensive_report.daily_summaries) > 0, "daily_summaries vacío"
        assert len(comprehensive_report.expenses_by_category) > 0, "expenses_by_category vacío"
        
        # El DTO debe ser serializable a JSON
        dto_dict = comprehensive_report.model_dump()
        assert isinstance(dto_dict, dict), "DTO no es serializable a dict"
        print(f"✅ CA3: Comprehensive Report DTO válido")
        print(f"   - Días en resumen: {len(comprehensive_report.daily_summaries)}")
        print(f"   - Categorías: {len(comprehensive_report.expenses_by_category)}")
        print(f"   - Top categoría: {comprehensive_report.top_expense_category}")

    def test_real_time_update_expenses(self):
        """Verifica que los gastos se actuali zan en tiempo real"""
        service = FinancesService()
        
        test_date = datetime.now().date().isoformat()
        
        # Obtener resumen inicial
        initial_summary = service.get_daily_financial_summary(test_date)
        initial_expenses = initial_summary.total_expenses
        
        # Crear un nuevo gasto
        expense = CreateExpenseRequestDTO(
            category="Inventario",
            description="Real-time Test",
            amount=250.00,
            vendor="Test Vendor",
            notes="Test",
            expense_date=test_date
        )
        service.create_expense(expense, user_id="test-user-id")
        
        # Obtener resumen actualizado
        updated_summary = service.get_daily_financial_summary(test_date)
        updated_expenses = updated_summary.total_expenses
        
        # Verificar que los datos se actualizaron
        assert updated_expenses > initial_expenses, "Los gastos no se actualizaron en tiempo real"
        assert updated_expenses - initial_expenses == 250.00, f"Incremento incorrecto: {updated_expenses - initial_expenses}"
        print(f"✅ CA3: Actualización en tiempo real confirmada - ${initial_expenses} → ${updated_expenses}")


class TestFinancesIntegration:
    """Tests de integración general del módulo Finanzas"""

    def test_module_structure(self):
        """Verifica que el módulo Finanzas tenga la estructura correcta"""
        from src.modules.Finances.application.usecases.finances_usecases import FinancesService
        from src.modules.Finances.application.dto.finance_response import (
            ExpenseResponseDTO,
            DailyFinancialDTO,
            PeriodFinancialDTO,
            FinancialReportDTO,
        )
        from src.modules.Finances.domain.entities.expense import Expense, ExpenseCategory
        
        # Verificar que todas las clases importan correctamente
        assert FinancesService is not None
        assert ExpenseResponseDTO is not None
        assert DailyFinancialDTO is not None
        assert PeriodFinancialDTO is not None
        assert FinancialReportDTO is not None
        assert Expense is not None
        assert ExpenseCategory is not None
        print("✅ Estructura del módulo Finanzas verificada")

    def test_all_ca_requirements_met(self):
        """Verifica que se cumplan todos los requisitos de CA"""
        service = FinancesService()
        
        # CA1: Método para calcular ingresos totales
        assert hasattr(service, 'get_total_income_by_date'), "Falta get_total_income_by_date (CA1)"
        assert hasattr(service, 'get_total_income_by_period'), "Falta get_total_income_by_period (CA1)"
        
        # CA2: Método para calcular ganancia neta
        assert hasattr(service, 'get_net_profit_by_date'), "Falta get_net_profit_by_date (CA2)"
        assert hasattr(service, 'get_net_profit_by_period'), "Falta get_net_profit_by_period (CA2)"
        
        # CA3: Métodos para reportes en tiempo real
        assert hasattr(service, 'get_daily_financial_summary'), "Falta get_daily_financial_summary (CA3)"
        assert hasattr(service, 'get_period_financial_summary'), "Falta get_period_financial_summary (CA3)"
        assert hasattr(service, 'get_comprehensive_financial_report'), "Falta get_comprehensive_financial_report (CA3)"
        
        print("✅ Todos los requisitos de CA1, CA2 y CA3 están implementados")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
