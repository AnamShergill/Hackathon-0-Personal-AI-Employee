---
type: odoo_action
action: list_partners
approved: true
priority: low
created: 2026-03-30 17:42:30
---

# Odoo Action: List All Partners

**Action:** list_partners
**HITL Required:** no (read-only query)
**Reason:** Query existing partners in Odoo

## Data
- Limit: 10
- Fields: name, email, phone

## Context
Test action to verify approved_watcher can execute Odoo queries.
This is a read-only operation that lists existing partners.

---

**Status:** Approved and ready for execution


---

**Execution Result**

status: completed
executed_at: 2026-03-30T17:42:46.311001

```

Found 3 partners:
  - ID 6: AI Employee Test Client (test@aiemployee.local)
  - ID 3: Administrator (pinkyshergill1986@gmail.com)
  - ID 1: My Company (pinkyshergill1986@gmail.com)

```
