"""
Payroll Module - Basic Payroll Management System.

This module provides:
- CA1: Worked hours calculation (normal vs overtime) for employees in a date range
- CA2: Justified/unjustified absence records for payroll deduction
- CA3: JSON format payroll data consumable by external payroll systems

Implemented with hexagonal architecture:
- Domain: Business entities and validation rules
- Application: DTOs and use case services
- Infrastructure: Database repositories and REST API endpoints
"""

from src.modules.Payroll.domain.entities import (
    PayrollPeriod,
    WorkHours,
    PayrollAbsence,
    PayrollDeduction,
    PayrollCalculation,
)
from src.modules.Payroll.infrastructure.api.payroll_router import payroll_router

__all__ = [
    "PayrollPeriod",
    "WorkHours",
    "PayrollAbsence",
    "PayrollDeduction",
    "PayrollCalculation",
    "payroll_router",
]
