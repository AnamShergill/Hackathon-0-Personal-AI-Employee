# Skill 12: Email to Odoo Extractor

## Purpose
Analyze incoming emails to detect and extract accounting-related information (invoices, quotes, purchase orders, client onboarding) and prepare structured data for Odoo record creation with mandatory HITL approval.

## When to Use
- Email subject/body contains: invoice, billing, payment, quote, purchase order, PO, client onboarding
- Email mentions amounts, prices, or financial terms
- Email requests invoice generation
- Email contains client/vendor information for accounting
- Email discusses payment terms, due dates, or financial transactions

## When NOT to Use
- General correspondence without financial content
- Simple questions or status updates
- Internal team communication
- Emails already processed by other skills
- Non-business emails

---

## Detection Keywords

### High Priority (Always Extract)
- invoice, billing, bill, payment
- quote, quotation, estimate
- purchase order, PO, order confirmation
- amount, total, price, cost
- due date, payment terms
- client onboarding, new customer

### Medium Priority (Check Context)
- services rendered, consulting fees
- project cost, budget
- subscription, recurring payment
- deposit, advance payment

### Low Priority (May be Accounting)
- contract, agreement (if mentions money)
- proposal (if includes pricing)

---

## Extraction Logic

### 1. Document Type Detection
Analyze email to determine type:
- **Invoice Request:** "Please send invoice", "invoice for", "bill us for"
- **Quote Request:** "quote for", "how much for", "pricing for"
- **Purchase Order:** "PO #", "purchase order", "order confirmation"
- **Client Onboarding:** "new client", "onboard", "setup account"
- **Payment Notification:** "payment received", "paid invoice"

### 2. Partner (Customer/Vendor) Extraction
Extract from email:
- **Name:** Company name or person name
  - Look in: From field, email signature, body text
  - Patterns: "From: [Name]", "[Name] Inc", "[Name] Corporation"
- **Email:** Sender email address
- **Phone:** Phone numbers in signature or body
  - Patterns: +XX-XXX-XXXXXXX, (XXX) XXX-XXXX
- **Type:** Company or Individual
  - Company if: Inc, Corp, LLC, Ltd, Company, Organization
  - Individual otherwise

### 3. Invoice Data Extraction
Extract financial details:
- **Invoice Number:** "Invoice #123", "INV-2026-001", "Bill #"
- **Date:** Email date or mentioned date
- **Due Date:** "Due: [date]", "Payment by [date]", "Net 30"
- **Amount:** "$1,500", "PKR 50,000", "1500.00 USD"
- **Currency:** USD, PKR, EUR, GBP (default: USD)
- **Description:** Service description or product name

### 4. Line Items Extraction
Parse itemized lists:
```
- Consulting: 10 hours @ $150/hr = $1,500
- Development: 20 hours @ $125/hr = $2,500
- Project Management: 5 hours @ $200/hr = $1,000
Total: $5,000
```

Extract:
- Description: "Consulting", "Development"
- Quantity: 10, 20, 5
- Unit Price: $150, $125, $200
- Subtotal: $1,500, $2,500, $1,000

### 5. Payment Terms
- **Net 30:** Due in 30 days
- **Net 15:** Due in 15 days
- **Due on receipt:** Immediate
- **Specific date:** "Due: April 15, 2026"

---

## Output Format

### Create Action File in Pending_Approval/

**Filename:** `odoo_invoice_[partner]_[date].md` or `odoo_partner_[name]_[date].md`

**Structure:**
```markdown
---
type: odoo_action
action: create_invoice
approved: false
priority: high
created: YYYY-MM-DD HH:MM:SS
source_email: [email_id or filename]
---

# Odoo Action: Create Invoice for [Partner Name]

**Action:** create_invoice
**HITL Required:** yes (financial transaction)
**Reason:** Invoice amount $[amount] requires human approval

## Partner Information
- Name: [Company/Person Name]
- Email: [email@domain.com]
- Phone: [+XX-XXX-XXXXXXX]
- Type: [Company|Individual]
- Existing Partner ID: [ID if found, or "NEW" if needs creation]

## Invoice Details
- Invoice Number: [INV-XXX or "Auto"]
- Invoice Date: [YYYY-MM-DD]
- Due Date: [YYYY-MM-DD]
- Currency: [USD|PKR|EUR]
- Payment Terms: [Net 30|Net 15|Immediate]

## Line Items
1. [Description]: [Qty] x $[Price] = $[Subtotal]
2. [Description]: [Qty] x $[Price] = $[Subtotal]

**Total Amount:** $[Total]

## Original Email Content
```
[Relevant excerpt from email]
```

## Approval Checklist
- [ ] Partner information verified
- [ ] Amount and line items correct
- [ ] Due date appropriate
- [ ] Services/products delivered or agreed
- [ ] Ready to create invoice in Odoo

## Instructions
To approve:
1. Review all details above
2. Check partner exists in Odoo (or will be created)
3. Verify amount and line items
4. Move this file to Approved/ folder

To reject:
1. Add rejection reason below
2. Move to Needs_Action/ for revision
```

---

## Extraction Examples

### Example 1: Simple Invoice Request

**Email:**
```
From: john@acmecorp.com
Subject: Invoice Request - March Consulting

Hi,

Please send invoice for March consulting services:
- 40 hours @ $125/hour = $5,000

Due: April 15, 2026

Thanks,
John Smith
Acme Corporation
+1-555-123-4567
```

**Extracted Data:**
```markdown
---
type: odoo_action
action: create_invoice
approved: false
priority: high
source_email: email_20260330_123456_abc123.md
---

# Odoo Action: Create Invoice for Acme Corporation

**Action:** create_invoice
**HITL Required:** yes (amount $5,000 > $500 threshold)

## Partner Information
- Name: Acme Corporation
- Email: john@acmecorp.com
- Phone: +1-555-123-4567
- Type: Company
- Existing Partner ID: NEW (needs creation)

## Invoice Details
- Invoice Number: Auto
- Invoice Date: 2026-03-30
- Due Date: 2026-04-15
- Currency: USD
- Payment Terms: Net 15

## Line Items
1. March Consulting Services: 40 hours x $125.00 = $5,000.00

**Total Amount:** $5,000.00

## Original Email Content
```
Please send invoice for March consulting services:
- 40 hours @ $125/hour = $5,000
Due: April 15, 2026
```
```

### Example 2: Detailed Invoice with Multiple Items

**Email:**
```
From: billing@techstart.io
Subject: Invoice for Q1 2026 Services

Please invoice us for Q1 services:

1. Software Development: 80 hours @ $150/hr = $12,000
2. UI/UX Design: 20 hours @ $100/hr = $2,000
3. Project Management: 15 hours @ $125/hr = $1,875

Subtotal: $15,875
Tax (5%): $793.75
Total: $16,668.75

Payment terms: Net 30
PO Number: PO-2026-Q1-001

Best regards,
Sarah Johnson
TechStart Inc.
sarah@techstart.io
+92-321-7654321
```

**Extracted Data:**
```markdown
---
type: odoo_action
action: create_invoice
approved: false
priority: high
source_email: email_20260330_140000_xyz789.md
---

# Odoo Action: Create Invoice for TechStart Inc

**Action:** create_invoice
**HITL Required:** yes (amount $16,668.75 > $500 threshold)

## Partner Information
- Name: TechStart Inc
- Email: sarah@techstart.io
- Phone: +92-321-7654321
- Type: Company
- Existing Partner ID: NEW (needs creation)

## Invoice Details
- Invoice Number: Auto
- Invoice Date: 2026-03-30
- Due Date: 2026-04-30 (Net 30)
- Currency: USD
- Payment Terms: Net 30
- Reference: PO-2026-Q1-001

## Line Items
1. Software Development: 80 hours x $150.00 = $12,000.00
2. UI/UX Design: 20 hours x $100.00 = $2,000.00
3. Project Management: 15 hours x $125.00 = $1,875.00

**Subtotal:** $15,875.00
**Tax (5%):** $793.75
**Total Amount:** $16,668.75

## Original Email Content
```
Please invoice us for Q1 services:
1. Software Development: 80 hours @ $150/hr = $12,000
2. UI/UX Design: 20 hours @ $100/hr = $2,000
3. Project Management: 15 hours @ $125/hr = $1,875
Total: $16,668.75
Payment terms: Net 30
```
```

### Example 3: New Client Onboarding

**Email:**
```
From: contact@newclient.com
Subject: New Client Setup

Hi,

We'd like to start working with you. Here's our information:

Company: NewClient Solutions Ltd
Contact: Michael Brown
Email: contact@newclient.com
Phone: +92-300-9876543
Address: 123 Business St, Karachi

Please set us up in your system.

Thanks!
```

**Extracted Data:**
```markdown
---
type: odoo_action
action: create_partner
approved: false
priority: medium
source_email: email_20260330_150000_def456.md
---

# Odoo Action: Create New Customer - NewClient Solutions

**Action:** create_partner
**HITL Required:** yes (new customer creation)

## Partner Information
- Name: NewClient Solutions Ltd
- Contact Person: Michael Brown
- Email: contact@newclient.com
- Phone: +92-300-9876543
- Address: 123 Business St, Karachi
- Type: Company
- Customer: Yes
- Vendor: No

## Context
New client requesting setup in accounting system.
No immediate invoice, just partner record creation.

## Approval Checklist
- [ ] Company name verified
- [ ] Contact information validated
- [ ] Credit terms discussed (if applicable)
- [ ] Ready to onboard

## Instructions
Approve by moving to Approved/ folder.
This will create the partner record in Odoo.
```

---

## Integration with Orchestrator

### In 00_MAIN_ORCHESTRATOR.md

Add after email processing and task extraction:

```markdown
## Step 4: Check for Accounting Content

After extracting tasks and drafting replies, check if email contains accounting information:

**Trigger Keywords:**
- invoice, billing, payment, quote
- purchase order, PO
- client onboarding, new customer
- amount, price, cost, total

**If detected:**
1. Call Skill 12: EMAIL_TO_ODOO_EXTRACTOR
2. Extract structured data
3. Create action file in Pending_Approval/
4. Flag for HITL approval
5. Continue with normal email processing
```

### Detection Logic
```python
def is_accounting_email(email_content: str) -> bool:
    """Check if email contains accounting information"""
    keywords = [
        'invoice', 'billing', 'bill', 'payment',
        'quote', 'quotation', 'estimate',
        'purchase order', 'po #', 'po number',
        'client onboarding', 'new customer',
        'amount', 'total', 'price', 'cost',
        'due date', 'payment terms'
    ]
    
    content_lower = email_content.lower()
    return any(keyword in content_lower for keyword in keywords)
```

---

## HITL (Human-in-the-Loop) Rules

### ALWAYS Require Approval
1. **All financial record creation**
   - Creating invoices (any amount)
   - Creating quotes
   - Recording purchase orders
   - Creating new partners with financial implications

2. **Data Validation Required**
   - Extracted amounts need verification
   - Partner details need confirmation
   - Line items need review
   - Due dates need approval

3. **Security & Compliance**
   - Financial data accuracy critical
   - Legal implications of invoices
   - Customer relationship management
   - Audit trail requirements

### Never Auto-Execute
- ❌ Creating invoices without approval
- ❌ Creating partners without review
- ❌ Modifying existing financial records
- ❌ Posting invoices (always draft)
- ❌ Recording payments

### Safe Operations (Still Require HITL)
- ✅ Creating draft invoices (not posted)
- ✅ Creating partner records (can be edited)
- ✅ Extracting data (no Odoo changes)

---

## Extraction Patterns

### Amount Patterns
```regex
\$\d+[,\d]*\.?\d*
PKR\s*\d+[,\d]*\.?\d*
\d+[,\d]*\.?\d*\s*(USD|PKR|EUR|GBP)
Total:\s*\$?\d+[,\d]*\.?\d*
```

### Date Patterns
```regex
\d{4}-\d{2}-\d{2}
\d{1,2}/\d{1,2}/\d{4}
(January|February|...|December)\s+\d{1,2},?\s+\d{4}
Due:\s*[date]
Net\s+(\d+)  # Net 30 = 30 days from invoice date
```

### Line Item Patterns
```regex
-\s*(.+?):\s*(\d+)\s*(hours?|units?|pcs?)?\s*@\s*\$?(\d+\.?\d*)\s*=\s*\$?(\d+\.?\d*)
\d+\.\s*(.+?):\s*(\d+)\s*x\s*\$?(\d+\.?\d*)\s*=\s*\$?(\d+\.?\d*)
```

### Contact Patterns
```regex
Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})
Phone:\s*(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})
```

---

## Workflow

### Step 1: Email Arrives
- Gmail watcher detects new email
- Creates file in Needs_Action/

### Step 2: Orchestrator Processes
- 01_EMAIL_PROCESSOR analyzes email
- 03_TASK_EXTRACTOR identifies tasks
- **12_EMAIL_TO_ODOO_EXTRACTOR checks for accounting content**

### Step 3: Data Extraction
If accounting content detected:
1. Determine document type (invoice, quote, PO, partner)
2. Extract partner information
3. Extract financial details
4. Extract line items
5. Calculate totals
6. Determine due dates

### Step 4: Create Action File
- Generate structured action file
- Save to Pending_Approval/
- Flag as HIGH priority
- Include all extracted data
- Add approval checklist

### Step 5: HITL Review
- Human reviews extracted data
- Verifies amounts and details
- Checks partner information
- Approves or rejects

### Step 6: Execution
- If approved: Move to Approved/
- approved_watcher detects odoo_action
- Calls actions/odoo_rpc.py
- Creates draft record in Odoo
- Moves to Done/ with result

### Step 7: Verification
- Human verifies record in Odoo
- Edits if needed in Odoo UI
- Posts invoice when ready
- Sends to customer

---

## Error Handling

### Incomplete Data
If extraction incomplete:
```markdown
## Extraction Status
- Partner Name: ✅ Found
- Email: ✅ Found
- Amount: ❌ NOT FOUND - Please add manually
- Line Items: ⚠️  Partial - Review and complete

**Action Required:** Human must complete missing data before approval
```

### Ambiguous Data
If multiple interpretations possible:
```markdown
## Data Ambiguity Warning
- Found 2 possible amounts: $1,500 and $2,000
- Found 2 possible due dates: April 15 and April 30

**Action Required:** Human must select correct values
```

### Partner Matching
If partner might already exist:
```markdown
## Partner Matching
- Extracted: "Acme Corp"
- Possible matches in Odoo:
  - ID 15: Acme Corporation (acme@corp.com)
  - ID 23: ACME Corp Ltd (info@acme.com)

**Action Required:** Select existing partner or create new
```

---

## Integration Points

### With Email Processor (Skill 01)
- Receives processed email data
- Gets sender, subject, body
- Accesses email metadata

### With Task Extractor (Skill 03)
- Coordinates task identification
- Shares extracted information
- Avoids duplicate processing

### With Odoo RPC (actions/odoo_rpc.py)
- Provides structured data
- Calls appropriate RPC methods
- Handles responses

### With Approved Watcher
- Creates files in standard format
- Uses consistent naming
- Includes all required metadata

---

## Quality Checks

### Before Creating Action File
1. ✅ At least one financial keyword detected
2. ✅ Partner name extracted (or email sender available)
3. ✅ Amount extracted (or line items present)
4. ✅ Document type determined
5. ✅ No duplicate action file exists

### Data Validation
1. ✅ Amount is positive number
2. ✅ Email format is valid
3. ✅ Phone format is reasonable
4. ✅ Date is valid and not in past (for due dates)
5. ✅ Currency is supported

### Confidence Scoring
- **High Confidence (90-100%):** All key fields extracted, clear invoice request
- **Medium Confidence (70-89%):** Most fields extracted, some ambiguity
- **Low Confidence (50-69%):** Partial extraction, significant gaps

**Rule:** Only create action file if confidence > 70%

---

## Examples of Emails to Process

### ✅ Should Extract
1. "Please invoice us for 10 hours of consulting at $150/hr"
2. "Send me a quote for the project we discussed"
3. "Here's our PO #12345 for $5,000"
4. "New client setup: ABC Corp, contact@abc.com"
5. "Bill for March services: $2,500"

### ❌ Should NOT Extract
1. "Thanks for your email" (no financial content)
2. "Meeting scheduled for tomorrow" (no accounting)
3. "How are you?" (general correspondence)
4. "Project update: 50% complete" (status, not billing)
5. "Can we reschedule?" (no financial content)

---

## Logging & Monitoring

### Log Each Extraction
```
[2026-03-30 17:00:00] EMAIL_TO_ODOO: Detected accounting email
[2026-03-30 17:00:01] EMAIL_TO_ODOO: Document type: invoice_request
[2026-03-30 17:00:01] EMAIL_TO_ODOO: Partner: Acme Corp (NEW)
[2026-03-30 17:00:01] EMAIL_TO_ODOO: Amount: $5,000.00 USD
[2026-03-30 17:00:01] EMAIL_TO_ODOO: Confidence: 95%
[2026-03-30 17:00:02] EMAIL_TO_ODOO: Created: Pending_Approval/odoo_invoice_acme_20260330.md
```

### Metrics to Track
- Total emails scanned
- Accounting emails detected
- Extraction success rate
- Confidence score distribution
- HITL approval rate
- Invoices created in Odoo
- Average extraction time

---

## Testing

### Test Cases

**Test 1: Simple Invoice**
```
Email: "Invoice for $500 consulting"
Expected: Extract amount, create action file
```

**Test 2: Detailed Invoice**
```
Email: Multi-line invoice with items
Expected: Extract all line items, calculate total
```

**Test 3: New Client**
```
Email: Client onboarding with contact info
Expected: Extract partner data, create partner action
```

**Test 4: Ambiguous Email**
```
Email: Mentions "invoice" but no clear amount
Expected: Low confidence, request human clarification
```

**Test 5: Non-Accounting Email**
```
Email: General question, no financial content
Expected: Skip extraction, process normally
```

---

## Future Enhancements

### Phase 3
- [ ] OCR for invoice attachments (PDF, images)
- [ ] Multi-currency conversion
- [ ] Automatic partner matching (fuzzy search)
- [ ] Tax calculation based on location
- [ ] Recurring invoice detection
- [ ] Payment link generation
- [ ] Invoice PDF generation and email

### Phase 4
- [ ] Machine learning for better extraction
- [ ] Confidence score improvement
- [ ] Multi-language support
- [ ] Integration with bank feeds
- [ ] Automatic payment reconciliation

---

## Configuration

### Environment Variables
```bash
# In odoo-docker/.env
ODOO_URL=http://localhost:8069
ODOO_DB_NAME=ai_employee_db
ODOO_USERNAME=pinkyshergill1986@gmail.com
ODOO_PASSWORD=anamthecoder

# Thresholds
INVOICE_AUTO_APPROVE_THRESHOLD=100  # USD
HITL_REQUIRED_THRESHOLD=500  # USD
```

### Extraction Settings
```python
# In extraction logic
MIN_CONFIDENCE_SCORE = 70  # Minimum to create action file
MAX_LINE_ITEMS = 50  # Maximum line items to extract
DEFAULT_CURRENCY = "USD"
DEFAULT_PAYMENT_TERMS = "Net 30"
```

---

## Security & Compliance

### Data Privacy
- Email content stored locally only
- No external API calls for extraction
- Sensitive data in Pending_Approval/ (not public)
- HITL review before Odoo creation

### Audit Trail
- All extractions logged
- Original email preserved
- Action files timestamped
- Odoo records linked to source email

### Access Control
- Only approved users can move to Approved/
- Odoo access restricted to admin
- Financial data requires authentication

---

## Troubleshooting

### Issue: No Data Extracted
**Cause:** Email doesn't contain clear financial information
**Fix:** 
- Check if keywords present
- Review email format
- May need manual data entry

### Issue: Wrong Amount Extracted
**Cause:** Multiple amounts in email, wrong one selected
**Fix:**
- Human reviews in Pending_Approval/
- Corrects amount before approval
- Extraction logic learns from patterns

### Issue: Partner Not Found
**Cause:** New customer, not in Odoo yet
**Fix:**
- Action file includes partner creation
- Creates partner first, then invoice
- Links automatically

### Issue: Duplicate Invoice
**Cause:** Same email processed twice
**Fix:**
- Check source_email field
- Skip if already processed
- Log duplicate detection

---

## Success Indicators

✅ Accounting emails detected automatically  
✅ Data extracted with >70% confidence  
✅ Action files created in Pending_Approval/  
✅ Human reviews and approves  
✅ Records created in Odoo successfully  
✅ Files moved to Done/ with results  
✅ No manual data entry needed  
✅ Audit trail maintained

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier)  
**Dependencies:** 01_EMAIL_PROCESSOR, 11_ODOO_ACCOUNTING, actions/odoo_rpc.py
