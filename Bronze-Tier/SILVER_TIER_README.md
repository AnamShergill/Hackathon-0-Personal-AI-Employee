# 🥈 Silver Tier - WhatsApp Integration

## Overview

Silver Tier extends the Bronze Tier AI Employee with **WhatsApp monitoring**, creating a unified multi-channel autonomous assistant that processes both emails and WhatsApp messages through the same intelligent pipeline.

---

## 🎯 What's New

### WhatsApp Watcher (`Watchers/whatsapp_watcher.py`)

- **Automated WhatsApp Web** - Uses Playwright to monitor WhatsApp
- **Persistent Session** - QR code scan only once, session saved
- **Smart Polling** - Checks for unread messages every 60 seconds
- **Priority Detection** - Automatic urgency scoring based on keywords
- **Unified Format** - Creates markdown files compatible with email processor
- **Robust Error Handling** - Automatic recovery from browser crashes

### Key Features

✅ **Multi-Channel Monitoring**
- Gmail (Bronze Tier)
- WhatsApp (Silver Tier)
- Both feed into same `Needs_Action/` folder

✅ **Intelligent Priority Scoring**
- HIGH: urgent, ASAP, emergency, payment keywords
- MEDIUM: important, help, please
- LOW: regular messages

✅ **Seamless Integration**
- WhatsApp messages processed by existing email processor
- Same dashboard shows all channels
- Unified Ralph Wiggum loop

✅ **Session Persistence**
- QR code scan only once
- Browser session saved in `Watchers/whatsapp_session/`
- Automatic login on subsequent runs

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Run setup script
chmod +x setup_silver_tier.sh
./setup_silver_tier.sh

# Or manually:
pip install playwright
playwright install chromium
```

### 2. Start WhatsApp Watcher

```bash
python Watchers/whatsapp_watcher.py
```

### 3. Scan QR Code

1. Browser opens to WhatsApp Web
2. QR code appears
3. Open WhatsApp on phone → Settings → Linked Devices
4. Scan QR code
5. Session saved automatically

### 4. Monitor Messages

- Watcher polls every 60 seconds
- New messages → `Needs_Action/whatsapp_*.md`
- Process with: `python Skills/email_processor.py`

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Input Sources                         │
├─────────────────────────────────────────────────────────┤
│  Gmail Watcher          │  WhatsApp Watcher (NEW)       │
│  (Bronze Tier)          │  (Silver Tier)                │
│  ↓                      │  ↓                            │
│  email_*.md             │  whatsapp_*.md                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Needs_Action/ Folder                        │
│  (Unified queue for all message sources)                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           AI Agent Processing Pipeline                   │
│  • Priority Scoring                                      │
│  • Task Extraction                                       │
│  • Reply Drafting                                        │
│  • HITL Flagging                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Output & Actions                         │
│  Plans/ → Done/ → Dashboard Updates                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Polling Interval

Edit `Watchers/whatsapp_watcher.py`:

```python
# Default: 60 seconds
watcher = WhatsAppWatcher(interval=60, headless=False)

# Faster polling: 30 seconds
watcher = WhatsAppWatcher(interval=30, headless=False)

# Slower polling: 120 seconds (2 minutes)
watcher = WhatsAppWatcher(interval=120, headless=False)
```

### Headless Mode

After QR code is scanned:

```python
# Run without visible browser (saves resources)
watcher = WhatsAppWatcher(interval=60, headless=True)
```

### Priority Keywords

Customize in `whatsapp_watcher.py`:

```python
URGENT_KEYWORDS = [
    'urgent', 'asap', 'immediately', 'now', 'emergency',
    # Add your own:
    'boss', 'client', 'deadline', 'meeting', 'critical'
]
```

---

## 📝 Message Format

WhatsApp messages are saved as markdown files:

```markdown
---
source: "WhatsApp"
sender: "John Doe"
date_received: "2026-03-19T23:45:00"
timestamp: "23:45"
message_id: "abc123def456"
priority: high
status: new
processed: false
---

# WhatsApp Message from: John Doe

**Received:** 23:45

**Priority:** HIGH

**Message ID:** abc123def456

## Message Content

URGENT: Need the report by tomorrow morning!

---

*Processed by WhatsApp Watcher at 2026-03-19T23:45:30*
```

---

## 🎯 Usage Examples

### Example 1: Urgent Client Message

**WhatsApp Message:**
```
Client: "URGENT: Payment issue with invoice #1234. Need help ASAP!"
```

**What Happens:**
1. Watcher detects unread message
2. Priority: HIGH (urgent + ASAP + payment)
3. Creates: `Needs_Action/whatsapp_20260319_234500_abc123.md`
4. Email processor creates action plan
5. Flags for HITL (financial transaction)
6. Dashboard updated

### Example 2: Regular Check-in

**WhatsApp Message:**
```
Friend: "Hey, how's the project going?"
```

**What Happens:**
1. Watcher detects unread message
2. Priority: LOW (no urgent keywords)
3. Creates: `Needs_Action/whatsapp_20260319_234530_def456.md`
4. Email processor creates plan
5. No HITL flag needed
6. Dashboard updated

---

## 🔄 Running Both Watchers

### Option 1: Separate Terminals

```bash
# Terminal 1: Gmail
python Watchers/gmail_watcher.py

# Terminal 2: WhatsApp
python Watchers/whatsapp_watcher.py

# Terminal 3: Process messages
python Skills/email_processor.py
```

### Option 2: Background Processes (Linux/Mac)

```bash
# Start Gmail watcher in background
nohup python Watchers/gmail_watcher.py > Logs/gmail_bg.log 2>&1 &

# Start WhatsApp watcher in background
nohup python Watchers/whatsapp_watcher.py > Logs/whatsapp_bg.log 2>&1 &

# Check processes
ps aux | grep watcher

# Stop processes
pkill -f gmail_watcher
pkill -f whatsapp_watcher
```

### Option 3: Orchestrator (Future Enhancement)

Create `orchestrator_silver.py` to manage both watchers.

---

## 🐛 Troubleshooting

### QR Code Issues

**Problem:** QR code doesn't appear

**Solution:**
```bash
# Delete session and restart
rm -rf Watchers/whatsapp_session/
python Watchers/whatsapp_watcher.py
```

### Browser Crashes

**Problem:** Browser closes unexpectedly

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install --force chromium

# Check logs
tail -f Logs/whatsapp_watcher.log
```

### No Messages Detected

**Problem:** Watcher runs but doesn't find messages

**Check:**
1. Messages are unread (blue dot in WhatsApp)
2. Browser window shows WhatsApp Web loaded
3. Wait full 60 seconds for next poll
4. Check logs for errors

**Debug:**
```bash
# View detailed logs
tail -f Logs/whatsapp_watcher.log

# Check processed messages
cat Watchers/whatsapp_session/processed_messages.txt
```

### Selector Errors

**Problem:** "Selector not found" errors

**Cause:** WhatsApp Web updated their HTML

**Solution:**
1. Open WhatsApp Web in browser
2. Use DevTools to inspect elements
3. Update selectors in `SELECTORS` dictionary
4. Common selectors to check:
   - `chat_list`
   - `message_container`
   - `contact_name`

---

## 🔐 Security & Privacy

### Session Data
- Stored locally in `Watchers/whatsapp_session/`
- Contains browser profile and login cookies
- **Never commit to git** (in .gitignore)
- Delete folder to log out completely

### Message Data
- All messages stored locally as markdown files
- No external API calls (except WhatsApp Web)
- No cloud storage
- Processing happens on your machine

### WhatsApp Terms of Service
⚠️ **Important:**
- Automation may violate WhatsApp ToS
- Use at your own risk
- Recommended for personal use only
- Not for commercial/bulk messaging
- WhatsApp may ban accounts using automation

### Best Practices
- Use on personal account only
- Don't spam or send bulk messages
- Respect privacy of contacts
- Monitor for WhatsApp policy changes

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Real-time log monitoring
tail -f Logs/whatsapp_watcher.log

# Last 50 lines
tail -n 50 Logs/whatsapp_watcher.log

# Search for errors
grep ERROR Logs/whatsapp_watcher.log
```

### Check Statistics

```bash
# Count processed messages
wc -l Watchers/whatsapp_session/processed_messages.txt

# List WhatsApp messages
ls -lh Needs_Action/whatsapp_*

# Count by priority
grep "priority: high" Needs_Action/whatsapp_* | wc -l
```

### Dashboard Integration

Dashboard automatically shows:
- Total messages (Gmail + WhatsApp)
- Priority breakdown
- Recent activity from both sources
- Processing statistics

---

## 🎯 Silver Tier Checklist

- [x] WhatsApp watcher implemented
- [x] Persistent session (QR code once)
- [x] Priority detection
- [x] Markdown file creation
- [x] Error handling & logging
- [x] Integration with existing processor
- [x] Documentation complete
- [ ] WhatsApp-specific skill (optional)
- [ ] Orchestrator for both watchers (optional)
- [ ] MCP email sender (Gold Tier)

---

## 🚀 Next Steps: Gold Tier

### Planned Features

1. **MCP Email Sender**
   - Send emails via Model Context Protocol
   - Human approval workflow
   - Draft → Approve → Send pipeline

2. **Advanced NLP**
   - Sentiment analysis
   - Entity extraction (names, dates, amounts)
   - Intent classification

3. **Calendar Integration**
   - Extract meeting requests
   - Create calendar events
   - Send confirmations

4. **Multi-Channel Reply**
   - Reply to WhatsApp messages
   - Reply to emails
   - Unified reply interface

---

## 📚 Additional Resources

- [SILVER_TIER_SETUP.md](SILVER_TIER_SETUP.md) - Detailed setup guide
- [Playwright Documentation](https://playwright.dev/python/) - Browser automation
- [WhatsApp Web](https://web.whatsapp.com) - Official web client
- [Company_Handbook.md](Company_Handbook.md) - Rules and policies

---

## 🤝 Contributing

Found a bug or have an improvement?

1. Check WhatsApp Web for selector changes
2. Update `SELECTORS` dictionary
3. Test thoroughly
4. Submit pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

**Silver Tier Status:** Complete ✅  
**Next Milestone:** Gold Tier - MCP Integration 🚀

---

*Last Updated: March 19, 2026*  
*Version: Silver Tier v1.0*
