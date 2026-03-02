import sqlite3
import os

SCRIPT = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS menu_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL CHECK(price >= 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_number TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    table_number INTEGER,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','preparing','ready','served','cancelled')),
    total_amount REAL NOT NULL DEFAULT 0 CHECK(total_amount >= 0),
    tax_amount REAL NOT NULL DEFAULT 0 CHECK(tax_amount >= 0),
    discount_amount REAL NOT NULL DEFAULT 0 CHECK(discount_amount >= 0),
    final_amount REAL NOT NULL DEFAULT 0 CHECK(final_amount >= 0),
    payment_status TEXT NOT NULL DEFAULT 'unpaid'
        CHECK(payment_status IN ('unpaid','paid','refunded')),
    payment_method TEXT
        CHECK(payment_method IN ('cash','card','transfer') OR payment_method IS NULL),
    special_instructions TEXT,
    waiter_id TEXT NOT NULL,
    cancelled_by TEXT,
    cancelled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (waiter_id) REFERENCES users(id),
    FOREIGN KEY (cancelled_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    menu_item_id TEXT NOT NULL,
    menu_item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    subtotal REAL NOT NULL CHECK(subtotal >= 0),
    special_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

CREATE TRIGGER IF NOT EXISTS trg_orders_set_updated_at
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    UPDATE orders
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_recalculate_order_after_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET
        total_amount = (
            SELECT IFNULL(SUM(subtotal),0)
            FROM order_items
            WHERE order_id = NEW.order_id
        ),
        tax_amount = (
            SELECT IFNULL(SUM(subtotal),0) * 0.18
            FROM order_items
            WHERE order_id = NEW.order_id
        ),
        final_amount = (
            (SELECT IFNULL(SUM(subtotal),0)
             FROM order_items
             WHERE order_id = NEW.order_id)
            +
            ((SELECT IFNULL(SUM(subtotal),0)
              FROM order_items
              WHERE order_id = NEW.order_id) * 0.18)
            -
            discount_amount
        )
    WHERE id = NEW.order_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_recalculate_order_after_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET
        total_amount = (
            SELECT IFNULL(SUM(subtotal),0)
            FROM order_items
            WHERE order_id = NEW.order_id
        ),
        tax_amount = (
            SELECT IFNULL(SUM(subtotal),0) * 0.18
            FROM order_items
            WHERE order_id = NEW.order_id
        ),
        final_amount = (
            (SELECT IFNULL(SUM(subtotal),0)
             FROM order_items
             WHERE order_id = NEW.order_id)
            +
            ((SELECT IFNULL(SUM(subtotal),0)
              FROM order_items
              WHERE order_id = NEW.order_id) * 0.18)
            -
            discount_amount
        )
    WHERE id = NEW.order_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_recalculate_order_after_delete
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET
        total_amount = (
            SELECT IFNULL(SUM(subtotal),0)
            FROM order_items
            WHERE order_id = OLD.order_id
        ),
        tax_amount = (
            SELECT IFNULL(SUM(subtotal),0) * 0.18
            FROM order_items
            WHERE order_id = OLD.order_id
        ),
        final_amount = (
            (SELECT IFNULL(SUM(subtotal),0)
             FROM order_items
             WHERE order_id = OLD.order_id)
            +
            ((SELECT IFNULL(SUM(subtotal),0)
              FROM order_items
              WHERE order_id = OLD.order_id) * 0.18)
            -
            discount_amount
        )
    WHERE id = OLD.order_id;
END;

"""

conn = sqlite3.connect('kitchai.db')
conn.executescript(SCRIPT)
conn.commit()
conn.close()
print("Tablas y triggers creados.")
