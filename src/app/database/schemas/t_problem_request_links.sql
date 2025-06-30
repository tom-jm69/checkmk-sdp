CREATE TABLE IF NOT EXISTS t_problem_request_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    request_id INTEGER NOT NULL,
    linked_at TIMESTAMP DEFAULT (datetime('now')),
    FOREIGN KEY (alert_id) REFERENCES t_checkmk_problems(id),
    FOREIGN KEY (request_id) REFERENCES t_servicedesk_requests(id),
    UNIQUE(alert_id, request_id)
);
