ALTER TABLE inventory_alerts
ADD COLUMN is_viewed INTEGER NOT NULL DEFAULT 0;

ALTER TABLE inventory_alerts
ADD COLUMN check_date TEXT;

ALTER TABLE inventory_alerts
ADD COLUMN viewed_at TEXT;

UPDATE inventory_alerts
SET
    is_viewed = CASE
        WHEN is_resolved = 1 THEN 1
        ELSE is_viewed
    END,
    viewed_at = CASE
        WHEN is_resolved = 1
        AND viewed_at IS NULL THEN resolved_at
        ELSE viewed_at
    END;

CREATE INDEX IF NOT EXISTS idx_inventory_alerts_check_date ON inventory_alerts (check_date);

CREATE INDEX IF NOT EXISTS idx_inventory_alerts_dashboard ON inventory_alerts (is_resolved, is_viewed, created_at);