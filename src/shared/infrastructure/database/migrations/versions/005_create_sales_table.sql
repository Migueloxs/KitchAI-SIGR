CREATE TABLE
    IF NOT EXISTS sales (
        id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        order_number TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        waiter_id TEXT NOT NULL,
        payment_method TEXT,
        total_amount REAL NOT NULL DEFAULT 0,
        tax_amount REAL NOT NULL DEFAULT 0,
        discount_amount REAL NOT NULL DEFAULT 0,
        final_amount REAL NOT NULL DEFAULT 0,
        items_count INTEGER NOT NULL DEFAULT 0,
        sale_date TEXT NOT NULL,
        registered_at TEXT NOT NULL,
        UNIQUE (order_id)
    );

CREATE INDEX IF NOT EXISTS idx_sales_order_id ON sales (order_id);

CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales (sale_date);

CREATE INDEX IF NOT EXISTS idx_sales_waiter_id ON sales (waiter_id);

CREATE INDEX IF NOT EXISTS idx_sales_registered_at ON sales (registered_at);

CREATE TABLE
    IF NOT EXISTS sale_items (
        id TEXT PRIMARY KEY,
        sale_id TEXT NOT NULL,
        menu_item_id TEXT NOT NULL,
        menu_item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (id)
    );

CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items (sale_id);