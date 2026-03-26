-- Migration 007: Create shifts and shift assignments tables
-- For: Gestión de Horarios y Turnos de Trabajo (Issue)
-- Shifts table: Define weekly shift patterns
CREATE TABLE
    IF NOT EXISTS shifts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        -- 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        day_of_week INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        -- Format: HH:MM (24-hour)
        end_time TEXT NOT NULL,
        -- Format: HH:MM (24-hour)
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (name, day_of_week)
    );

CREATE INDEX IF NOT EXISTS idx_shifts_day_of_week ON shifts (day_of_week);

CREATE INDEX IF NOT EXISTS idx_shifts_is_active ON shifts (is_active);

-- Shift assignments table: Assign shifts to employees
CREATE TABLE
    IF NOT EXISTS shift_assignments (
        id TEXT PRIMARY KEY,
        shift_id TEXT NOT NULL,
        employee_id TEXT NOT NULL,
        start_date TEXT NOT NULL,
        -- Format: YYYY-MM-DD
        end_date TEXT,
        -- Format: YYYY-MM-DD or NULL for indefinite
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (shift_id) REFERENCES shifts (id),
        FOREIGN KEY (employee_id) REFERENCES users (id),
        UNIQUE (shift_id, employee_id, start_date)
    );

CREATE INDEX IF NOT EXISTS idx_shift_assignments_shift_id ON shift_assignments (shift_id);

CREATE INDEX IF NOT EXISTS idx_shift_assignments_employee_id ON shift_assignments (employee_id);

CREATE INDEX IF NOT EXISTS idx_shift_assignments_start_date ON shift_assignments (start_date);

CREATE INDEX IF NOT EXISTS idx_shift_assignments_end_date ON shift_assignments (end_date);

-- View for active shift assignments
CREATE VIEW
    IF NOT EXISTS active_shift_assignments AS
SELECT
    sa.id,
    sa.shift_id,
    sa.employee_id,
    s.name,
    s.day_of_week,
    s.start_time,
    s.end_time,
    u.name as employee_name,
    u.email,
    sa.start_date,
    sa.end_date,
    sa.notes,
    sa.created_at,
    sa.updated_at
FROM
    shift_assignments sa
    JOIN shifts s ON sa.shift_id = s.id
    JOIN users u ON sa.employee_id = u.id
WHERE
    s.is_active = 1
    AND (
        sa.end_date IS NULL
        OR sa.end_date >= date ('now')
    )
    AND sa.start_date <= date ('now');