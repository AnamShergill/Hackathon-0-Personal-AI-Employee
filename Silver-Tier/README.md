# Silver Tier - Multi-Source Automation

## What This Tier Adds
- WhatsApp monitoring (via Playwright)
- LinkedIn post generation and automation
- Multi-source orchestration
- Enhanced dashboard with multiple channels

## Prerequisites
- Bronze Tier setup complete
- Playwright installed: `playwright install chromium`

## How to Run
```bash
# Start WhatsApp watcher
python Watchers/whatsapp_watcher.py

# Start LinkedIn poster
python Watchers/linkedin_poster.py

# Run orchestrator
python orchestrator.py
```

## Key Files
- `Watchers/whatsapp_watcher.py` - WhatsApp Web automation
- `Watchers/linkedin_poster.py` - LinkedIn posting
- `Skills/08_LINKEDIN_POST_GENERATOR.md` - Post generation
- `Skills/09_WHATSAPP_PROCESSOR.md` - WhatsApp processing

## Next Steps
See `../Gold-Tier/` for automated email sending and advanced workflows
