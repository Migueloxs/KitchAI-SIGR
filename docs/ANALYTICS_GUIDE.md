## Analytics and Metrics API Guide

### Overview

The Analytics Module provides comprehensive data analysis and metrics endpoints for constructing dynamic dashboards and recommendation panels. Built on the **Clean Architecture** pattern, it integrates seamlessly with KitchAI SIGR's existing infrastructure.

---

## 🎯 Acceptance Criteria

### CA1: Aggregated Sales Data
✅ The API returns aggregated sales data by:
- **Product**: Individual product performance with quantity sold and revenue
- **Hour**: Hourly trends showing peak hours and revenue distribution
- **Category**: Category-level analysis for easier business insights
- **Service Type**: Breakdown by dine-in, delivery, and takeaway

All data returned in **JSON format** for easy integration with frontend dashboards.

### CA2: Filtering Capabilities
✅ The API supports advanced filtering:
- **Date Range**: `start_date` and `end_date` (YYYY-MM-DD format, required)
- **Service Type**: `service_type` (dine-in, delivery, takeaway, or all)
- **Employee**: `employee_id` (filter by specific employee)
- **Category**: `category_name` (filter by product category)

Filters can be combined for precise data analysis.

### CA3: Metadata and Comparatives
✅ Responses include:
- **Metadata**: Total revenue, cost, profit, tax, discounts, transactions
- **Percentages**: Profit margin, percentage distribution by service type
- **Comparatives**: Automatic comparison with previous period (same day/week/month/quarter/year)
- **Insights**: Top products, peak hours, employee performance

---

## 📋 API Endpoints

### 1. GET `/api/analytics/sales-data`

**Purpose**: Get aggregated sales data with optional filters (CA1, CA2, CA3)

**Authentication**: Required (JWT Bearer Token)

**Query Parameters**:
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `service_type` (string, optional): 'dine-in', 'delivery', 'takeaway', or 'all' (default: all)
- `employee_id` (string, optional): Filter by employee ID
- `category_name` (string, optional): Filter by category name

**Response**:
```json
{
  "date_range_start": "2026-03-20",
  "date_range_end": "2026-03-27",
  "sales_by_product": [
    {
      "product_id": "prod-123",
      "product_name": "Pizza Margherita",
      "category_name": "Pizzas",
      "total_quantity": 45,
      "total_revenue": 450.00,
      "total_profit": 315.00,
      "total_discount": 0.00,
      "transaction_count": 25
    }
  ],
  "sales_by_hour": [
    {
      "hour": 12,
      "revenue": 150.00,
      "quantity_sold": 30,
      "transaction_count": 10,
      "average_price_per_item": 5.00
    }
  ],
  "sales_by_category": [
    {
      "product_id": "Pizzas",
      "product_name": "Pizzas",
      "category_name": "Pizzas",
      "total_quantity": 100,
      "total_revenue": 900.00,
      "total_profit": 630.00,
      "total_discount": 0.00,
      "transaction_count": 50
    }
  ],
  "sales_by_service_type": [
    {
      "service_type": "dine-in",
      "revenue": 600.00,
      "transaction_count": 40,
      "percentage_of_total": 66.67
    }
  ],
  "metadata": {
    "total_revenue": 900.00,
    "total_cost": 270.00,
    "total_profit": 630.00,
    "total_discount": 0.00,
    "total_tax": 180.00,
    "total_transactions": 50,
    "average_ticket": 18.00,
    "profit_margin": 70.00
  }
}
```

**Example Requests**:
```bash
# Get all sales for a date range
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-20&end_date=2026-03-27" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by dine-in service only
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-20&end_date=2026-03-27&service_type=dine-in" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by specific employee
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-20&end_date=2026-03-27&employee_id=emp-123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by category and date
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-20&end_date=2026-03-27&category_name=Pizzas" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. GET `/api/analytics/comparative`

**Purpose**: Get comparative analysis with previous period (CA3)

**Authentication**: Required (JWT Bearer Token)

**Query Parameters**:
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `period_type` (string, optional): 'day', 'week', 'month', 'quarter', 'year' (default: 'day')
- `service_type` (string, optional): Filter by service type

**Response**:
```json
{
  "current_sales_data": {
    "date_range_start": "2026-03-27",
    "date_range_end": "2026-03-27",
    "sales_by_product": [...],
    "sales_by_hour": [...],
    "sales_by_category": [...],
    "sales_by_service_type": [...],
    "metadata": {
      "total_revenue": 500.00,
      "total_cost": 150.00,
      "total_profit": 350.00,
      "total_discount": 0.00,
      "total_tax": 100.00,
      "total_transactions": 25,
      "average_ticket": 20.00,
      "profit_margin": 70.00
    }
  },
  "comparison_with_previous": {
    "period_type": "day",
    "current_period": {
      "total_revenue": 500.00,
      "total_cost": 150.00,
      "total_profit": 350.00,
      "total_transactions": 25
    },
    "previous_period": {
      "total_revenue": 450.00,
      "total_cost": 135.00,
      "total_profit": 315.00,
      "total_transactions": 22
    },
    "changes": {
      "revenue_change_percentage": 11.11,
      "profit_change_percentage": 11.11,
      "transaction_growth_percentage": 13.64
    }
  },
  "top_products": [
    {
      "product_id": "prod-1",
      "product_name": "Pizza Margherita",
      "category_name": "Pizzas",
      "total_quantity": 10,
      "total_revenue": 100.00,
      "total_profit": 70.00,
      "total_discount": 0.00,
      "transaction_count": 5
    }
  ],
  "top_employee": {
    "employee_id": "emp-1",
    "total_sales": 500.00,
    "total_transactions": 25,
    "average_ticket": 20.00,
    "items_sold": 100
  },
  "peak_hours": [
    {
      "hour": 12,
      "revenue": 200.00,
      "quantity_sold": 40,
      "transaction_count": 15,
      "average_price_per_item": 5.00
    }
  ]
}
```

**Example Requests**:
```bash
# Compare today with yesterday
curl -X GET "http://localhost:8000/api/analytics/comparative?start_date=2026-03-27&end_date=2026-03-27&period_type=day" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Compare this week with last week
curl -X GET "http://localhost:8000/api/analytics/comparative?start_date=2026-03-20&end_date=2026-03-27&period_type=week" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Compare this month with last month
curl -X GET "http://localhost:8000/api/analytics/comparative?start_date=2026-03-01&end_date=2026-03-27&period_type=month" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. GET `/api/analytics/dashboard`

**Purpose**: Get quick dashboard summary for a specific date

**Authentication**: Required (JWT Bearer Token)

**Query Parameters**:
- `date` (string, optional): Date in YYYY-MM-DD format (default: today)

**Response**:
```json
{
  "date": "2026-03-27",
  "total_revenue": 500.00,
  "total_profit": 350.00,
  "total_transactions": 25,
  "average_ticket": 20.00,
  "peak_hour": 12,
  "peak_hour_revenue": 100.00,
  "dine_in_revenue": 300.00,
  "delivery_revenue": 150.00,
  "takeaway_revenue": 50.00
}
```

**Example Requests**:
```bash
# Get today's dashboard summary
curl -X GET "http://localhost:8000/api/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get dashboard for specific date
curl -X GET "http://localhost:8000/api/analytics/dashboard?date=2026-03-20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔐 Authentication & Authorization

All Analytics endpoints require:
1. **Valid JWT token** in request header: `Authorization: Bearer {token}`
2. **Admin or Employee role** to access analytics data

Obtain a token by logging in:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d {
    "email": "user@example.com",
    "password": "password"
  }
```

---

## 📊 Data Aggregation & Calculations

### Metadata Calculations

- **Profit Margin**: `(total_profit / total_revenue) * 100`
- **Average Ticket**: `total_revenue / total_transactions`
- **Percentage by Service Type**: `(service_type_revenue / total_revenue) * 100`
- **Average Price per Item**: `revenue / quantity_sold`

### Period Comparison Calculations

- **Revenue Change %**: `((current_revenue - previous_revenue) / previous_revenue) * 100`
- **Profit Change %**: `((current_profit - previous_profit) / previous_profit) * 100`
- **Transaction Growth %**: `((current_transactions - previous_transactions) / previous_transactions) * 100`

---

## 🔄 Database Structure

The Analytics module uses the following tables:

### `analytics_sales_aggregates`
Stores aggregated sales data by product, hour, category, and service type.

**Key Columns**:
- `date`: Date of the sale
- `product_id`, `product_name`, `category_id`, `category_name`: Product info
- `hour`: Hour of the day (0-23)
- `service_type`: dine-in, delivery, or takeaway
- `employee_id`: Employee who processed the transaction
- `quantity_sold`, `revenue`, `cost`, `profit`: Sales metrics
- `discount_applied`, `tax_collected`: Financial details

**Indexes**:
- Date, Product, Category, Service Type, Employee, Hour (for fast querying)

### `analytics_daily_summary`
Aggregated daily summary for quick dashboard access.

### `analytics_period_comparison`
Pre-calculated comparisons for efficient retrieval.

### Views
- `analytics_dashboard_summary`: Real-time dashboard data
- `analytics_product_performance`: Product-level analysis
- `analytics_hourly_trends`: Hourly trends over time

---

## 🚀 Usage Examples

### Example 1: Daily Sales Report
```bash
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-27&end_date=2026-03-27" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Use for:
- Daily operations review
- Quick performance check
- Staff briefing

### Example 2: Weekly Comparison
```bash
curl -X GET "http://localhost:8000/api/analytics/comparative?start_date=2026-03-20&end_date=2026-03-27&period_type=week" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Use for:
- Weekly performance review
- Trend analysis
- Target achievement tracking

### Example 3: Product Category Analysis
```bash
curl -X GET "http://localhost:8000/api/analytics/sales-data?start_date=2026-03-20&end_date=2026-03-27&category_name=Pizzas" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Use for:
- Category performance analysis
- Inventory planning
- Menu optimization

### Example 4: Employee Performance Tracking
```bash
curl -X GET "http://localhost:8000/api/analytics/comparative?start_date=2026-03-27&end_date=2026-03-27&period_type=day" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Access top_employee in response for individual performance metrics.

---

## ⚠️ Error Handling

### 400 Bad Request
- Invalid date format
- Unsupported service type
- Missing required parameters

### 403 Forbidden
- User lacks admin/employee role

### 404 Not Found
- Invalid employee ID
- Non-existent category

### 500 Internal Server Error
- Database connection issues
- Calculation errors

---

## 📝 Implementation Notes

- **Architecture**: Clean Architecture with Domain, Application, Infrastructure layers
- **Database**: Turso (SQLite-compatible)
- **Authentication**: JWT-based with role-based access control
- **Performance**: Indexed queries for fast data retrieval
- **Scalability**: Aggregated data to handle large datasets efficiently

---

## 🔄 Integration with Dashboard

The three endpoints work together:

1. **`/sales-data`** - Core data retrieval with filtering
2. **`/comparative`** - Trend analysis and insights
3. **`/dashboard`** - Quick metrics for dashboard tiles

Frontend teams can:
- Use `/dashboard` for real-time dashboard widgets
- Use `/sales-data` for detailed analytics pages
- Use `/comparative` for trend and performance reports

---

## 📞 Support

For issues or questions:
- Check the test files: `test_analytics_module.py`, `test_analytics_api.py`
- Review database migrations: `010_create_analytics_tables.sql`
- Consult module files in `src/modules/Analytics/`
