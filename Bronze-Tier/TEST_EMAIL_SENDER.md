# Email Sender Testing Guide

## Overview

This guide shows how to manually test the `actions/email_sender.py` script.

---

## Prerequisites

### 1. Configure SMTP Settings

Edit your `.env` file (create from `.env.example` if needed):

```bash
# Copy example if .env doesn't exist
cp .env.example .env
```

Add these settings to `.env`:

```env
# Email Sending Configuration (Gold Tier)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=your_app_password_here
FROM_EMAIL=your.email@gmail.com
```

### 2. Get Gmail App Password (if using Gmail)

**Important**: Don't use your regular Gmail password!

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Select "Mail" and your device
4. Click "Generate"
5. Copy the 16-character password
6. Paste it as `SMTP_PASS` in `.env`

**Note**: You need 2-Factor Authentication enabled to create app passwords.

### 3. Verify Dependencies

```bash
# Check if python-dotenv is installed
python -c "import dotenv; print('✅ dotenv installed')"

# If not installed:
uv pip install --system python-dotenv
```

---

## Manual Testing

### Test 1: Simple Email to Yourself

#### Step 1: Create Test Email File

```bash
cat > Approved/email_test_simple.md << 'EOF'
to: your.email@gmail.com
subject: Test Email from AI Employee
from: your.email@gmail.com

Hello,

This is a test email sent by the AI Employee email sender script.

If you receive this, the email sending functionality is working correctly!

Best regards,
AI Employee System
EOF
```

**Replace `your.email@gmail.com` with your actual email address!**

#### Step 2: Run the Sender Script

```bash
python actions/email_sender.py --file Approved/email_test_simple.md
```

#### Step 3: Check Output

**Expected output:**
```
2026-03-21 18:45:00 - __main__ - INFO - ================================================================================
2026-03-21 18:45:00 - __main__ - INFO - Processing email file: Approved/email_test_simple.md
2026-03-21 18:45:00 - __main__ - INFO - ================================================================================
2026-03-21 18:45:00 - __main__ - INFO - Parsing email file: Approved/email_test_simple.md
2026-03-21 18:45:00 - __main__ - INFO - Parsed email - To: your.email@gmail.com, Subject: Test Email from AI Employee
2026-03-21 18:45:00 - __main__ - INFO - Preparing to send email...
2026-03-21 18:45:00 - __main__ - INFO - Sending to 1 recipient(s)
2026-03-21 18:45:00 - __main__ - INFO - Logging in as: your.email@gmail.com
2026-03-21 18:45:00 - __main__ - INFO - Sending email...
2026-03-21 18:45:01 - __main__ - INFO - ✅ Email sent successfully!
2026-03-21 18:45:01 - __main__ - INFO - Updating file with success status...
2026-03-21 18:45:01 - __main__ - INFO - ✅ File updated with success status
2026-03-21 18:45:01 - __main__ - INFO - ✅ File moved to: Approved/Done/email_test_simple.md
2026-03-21 18:45:01 - __main__ - INFO - ================================================================================
2026-03-21 18:45:01 - __main__ - INFO - ✅ EMAIL SENT SUCCESSFULLY
2026-03-21 18:45:01 - __main__ - INFO - ================================================================================
```

#### Step 4: Verify Results

1. **Check your email inbox** - You should receive the test email
2. **Check the file moved**:
   ```bash
   cat Approved/Done/email_test_simple.md
   ```
   Should show the original content plus:
   ```
   ---
   
   **Send Result**
   
   status: sent
   sent_at: 2026-03-21T18:45:01.123456+05:00
   ```

3. **Check logs**:
   ```bash
   cat Logs/email_sender.log
   ```

---

### Test 2: Email with CC

```bash
cat > Approved/email_test_cc.md << 'EOF'
to: recipient@example.com
subject: Test with CC
cc: another@example.com, third@example.com

This email has multiple recipients via CC field.

Testing CC functionality.
EOF
```

```bash
python actions/email_sender.py --file Approved/email_test_cc.md
```

---

### Test 3: Email with Custom From

```bash
cat > Approved/email_test_from.md << 'EOF'
to: recipient@example.com
subject: Test with Custom From
from: custom.sender@example.com

This email uses a custom from address.

Note: The from address must be authorized by your SMTP server.
EOF
```

```bash
python actions/email_sender.py --file Approved/email_test_from.md
```

---

### Test 4: Simulate Failure (Invalid Recipient)

```bash
cat > Approved/email_test_fail.md << 'EOF'
to: invalid-email-address
subject: This Should Fail

This email has an invalid recipient and should fail.
EOF
```

```bash
python actions/email_sender.py --file Approved/email_test_fail.md
```

**Expected**: Error message, file moved to `Needs_Action/` with error appended.

---

## Troubleshooting

### Error: "SMTP_USER not configured"

**Solution**: Add SMTP settings to `.env` file.

```bash
# Check if .env exists
ls -la .env

# If not, copy from example
cp .env.example .env

# Edit and add SMTP settings
nano .env
```

### Error: "SMTP authentication failed"

**Possible causes**:
1. **Wrong password**: Make sure you're using an App Password, not your regular Gmail password
2. **2FA not enabled**: Enable 2-Factor Authentication on your Google account
3. **Less secure apps**: Gmail may block the connection (use App Password instead)

**Solution**:
1. Go to https://myaccount.google.com/apppasswords
2. Generate a new App Password
3. Update `SMTP_PASS` in `.env`

### Error: "File not found"

**Solution**: Make sure the file path is correct and the file exists.

```bash
# Check if file exists
ls -la Approved/email_test_simple.md

# Run from project root directory
pwd
```

### Error: "Missing required field: 'to'"

**Solution**: Make sure the email file has proper format:

```
to: recipient@example.com
subject: Subject Line

Body text here...
```

**Note**: There must be a blank line between headers and body!

### Error: "Connection timeout"

**Possible causes**:
1. Firewall blocking port 587
2. No internet connection
3. SMTP server is down

**Solution**:
1. Check internet connection
2. Try different SMTP port (465 for SSL)
3. Check firewall settings

---

## Verification Checklist

After successful test:

- [ ] Email received in inbox
- [ ] File moved to `Approved/Done/`
- [ ] File has `status: sent` appended
- [ ] File has `sent_at` timestamp
- [ ] Log file created in `Logs/email_sender.log`
- [ ] No errors in log file
- [ ] Exit code is 0 (success)

---

## Integration with Approved Watcher

Once manual testing works, the `approved_watcher.py` will automatically:

1. Detect email files in `Approved/` folder
2. Check for `approved: true` in frontmatter
3. Call `python actions/email_sender.py --file <path>`
4. Process the result

**To test full workflow**:

```bash
# 1. Create email in Pending_Approval/
cat > Pending_Approval/email_test_workflow.md << 'EOF'
---
type: email_send
approved: false
---

to: your.email@gmail.com
subject: Workflow Test

This tests the full approval workflow.
EOF

# 2. Review and approve (edit file, set approved: true)
nano Pending_Approval/email_test_workflow.md
# Change: approved: false → approved: true

# 3. Move to Approved/
mv Pending_Approval/email_test_workflow.md Approved/

# 4. Run approved watcher (or wait for it to detect)
# The watcher will automatically call email_sender.py
```

---

## Next Steps

After successful testing:

1. ✅ Configure real SMTP credentials in `.env`
2. ✅ Test sending to yourself
3. ✅ Test with CC recipients
4. ✅ Test failure handling
5. ✅ Update `approved_watcher.py` to detect email files
6. ✅ Test full workflow (Pending → Approved → Sent)
7. ✅ Monitor `Logs/email_sender.log` for issues

---

## Security Notes

- **Never commit `.env` file** - It contains sensitive credentials
- **Use App Passwords** - Don't use your main Gmail password
- **Rotate passwords regularly** - Change App Password every 90 days
- **Monitor sent emails** - Check `Approved/Done/` for audit trail
- **Review logs** - Check `Logs/email_sender.log` for suspicious activity

---

## Quick Commands

```bash
# Test simple email
python actions/email_sender.py --file Approved/email_test_simple.md

# Check logs
cat Logs/email_sender.log

# Check sent emails
ls -la Approved/Done/

# Check failed emails
ls -la Needs_Action/

# View file with status
cat Approved/Done/email_test_simple.md

# Clean up test files
rm -f Approved/email_test_*.md
rm -f Approved/Done/email_test_*.md
rm -f Needs_Action/email_test_*.md
```

---

**Ready to test!** Start with Test 1 (simple email to yourself).
