-- Migration 009: Create payroll management tables
-- For: Gestión de Nómina Básica (Payroll Management)
-- Provides hours tracking, absences, and payroll calculations

-- Payroll periods table: Define payroll periods (weekly, bi-weekly, monthly, etc.)
CREATE TABLE IF NOT EXISTS payroll_periods (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    -- e.g., "2026-03 (March 2026)", "W13 2026 (Week 13)", etc.
    period_type TEXT NOT NULL,
    -- WEEKLY, BIWEEKLY, MONTHLY, CUSTOM
    start_date TEXT NOT NULL,
    -- Format: YYYY-MM-DD
    end_date TEXT NOT NULL,
    -- Format: YYYY-MM-DD
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (period_type, start_date, end_date)
);

CREATE INDEX IF NOT EXISTS idx_payroll_periods_is_active ON payroll_periods (is_active);
CREATE INDEX IF NOT EXISTS idx_payroll_periods_start_date ON payroll_periods (start_date);
CREATE INDEX IF NOT EXISTS idx_payroll_periods_end_date ON payroll_periods (end_date);

-- Work hours summary table: Summary of hours worked per employee per period
CREATE TABLE IF NOT EXISTS work_hours (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    payroll_period_id TEXT NOT NULL,
    normal_hours REAL NOT NULL DEFAULT 0,
    -- Hours within standard hours (e.g., 40 hours for 8-hour workdays)
    overtime_hours REAL NOT NULL DEFAULT 0,
    -- Hours beyond standard (extra hours)
    total_hours REAL NOT NULL DEFAULT 0,
    -- normal_hours + overtime_hours
    minutes_late INTEGER NOT NULL DEFAULT 0,
    -- Total minutes late during period
    times_late INTEGER NOT NULL DEFAULT 0,
    -- Number of times employee was late
    notes TEXT,
    calculated_at TEXT,
    -- ISO 8601 when calculated
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods (id),
    UNIQUE (employee_id, payroll_period_id)
);

CREATE INDEX IF NOT EXISTS idx_work_hours_employee_id ON work_hours (employee_id);
CREATE INDEX IF NOT EXISTS idx_work_hours_payroll_period_id ON work_hours (payroll_period_id);
CREATE INDEX IF NOT EXISTS idx_work_hours_employee_period ON work_hours (employee_id, payroll_period_id);

-- Payroll absences table: Track justified and unjustified absences
CREATE TABLE IF NOT EXISTS payroll_absences (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    absence_date TEXT NOT NULL,
    -- Format: YYYY-MM-DD
    absence_type TEXT NOT NULL,
    -- JUSTIFIED (vacations, medical leave, etc) or UNJUSTIFIED (no-show)
    reason TEXT NOT NULL,
    -- Human readable reason
    description TEXT,
    -- Additional details
    is_paid BOOLEAN NOT NULL DEFAULT 0,
    -- Whether paid or deducted from salary
    payroll_period_id TEXT,
    -- Link to payroll period
    created_by TEXT,
    -- Who recorded this absence (manager ID)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_absences_employee_id ON payroll_absences (employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_absences_absence_date ON payroll_absences (absence_date);
CREATE INDEX IF NOT EXISTS idx_payroll_absences_absence_type ON payroll_absences (absence_type);
CREATE INDEX IF NOT EXISTS idx_payroll_absences_payroll_period ON payroll_absences (payroll_period_id);

-- Payroll deductions table: Track deductions and adjustments
CREATE TABLE IF NOT EXISTS payroll_deductions (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    payroll_period_id TEXT NOT NULL,
    deduction_type TEXT NOT NULL,
    -- ABSENCE, DISCOUNT, OTHER
    amount REAL NOT NULL,
    -- Deduction amount (positive number)
    reason TEXT NOT NULL,
    description TEXT,
    created_by TEXT,
    -- Manager who created this deduction
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_deductions_employee_id ON payroll_deductions (employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_deductions_payroll_period_id ON payroll_deductions (payroll_period_id);

-- Payroll calculations table: Store calculated payroll for audit trail
CREATE TABLE IF NOT EXISTS payroll_calculations (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    payroll_period_id TEXT NOT NULL,
    normal_hours REAL NOT NULL,
    overtime_hours REAL NOT NULL,
    hourly_rate REAL NOT NULL,
    -- Base hourly rate at calculation time
    overtime_multiplier REAL NOT NULL DEFAULT 1.5,
    -- Multiplier for overtime (e.g., 1.5x)
    base_salary REAL NOT NULL,
    -- normal_hours * hourly_rate
    overtime_salary REAL NOT NULL,
    -- overtime_hours * hourly_rate * overtime_multiplier
    gross_salary REAL NOT NULL,
    -- base_salary + overtime_salary
    total_deductions REAL NOT NULL DEFAULT 0,
    -- Sum of all deductions
    net_salary REAL NOT NULL,
    -- gross_salary - total_deductions
    status TEXT NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, CALCULATED, APPROVED, PAID
    calculated_at TEXT NOT NULL,
    -- ISO 8601 when calculated
    approved_by TEXT,
    -- Manager who approved
    approved_at TEXT,
    paid_at TEXT,
    -- When payment was processed
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods (id),
    FOREIGN KEY (approved_by) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_calculations_employee_id ON payroll_calculations (employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_calculations_payroll_period_id ON payroll_calculations (payroll_period_id);
CREATE INDEX IF NOT EXISTS idx_payroll_calculations_status ON payroll_calculations (status);

-- View: Employee hours per payroll period (CA1)
CREATE VIEW IF NOT EXISTS employee_hours_summary AS
SELECT
    wh.id,
    wh.employee_id,
    u.name as employee_name,
    u.email,
    pp.id as payroll_period_id,
    pp.name as payroll_period_name,
    pp.start_date,
    pp.end_date,
    wh.normal_hours,
    wh.overtime_hours,
    wh.total_hours,
    wh.minutes_late,
    wh.times_late,
    COUNT(DISTINCT CASE WHEN ar.is_late = 1 THEN ar.id END) as attendance_late_count,
    COUNT(DISTINCT CASE WHEN ar.status = 'CHECKED_OUT' THEN ar.id END) as days_present
FROM
    work_hours wh
    JOIN users u ON wh.employee_id = u.id
    JOIN payroll_periods pp ON wh.payroll_period_id = pp.id
    LEFT JOIN attendance_records ar ON wh.employee_id = ar.employee_id
    AND DATE(ar.check_in_time) >= pp.start_date
    AND DATE(ar.check_in_time) <= pp.end_date
GROUP BY
    wh.id,
    wh.employee_id,
    u.name,
    u.email,
    pp.id,
    pp.name,
    pp.start_date,
    pp.end_date,
    wh.normal_hours,
    wh.overtime_hours,
    wh.total_hours,
    wh.minutes_late,
    wh.times_late;

-- View: Employee absences summary per payroll period (CA2)
CREATE VIEW IF NOT EXISTS employee_absences_summary AS
SELECT
    u.id as employee_id,
    u.name as employee_name,
    u.email,
    pp.id as payroll_period_id,
    pp.name as payroll_period_name,
    pp.start_date,
    pp.end_date,
    COUNT(CASE WHEN pa.absence_type = 'JUSTIFIED' THEN 1 END) as justified_absences,
    COUNT(CASE WHEN pa.absence_type = 'UNJUSTIFIED' THEN 1 END) as unjustified_absences,
    COUNT(pa.id) as total_absences,
    COUNT(CASE WHEN pa.is_paid = 1 THEN 1 END) as paid_absences,
    GROUP_CONCAT(pa.reason, '; ') as absence_reasons
FROM
    users u
    CROSS JOIN payroll_periods pp
    LEFT JOIN payroll_absences pa ON u.id = pa.employee_id
    AND pp.id = pa.payroll_period_id
WHERE
    u.role_id IN (
        SELECT
            id
        FROM
            roles
        WHERE
            name IN ('employee', 'waiter', 'chef')
    )
GROUP BY
    u.id,
    u.name,
    u.email,
    pp.id,
    pp.name,
    pp.start_date,
    pp.end_date;

-- View: Payroll summary for export (CA3 - JSON consumable)
CREATE VIEW IF NOT EXISTS payroll_export_summary AS
SELECT
    pc.id as payroll_id,
    pc.employee_id,
    u.name as employee_name,
    u.email,
    pp.name as payroll_period,
    pp.start_date,
    pp.end_date,
    pc.normal_hours,
    pc.overtime_hours,
    pc.hourly_rate,
    pc.overtime_multiplier,
    pc.base_salary,
    pc.overtime_salary,
    pc.gross_salary,
    COALESCE(
        (
            SELECT
                SUM(amount)
            FROM
                payroll_deductions pd
            WHERE
                pd.employee_id = pc.employee_id
                AND pd.payroll_period_id = pc.payroll_period_id
        ),
        0
    ) as total_deductions,
    pc.net_salary,
    pc.status,
    pc.calculated_at,
    pc.approved_by,
    pc.approved_at,
    pc.paid_at
FROM
    payroll_calculations pc
    JOIN users u ON pc.employee_id = u.id
    JOIN payroll_periods pp ON pc.payroll_period_id = pp.id;
