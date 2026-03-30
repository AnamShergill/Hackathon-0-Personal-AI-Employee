# Gmail Watcher Troubleshooting Guide

## Issue: Watcher Not Detecting My Starred Emails

### Understanding Gmail Labels

Gmail has two different ways to mark emails as important:

1. **Starred (Manual)**: Yellow star icon ⭐
   - You manually click the star
   - Gmail query: `is:starred`

2. **Important (Automatic)**: Yellow arrow icon ➤
   - Gmail automatically marks based on your patterns
   - Gmail query: `is:important`

### Current Watcher Query

The watcher now uses: `is:unread (is:starred OR is:important) -in:sent`

This means it will catch emails that are:
- ✅ Unread AND starred by you, OR
- ✅ Unread AND marked important by Gmail
- ❌ Excludes emails in your Sent folder
- ❌ Only looks at emails from last 24 hours

---

## Quick Diagnostic Steps

### Step 1: Verify Your Email Meets Criteria

Open Gmail and check your test email:

1. **Is it UNREAD?** (bold text in inbox)
   - If read, mark as unread: Select email → More → Mark as unread

2. **Is it STARRED?** (yellow star visible)
   - If not starred, click the star icon

3. **Is it in INBOX?** (not in Sent, Spam, or Trash)
   - Check the folder/label

4. **Is it RECENT?** (sent within last 24 hours)
   - Watcher only looks at emails from last day

### Step 2: Test the Query Manually

Run the test script to see what Gmail returns:

```bash
python test_gmail_query.py
```

This will test 6 different queries and show you which one finds your email.

### Step 3: Check Watcher Logs

When the watcher runs, it should print:

```
Gmail Watcher running Gmail check at 2026-03-18 16:15:11...
Found X new emails
Created email file: Needs_Action/email_YYYYMMDD_HHMMSS_[id].md
```

If you see "Found 0 new emails", the query isn't matching your email.

---

## Common Issues & Solutions

### Issue 1: Email is Read

**Problem:** You opened the email in Gmail, so it's no longer unread.

**Solution:**
```
1. Go to Gmail
2. Select the email
3. Click "More" (three dots)
4. Click "Mark as unread"
5. Wait for next watcher poll (up to 5 minutes)
```

### Issue 2: Email is Not Starred

**Problem:** You marked it as "important" in your mind, but didn't click the star.

**Solution:**
```
1. Go to Gmail
2. Find your email
3. Click the star icon (should turn yellow)
4. Verify email is still unread
5. Wait for next watcher poll
```

### Issue 3: Email is Older Than 24 Hours

**Problem:** Watcher only looks at emails from last day.

**Solution:**
```
Option A: Send a new test email
Option B: Update the query to look further back:
   - Edit Watchers/gmail_watcher.py
   - Change: timedelta(days=1) to timedelta(days=7)
   - Restart watcher
```

### Issue 4: Email is in Sent Folder

**Problem:** You sent the email to yourself, and it's in Sent folder.

**Solution:**
```
The query excludes sent emails by design. To test:
1. Send email from ANOTHER account to yourself
2. Or remove "-in:sent" from the query in gmail_watcher.py
```

### Issue 5: Watcher Not Running

**Problem:** You started the watcher but closed the terminal.

**Solution:**
```bash
# Start watcher in a terminal and keep it open
python Watchers/gmail_watcher.py

# You should see output every 5 minutes:
# "Gmail Watcher running Gmail check at ..."
```

---

## Testing Different Queries

If you want to customize what emails the watcher catches, edit the query in `Watchers/gmail_watcher.py`:

### Option 1: Only Starred Emails
```python
query = f'is:unread is:starred -in:sent after:{one_day_ago}'
```

### Option 2: Only Important Emails (Gmail's automatic)
```python
query = f'is:unread is:important -in:sent after:{one_day_ago}'
```

### Option 3: All Unread Emails (no filtering)
```python
query = f'is:unread -in:sent after:{one_day_ago}'
```

### Option 4: Starred OR Important (Current - Recommended)
```python
query = f'is:unread (is:starred OR is:important) -in:sent after:{one_day_ago}'
```

### Option 5: Specific Label
```python
query = f'is:unread label:work -in:sent after:{one_day_ago}'
```

### Option 6: From Specific Sender
```python
query = f'is:unread from:boss@company.com -in:sent after:{one_day_ago}'
```

---

## Advanced Debugging

### Check Gmail API Directly

Use the test script to see exactly what Gmail returns:

```bash
python test_gmail_query.py
```

This will show:
- Which queries find your email
- Email subjects and senders
- Gmail labels applied

### Check Token Validity

If authentication seems broken:

```bash
# Delete the token and re-authenticate
rm token.json
python Watchers/gmail_watcher.py
# Browser will open for OAuth flow
```

### Check Credentials

Verify `credentials.json` exists and is valid:

```bash
ls -la credentials.json
# Should show the file exists

# If missing, download from Google Cloud Console:
# 1. Go to console.cloud.google.com
# 2. Select your project
# 3. APIs & Services → Credentials
# 4. Download OAuth 2.0 Client ID
# 5. Save as credentials.json in project root
```

---

## Still Not Working?

### Manual Test Process

1. **Send a test email:**
   ```
   From: another-account@gmail.com
   To: your-account@gmail.com
   Subject: TEST URGENT Payment
   Body: This is a test for the AI employee
   ```

2. **In Gmail, verify:**
   - Email appears in Inbox
   - Email is unread (bold)
   - Click the star to mark it
   - Email has yellow star icon

3. **Check watcher output:**
   ```bash
   python Watchers/gmail_watcher.py
   ```
   
   Wait for output (up to 5 minutes):
   ```
   Gmail Watcher running Gmail check at 2026-03-18 16:20:00...
   Found 1 new emails
   Created email file: Needs_Action/email_20260318_162000_abc123.md
   ```

4. **Verify file created:**
   ```bash
   ls Needs_Action/
   # Should show the new email file
   ```

5. **If still no file:**
   - Run `python test_gmail_query.py` to debug
   - Check watcher terminal for errors
   - Verify Gmail API quota not exceeded
   - Check internet connection

---

## Contact & Support

If you've tried all the above and it still doesn't work:

1. Check the watcher terminal for error messages
2. Run the test script and share the output
3. Verify your Gmail settings allow API access
4. Check Google Cloud Console for API quota limits

---

## Quick Reference

### Restart Watcher
```bash
# Stop current watcher (Ctrl+C)
# Start fresh
python Watchers/gmail_watcher.py
```

### Force Re-authentication
```bash
rm token.json
python Watchers/gmail_watcher.py
```

### Test Query
```bash
python test_gmail_query.py
```

### Check Files
```bash
ls Needs_Action/
ls Plans/
ls Done/
```

---

**Last Updated:** March 18, 2026  
**Watcher Version:** Bronze Tier v1.0
