CREATE TABLE
    IF NOT EXISTS order_inventory_updates (
        order_id TEXT PRIMARY KEY,
        triggered_status TEXT NOT NULL,
        processed_at TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS inventory_alerts (
        id TEXT PRIMARY KEY,
        inventory_item_id TEXT NOT NULL,
        order_id TEXT,
        alert_type TEXT NOT NULL,
        message TEXT NOT NULL,
        current_quantity REAL NOT NULL,
        minimum_stock REAL NOT NULL,
        is_resolved INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        resolved_at TEXT
    );

CREATE INDEX IF NOT EXISTS idx_inventory_alerts_item ON inventory_alerts (inventory_item_id);

CREATE INDEX IF NOT EXISTS idx_inventory_alerts_active ON inventory_alerts (is_resolved, created_at);