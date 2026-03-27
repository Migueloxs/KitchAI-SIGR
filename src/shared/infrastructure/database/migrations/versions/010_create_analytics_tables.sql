-- Migration: Create Analytics Tables for Dashboard and Metrics
-- Date: 2026-03-27
-- Purpose: Store aggregated data for sales analysis, metrics and visualizations

-- Create analytics_sales_aggregates table
CREATE TABLE IF NOT EXISTS analytics_sales_aggregates (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    product_id TEXT,
    product_name TEXT NOT NULL,
    category_id TEXT,
    category_name TEXT NOT NULL,
    hour INTEGER,
    service_type TEXT, -- 'delivery', 'dine-in', 'takeaway'
    employee_id TEXT,
    quantity_sold INTEGER NOT NULL DEFAULT 0,
    revenue REAL NOT NULL DEFAULT 0.0,
    cost REAL NOT NULL DEFAULT 0.0,
    profit REAL NOT NULL DEFAULT 0.0,
    discount_applied REAL NOT NULL DEFAULT 0.0,
    tax_collected REAL NOT NULL DEFAULT 0.0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, product_id, hour, service_type, employee_id),
    FOREIGN KEY(employee_id) REFERENCES users(id)
);

-- Create analytics_daily_summary table
CREATE TABLE IF NOT EXISTS analytics_daily_summary (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    total_revenue REAL NOT NULL DEFAULT 0.0,
    total_cost REAL NOT NULL DEFAULT 0.0,
    total_profit REAL NOT NULL DEFAULT 0.0,
    total_discount REAL NOT NULL DEFAULT 0.0,
    total_tax REAL NOT NULL DEFAULT 0.0,
    total_transactions INTEGER NOT NULL DEFAULT 0,
    total_items_sold INTEGER NOT NULL DEFAULT 0,
    average_ticket REAL NOT NULL DEFAULT 0.0,
    
    -- Statistics by service type
    dine_in_revenue REAL NOT NULL DEFAULT 0.0,
    dine_in_transactions INTEGER NOT NULL DEFAULT 0,
    delivery_revenue REAL NOT NULL DEFAULT 0.0,
    delivery_transactions INTEGER NOT NULL DEFAULT 0,
    takeaway_revenue REAL NOT NULL DEFAULT 0.0,
    takeaway_transactions INTEGER NOT NULL DEFAULT 0,
    
    -- Statistics by hour (peak hours analysis)
    peak_hour INTEGER,
    peak_hour_revenue REAL NOT NULL DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics_period_comparison table (for comparing with previous periods)
CREATE TABLE IF NOT EXISTS analytics_period_comparison (
    id TEXT PRIMARY KEY,
    period_start_date TEXT NOT NULL,
    period_end_date TEXT NOT NULL,
    period_type TEXT NOT NULL, -- 'day', 'week', 'month', 'quarter', 'year'
    
    -- Current period
    current_revenue REAL NOT NULL DEFAULT 0.0,
    current_cost REAL NOT NULL DEFAULT 0.0,
    current_profit REAL NOT NULL DEFAULT 0.0,
    current_transactions INTEGER NOT NULL DEFAULT 0,
    
    -- Previous period for comparison
    previous_period_start_date TEXT NOT NULL,
    previous_period_end_date TEXT NOT NULL,
    previous_revenue REAL NOT NULL DEFAULT 0.0,
    previous_cost REAL NOT NULL DEFAULT 0.0,
    previous_profit REAL NOT NULL DEFAULT 0.0,
    previous_transactions INTEGER NOT NULL DEFAULT 0,
    
    -- Calculations
    revenue_change_percentage REAL,
    profit_change_percentage REAL,
    transaction_growth_percentage REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics_employee_performance table
CREATE TABLE IF NOT EXISTS analytics_employee_performance (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    date TEXT NOT NULL,
    total_sales REAL NOT NULL DEFAULT 0.0,
    total_transactions INTEGER NOT NULL DEFAULT 0,
    average_ticket REAL NOT NULL DEFAULT 0.0,
    items_sold INTEGER NOT NULL DEFAULT 0,
    rating REAL,
    
    UNIQUE(employee_id, date),
    FOREIGN KEY(employee_id) REFERENCES users(id),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_date ON analytics_sales_aggregates(date);
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_product ON analytics_sales_aggregates(product_id);
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_category ON analytics_sales_aggregates(category_name);
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_service ON analytics_sales_aggregates(service_type);
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_employee ON analytics_sales_aggregates(employee_id);
CREATE INDEX IF NOT EXISTS idx_analytics_sales_agg_hour ON analytics_sales_aggregates(hour);

CREATE INDEX IF NOT EXISTS idx_analytics_daily_summary_date ON analytics_daily_summary(date);
CREATE INDEX IF NOT EXISTS idx_analytics_period_comparison_dates ON analytics_period_comparison(period_start_date, period_end_date);
CREATE INDEX IF NOT EXISTS idx_analytics_employee_perf_date ON analytics_employee_performance(date);
CREATE INDEX IF NOT EXISTS idx_analytics_employee_perf_emp ON analytics_employee_performance(employee_id);

-- Create view for dashboard data (aggregating multiple tables)
CREATE VIEW IF NOT EXISTS analytics_dashboard_summary AS
SELECT 
    ds.date,
    ds.total_revenue,
    ds.total_cost,
    ds.total_profit,
    ds.total_discount,
    ds.total_tax,
    ds.total_transactions,
    ds.total_items_sold,
    ds.average_ticket,
    ds.dine_in_revenue,
    ds.dine_in_transactions,
    ds.delivery_revenue,
    ds.delivery_transactions,
    ds.takeaway_revenue,
    ds.takeaway_transactions,
    ds.peak_hour,
    ds.peak_hour_revenue
FROM analytics_daily_summary ds
ORDER BY ds.date DESC;

-- Create view for product analytics
CREATE VIEW IF NOT EXISTS analytics_product_performance AS
SELECT 
    date,
    product_id,
    product_name,
    category_name,
    SUM(quantity_sold) as total_quantity,
    SUM(revenue) as total_revenue,
    SUM(profit) as total_profit,
    AVG(quantity_sold) as avg_quantity_per_transaction,
    COUNT(DISTINCT service_type) as service_types_sold
FROM analytics_sales_aggregates
GROUP BY date, product_id, product_name, category_name
ORDER BY date DESC, total_revenue DESC;

-- Create view for hourly trends
CREATE VIEW IF NOT EXISTS analytics_hourly_trends AS
SELECT 
    date,
    hour,
    SUM(revenue) as hour_revenue,
    SUM(quantity_sold) as hour_quantity,
    SUM(transaction_count) as hour_transactions,
    AVG(revenue / NULLIF(quantity_sold, 0)) as avg_price_per_item
FROM analytics_sales_aggregates
WHERE hour IS NOT NULL
GROUP BY date, hour
ORDER BY date DESC, hour;
