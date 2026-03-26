-- Migration 008: Create attendance control tables
-- For: Attendance Control and Entry/Exit Registration System (User Story)
-- Provides comprehensive attendance tracking with automatic alerts

-- Attendance Records table: Log of employee check-ins and check-outs
CREATE TABLE IF NOT EXISTS attendance_records (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    shift_assignment_id TEXT,
    check_in_time TEXT NOT NULL,
    -- ISO 8601 format with timezone
    check_out_time TEXT,
    -- ISO 8601 format with timezone (NULL if not checked out yet)
    duration_minutes INTEGER,
    -- Duration in minutes between check_in and check_out
    status TEXT NOT NULL DEFAULT 'CHECKED_IN',
    -- CHECKED_IN, CHECKED_OUT, NO_CHECKOUT, LATE
    is_late BOOLEAN NOT NULL DEFAULT 0,
    -- 1 if checked in after shift start + tolerance
    late_by_minutes INTEGER,
    -- Minutes late (NULL if not late)
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (shift_assignment_id) REFERENCES shift_assignments (id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_attendance_records_employee_id ON attendance_records (employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_check_in_time ON attendance_records (check_in_time);
CREATE INDEX IF NOT EXISTS idx_attendance_records_status ON attendance_records (status);
CREATE INDEX IF NOT EXISTS idx_attendance_records_shift_assignment ON attendance_records (shift_assignment_id);

-- Index for daily reports
CREATE INDEX IF NOT EXISTS idx_attendance_records_date ON attendance_records (
    date(check_in_time)
);

-- Attendance Alerts table: Automatic alerts about attendance issues
CREATE TABLE IF NOT EXISTS attendance_alerts (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    -- NO_CHECK_IN, LATE_ARRIVAL, NO_CHECK_OUT, EARLY_DEPARTURE, ABSENT
    description TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'WARNING',
    -- INFO, WARNING, CRITICAL
    shift_assignment_id TEXT,
    referenced_attendance_id TEXT,
    -- Reference to the attendance record that triggered the alert
    is_acknowledged BOOLEAN NOT NULL DEFAULT 0,
    -- Whether a manager has acknowledged this alert
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    auto_resolved BOOLEAN NOT NULL DEFAULT 0,
    resolved_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (shift_assignment_id) REFERENCES shift_assignments (id),
    FOREIGN KEY (referenced_attendance_id) REFERENCES attendance_records (id),
    FOREIGN KEY (acknowledged_by) REFERENCES users (id)
);

-- Indexes for alerts
CREATE INDEX IF NOT EXISTS idx_attendance_alerts_employee_id ON attendance_alerts (employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_alerts_alert_type ON attendance_alerts (alert_type);
CREATE INDEX IF NOT EXISTS idx_attendance_alerts_created_at ON attendance_alerts (created_at);
CREATE INDEX IF NOT EXISTS idx_attendance_alerts_is_acknowledged ON attendance_alerts (is_acknowledged);

-- Attendance Check Log: Log of daily checks for employees who haven't checked in
CREATE TABLE IF NOT EXISTS attendance_check_log (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    shift_assignment_id TEXT NOT NULL,
    check_date TEXT NOT NULL,
    -- Format: YYYY-MM-DD
    shift_start_time TEXT NOT NULL,
    -- Format: HH:MM from the shift
    tolerance_end_time TEXT NOT NULL,
    -- shift_start_time + tolerance_minutes
    check_status TEXT NOT NULL DEFAULT 'PENDING',
    -- PENDING, NO_CHECK_IN, CHECKED_IN, ABSENT
    alert_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (shift_assignment_id) REFERENCES shift_assignments (id),
    FOREIGN KEY (alert_id) REFERENCES attendance_alerts (id)
);

-- Indexes for check log
CREATE INDEX IF NOT EXISTS idx_attendance_check_log_employee_date ON attendance_check_log (employee_id, check_date);
CREATE INDEX IF NOT EXISTS idx_attendance_check_log_status ON attendance_check_log (check_status);

-- View for today's attendance status
CREATE VIEW IF NOT EXISTS today_attendance_summary AS
SELECT
    u.id as employee_id,
    u.name as employee_name,
    u.email,
    COALESCE(ar.check_in_time, 'NOT CHECKED IN') as check_in_time,
    COALESCE(ar.check_out_time, 'NOT CHECKED OUT') as check_out_time,
    COALESCE(ar.is_late, 0) as is_late,
    COALESCE(ar.status, 'ABSENT') as status,
    COUNT(CASE WHEN aa.alert_type = 'NO_CHECK_IN' THEN 1 END) as pending_alerts
FROM
    users u
    LEFT JOIN shift_assignments sa ON u.id = sa.employee_id
    AND sa.start_date <= date('now')
    AND (sa.end_date IS NULL OR sa.end_date >= date('now'))
    LEFT JOIN shifts s ON sa.shift_id = s.id
    AND s.day_of_week = cast(strftime('%w', 'now') as integer)
    LEFT JOIN attendance_records ar ON u.id = ar.employee_id
    AND date(ar.check_in_time) = date('now')
    LEFT JOIN attendance_alerts aa ON u.id = aa.employee_id
    AND date(aa.created_at) = date('now')
    AND aa.is_acknowledged = 0
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
    ar.check_in_time,
    ar.check_out_time,
    ar.is_late,
    ar.status;

-- View for attendance reports
CREATE VIEW IF NOT EXISTS attendance_report_summary AS
SELECT
    u.id as employee_id,
    u.name as employee_name,
    DATE(ar.check_in_time) as attendance_date,
    s.name as shift_name,
    s.start_time as scheduled_check_in,
    ar.check_in_time,
    ar.check_out_time,
    CASE
        WHEN ar.check_in_time IS NULL THEN 'ABSENT'
        WHEN ar.is_late = 1 THEN 'LATE'
        WHEN ar.check_out_time IS NULL THEN 'NO_CHECKOUT'
        ELSE 'PRESENT'
    END as attendance_status,
    ar.late_by_minutes,
    COUNT(aa.id) as alert_count
FROM
    users u
    LEFT JOIN shift_assignments sa ON u.id = sa.employee_id
    LEFT JOIN attendance_records ar ON u.id = ar.employee_id
    LEFT JOIN shifts s ON sa.shift_id = s.id
    LEFT JOIN attendance_alerts aa ON u.id = aa.employee_id
    AND date(aa.created_at) = DATE(ar.check_in_time)
GROUP BY
    u.id,
    u.name,
    DATE(ar.check_in_time),
    s.name,
    s.start_time,
    ar.check_in_time,
    ar.check_out_time,
    ar.is_late,
    ar.late_by_minutes;
