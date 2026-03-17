CREATE TABLE
    IF NOT EXISTS menu_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        order_number TEXT NOT NULL UNIQUE,
        customer_name TEXT NOT NULL,
        customer_phone TEXT,
        table_number INTEGER,
        status TEXT NOT NULL,
        service_type TEXT NOT NULL,
        total_amount REAL NOT NULL DEFAULT 0,
        tax_amount REAL NOT NULL DEFAULT 0,
        discount_amount REAL NOT NULL DEFAULT 0,
        final_amount REAL NOT NULL DEFAULT 0,
        payment_status TEXT NOT NULL DEFAULT 'PENDING',
        payment_method TEXT,
        special_instructions TEXT,
        waiter_id TEXT,
        cancelled_by TEXT,
        cancelled_at TEXT,
        cancellation_reason TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        preparation_started_at TEXT,
        ready_at TEXT,
        completed_at TEXT,
        preparation_time INTEGER,
        total_time INTEGER
    );

CREATE TABLE
    IF NOT EXISTS order_items (
        id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        menu_item_id TEXT NOT NULL,
        menu_item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        special_notes TEXT,
        created_at TEXT NOT NULL
    );

CREATE INDEX IF NOT EXISTS idx_orders_waiter_id ON orders (waiter_id);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id);