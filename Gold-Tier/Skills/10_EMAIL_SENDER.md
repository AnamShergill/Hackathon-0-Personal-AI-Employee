# Skill: 10_EMAIL_SENDER

## Overview
This skill enables sending real outbound emails (replies, follow-ups, confirmations) through the AI Employee system. All emails require human approval via the HITL workflow before sending. This skill defines the format, rules, and execution process for email sending.

## Version
1.0 - Gold Tier Phase 1

## Purpose

Send professional outbound emails only after explicit human approval. This skill:
- Defines the format for email drafts ready to send
- Enforces strict HITL approval requirements
- Integrates with approved_watcher.py for automated sending
- Tracks sent emails and handles errors
- Maintains audit trail in Done/Sent/ folders

## When to Use

Use this skill when:
1. **Reply drafts are ready**: After 02_EMAIL_REPLY_DRAFTER.md creates a draft
2. **Follow-up needed**: Plan/task explicitly requires sending email
3. **Confirmation required**: Booking, meeting, order confirmations
4. **Status updates**: Project updates, delivery notifications
5. **Outreach**: Sales, networking (with extra HITL scrutiny)

**DO NOT use for**:
- Unsolicited bulk emails (spam)
- Emails without human approval
- Sensitive content without HITL review
- Automated responses to unknown senders

## Rules (STRICTLY ENFORCED)

### 1. Approval Requirements
- ✅ **MUST** be in `Approved/` folder
- ✅ **MUST** have `approved: true` in frontmatter OR human approval note
- ✅ **MUST** pass all safety checks before sending
- ❌ **NEVER** send directly from `Pending_Approval/` or `Plans/`

### 2. HITL Triggers (Flag for Human Review)
Automatically flag and move to `Pending_Approval/` if email contains:

**Financial Content**:
- Money amounts > $50 (any currency: $, €, £, Rs, PKR)
- Payment, invoice, transaction, refund mentions
- Banking, account, credit card information

**Legal/Sensitive Content**:
- Contract, agreement, terms, NDA mentions
- Legal, compliance, regulation language
- Confidential, proprietary, trade secret mentions
- Password, credentials, access codes

**Structural Concerns**:
- More than 4 recipients (To + CC combined)
- Attachments requested or mentioned
- External domains not in whitelist
- Reply-to address different from sender

**Content Flags**:
- Urgent/ASAP with money or legal content
- Requests for personal information
- Mentions of competitors
- Negative sentiment (complaints, disputes)

### 3. Tone and Style
- **Professional**: Business-appropriate language
- **Concise**: Clear and to the point
- **Consistent**: Match user's past email style
- **Polite**: Follow Company_Handbook.md politeness protocol
- **Accurate**: Verify all facts, dates, amounts

### 4. Post-Send Actions
After successful send:
1. Append send metadata to .md file
2. Update status to `sent`
3. Record timestamp and message ID
4. Move to `Done/` or `Sent/` folder
5. Update Dashboard.md with send count

After failed send:
1. Append error details to .md file
2. Update status to `error`
3. Move to `Pending_Approval/` or `Logs/email_errors/`
4. Alert human via Dashboard.md
5. Do NOT retry automatically

## Input Format

Email drafts ready for sending must have this frontmatter structure:

```yaml
---
type: "email_send"
to: "recipient@example.com"
subject: "Meeting Confirmation - March 25th"
from: "your.email@company.com"  # Optional, defaults to configured sender
cc: "manager@company.com, team@company.com"  # Optional
bcc: ""  # Optional, rarely used
reply_to: ""  # Optional, defaults to 'from'
priority: "normal"  # normal, high, low
approved: true  # REQUIRED for sending
approved_by: "Human Name"  # Optional but recommended
approved_at: "2026-03-21T18:00:00"  # ISO timestamp
original_message_id: "19d00c1b"  # If replying to specific email
thread_id: "thread_abc123"  # If part of conversation thread
---

# Email Draft - Meeting Confirmation

## To: recipient@example.com

## Subject: Meeting Confirmation - March 25th

## Body

Dear [Recipient Name],

Thank you for your email regarding the meeting on March 25th.

I can confirm the following details:
- Date: March 25, 2026
- Time: 2:00 PM EST
- Duration: 1 hour
- Location: Virtual (Zoom link to follow)

Please let me know if you need any changes to this schedule.

Best regards,
[Your Name]

---

## Metadata
- **Draft created**: 2026-03-21T17:30:00
- **Created by**: 02_EMAIL_REPLY_DRAFTER
- **Requires approval**: Yes
- **Safety checks**: Passed

## Approval Notes
[Human adds notes here before approving]
```

## Execution Flow

### Step 1: Draft Creation
Email processor (01, 02, or task) creates draft in `Pending_Approval/`:
- Filename: `email_send_[timestamp]_[recipient_hash].md`
- Contains all required frontmatter fields
- Body formatted and ready to send
- Safety checks noted

### Step 2: Human Review
Human reviews draft in `Pending_Approval/`:
1. Reads email content
2. Verifies recipient, subject, body
3. Checks for errors or improvements
4. Edits if needed
5. Adds `approved: true` to frontmatter
6. Moves file to `Approved/`

### Step 3: Automated Sending
`approved_watcher.py` detects file in `Approved/`:
1. Validates frontmatter has `approved: true`
2. Re-runs safety checks
3. Calls `python actions/email_sender.py --file <path>`
4. Waits for send confirmation
5. Processes result (success or error)

### Step 4: Post-Send Processing
On success, append to .md file:
```yaml
---
status: "sent"
sent_at: "2026-03-21T18:05:23"
message_id: "CABc123xyz@mail.gmail.com"
send_method: "gmail_api"
---

<COMPLETE>
Email sent successfully at 2026-03-21T18:05:23
Message ID: CABc123xyz@mail.gmail.com
Recipient: recipient@example.com
Subject: Meeting Confirmation - March 25th
</COMPLETE>
```

Move to `Done/` or `Sent/` folder.

On failure, append:
```yaml
---
status: "error"
error_at: "2026-03-21T18:05:23"
error_message: "SMTP connection failed: timeout"
retry_count: 0
---

<ERROR>
Email send failed at 2026-03-21T18:05:23
Error: SMTP connection failed: timeout
Action: Moved back to Pending_Approval/ for human review
</ERROR>
```

Move to `Pending_Approval/` with error note.

## Safety Checks

Before sending, verify:

### Required Fields
- [ ] `to` field present and valid email format
- [ ] `subject` field present and not empty
- [ ] `body` field present and not empty
- [ ] `approved: true` in frontmatter
- [ ] File is in `Approved/` folder

### Content Validation
- [ ] No money amounts > $50 (unless pre-approved)
- [ ] No legal/contract language (unless pre-approved)
- [ ] No sensitive personal information
- [ ] No suspicious links or attachments
- [ ] Recipient count ≤ 4 (unless pre-approved)

### Technical Validation
- [ ] Email addresses valid format
- [ ] Subject line < 200 characters
- [ ] Body < 50KB (reasonable size)
- [ ] No HTML injection attempts
- [ ] No script tags or malicious content

### Business Rules
- [ ] Recipient not in blocklist
- [ ] Sender domain matches configured domain
- [ ] Rate limit not exceeded (max 50/hour)
- [ ] Not duplicate of recently sent email
- [ ] Complies with Company_Handbook.md rules

## Example Workflow

### Example 1: Simple Reply

**Input** (in `Pending_Approval/email_send_20260321_180000_abc123.md`):
```yaml
---
type: "email_send"
to: "client@example.com"
subject: "Re: Project Status Inquiry"
approved: false
---

# Email Reply Draft

## Body

Hi [Client Name],

Thank you for your inquiry about the project status.

I'm happy to report that we're on track for the March 30th deadline. 
All major milestones have been completed, and we're currently in the 
testing phase.

I'll send a detailed status report by end of week.

Best regards,
[Your Name]
```

**Human Action**:
1. Reviews email
2. Changes `approved: false` to `approved: true`
3. Moves to `Approved/`

**System Action**:
1. `approved_watcher.py` detects file
2. Validates approval
3. Sends email via `actions/email_sender.py`
4. Appends send metadata
5. Moves to `Done/`

**Result**: Email sent, client receives reply, file archived.

### Example 2: Flagged for HITL

**Input** (draft mentions money):
```yaml
---
type: "email_send"
to: "vendor@example.com"
subject: "Invoice Payment Confirmation"
---

Body mentions: "Payment of $5,000 has been processed..."
```

**System Action**:
1. Email processor detects $5,000 (> $50 threshold)
2. Adds HITL flag: `requires_approval: true`
3. Adds note: `hitl_reason: "Financial amount > $50"`
4. Saves to `Pending_Approval/` (not `Approved/`)
5. Updates Dashboard with pending approval count

**Human Action**:
1. Reviews financial email carefully
2. Verifies payment details are correct
3. Adds approval note
4. Sets `approved: true`
5. Moves to `Approved/`

**System Action**:
1. Sends email with financial content
2. Archives with extra metadata
3. Logs financial email send

### Example 3: Send Failure

**Scenario**: Network error during send

**System Action**:
1. Attempts to send email
2. Catches exception: `SMTPServerDisconnected`
3. Appends error to .md file
4. Sets `status: error`
5. Moves back to `Pending_Approval/`
6. Updates Dashboard: "1 email failed to send"

**Human Action**:
1. Sees error notification in Dashboard
2. Reviews error details in .md file
3. Checks network/SMTP settings
4. Fixes issue
5. Re-approves email (moves to `Approved/` again)

**System Action**:
1. Retries send
2. Succeeds
3. Archives with retry note

## Integration Points

### With Other Skills
- **02_EMAIL_REPLY_DRAFTER**: Creates drafts → 10_EMAIL_SENDER sends them
- **01_EMAIL_PROCESSOR**: Identifies emails needing replies → triggers drafting
- **03_TASK_EXTRACTOR**: Extracts "send email" tasks → creates send drafts
- **05_DASHBOARD_UPDATER**: Tracks sent email counts and status

### With Watchers
- **approved_watcher.py**: Detects approved emails → triggers sending
- **gmail_watcher.py**: Monitors for replies to sent emails

### With Actions
- **actions/email_sender.py**: Actual sending implementation (Gmail API, SMTP, etc.)

## Dashboard Tracking

Update Dashboard.md with:
```markdown
## Email Activity (Last 24h)
- **Emails Sent**: 12
- **Pending Approval**: 3
- **Failed Sends**: 1
- **Success Rate**: 92%

## Recent Sent Emails
- [18:05] Meeting Confirmation → client@example.com ✅
- [17:30] Project Update → team@company.com ✅
- [16:45] Invoice Follow-up → vendor@example.com ❌ (retry pending)
```

## Error Handling

### Common Errors and Solutions

**Authentication Failed**:
- Check Gmail API credentials
- Verify OAuth token is valid
- Re-authenticate if needed

**Recipient Invalid**:
- Validate email format
- Check for typos
- Verify domain exists

**Rate Limit Exceeded**:
- Wait before retry
- Reduce send frequency
- Use batch sending if available

**Network Timeout**:
- Retry with exponential backoff
- Check internet connection
- Verify SMTP server is reachable

**Content Rejected**:
- Check for spam triggers
- Verify no blacklisted links
- Ensure proper formatting

## Security Considerations

1. **Credentials**: Never log email passwords or API keys
2. **Content**: Sanitize all user input before sending
3. **Recipients**: Validate all email addresses
4. **Rate Limiting**: Prevent abuse with send limits
5. **Audit Trail**: Log all send attempts with timestamps
6. **Encryption**: Use TLS for SMTP connections
7. **Privacy**: Respect GDPR and data protection laws

## Future Enhancements (Gold Tier+)

- **Templates**: Pre-approved email templates for common scenarios
- **Scheduling**: Send emails at specific times
- **A/B Testing**: Test different subject lines
- **Tracking**: Open rates, click rates (with consent)
- **Signatures**: Automatic signature insertion
- **Attachments**: Support for file attachments (with virus scanning)
- **Rich HTML**: HTML email templates
- **Internationalization**: Multi-language support

## Dependencies

- Python 3.13+
- Gmail API or SMTP library
- OAuth2 credentials (for Gmail)
- Company_Handbook.md (for rules)
- approved_watcher.py (for automation)
- actions/email_sender.py (for actual sending)

---

*Email Sender Skill - Gold Tier Phase 1*
*Enables safe, approved outbound email communication*
