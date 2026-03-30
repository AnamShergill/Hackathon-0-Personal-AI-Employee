# 🚀 Silver Tier Quick Start

## Installation (One-Time Setup)

```bash
# Install Playwright
pip install playwright
playwright install chromium
```

## First Run (QR Code Scan)

```bash
# Start watcher
python Watchers/whatsapp_watcher.py

# Browser opens → Scan QR code with phone
# Session saved → Never need to scan again!
```

## Normal Operation

```bash
# Terminal 1: Gmail Watcher
python Watchers/gmail_watcher.py

# Terminal 2: WhatsApp Watcher  
python Watchers/whatsapp_watcher.py

# Terminal 3: Process Messages
python Skills/email_processor.py

# Check Dashboard
cat Dashboard.md
```

## Test It

```bash
# Send yourself a WhatsApp message:
"URGENT: Test message"

# Wait 60 seconds, then check:
ls Needs_Action/whatsapp_*
cat Needs_Action/whatsapp_*.md
```

## Troubleshooting

```bash
# View logs
tail -f Logs/whatsapp_watcher.log

# Reset session (if needed)
rm -rf Watchers/whatsapp_session/

# Reinstall browsers
playwright install --force chromium
```

## Key Files

- `Watchers/whatsapp_watcher.py` - Main script
- `Watchers/whatsapp_session/` - Session data (don't delete!)
- `Logs/whatsapp_watcher.log` - Logs
- `Needs_Action/whatsapp_*.md` - Messages

## Configuration

```python
# Edit whatsapp_watcher.py:

# Change polling interval (default: 60s)
watcher = WhatsAppWatcher(interval=30, headless=False)

# Enable headless mode (after QR scan)
watcher = WhatsAppWatcher(interval=60, headless=True)
```

## Priority Detection

- **HIGH**: urgent, ASAP, payment, emergency
- **MEDIUM**: important, help, please
- **LOW**: regular messages

## Next Steps

1. ✅ Install Playwright
2. ✅ Run watcher & scan QR
3. ✅ Send test message
4. ✅ Verify file created
5. ✅ Process with email processor
6. ✅ Check dashboard
7. 🎯 Start Gold Tier!

---

**Full Documentation:** See `SILVER_TIER_README.md`
