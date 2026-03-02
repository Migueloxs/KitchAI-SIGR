import sqlite3
conn = sqlite3.connect('kitchai.db')
conn.execute("INSERT OR REPLACE INTO menu_items (id, name, description, price, is_active) VALUES ('item-123', 'Hamburguesa Clasica', 'test desc', 350.00, 1), ('item-456', 'Refresco', 'test desc', 50.00, 1)")
conn.commit()
conn.close()
