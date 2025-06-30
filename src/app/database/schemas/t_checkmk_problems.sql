CREATE TABLE IF NOT EXISTS t_checkmk_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_name TEXT NOT NULL,
    service_check_command TEXT,
    service_description TEXT,
    problem_id TEXT NOT NULL UNIQUE,
    type TEXT CHECK(type IN ('host', 'service')) NOT NULL,
    state TEXT NOT NULL,
    acknowledged INT NOT NULL DEFAULT 0,
    raw_payload TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now')),
    updated_at TIMESTAMP DEFAULT (datetime('now'))
);
