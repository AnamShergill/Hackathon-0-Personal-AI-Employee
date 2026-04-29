---
type: odoo_action
action: create_partner
approved: true
priority: medium
created: 2026-03-30 17:41:00
---

# Odoo Action: Create New Customer

**Action:** create_partner
**HITL Required:** yes (new customer creation)
**Reason:** Creating new customer record in accounting system

## Data
- Name: Acme Corporation
- Email: contact@acme.com
- Phone: +92-300-ACME123
- Type: Company
- Customer: Yes
- Vendor: No

## Context
Test action to verify end-to-end Odoo integration workflow.
This will create a new customer in Odoo via the approved_watcher automation.

## Approval Checklist
- [x] Customer name verified
- [x] Contact information valid
- [x] Ready to create in Odoo

**Status:** Ready for approval

---

## Instructions
To approve this action:
1. Review the customer details above
2. Move this file to Approved/ folder
3. approved_watcher will automatically execute the action
4. Check Done/ folder for results


---

**Execution Failed**

status: failed
attempted_at: 2026-03-30T17:42:15.862253
error: 2026-03-30 17:42:13,818 - __main__ - INFO - Initialized Odoo RPC client for http://localhost:8069
2026-03-30 17:42:13,819 - __main__ - INFO - Authenticating as pinkyshergill1986@gmail.com on database ai_employee_db
2026-03-30 17:42:15,789 - __main__ - INFO - \u2705 Authentication successful! UID: 2
2026-03-30 17:42:15,791 - __main__ - ERROR - --name required for create_partner

