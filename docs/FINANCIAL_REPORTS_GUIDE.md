# Financial Reports API Guide

**Issue**: #13 - Implementa APIs para Reportes Financieros

## Overview

The Financial Reports APIs provide comprehensive financial analysis and reporting capabilities for restaurant management. All endpoints follow the hexagonal architecture pattern and integrate with Turso database.

### Requirements

- **CA1**: Return sales, income, and expense data filtered by date in JSON format
- **CA2**: Support additional filters (payment method, employee, product category)
- **CA3**: Include metadata (totals, averages, comparisons with previous periods)

---

## Authentication

All endpoints require authentication via JWT token. Different permission levels apply:

- **Admin Only**: Comparison reports, detailed financial reports
- **Admin/Employee**: Sales reports, filtered sales, payment method summaries

### Auth Header

```bash
Authorization: Bearer {JWT_TOKEN}
```

---

## API Endpoints

### 1. Sales Report by Period (CA1)

**Endpoint**: `GET /api/finances/reports/sales-by-period/`

**Description**: Return detailed sales, income, and expenses filtered by date range.

**Query Parameters**:
- `start_date` (required): Start date in `YYYY-MM-DD` format
- `end_date` (required): End date in `YYYY-MM-DD` format

**Required Role**: Admin or Employee

**Example Request**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/sales-by-period/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response** (200 OK):
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "days": 31
  },
  "sales_detail": [
    {
      "sale_id": "uuid-1",
      "order_number": "ORD-001",
      "customer_name": "Juan García",
      "employee_name": "Carlos",
      "total_amount": 2500.00,
      "payment_method": "Tarjeta",
      "sale_date": "2024-01-15T18:30:00",
      "items": [
        {
          "item_name": "Ceviche",
          "quantity": 1,
          "unit_price": 500.00,
          "subtotal": 500.00
        }
      ]
    }
  ],
  "summary": {
    "total_sales": 50000.00,
    "total_transactions": 25,
    "average_transaction": 2000.00,
    "currency": "DOP"
  }
}
```

---

### 2. Sales Report by Payment Method (CA2)

**Endpoint**: `GET /api/finances/reports/sales-by-payment-method/`

**Description**: Filter sales by payment method with aggregated metrics.

**Query Parameters**:
- `start_date` (required): Start date in `YYYY-MM-DD` format
- `end_date` (required): End date in `YYYY-MM-DD` format
- `payment_method` (required): Payment method (e.g., "Efectivo", "Tarjeta", "Cheque")

**Required Role**: Admin or Employee

**Example Request**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/sales-by-payment-method/?start_date=2024-01-01&end_date=2024-01-31&payment_method=Tarjeta" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response** (200 OK):
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "days": 31
  },
  "sales_detail": [
    {
      "sale_id": "uuid-1",
      "order_number": "ORD-001",
      "customer_name": "Juan García",
      "employee_name": "Carlos",
      "total_amount": 2500.00,
      "payment_method": "Tarjeta",
      "sale_date": "2024-01-15T18:30:00",
      "items": []
    }
  ],
  "summary": {
    "total_sales": 25000.00,
    "total_transactions": 10,
    "average_transaction": 2500.00,
    "currency": "DOP"
  }
}
```

---

### 3. Sales Report by Employee (CA2)

**Endpoint**: `GET /api/finances/reports/sales-by-employee/`

**Description**: Filter sales by employee (waiter/mesero) with performance metrics.

**Query Parameters**:
- `start_date` (required): Start date in `YYYY-MM-DD` format
- `end_date` (required): End date in `YYYY-MM-DD` format
- `employee_id` (required): Employee UUID

**Required Role**: Admin or Employee

**Example Request**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/sales-by-employee/?start_date=2024-01-01&end_date=2024-01-31&employee_id=uuid-employee-1" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response** (200 OK):
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "days": 31
  },
  "sales_detail": [
    {
      "sale_id": "uuid-1",
      "order_number": "ORD-001",
      "customer_name": "Juan García",
      "employee_name": "Carlos",
      "total_amount": 2500.00,
      "payment_method": "Tarjeta",
      "sale_date": "2024-01-15T18:30:00",
      "items": []
    }
  ],
  "summary": {
    "total_sales": 15000.00,
    "total_transactions": 8,
    "average_transaction": 1875.00,
    "currency": "DOP"
  }
}
```

---

### 4. Detailed Financial Report (CA3)

**Endpoint**: `GET /api/finances/reports/detailed/`

**Description**: Comprehensive financial report with all breakdowns and metadata (CA3 requirements).

**Query Parameters**:
- `start_date` (required): Start date in `YYYY-MM-DD` format
- `end_date` (required): End date in `YYYY-MM-DD` format

**Required Role**: Admin Only

**Example Request**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/detailed/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response** (200 OK):
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "days": 31
  },
  "metrics": {
    "total_revenue": 50000.00,
    "total_expenses": 10000.00,
    "total_profit": 40000.00,
    "profit_margin_percentage": 80.0,
    "average_daily_revenue": 1612.90,
    "average_daily_expenses": 322.58,
    "average_daily_profit": 1290.32
  },
  "payment_method_breakdown": [
    {
      "payment_method": "Tarjeta",
      "transaction_count": 10,
      "total_amount": 25000.00,
      "average_transaction": 2500.00,
      "percentage_of_total": 50.0
    },
    {
      "payment_method": "Efectivo",
      "transaction_count": 15,
      "total_amount": 25000.00,
      "average_transaction": 1666.67,
      "percentage_of_total": 50.0
    }
  ],
  "employee_performance": [
    {
      "employee_id": "uuid-emp-1",
      "employee_name": "Carlos",
      "sales_count": 8,
      "total_sales": 15000.00,
      "average_sale": 1875.00,
      "percentage_of_sales": 30.0
    }
  ],
  "product_category_breakdown": [
    {
      "category": "Platos Principales",
      "items_sold": 25,
      "total_amount": 25000.00,
      "average_price": 1000.00,
      "percentage_of_revenue": 50.0
    }
  ],
  "sales_detail": [
    {
      "sale_id": "uuid-1",
      "order_number": "ORD-001",
      "customer_name": "Juan García",
      "employee_name": "Carlos",
      "total_amount": 2500.00,
      "payment_method": "Tarjeta",
      "sale_date": "2024-01-15T18:30:00",
      "items": [
        {
          "item_name": "Ceviche",
          "quantity": 1,
          "unit_price": 500.00,
          "subtotal": 500.00
        }
      ]
    }
  ]
}
```

---

### 5. Financial Comparison Report (CA3)

**Endpoint**: `GET /api/finances/reports/comparison/`

**Description**: Compare two periods with growth rates and auto-generated business insights.

**Query Parameters**:
- `current_start` (required): Current period start date in `YYYY-MM-DD` format
- `current_end` (required): Current period end date in `YYYY-MM-DD` format
- `previous_start` (required): Previous period start date in `YYYY-MM-DD` format
- `previous_end` (required): Previous period end date in `YYYY-MM-DD` format

**Required Role**: Admin Only

**Example Request**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/comparison/?current_start=2024-02-01&current_end=2024-02-29&previous_start=2024-01-01&previous_end=2024-01-31" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response** (200 OK):
```json
{
  "comparison": {
    "current_period": {
      "start_date": "2024-02-01",
      "end_date": "2024-02-29",
      "days": 29
    },
    "previous_period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "days": 31
    }
  },
  "metrics_comparison": {
    "current": {
      "total_revenue": 55000.00,
      "total_expenses": 11000.00,
      "total_profit": 44000.00,
      "profit_margin_percentage": 80.0
    },
    "previous": {
      "total_revenue": 50000.00,
      "total_expenses": 10000.00,
      "total_profit": 40000.00,
      "profit_margin_percentage": 80.0
    },
    "growth": {
      "revenue_growth_percentage": 10.0,
      "expense_growth_percentage": 10.0,
      "profit_growth_percentage": 10.0,
      "margin_change_percentage": 0.0
    }
  },
  "insights": [
    "📈 Ingresos crecieron 10.0% respecto al período anterior",
    "💰 El margen de ganancia se mantuvo estable en 80.0%",
    "⚠️ Los gastos aumentaron al mismo ritmo que los ingresos (10.0%)"
  ]
}
```

---

## Error Handling

All endpoints return standardized error responses:

### 400 Bad Request
```json
{
  "detail": "Error al generar reporte: Fecha inválida o formato incorrecto"
}
```

### 403 Forbidden
```json
{
  "detail": "Solo administradores pueden acceder a reportes financieros"
}
```

### 401 Unauthorized
```json
{
  "detail": "No autorizado"
}
```

---

## Response Models (Pydantic DTOs)

### FilteredSalesReportDTO
Base response model for all filtered sales reports (CA1, CA2).

Fields:
- `period`: Date range information
- `sales_detail`: List of individual sales with item breakdowns
- `summary`: Aggregated totals and averages

### DetailedFinancialReportDTO (CA3)
Comprehensive report with all financial breakdowns.

Fields:
- `period`: Date range
- `metrics`: Aggregated financial metrics
- `payment_method_breakdown`: Sales grouped by payment method
- `employee_performance`: Sales metrics by employee
- `product_category_breakdown`: Sales by product category
- `sales_detail`: Individual transaction details

### FinancialComparisonReportDTO (CA3)
Period-over-period comparison with insights.

Fields:
- `comparison`: Period definitions
- `metrics_comparison`: Current vs previous metrics with growth rates
- `insights`: Auto-generated business insights

---

## Implementation Details

### Architecture Pattern
Follows hexagonal architecture with three layers:

1. **Domain Layer**
   - DTOs: `financial_reports_dto.py` (11 Pydantic models)
   - Repository Interface

2. **Application Layer**
   - Service: `FinancesService` with 6 reporting methods
   - Use Cases: Business logic for aggregation and insights

3. **Infrastructure Layer**
   - Repository: `FinancialReportsRepository` with 10 SQL query methods
   - Router: `finances_router.py` with 6 REST endpoints
   - Database: Turso (LibSQL)

### Database Tables Used

- `sales`: Order information (id, order_number, customer_name, payment_method, total_amount, sale_date)
- `sale_items`: Line items (order_id, menu_item_id, quantity, unit_price)
- `expenses`: Expense records (id, category, amount, expense_date)
- `expense_categories`: Predefined categories
- `users`: Employee/waiter information (id, name, role_id)

### Query Optimization

- Parameterized queries prevent SQL injection
- JOINs performed at database level for efficiency
- Aggregation done at DB level (COUNT, SUM, AVG)
- Minimal data transfer between API and database

---

## Testing

### Manual Testing with cURL

1. **Generate a valid JWT token** (see AUTH_GUIDE.md)

2. **Test Sales by Period endpoint**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/sales-by-period/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

3. **Test Comparison Report endpoint**:
```bash
curl -X GET "http://localhost:8001/api/finances/reports/comparison/?current_start=2024-02-01&current_end=2024-02-29&previous_start=2024-01-01&previous_end=2024-01-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Swagger UI

Access the interactive API documentation at:
```
http://localhost:8001/docs
```

All endpoints are documented with:
- Parameter descriptions
- Response model examples
- Authorization requirements
- Test functionality

---

## Calculation Examples

### Growth Rate Calculation
```
Growth % = (current_value - previous_value) / previous_value × 100
Example: (55000 - 50000) / 50000 × 100 = 10.0%
```

### Profit Margin Calculation
```
Profit Margin % = (total_profit / total_revenue) × 100
Example: (44000 / 55000) × 100 = 80.0%
```

### Percentage of Total Calculation
```
% = (item_value / total_value) × 100
Example: (25000 / 50000) × 100 = 50.0%
```

---

## Future Enhancements

1. **Export Formats**: PDF, Excel, CSV downloads
2. **Scheduled Reports**: Automated email reports
3. **Forecasting**: Optional revenue forecasting based on trends
4. **Custom Metrics**: User-defined KPI calculations
5. **Real-time Dashboard**: WebSocket updates for live metrics
6. **Advanced Filters**: Multiple simultaneous filters
7. **Report Templates**: Customizable report layouts

---

## Troubleshooting

### Common Issues

**Issue**: "Invalid date format"
- **Solution**: Ensure dates are in `YYYY-MM-DD` format (e.g., 2024-01-15)

**Issue**: "Unauthorized access to reports"
- **Solution**: Verify JWT token is valid and user has admin/employee role

**Issue**: "No data returned"
- **Solution**: Check if sales exist in the specified date range in the database

---

## Support

For issues or questions about the Financial Reports API, refer to:
- [API_AUTH_GUIDE.md](API_AUTH_GUIDE.md) - Authentication details
- [README_AUTH.md](README_AUTH.md) - Role-based access control
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Overall system architecture
