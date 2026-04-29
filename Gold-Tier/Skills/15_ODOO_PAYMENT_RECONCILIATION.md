# Skill 15: Odoo Payment Reconciliation

## Purpose
Automatically detect payment notifications in incoming emails, extract payment details, match them with outstanding invoices in Odoo, and record payments after human approval. This skill ensures accurate financial record-keeping while maintaining strict HITL (Human-In-The-Loop) controls.

## When to Use
- Email contains payment confirmation or notification
- Keywords: "payment received", "paid invoice", "payment confirmation", "wire transfer", "ACH payment", "check received", "payment processed"
- Email references invoice numbers or amounts
- Bank notification emails about incoming payments
- Customer payment confirmations

## When NOT to Use
- Payment requests (not confirmations)
- Invoice creation emails
- Payment reminders
- Refund notifications (different workflow)
- Partial payment discussions (requires manual review)

---

## CRITICAL SAFETY RULES

### 🔴 MANDATORY HITL APPROVAL
1. **NEVER** record payments automatically
2. **ALWAYS** create action file in Pending_Approval/
3. **REQUIRE** human to move to Approved/ before execution
4. **VERIFY** payment details before recording
5. **LOG** all payment operations with full audit trail

### 🔴 FINANCIAL CONTROLS
1. Payment amount must match invoice amount (or be explicitly marked as partial)
2. Payment date must be reasonable (not future, not too old)
3. Invoice must exist and be in "not_paid" or "partial" state
4. Payment method must be valid
5. All discrepancies must be flagged for human review

### 🔴 MATCHING RULES
1. Exact invoice number match (highest confidence)
2. Amount + customer match (high confidence)
3. Amount + date range match (medium confidence)
4. Multiple matches → flag for human selection
5. No matches → flag for manual investigation

---

## Input Format

### Email Content
The skill processes emails containing payment information:

```
From: payments@bank.com
Subject: Payment Received - Invoice #INV/2026/0001

Dear Merchant,

We have received a payment of $3,750.00 from TechCorp Solutions Ltd.

Payment Details:
- Amount: $3,750.00
- Reference: INV/2026/0001
- Date: March 30, 2026
- Method: Wire Transfer
- Transaction ID: WT-2026-03-30-12345

The funds will be available in your account within 1-2 business days.

Best regards,
Payment Processing Team
```

---

## Extraction Logic

### 1. Payment Detection
Identify payment-related emails using keywords:
- "payment received"
- "payment confirmation"
- "paid invoice"
- "wire transfer received"
- "ACH payment"
- "check deposited"
- "payment processed"
- "funds received"

### 2. Data Extraction
Extract key payment details:

**Amount:**
- Pattern: `$X,XXX.XX` or `USD X,XXX.XX` or `Amount: X,XXX.XX`
- Validation: Must be positive number
- Format: Convert to float

**Invoice Reference:**
- Pattern: `INV/YYYY/XXXX` or `Invoice #XXXX` or `Ref: XXXX`
- Validation: Must match Odoo invoice naming pattern
- Multiple references: Extract all, flag for review

**Payment Date:**
- Pattern: `YYYY-MM-DD` or `Month DD, YYYY`
- Default: Email received date if not specified
- Validation: Not in future, not older than 90 days

**Payer/Customer:**
- Extract from email sender or body
- Match against Odoo partner names
- Validation: Must exist in Odoo

**Payment Method:**
- Keywords: "wire transfer", "ACH", "check", "credit card", "bank transfer"
- Default: "bank_transfer" if not specified
- Validation: Must be valid Odoo payment method

**Transaction ID:**
- Pattern: Any alphanumeric reference
- Optional but recommended for audit trail

---

## Matching Algorithm

### Step 1: Search Open Invoices
Query Odoo for invoices matching criteria:

```python
# Priority 1: Exact invoice number match
if invoice_reference:
    invoices = search_open_invoices(invoice_number=invoice_reference)
    if len(invoices) == 1:
        return invoices[0]  # High confidence match

# Priority 2: Amount + Customer match
if amount and customer:
    invoices = search_open_invoices(amount=amount, partner=customer)
    if len(invoices) == 1:
        return invoices[0]  # High confidence match
    elif len(invoices) > 1:
        return invoices  # Multiple matches - human selection required

# Priority 3: Amount only (within date range)
if amount:
    invoices = search_open_invoices(amount=amount, date_range=30_days)
    if len(invoices) == 1:
        return invoices[0]  # Medium confidence match
    elif len(invoices) > 1:
        return invoices  # Multiple matches - human selection required

# No match found
return None  # Flag for manual investigation
```

### Step 2: Confidence Scoring
Assign confidence level to each match:

- **Exact Match (95-100%)**: Invoice number + amount match
- **High Confidence (80-94%)**: Amount + customer + date range match
- **Medium Confidence (60-79%)**: Amount match only
- **Low Confidence (40-59%)**: Partial information match
- **No Match (0%)**: No matching invoices found

### Step 3: Multiple Match Handling
When multiple invoices match:

```markdown
## Multiple Invoice Matches Found

Payment Amount: $5,000.00
Customer: ABC Corp

Possible Matches:
1. INV/2026/0015 - $5,000.00 - Due: 2026-03-25 (5 days overdue) ⭐ RECOMMENDED
2. INV/2026/0018 - $5,000.00 - Due: 2026-04-05 (6 days remaining)
3. INV/2026/0020 - $5,000.00 - Due: 2026-04-10 (11 days remaining)

**Action Required:** Human must select correct invoice or investigate further.

**Recommendation:** Match #1 (oldest/overdue invoice) unless payment reference indicates otherwise.
```

---

## Output Format

### Action File: `odoo_payment_YYYYMMDD_HHMMSS.md`

```markdown
---
type: odoo_record_payment
source: email
priority: HIGH
requires_approval: true
created: 2026-03-30T19:30:00
---

# Payment Recording Action

## Payment Details

**Amount:** $3,750.00  
**Payment Date:** 2026-03-30  
**Payment Method:** Wire Transfer  
**Transaction ID:** WT-2026-03-30-12345  
**Reference:** INV/2026/0001  

## Customer Information

**Customer:** TechCorp Solutions Ltd  
**Customer ID:** 7 (Odoo Partner ID)  
**Email:** contact@techcorp.com  

## Invoice Match

**Match Confidence:** 98% (Exact invoice number + amount match)  
**Invoice Number:** INV/2026/0001  
**Invoice ID:** 2 (Odoo)  
**Invoice Amount:** $3,750.00  
**Invoice Status:** not_paid  
**Invoice Due Date:** 2026-04-15  

✅ **Perfect Match:** Payment amount matches invoice amount exactly.

## Proposed Action

Record payment of $3,750.00 against invoice INV/2026/0001 in Odoo.

**Payment Journal:** Bank (ID: 1)  
**Payment Type:** Inbound  
**Reconciliation:** Automatic (full payment)  

## Verification Checklist

- [x] Payment amount matches invoice amount
- [x] Invoice exists and is unpaid
- [x] Customer matches invoice customer
- [x] Payment date is reasonable
- [x] Payment method is valid
- [ ] **HUMAN APPROVAL REQUIRED**

## Execution

Once approved (moved to Approved/ folder), the system will:
1. Create payment record in Odoo
2. Link payment to invoice
3. Mark invoice as "paid"
4. Update customer account balance
5. Log transaction in audit trail
6. Move this file to Done/

## Safety Notes

⚠️ This action will modify financial records in Odoo.  
⚠️ Ensure all details are correct before approval.  
⚠️ Payment cannot be easily reversed once recorded.  

---

**Original Email:** email_20260330_193000_payment.md  
**Extracted By:** 15_ODOO_PAYMENT_RECONCILIATION  
**Created:** 2026-03-30 19:30:00  
**Status:** Pending Human Approval
```

---

## Odoo Integration

### Functions Required

#### 1. Search Open Invoices
```python
def search_open_invoices(
    invoice_number: str = None,
    amount: float = None,
    partner_id: int = None,
    date_from: str = None,
    date_to: str = None
) -> List[Dict]:
    """
    Search for open (unpaid/partially paid) invoices in Odoo.
    
    Returns list of matching invoices with details.
    """
```

#### 2. Create Payment
```python
def create_payment(
    amount: float,
    payment_date: str,
    partner_id: int,
    payment_method: str = 'bank_transfer',
    reference: str = None,
    journal_id: int = 1  # Bank journal
) -> int:
    """
    Create a payment record in Odoo.
    
    Returns payment ID.
    """
```

#### 3. Reconcile Payment with Invoice
```python
def reconcile_payment(
    payment_id: int,
    invoice_id: int
) -> bool:
    """
    Link payment to invoice and mark as paid/partially paid.
    
    Returns True if successful.
    """
```

---

## Workflow

### End-to-End Flow

```
1. Email Arrives
   ↓
2. Gmail Watcher → Needs_Action/email_*.md
   ↓
3. Main Orchestrator → Routes to Email Processor
   ↓
4. Email Processor → Detects payment keywords
   ↓
5. Payment Reconciliation Skill (THIS SKILL)
   ├─ Extract payment details
   ├─ Search Odoo for matching invoices
   ├─ Calculate match confidence
   ├─ Generate action file
   └─ Save to Pending_Approval/odoo_payment_*.md
   ↓
6. HUMAN REVIEW
   ├─ Verify payment details
   ├─ Confirm invoice match
   ├─ Check for discrepancies
   └─ Move to Approved/ if correct
   ↓
7. Approved Watcher → Detects odoo_record_payment
   ↓
8. Odoo RPC Client
   ├─ Create payment record
   ├─ Link to invoice
   ├─ Mark invoice as paid
   └─ Log transaction
   ↓
9. Success
   ├─ Update action file with result
   ├─ Move to Done/
   └─ Update Dashboard
```

---

## Edge Cases & Handling

### Case 1: Partial Payment
```markdown
**Payment Amount:** $2,000.00  
**Invoice Amount:** $5,000.00  
**Difference:** -$3,000.00 (Partial payment)

⚠️ **Partial Payment Detected**

Action: Record as partial payment, invoice remains in "partial" state.
Remaining balance: $3,000.00
```

### Case 2: Overpayment
```markdown
**Payment Amount:** $5,500.00  
**Invoice Amount:** $5,000.00  
**Difference:** +$500.00 (Overpayment)

⚠️ **Overpayment Detected**

Possible reasons:
- Payment includes multiple invoices
- Customer error
- Currency conversion difference

Action Required: Human must investigate and decide how to allocate excess.
```

### Case 3: No Invoice Match
```markdown
**Payment Amount:** $1,234.56  
**Customer:** Unknown Corp  
**Reference:** PAYMENT-2026-03

❌ **No Matching Invoice Found**

Possible reasons:
- Invoice not yet created in Odoo
- Reference number incorrect
- Payment for non-invoiced service
- Wrong customer identification

Action Required: Human must manually match or create invoice first.
```

### Case 4: Multiple Matches
```markdown
**Payment Amount:** $1,000.00  
**Customer:** ABC Corp

⚠️ **Multiple Invoices Match**

Found 3 invoices:
1. INV/2026/0010 - $1,000.00 - Due: 2026-03-20 (10 days overdue) ⭐
2. INV/2026/0012 - $1,000.00 - Due: 2026-04-01 (2 days remaining)
3. INV/2026/0015 - $1,000.00 - Due: 2026-04-10 (11 days remaining)

Recommendation: Apply to oldest invoice (INV/2026/0010) unless specified otherwise.

Action Required: Human must select correct invoice.
```

### Case 5: Currency Mismatch
```markdown
**Payment Amount:** €3,200.00 (EUR)  
**Invoice Amount:** $3,750.00 (USD)  
**Exchange Rate:** 1 EUR = 1.17 USD  
**Converted Amount:** $3,744.00

⚠️ **Currency Conversion Required**

Difference: -$6.00 (within acceptable range)

Action: Record payment with currency conversion note.
```

---

## Integration with Email Processor

### Detection in 12_EMAIL_TO_ODOO_EXTRACTOR.md

Add payment detection logic:

```python
def detect_content_type(email_content: str) -> str:
    """Detect if email is invoice, payment, or other"""
    
    payment_keywords = [
        'payment received', 'payment confirmation', 'paid invoice',
        'wire transfer received', 'ach payment', 'check deposited',
        'payment processed', 'funds received', 'payment successful'
    ]
    
    invoice_keywords = [
        'invoice attached', 'please find invoice', 'billing statement',
        'purchase order', 'quote', 'proposal'
    ]
    
    content_lower = email_content.lower()
    
    # Check for payment
    if any(keyword in content_lower for keyword in payment_keywords):
        return 'payment'
    
    # Check for invoice
    if any(keyword in content_lower for keyword in invoice_keywords):
        return 'invoice'
    
    return 'other'
```

---

## Testing

### Test Case 1: Perfect Match
```markdown
Email: "Payment of $3,750.00 received for Invoice INV/2026/0001"
Expected: Single match, 98% confidence, auto-suggest
```

### Test Case 2: Amount Match Only
```markdown
Email: "Received $5,000.00 from ABC Corp"
Expected: Multiple matches if multiple $5K invoices exist
```

### Test Case 3: No Match
```markdown
Email: "Payment of $999.99 received"
Expected: No match found, flag for manual review
```

### Test Case 4: Partial Payment
```markdown
Email: "Partial payment of $2,000.00 for Invoice INV/2026/0005 ($5,000.00 total)"
Expected: Partial payment action, remaining balance calculated
```

---

## Audit Trail

Every payment operation must log:

```json
{
  "timestamp": "2026-03-30T19:30:00Z",
  "action": "payment_recorded",
  "payment_id": 15,
  "invoice_id": 2,
  "amount": 3750.00,
  "currency": "USD",
  "partner_id": 7,
  "partner_name": "TechCorp Solutions Ltd",
  "payment_method": "bank_transfer",
  "reference": "INV/2026/0001",
  "transaction_id": "WT-2026-03-30-12345",
  "approved_by": "human",
  "approved_at": "2026-03-30T19:35:00Z",
  "executed_by": "approved_watcher",
  "executed_at": "2026-03-30T19:35:15Z",
  "status": "success",
  "invoice_status_before": "not_paid",
  "invoice_status_after": "paid"
}
```

---

## Error Handling

### Odoo Connection Failed
```markdown
❌ **Error:** Cannot connect to Odoo

Action: Retry connection, if fails move to Needs_Action/ with error note.
```

### Payment Creation Failed
```markdown
❌ **Error:** Payment record creation failed in Odoo

Reason: [Odoo error message]

Action: Log error, move to Needs_Action/ for manual processing.
```

### Reconciliation Failed
```markdown
⚠️ **Warning:** Payment created but reconciliation failed

Payment ID: 15 (created successfully)
Invoice ID: 2 (reconciliation failed)

Action: Payment exists in Odoo but not linked to invoice.
Human must manually reconcile in Odoo interface.
```

---

## Success Indicators

✅ Payment detected in email  
✅ Payment details extracted accurately  
✅ Invoice match found with high confidence  
✅ Action file created in Pending_Approval/  
✅ Human reviewed and approved  
✅ Payment recorded in Odoo successfully  
✅ Invoice marked as paid  
✅ Audit trail logged  
✅ File moved to Done/  

---

## Configuration

### Settings
```python
PAYMENT_CONFIG = {
    'require_approval': True,  # NEVER set to False
    'min_confidence_auto_match': 95,  # Minimum confidence for auto-suggestion
    'max_payment_age_days': 90,  # Reject payments older than 90 days
    'allow_partial_payments': True,
    'allow_overpayments': False,  # Flag overpayments for review
    'default_payment_journal': 1,  # Bank journal ID
    'default_payment_method': 'bank_transfer',
    'currency_tolerance': 10.00,  # Allow $10 difference for currency conversion
}
```

---

## Dependencies

- **Odoo RPC Client** (`actions/odoo_rpc.py`)
- **Email Processor** (`Skills/12_EMAIL_TO_ODOO_EXTRACTOR.md`)
- **Approved Watcher** (`Watchers/approved_watcher.py`)
- **Main Orchestrator** (`Skills/00_MAIN_ORCHESTRATOR.md`)

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier Phase 5)  
**Safety Level:** CRITICAL (Financial Operations)  
**HITL Required:** MANDATORY
