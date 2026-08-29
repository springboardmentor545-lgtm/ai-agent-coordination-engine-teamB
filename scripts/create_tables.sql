CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    manager_id VARCHAR(20),
    leave_balance INTEGER NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS leave_history (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'approved', 'rejected', 'escalated', 'pending'
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_calendar (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    leave_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'on_leave'
);

CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    key VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS holidays (
    holiday_date DATE PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    thread_id VARCHAR(100) PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL REFERENCES employees(employee_id),
    start_date DATE,
    end_date DATE,
    decision_outcome VARCHAR(20),
    reason TEXT,
    cancelled_dates JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);