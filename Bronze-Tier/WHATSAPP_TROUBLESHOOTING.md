# WhatsApp Watcher Troubleshooting Guide

## Problem: Showing 0 Unread Chats

If the WhatsApp watcher is showing "0 unread chats" even though you have unread messages, follow these steps:

---

## Quick Diagnosis

### Step 1: Run the Simple Test

```bash
python test_whatsapp_simple.py
```

This will:
- Open WhatsApp Web
- Wait for it to load
- Search for unread indicators using multiple strategies
- Show you what it finds
- Take a screenshot

**What to look for:**
- Does it find any bold elements? (unread chats have bold names)
- Does it find any elements with "unread" in aria-label?
- Does it find any number badges?
- Does it find any chat containers at all?

---

### Step 2: Run the Live Debugger

```bash
python debug_whatsapp_live.py
```

This will:
- Open WhatsApp Web
- Wait 30 seconds for full load
- Analyze the DOM structure
- Show you what selectors are available
- Stay open for manual inspection

**What to check:**
- Are there any `role` attributes? (row, listitem, gridcell, etc.)
- Are there any `data-testid` attributes?
- Are there any `id` attributes on the chat list?
- Can you see chat names in the output?

---

## Common Issues & Solutions

### Issue 1: WhatsApp Not Fully Loaded

**Symptoms:**
- All selectors return 0 elements
- Page looks blank or shows loading spinner

**Solution:**
- Wait longer (30-60 seconds) after opening
- Check your internet connection
- Try refreshing the page
- Check if WhatsApp Web is down: https://downdetector.com/status/whatsapp/

---

### Issue 2: Not Logged In

**Symptoms:**
- QR code appears every time
- Session not persisting

**Solution:**
1. Delete the session folder:
   ```bash
   rm -rf Watchers/whatsapp_session
   ```
2. Run the watcher again:
   ```bash
   python Watchers/whatsapp_watcher.py
   ```
3. Scan the QR code
4. Wait for "Session saved" message
5. Don't close the browser immediately - wait 10 seconds

---

### Issue 3: Selectors Changed (WhatsApp Updated)

**Symptoms:**
- Used to work, now doesn't
- Debug shows different structure than expected

**Solution:**

1. **Manual Inspection:**
   - Open WhatsApp Web in browser
   - Right-click on a chat in the list
   - Click "Inspect" (F12)
   - Look at the HTML structure
   - Note the attributes: `role`, `data-testid`, `id`, `class`

2. **Update Selectors:**
   Edit `Watchers/whatsapp_watcher.py` and update the `SELECTORS` dictionary:

   ```python
   SELECTORS = {
       'chat_list_primary': '[NEW_SELECTOR_HERE]',
       'chat_item': 'div[role="NEW_ROLE_HERE"]',
       # ... etc
   }
   ```

3. **Common 2026 Selectors to Try:**
   ```python
   # Chat list containers:
   '[data-testid="chat-list"]'
   'div[role="grid"]'
   '#pane-side'
   'div[aria-label*="Chat list"]'
   
   # Chat items:
   'div[role="row"]'
   'div[role="listitem"]'
   'div[role="gridcell"]'
   '[data-testid^="cell-frame-container"]'
   
   # Unread indicators:
   'span[data-testid="icon-unread-count"]'
   '[aria-label*="unread" i]'
   'span[data-icon="unread-count"]'
   ```

---

### Issue 4: Messages Not Detected as Unread

**Symptoms:**
- Watcher finds chat items
- But doesn't detect them as unread
- Shows "Found 0 unread chats"

**Solution:**

The watcher uses multiple strategies to detect unread messages. Check which ones work:

1. **Enable scan_all mode** (temporary debugging):
   ```python
   # In Watchers/whatsapp_watcher.py, line ~90
   watcher = WhatsAppWatcher(interval=60, headless=False, scan_all=True)
   ```
   This will check the first 3 chats regardless of unread status.

2. **Check the detection logic** in `check_for_updates()`:
   - Strategy 1: Unread badge with count
   - Strategy 2: Unread dot indicator
   - Strategy 3: Green dot or unread marker
   - Strategy 4: Bold text

3. **Add more detection strategies:**
   Edit the `check_for_updates()` method and add:
   ```python
   # Strategy 5: Check for recent timestamp (today's messages)
   time_elem = chat_item.query_selector('span[data-testid="last-msg-time"]')
   if time_elem:
       timestamp = time_elem.inner_text()
       if timestamp in ['now', 'just now'] or ':' in timestamp:
           is_unread = True
           unread_reason = "recent timestamp"
   ```

---

### Issue 5: Can't Extract Message Content

**Symptoms:**
- Detects unread chat
- Opens the chat
- But can't extract message text
- Shows "No messages found in chat"

**Solution:**

1. **Check message container selector:**
   ```python
   # Try these in order:
   'div[data-testid="conversation-panel-body"]'
   'div[data-testid="conversation-panel-messages"]'
   'div[role="application"]'
   'div.copyable-area'
   ```

2. **Check message bubble selector:**
   ```python
   # Try these:
   'div[data-testid="msg-container"]'
   'div.message-in, div.message-out'
   'div[class*="message"]'
   'span.selectable-text'
   ```

3. **Enable debug screenshots:**
   The watcher already takes screenshots on errors. Check `Logs/` folder for:
   - `no_container_*.png` - Can't find message container
   - `whatsapp_load_error_*.png` - Page load issues

---

## Testing Workflow

### Full Test Sequence:

1. **Prepare test message:**
   - Send yourself a WhatsApp message from another number
   - Or ask someone to send you a message
   - Make sure it's UNREAD (don't open it on your phone)

2. **Run simple test:**
   ```bash
   python test_whatsapp_simple.py
   ```
   - Check if it detects the unread message
   - Review the output

3. **Run live debugger:**
   ```bash
   python debug_whatsapp_live.py
   ```
   - Manually inspect the DOM
   - Note the correct selectors

4. **Update selectors if needed:**
   - Edit `Watchers/whatsapp_watcher.py`
   - Update the `SELECTORS` dictionary

5. **Test the watcher:**
   ```bash
   python Watchers/whatsapp_watcher.py
   ```
   - Should detect the unread message
   - Should create a .md file in `Needs_Action/`

6. **Check the output:**
   ```bash
   ls -la Needs_Action/whatsapp_*.md
   ```
   - Should see a new file with today's timestamp

---

## Debug Logging

### Enable Verbose Logging:

Edit `Watchers/whatsapp_watcher.py` and change:

```python
# Line ~30
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    # ...
)
```

Then run:
```bash
python Watchers/whatsapp_watcher.py
```

Check the log file:
```bash
cat Logs/whatsapp_watcher.log
```

---

## Manual Workaround (If All Else Fails)

If the automated detection isn't working, you can manually trigger message processing:

1. **Create a test message file:**
   ```bash
   python -c "
from datetime import datetime
import hashlib

content = '''---
source: \"WhatsApp\"
sender: \"Test Contact\"
date_received: \"$(date -Iseconds)\"
timestamp: \"$(date +%H:%M)\"
message_id: \"test123\"
priority: medium
status: new
processed: false
---

# WhatsApp Message from: Test Contact

**Received:** $(date +%H:%M)

**Priority:** MEDIUM

**Message ID:** test123

## Message Content

This is a test message to verify the processing pipeline works.

---

*Manually created for testing*
'''
echo \"$content\" > Needs_Action/whatsapp_test_manual.md
"
   ```

2. **Run the orchestrator:**
   ```bash
   python orchestrator.py
   ```

3. **Check if it processes:**
   - Should move to `Done/` or create a plan in `Plans/`

---

## Getting Help

If none of these solutions work:

1. **Collect debug info:**
   - Run `python debug_whatsapp_live.py`
   - Save the output to a file
   - Take screenshots from `Logs/` folder

2. **Check WhatsApp Web version:**
   - Open WhatsApp Web in regular browser
   - Press F12 → Console
   - Type: `document.querySelector('meta[name="version"]')`
   - Note the version number

3. **Share details:**
   - WhatsApp Web version
   - Debug script output
   - Screenshots
   - Error messages from logs

---

## Quick Reference: Key Files

- `Watchers/whatsapp_watcher.py` - Main watcher code
- `Logs/whatsapp_watcher.log` - Log file
- `Watchers/whatsapp_session/` - Browser session data
- `Needs_Action/whatsapp_*.md` - Detected messages
- `test_whatsapp_simple.py` - Simple test script
- `debug_whatsapp_live.py` - Detailed debugger

---

## Success Indicators

You'll know it's working when:

✅ Watcher shows "Found X unread chats"
✅ Creates .md files in `Needs_Action/`
✅ Files have correct sender and message content
✅ Log shows "✅ Created message file: ..."
✅ No error screenshots in `Logs/`

---

## Next Steps After Fixing

Once the watcher is working:

1. Test with multiple messages
2. Test with different message types (text, emojis, etc.)
3. Test priority detection (urgent keywords)
4. Test the full pipeline (watcher → orchestrator → processor)
5. Add to `run_all_watchers.py` for continuous monitoring
