CREATE TABLE
    IF NOT EXISTS inventory_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        current_quantity REAL NOT NULL DEFAULT 0 CHECK (current_quantity >= 0),
        minimum_stock REAL NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
        unit TEXT NOT NULL DEFAULT 'unit',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

CREATE INDEX IF NOT EXISTS idx_inventory_items_category ON inventory_items (category);