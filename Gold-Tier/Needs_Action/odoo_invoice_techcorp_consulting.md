---
type: odoo_action
action: create_invoice
approved: true
priority: high
created: 2026-03-30 17:50:00
source_email: email_test_invoice_request.md
---

# Odoo Action: Create Invoice for TechCorp Solutions

**Action:** create_invoice
**HITL Required:** yes (amount $3,750 > $500 threshold)
**Reason:** Invoice amount requires human approval before creation in Odoo

## Partner Information
- Name: TechCorp Solutions Ltd
- Email: billing@techcorp.io
- Phone: +92-321-5551234
- Type: Company
- Existing Partner ID: NEW (will be created if not found)

## Invoice Details
- Invoice Number: Auto (Odoo will generate)
- Invoice Date: 2026-03-30
- Due Date: 2026-04-30 (Net 30)
- Currency: USD
- Payment Terms: Net 30
- Reference: March 2026 Consulting Services

## Line Items
1. Software Consulting: 20.0 x $150.0 = $3000.0
2. Technical Documentation: 5.0 x $150.0 = $750.0

**Total Amount:** $3,750.00

## Original Email Content
```
From: billing@techcorp.io
Subject: Invoice Request - March Consulting

Hi,

Please send invoice for March consulting services:

1. Software Consulting: 20 hours @ $150/hr = $3,000
2. Technical Documentation: 5 hours @ $150/hr = $750

Total: $3,750
Payment terms: Net 30
Due: April 30, 2026

Thanks,
Sarah Johnson
TechCorp Solutions Ltd
+92-321-5551234
```

## Extraction Confidence
- Partner Name: ✅ High (95%)
- Email: ✅ High (100%)
- Phone: ✅ High (100%)
- Line Items: ✅ High (95%)
- Total Amount: ✅ High (100%)
- Due Date: ✅ High (100%)

**Overall Confidence:** 98%

## Approval Checklist
- [ ] Partner information verified (TechCorp Solutions Ltd)
- [ ] Amount correct ($3,750.00)
- [ ] Line items accurate (20 hrs + 5 hrs consulting)
- [ ] Due date appropriate (Net 30 - April 30)
- [ ] Services delivered or agreed upon
- [ ] Ready to create draft invoice in Odoo

## Instructions
**To approve:**
1. Review all details above
2. Verify services were delivered
3. Check amount calculation
4. Move this file to Approved/ folder
5. approved_watcher will automatically create the invoice in Odoo

**To reject:**
1. Add rejection reason below
2. Move to Needs_Action/ for revision

---

## Expected Result
- Partner "TechCorp Solutions Ltd" created in Odoo (if new)
- Draft invoice created with 2 line items
- Total: $3,750.00
- Status: Draft (not posted)
- Human can review and edit in Odoo before posting


---

**Execution Failed**

status: failed
attempted_at: 2026-03-30T18:02:46.404574
error: 2026-03-30 18:02:44,283 - __main__ - INFO - Initialized Odoo RPC client for http://localhost:8069
2026-03-30 18:02:44,283 - __main__ - INFO - Authenticating as pinkyshergill1986@gmail.com on database ai_employee_db
2026-03-30 18:02:45,836 - __main__ - INFO - \u2705 Authentication successful! UID: 2
2026-03-30 18:02:45,929 - __main__ - INFO - \u2705 Created partner: TechCorp Solutions Ltd (ID: 7)
2026-03-30 18:02:45,929 - __main__ - INFO - Created new partner: TechCorp Solutions Ltd (ID: 7)
2026-03-30 18:02:46,348 - __main__ - INFO - \u2705 Created invoice ID: 2 for partner 7
2026-03-30 18:02:46,350 - __main__ - ERROR - Operation failed: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>

