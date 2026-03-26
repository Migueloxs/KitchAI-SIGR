-- Migration 006: Create expenses table for financial tracking
-- CA1: Track all expenses (compras, gastos operativos)
-- CA2: Calculate net profit by subtracting expenses from sales
-- CA3: Real-time financial data
CREATE TABLE
    IF NOT EXISTS expenses (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        vendor TEXT,
        notes TEXT,
        expense_date TEXT NOT NULL,
        registered_at TEXT NOT NULL,
        registered_by TEXT,
        FOREIGN KEY (registered_by) REFERENCES users (id)
    );

CREATE TABLE
    IF NOT EXISTS expense_categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TEXT NOT NULL
    );

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (expense_date);

CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses (category);

CREATE INDEX IF NOT EXISTS idx_expenses_registered_at ON expenses (registered_at);

-- Insert default expense categories
INSERT
OR IGNORE INTO expense_categories (id, name, description, created_at)
VALUES
    (
        'cat-001',
        'Compras de Inventario',
        'Compras de productos para el inventario',
        datetime ('now')
    ),
    (
        'cat-002',
        'Servicios Generales',
        'Agua, luz, internet, telefonía',
        datetime ('now')
    ),
    (
        'cat-003',
        'Mantenimiento',
        'Mantenimiento de equipos e instalaciones',
        datetime ('now')
    ),
    (
        'cat-004',
        'Suministros',
        'Artículos de limpieza, empaques, etc.',
        datetime ('now')
    ),
    (
        'cat-005',
        'Nómina',
        'Salarios y beneficios de empleados',
        datetime ('now')
    ),
    (
        'cat-006',
        'Marketing',
        'Publicidad y promociones',
        datetime ('now')
    ),
    (
        'cat-007',
        'Transporte',
        'Combustible y gastos de transporte',
        datetime ('now')
    ),
    (
        'cat-008',
        'Otros',
        'Otros gastos operativos',
        datetime ('now')
    );