# Bronze Tier - Email-Only Automation

## What This Tier Provides
- Gmail monitoring and processing
- Email reply drafting
- Task extraction from emails
- Priority scoring
- Dashboard updates
- Archive management

## How to Run
```bash
# Start Gmail watcher
python Watchers/gmail_watcher.py

# Process emails
python Skills/email_processor.py

# Check dashboard
cat Dashboard.md
```

## Key Files
- `Watchers/gmail_watcher.py` - Monitors Gmail inbox
- `Skills/01-07_*.md` - Email processing skills
- `Inbox/`, `Needs_Action/`, `Done/` - Email workflow folders

## Next Steps
See `../Silver-Tier/` for multi-source automation (WhatsApp + LinkedIn)
