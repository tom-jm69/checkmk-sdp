# Todo's

---

- Use same pydantic model for view/add requests
- Felder anlegen (cmk als prefix)
- Acknowledge Service/Host Problem after ticket status is not open
- Feature Request http://localhost:8080/cmk/check_mk/api/1.0/domain-types/acknowledge/collections/host allow expire_on for service and host ack

- Same Problem IDs do not create tickets, but rather get updated in db
- Problems are acknowledged in checkmk when the request status has changed
- Fix get_hosts (use fields instead of columns to get the hostname) (The model or params/data are somewhat wrong)
