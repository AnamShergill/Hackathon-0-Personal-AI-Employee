# Skill 11: Odoo Accounting Integration

## Purpose
Interact with local Odoo instance for accounting automation: create/update invoices, manage partners (customers/vendors), query financial data, and maintain accounting records.

## When to Use
- Email mentions invoice, payment, billing, or accounting
- Task requires creating/updating customer/vendor records
- Need to track unpaid invoices or financial status
- Request to generate invoice from email data
- Query about customer payment status
- Need to record financial transactions

## When NOT to Use
- Simple email replies (use Email Sender)
- Non-financial tasks
- Before Odoo is initialized and running
- When data is incomplete (missing amount, customer, etc.)

---

## Input Format

### Action File Structure
```markdown
---
type: odoo_action
action: [create_partner|create_invoice|update_partner|query_invoices]
approved: false
priority: [high|medium|low]
created: YYYY-MM-DD HH:MM:SS
---

# Odoo Action: [Action Name]

**Action:** [create_partner|create_invoice|update_partner|query_invoices]
**HITL Required:** [yes|no]
**Reason:** [Brief explanation]

## Data

[Action-specific data in structured format]

## Context

[Original email or task context]
```

### Supported Actions

#### 1. Create Partner (Customer/Vendor)
```markdown
**Action:** create_partner

## Data
- Name: ABC Corporation
- Email: contact@abc.com
- Phone: +92-300-1234567
- Type: Company
- Customer: Yes
- Vendor: No
```

#### 2. Create Invoice
```markdown
**Action:** create_invoice

## Data
- Partner: ABC Corporation (ID: 123 or name)
- Amount: 5000.00
- Currency: PKR
- Description: Consulting services for March 2026
- Due Date: 2026-04-15
- Invoice Lines:
  - Service: Software Development (Qty: 40 hours @ 125/hr = 5000)
  - Service: Project Management (Qty: 10 hours @ 150/hr = 1500)
- Total: 6500.00
```

#### 3. Update Partner
```markdown
**Action:** update_partner

## Data
- Partner ID: 123
- Updates:
  - Email: newemail@abc.com
  - Phone: +92-300-9876543
  - Address: Updated address
```

#### 4. Query Unpaid Invoices
```markdown
**Action:** query_invoices

## Data
- Partner: ABC Corporation (optional)
- Status: unpaid
- Limit: 10
```

---

## Execution

### Command
```bash
python actions/odoo_rpc.py --action [ACTION] [OPTIONS]
```

### Examples

**Test Connection:**
```bash
python actions/odoo_rpc.py --action test
```

**Create Partner:**
```bash
python actions/odoo_rpc.py --action create_partner \
  --name "ABC Corporation" \
  --email "contact@abc.com" \
  --phone "+92-300-1234567"
```

**Create Invoice:**
```bash
python actions/odoo_rpc.py --action create_invoice \
  --partner-id 123 \
  --amount 5000.00 \
  --description "Consulting services"
```

**List Partners:**
```bash
python actions/odoo_rpc.py --action list_partners
```

**Query Unpaid Invoices:**
```bash
python actions/odoo_rpc.py --action unpaid_invoices --partner-id 123
```

---

## HITL (Human-in-the-Loop) Triggers

### ALWAYS Require Approval (HIGH Priority)
1. **Financial Transactions > $500 USD (or 150,000 PKR)**
   - Creating invoices above threshold
   - Any payment recording
   - Journal entries affecting cash/bank accounts

2. **New Customer/Vendor Creation**
   - First-time partner creation
   - Partner with credit terms
   - International partners

3. **Invoice Modifications**
   - Editing existing invoices
   - Canceling invoices
   - Applying credits/refunds

4. **Bulk Operations**
   - Creating multiple invoices at once
   - Batch partner updates
   - Mass payment recording

### Auto-Execute (LOW Priority)
1. **Read-Only Queries**
   - Listing partners
   - Querying unpaid invoices
   - Checking payment status
   - Generating reports

2. **Small Invoices < $100 USD**
   - Routine service invoices
   - Recurring billing
   - Pre-approved customers

3. **Partner Updates (Non-Financial)**
   - Updating contact info
   - Adding notes
   - Updating addresses

---

## Safety Rules

### Pre-Execution Checks
1. ✅ Verify Odoo is running (`docker compose ps`)
2. ✅ Validate all required fields present
3. ✅ Check partner exists (for invoices)
4. ✅ Verify amount is positive and reasonable
5. ✅ Confirm currency matches company settings
6. ✅ Check for duplicate invoices (same partner + amount + date)

### Post-Execution Validation
1. ✅ Verify record created (check returned ID)
2. ✅ Log transaction details
3. ✅ Update task file with result
4. ✅ Move to appropriate folder (Done/ or Needs_Action/)
5. ✅ Notify if HITL approval needed

### Error Handling
- **Connection Failed:** Check if Odoo containers are running
- **Authentication Failed:** Verify credentials in .env
- **Partner Not Found:** Create partner first or use partner ID
- **Invalid Amount:** Must be positive number
- **Duplicate Invoice:** Check if invoice already exists

---

## Output Format

### Success
```markdown
---
status: completed
executed_at: 2026-03-30 17:00:00
odoo_record_id: 456
---

# Odoo Action Result

**Action:** create_invoice
**Status:** ✅ Success
**Record ID:** 456
**Executed At:** 2026-03-30 17:00:00

## Details
- Partner: ABC Corporation (ID: 123)
- Invoice Number: INV/2026/0456
- Amount: $5,000.00
- Status: Draft
- View in Odoo: http://localhost:8069/web#id=456&model=account.move

## Next Steps
- Invoice created in draft state
- Review in Odoo and confirm
- Send to customer when ready
```

### Failure
```markdown
---
status: failed
error: Partner not found
attempted_at: 2026-03-30 17:00:00
---

# Odoo Action Failed

**Action:** create_invoice
**Status:** ❌ Failed
**Error:** Partner "XYZ Corp" not found in Odoo

## Suggested Fix
1. Create partner first: `create_partner --name "XYZ Corp"`
2. Or use existing partner ID
3. Then retry invoice creation

## Original Request
[Include original data]
```

---

## Integration with Orchestrator

### Detection in approved_watcher.py
```python
def _determine_file_type(self, file_path: Path) -> str:
    # Check for odoo_action type
    if 'odoo' in filename.lower():
        return 'odoo_action'
    
    # Check content
    with open(file_path, 'r') as f:
        content = f.read()
        if 'type: odoo_action' in content or 'type: "odoo_action"' in content:
            return 'odoo_action'
```

### Execution in approved_watcher.py
```python
def _execute_odoo_action(self, file_path: str) -> bool:
    logger.info(f"[ODOO] Executing Odoo action: {file_path}")
    
    # Parse file to extract action and data
    # Call odoo_rpc.py with appropriate arguments
    # Handle success/failure
    # Update file with result
    # Move to Done/ or Needs_Action/
```

---

## Examples

### Example 1: Create Invoice from Email
**Email Received:**
```
From: client@abc.com
Subject: Invoice Request - March Consulting

Hi,

Please send invoice for:
- 40 hours software development @ $125/hr = $5,000
- 10 hours project management @ $150/hr = $1,500
Total: $6,500

Due date: April 15, 2026

Thanks!
```

**Generated Action File:** `Pending_Approval/odoo_invoice_abc_march.md`
```markdown
---
type: odoo_action
action: create_invoice
approved: false
priority: high
created: 2026-03-30 16:00:00
---

# Odoo Action: Create Invoice for ABC Corp

**Action:** create_invoice
**HITL Required:** yes (amount > $500)
**Reason:** Invoice amount $6,500 exceeds auto-approval threshold

## Data
- Partner: ABC Corporation
- Total Amount: 6500.00 USD
- Due Date: 2026-04-15
- Invoice Lines:
  1. Software Development: 40 hrs @ $125/hr = $5,000
  2. Project Management: 10 hrs @ $150/hr = $1,500

## Context
Email from client@abc.com requesting invoice for March consulting services.

## Approval
- [ ] Amount verified
- [ ] Partner confirmed
- [ ] Services delivered
- [ ] Ready to invoice

**Approve by moving to Approved/ folder**
```

### Example 2: Query Unpaid Invoices
**Task:** Check unpaid invoices for ABC Corp

**Action File:** `Approved/odoo_query_unpaid_abc.md`
```markdown
---
type: odoo_action
action: query_invoices
approved: true
priority: low
created: 2026-03-30 16:30:00
---

# Odoo Action: Query Unpaid Invoices

**Action:** query_invoices
**HITL Required:** no (read-only)

## Data
- Partner: ABC Corporation
- Status: unpaid
- Limit: 10
```

**Result:** `Done/odoo_query_unpaid_abc.md`
```markdown
---
status: completed
executed_at: 2026-03-30 16:31:00
---

# Odoo Query Result

**Action:** query_invoices
**Status:** ✅ Success

## Unpaid Invoices for ABC Corporation

1. **INV/2026/0123** - $2,500.00 (Due: 2026-03-15) - OVERDUE
2. **INV/2026/0234** - $5,000.00 (Due: 2026-04-01) - Due soon
3. **INV/2026/0345** - $1,200.00 (Due: 2026-04-15)

**Total Unpaid:** $8,700.00

## Recommended Actions
- Follow up on overdue invoice INV/2026/0123
- Send reminder for INV/2026/0234 (due in 2 days)
```

---

## Monitoring & Logs

### Log File
`Logs/odoo_rpc.log`

### Metrics to Track
- Total invoices created
- Total partners added
- Average invoice amount
- HITL approval rate
- Error rate
- Response time

### Alerts
- Odoo connection failures
- Authentication errors
- Duplicate invoice attempts
- Unusual amounts (very high/low)

---

## Troubleshooting

### Issue: Connection Refused
**Cause:** Odoo containers not running
**Fix:**
```bash
cd Gold-Tier/odoo-docker
docker compose ps  # Check status
docker compose up -d  # Start if stopped
```

### Issue: Authentication Failed
**Cause:** Wrong credentials or database not initialized
**Fix:**
1. Check `.env` file has correct credentials
2. Verify database exists: http://localhost:8069
3. Re-run initial setup if needed

### Issue: Partner Not Found
**Cause:** Partner doesn't exist in Odoo
**Fix:**
1. Create partner first: `--action create_partner`
2. Or search for existing partner: `--action list_partners`
3. Use correct partner ID

### Issue: Invalid Amount
**Cause:** Amount is negative, zero, or malformed
**Fix:**
1. Verify amount is positive number
2. Check currency format
3. Ensure no special characters

---

## Future Enhancements

### Phase 3 (Future)
- [ ] Automatic payment recording from bank feeds
- [ ] Invoice PDF generation and email attachment
- [ ] Recurring invoice automation
- [ ] Multi-currency support
- [ ] Tax calculation automation
- [ ] Expense tracking integration
- [ ] Financial report generation
- [ ] Budget vs actual tracking
- [ ] Cash flow forecasting

---

## Configuration

### Environment Variables (odoo-docker/.env)
```bash
ODOO_URL=http://localhost:8069
ODOO_DB_NAME=ai_employee_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password_2026
ODOO_MASTER_PASSWORD=master_password_2026
```

### Dependencies
- Python 3.8+
- requests library
- python-dotenv
- Odoo 19.0 (Docker)
- PostgreSQL 16 (Docker)

---

## Security Notes

1. **Credentials:** Never commit .env files to git
2. **Access Control:** Odoo user should have limited permissions
3. **Audit Trail:** All actions logged with timestamp and user
4. **HITL:** Financial actions require human approval
5. **Validation:** All inputs validated before execution
6. **Backups:** Regular database backups recommended

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier)  
**Dependencies:** Odoo 19.0, actions/odoo_rpc.py, approved_watcher.py
