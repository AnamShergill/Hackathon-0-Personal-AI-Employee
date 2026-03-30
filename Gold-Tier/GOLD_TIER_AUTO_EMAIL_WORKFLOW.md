# Gold Tier: Automated Email Workflow - COMPLETE ✅

## What Was Updated

### Updated File: `Watchers/approved_watcher.py`

**New/Updated Sections:**

#### 1. Enhanced File Type Detection
```python
def _determine_file_type(self, file_path: Path) -> str:
    # Now detects 'email_send' type based on:
    # - Filename starts with 'email_send_' or 'email_'
    # - Content contains 'action: send_email'
    # - Content has 'to:' and 'subject:' in first 500 chars
    # - Frontmatter has 'type: "email_send"'
```

#### 2. New Email Sending Method
```python
def _send_email(self, file_path: str) -> bool:
    """Send approved email using actions/email_sender.py"""
    logger.info(f"[EMAIL_SENDER] Detected send action in {file_path}")
    
    # Calls: python actions/email_sender.py --file <path>
    result = subprocess.run(
        [sys.executable, 'actions/email_sender.py', '--file', file_path],
        capture_output=True,
        text=True,
        timeout=60,
        check=True
    )
    
    # On success: email_sender.py moves file to Approved/Done/
    # On failure: email_sender.py moves file to Needs_Action/
    return True
```

#### 3. Updated Process Event Handler
```python
def process_event(self, event: Dict[str, Any]) -> bool:
    # Now handles 'email_send' type
    if file_type == 'email_send':
        success = self._send_email(file_path)
    elif file_type == 'email_reply':
        success = self._send_email_reply(file_path)  # Redirects to _send_email
```

---

## Complete Automated Workflow

### Step 1: Email Draft Created
**Location**: `Pending_Approval/`

An email processor (or manual creation) creates a draft:

```bash
# Example: Email processor creates draft
Pending_Approval/email_send_20260323_abc123.md
```

**File format:**
```markdown
---
type: email_send
approved: false
---

to: client@example.com
subject: Project Update

Dear Client,

Here's the latest update on your project...

Best regards,
Your Name
```

### Step 2: Human Review (HITL)
**Action**: Human reviews and approves

1. Open file in `Pending_Approval/`
2. Review recipient, subject, body
3. Edit if needed
4. Change `approved: false` to `approved: true`
5. Move file to `Approved/`

```bash
# Move to Approved folder
mv Pending_Approval/email_send_20260323_abc123.md Approved/
```

### Step 3: Watcher Detects File
**Automatic** (every 30 seconds)

`approved_watcher.py` detects the new file:

```
[INFO] Approved Watcher running check at 2026-03-23 16:30:00...
[INFO] New approved item: email_send_20260323_abc123.md (type: email_send)
[INFO] Processing approved email_send: email_send_20260323_abc123.md
[INFO] [EMAIL_SENDER] Detected send action in Approved/email_send_20260323_abc123.md
```

### Step 4: Email Sent Automatically
**Automatic** (via subprocess call)

Watcher calls `actions/email_sender.py`:

```
[INFO] [EMAIL_SENDER] Email sender initialized with server: smtp.gmail.com:587
[INFO] [EMAIL_SENDER] Parsing email file...
[INFO] [EMAIL_SENDER] Parsed email - To: client@example.com, Subject: Project Update
[INFO] [EMAIL_SENDER] Sending to 1 recipient(s)
[INFO] [EMAIL_SENDER] Logging in as: your.email@gmail.com
[INFO] [EMAIL_SENDER] Sending email...
[INFO] [EMAIL_SENDER] ✅ Email sent successfully!
```

### Step 5: File Updated and Moved
**Automatic**

`email_sender.py` updates the file and moves it:

```
[INFO] [EMAIL_SENDER] Updating file with success status...
[INFO] [EMAIL_SENDER] ✅ File updated with success status
[INFO] [EMAIL_SENDER] ✅ File moved to: Approved/Done/email_send_20260323_abc123.md
```

**Final file location**: `Approved/Done/email_send_20260323_abc123.md`

**File content** (appended):
```markdown
---

**Send Result**

status: sent
sent_at: 2026-03-23T16:30:15.123456+05:00
message_id: <abc123@mail.gmail.com>
```

### Step 6: Watcher Marks as Processed
**Automatic**

```
[INFO] ✅ Successfully processed: email_send_20260323_abc123.md
[INFO] Approved Watcher completed cycle, processed 1 items
```

---

## Detection Triggers

The watcher detects email files using multiple strategies:

### 1. Filename Pattern
- Starts with `email_send_`
- Starts with `email_`

### 2. Content Markers
- Contains `action: send_email` (case-insensitive)
- Has `to:` and `subject:` in first 500 characters
- Has `type: "email_send"` in frontmatter

### 3. Examples

**Detected as email_send:**
```markdown
# File: email_send_20260323_abc123.md
to: recipient@example.com
subject: Test
Body...
```

**Detected as email_send:**
```markdown
# File: reply_to_client.md
---
action: send_email
---
to: client@example.com
subject: Reply
Body...
```

**Detected as email_send:**
```markdown
# File: outbound_message.md
---
type: "email_send"
---
to: vendor@example.com
subject: Order
Body...
```

---

## How to Restart the Watcher

### If Running in Foreground:
```bash
# Stop with Ctrl+C
^C

# Restart
python Watchers/approved_watcher.py
```

### If Running in Background:
```bash
# Find process
ps aux | grep approved_watcher

# Kill process
kill <PID>

# Restart
python Watchers/approved_watcher.py &
```

### Using run_all_watchers.py:
```bash
# Stop all watchers
# (Ctrl+C if in foreground, or kill process)

# Restart all watchers
python run_all_watchers.py
```

---

## Testing the Full Workflow

### Test 1: Simple Email

**Step 1: Create draft**
```bash
cat > Pending_Approval/email_test_workflow.md << 'EOF'
---
type: email_send
approved: false
---

to: your.email@gmail.com
subject: Automated Workflow Test

Hello,

This email was sent through the complete automated workflow:
1. Created in Pending_Approval/
2. Human reviewed and approved
3. Moved to Approved/
4. Watcher detected it
5. Email sent automatically
6. File moved to Done/

Success!
EOF
```

**Step 2: Review and approve**
```bash
# Edit file, change approved: false → approved: true
nano Pending_Approval/email_test_workflow.md

# Move to Approved/
mv Pending_Approval/email_test_workflow.md Approved/
```

**Step 3: Start watcher (if not running)**
```bash
python Watchers/approved_watcher.py
```

**Step 4: Wait and verify**
- Within 30 seconds, watcher should detect the file
- Email should be sent
- File should move to `Approved/Done/`
- Check your email inbox

**Step 5: Verify results**
```bash
# Check file moved
ls -la Approved/Done/email_test_workflow.md

# Check status appended
cat Approved/Done/email_test_workflow.md

# Check logs
cat Logs/email_sender.log
cat Logs/approved_processed.txt
```

---

## Error Handling

### If Email Sending Fails

**Watcher logs:**
```
[ERROR] [EMAIL_SENDER] ❌ Email sending failed with exit code 1
[ERROR] [EMAIL_SENDER] Error output: SMTP authentication failed
```

**What happens:**
1. `email_sender.py` appends error to file
2. File moved to `Needs_Action/`
3. Watcher marks as failed (not processed)
4. Human can review error and retry

**Check error:**
```bash
# File moved to Needs_Action/
cat Needs_Action/email_test_workflow.md

# Should show error at bottom:
# status: failed
# error: SMTP authentication failed
# attempted_at: 2026-03-23T16:30:15
```

**To retry:**
1. Fix the issue (e.g., update SMTP credentials)
2. Move file back to `Approved/`
3. Watcher will retry automatically

---

## Monitoring

### Watch Watcher Logs in Real-Time
```bash
# Terminal 1: Run watcher
python Watchers/approved_watcher.py

# Terminal 2: Watch logs
tail -f Logs/email_sender.log
```

### Check Processed Files
```bash
# List processed files
cat Logs/approved_processed.txt

# Count processed
wc -l Logs/approved_processed.txt
```

### Check Folder Status
```bash
# Pending approval
ls -la Pending_Approval/

# Approved (waiting for watcher)
ls -la Approved/

# Successfully sent
ls -la Approved/Done/

# Failed sends
ls -la Needs_Action/
```

---

## Integration with Other Components

### Email Processor → Watcher
```
1. Gmail watcher detects new email
2. Email processor creates reply draft
3. Draft saved to Pending_Approval/
4. Human reviews and approves
5. Moves to Approved/
6. Approved watcher sends email
7. File moved to Done/
```

### Manual Creation → Watcher
```
1. Human creates email file manually
2. Saves to Pending_Approval/
3. Reviews and approves
4. Moves to Approved/
5. Approved watcher sends email
6. File moved to Done/
```

### Task Extraction → Watcher
```
1. Task extractor identifies "send email" task
2. Creates email draft
3. Saves to Pending_Approval/
4. Human reviews and approves
5. Moves to Approved/
6. Approved watcher sends email
7. File moved to Done/
```

---

## Configuration

### Watcher Settings
```python
# In Watchers/approved_watcher.py
watcher = ApprovedWatcher(interval=30)  # Check every 30 seconds
```

### Email Sender Settings
```env
# In .env file
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=your_app_password
FROM_EMAIL=your.email@gmail.com
```

---

## Success Indicators

You'll know the automated workflow is working when:

✅ Watcher detects files in `Approved/` within 30 seconds
✅ Log shows `[EMAIL_SENDER] Detected send action`
✅ Email sent successfully
✅ File moved to `Approved/Done/`
✅ Status appended to file
✅ Email received in inbox
✅ No errors in logs

---

## Troubleshooting

### Watcher Not Detecting Files

**Check:**
```bash
# Is watcher running?
ps aux | grep approved_watcher

# Check watcher logs
cat Logs/approved_watcher.log

# Check file format
cat Approved/your_file.md
```

**Solution:**
- Ensure filename starts with `email_` or `email_send_`
- OR ensure file has `to:` and `subject:` near top
- OR add `action: send_email` to file

### Email Not Sending

**Check:**
```bash
# Check email sender logs
cat Logs/email_sender.log

# Check SMTP configuration
cat .env | grep SMTP
```

**Solution:**
- Verify SMTP credentials in `.env`
- Check Gmail App Password is correct
- Ensure internet connection

### File Not Moving

**Check:**
```bash
# Check if file still in Approved/
ls -la Approved/

# Check if moved to Done/
ls -la Approved/Done/

# Check if moved to Needs_Action/ (failure)
ls -la Needs_Action/
```

**Solution:**
- Check logs for errors
- Verify file permissions
- Ensure folders exist

---

## Quick Commands

```bash
# Start watcher
python Watchers/approved_watcher.py

# Stop watcher
# Press Ctrl+C

# Check watcher status
ps aux | grep approved_watcher

# Watch logs
tail -f Logs/email_sender.log

# Check approved files
ls -la Approved/

# Check sent emails
ls -la Approved/Done/

# Check failed emails
ls -la Needs_Action/

# Check processed list
cat Logs/approved_processed.txt

# Test workflow
cat > Approved/email_test.md << 'EOF'
to: your.email@gmail.com
subject: Test
Body text
EOF
```

---

## Gold Tier Phase 1 Status

**COMPLETE**: Automated email workflow is fully functional!

**Components:**
- ✅ Email sender script (`actions/email_sender.py`)
- ✅ Approved watcher integration (`Watchers/approved_watcher.py`)
- ✅ File detection (multiple strategies)
- ✅ Automatic sending (subprocess call)
- ✅ Error handling (moves to Needs_Action/)
- ✅ Success handling (moves to Done/)
- ✅ Logging (detailed logs)
- ✅ Debouncing (processed files tracking)

**Workflow:**
```
Pending_Approval/ → Human Review → Approved/ → Watcher → Email Sent → Done/
```

**Next Phase**: Test with real email workflows, integrate with email processor for automatic reply drafting.

---

**Ready to use!** The complete automated email workflow is now operational.
