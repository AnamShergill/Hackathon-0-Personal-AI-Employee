# Gold Tier - Automated Email Workflow (Active Workspace)

## What This Tier Adds
- Automated email sending
- Enhanced approval workflow
- Email sender action
- Complete HITL pipeline

## Prerequisites
- Bronze Tier setup complete
- Silver Tier setup complete
- SMTP credentials configured in `.env`

## How to Run
```bash
# Start all watchers
python run_all_watchers.py

# Or individually:
python Watchers/gmail_watcher.py
python Watchers/whatsapp_watcher.py
python Watchers/approved_watcher.py

# Run scheduler
python schedulers/daily_runner.py
```

## Workflow
1. Content generated → `Pending_Approval/`
2. Human reviews and approves → `Approved/`
3. Approved watcher detects and sends
4. Completed items → `Approved/Done/`

## Key Files
- `actions/email_sender.py` - Sends approved emails
- `Watchers/approved_watcher.py` - Monitors approved folder
- `Skills/10_EMAIL_SENDER.md` - Email sending skill
- `schedulers/daily_runner.py` - Task scheduler

## Configuration
Edit `.env` file with your SMTP settings:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=your_app_password
```

## Testing
See `TEST_EMAIL_SENDER.md` for complete testing guide
