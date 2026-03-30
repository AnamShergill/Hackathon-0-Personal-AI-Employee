# Silver Tier Setup Guide - WhatsApp Watcher

## 🎯 What's New in Silver Tier

Silver Tier adds WhatsApp monitoring to your AI Employee system:
- **WhatsApp Watcher** - Monitors WhatsApp Web for new messages
- **Persistent Session** - QR code scan only once
- **Priority Detection** - Automatic urgency scoring
- **Unified Processing** - WhatsApp messages processed like emails

---

## 📦 Installation

### Step 1: Install Playwright

```bash
# Install Playwright Python package
pip install playwright

# Install Playwright browsers (Chromium)
playwright install chromium
```

### Step 2: Verify Installation

```bash
# Check Playwright is installed
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed')"
```

---

## 🚀 First Run - QR Code Setup

### Start the WhatsApp Watcher

```bash
python Watchers/whatsapp_watcher.py
```

### What Happens:

1. **Browser Opens** - Chromium browser window opens
2. **WhatsApp Web Loads** - Navigates to web.whatsapp.com
3. **QR Code Appears** - You'll see a QR code on screen

### Scan the QR Code:

1. Open WhatsApp on your phone
2. Go to **Settings** → **Linked Devices**
3. Tap **"Link a Device"**
4. Scan the QR code in the browser window
5. Wait for "✅ QR code scanned successfully!" message

### Session Saved:

- Session data saved to `Watchers/whatsapp_session/`
- Next time you run, no QR code needed!
- Browser will automatically log in

---

## 🔄 Normal Operation

After first setup, the watcher will:

1. **Poll Every 60 Seconds** - Checks for new unread messages
2. **Extract Message Details** - Sender, text, timestamp
3. **Detect Priority** - Based on keywords (urgent, ASAP, payment, etc.)
4. **Create Markdown Files** - Saves to `Needs_Action/whatsapp_*.md`
5. **Track Processed** - Avoids duplicate processing

### Running the Watcher:

```bash
# Run in foreground (see logs)
python Watchers/whatsapp_watcher.py

# Stop with Ctrl+C
```

---

## 📁 File Structure

```
Watchers/
├── whatsapp_watcher.py       # Main watcher script
├── whatsapp_session/          # Session data (gitignored)
│   ├── Default/               # Browser profile
│   └── processed_messages.txt # Tracking file
└── gmail_watcher.py           # Existing Gmail watcher

Needs_Action/
├── email_*.md                 # Gmail messages
└── whatsapp_*.md              # WhatsApp messages (NEW)

Logs/
└── whatsapp_watcher.log       # WhatsApp watcher logs
```

---

## 🎯 Priority Detection

The watcher automatically assigns priority based on keywords:

### HIGH Priority (score ≥ 5):
- Contains: urgent, ASAP, immediately, emergency, critical
- Contains: payment, money, invoice, $, €, £
- Example: "URGENT: Payment needed ASAP"

### MEDIUM Priority (score 2-4):
- Contains: important, help, please, quick
- Contains: pay, invoice
- Example: "Can you help with this invoice?"

### LOW Priority (score < 2):
- Regular messages
- Example: "Hey, how are you?"

---

## 🧪 Testing

### Send Test Messages:

1. **From Another Phone** - Send yourself a WhatsApp message
2. **Include Keywords** - Try "URGENT: Test message"
3. **Wait 60 Seconds** - Watcher polls every minute
4. **Check Needs_Action/** - Look for `whatsapp_*.md` file

### Verify File Created:

```bash
ls Needs_Action/whatsapp_*
cat Needs_Action/whatsapp_*.md
```

### Expected Output:

```markdown
---
source: "WhatsApp"
sender: "Contact Name"
date_received: "2026-03-19T23:45:00"
timestamp: "23:45"
message_id: "abc123def456"
priority: high
status: new
processed: false
---

# WhatsApp Message from: Contact Name

**Received:** 23:45

**Priority:** HIGH

**Message ID:** abc123def456

## Message Content

URGENT: Test message

---

*Processed by WhatsApp Watcher at 2026-03-19T23:45:30*
```

---

## 🔧 Configuration

### Change Polling Interval:

Edit `Watchers/whatsapp_watcher.py`:

```python
# Default: 60 seconds
watcher = WhatsAppWatcher(interval=60, headless=False)

# Change to 30 seconds for faster polling
watcher = WhatsAppWatcher(interval=30, headless=False)
```

### Enable Headless Mode:

After QR code is scanned once:

```python
# Run without visible browser window
watcher = WhatsAppWatcher(interval=60, headless=True)
```

### Customize Priority Keywords:

Edit the `URGENT_KEYWORDS` list in `whatsapp_watcher.py`:

```python
URGENT_KEYWORDS = [
    'urgent', 'asap', 'immediately', 'now', 'emergency', 'critical',
    'important', 'help', 'please', 'quick', 'fast', 'hurry',
    # Add your own keywords:
    'boss', 'client', 'deadline', 'meeting'
]
```

---

## 🐛 Troubleshooting

### Issue: QR Code Not Appearing

**Solution:**
```bash
# Delete session and try again
rm -rf Watchers/whatsapp_session/
python Watchers/whatsapp_watcher.py
```

### Issue: Browser Crashes

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Issue: No Messages Detected

**Check:**
1. WhatsApp Web is loaded (check browser window)
2. Messages are unread (blue dot indicator)
3. Wait full 60 seconds for next poll
4. Check logs: `cat Logs/whatsapp_watcher.log`

### Issue: "Selector not found" Errors

**Cause:** WhatsApp Web updated their HTML structure

**Solution:**
- Update selectors in `SELECTORS` dictionary
- Check WhatsApp Web HTML with browser DevTools
- Report issue for selector updates

---

## 🔐 Security & Privacy

### Session Data:
- Stored in `Watchers/whatsapp_session/`
- Contains browser profile and login session
- **Never commit to git** (already in .gitignore)
- Delete folder to log out

### Message Data:
- Messages saved as markdown files locally
- No external API calls
- No cloud storage
- All processing happens on your machine

### WhatsApp Terms:
- Using automation may violate WhatsApp ToS
- Use at your own risk
- Recommended for personal use only
- Not for commercial/bulk messaging

---

## 🎯 Next Steps

### 1. Process WhatsApp Messages

Run the email processor (it works with WhatsApp messages too!):

```bash
python Skills/email_processor.py
```

### 2. Create WhatsApp-Specific Skill (Optional)

Create `Skills/09_WHATSAPP_PROCESSOR.md` for WhatsApp-specific handling.

### 3. Update Dashboard

Dashboard will show both Gmail and WhatsApp messages:

```bash
cat Dashboard.md
```

### 4. Run Both Watchers

In separate terminals:

```bash
# Terminal 1: Gmail
python Watchers/gmail_watcher.py

# Terminal 2: WhatsApp
python Watchers/whatsapp_watcher.py
```

---

## 📊 Monitoring

### Check Watcher Status:

```bash
# View logs
tail -f Logs/whatsapp_watcher.log

# Count processed messages
wc -l Watchers/whatsapp_session/processed_messages.txt

# List WhatsApp messages
ls Needs_Action/whatsapp_*
```

### Dashboard Integration:

The dashboard will automatically show:
- Total messages (Gmail + WhatsApp)
- Priority breakdown
- Recent activity from both sources

---

## 🚀 Silver Tier Complete!

Once WhatsApp watcher is running:

✅ Gmail monitoring (Bronze Tier)  
✅ WhatsApp monitoring (Silver Tier)  
✅ Unified message processing  
✅ Priority detection across channels  
✅ Single dashboard for all sources  

**Next:** Gold Tier - Add MCP email sender for automated replies!

---

## 📞 Support

### Common Commands:

```bash
# Start watcher
python Watchers/whatsapp_watcher.py

# View logs
tail -f Logs/whatsapp_watcher.log

# Check for new messages
ls Needs_Action/whatsapp_*

# Process messages
python Skills/email_processor.py

# Update dashboard
cat Dashboard.md
```

### Debug Mode:

Add more logging in `whatsapp_watcher.py`:

```python
# Change log level to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

---

**Silver Tier Status:** Ready to Deploy! 🎉
