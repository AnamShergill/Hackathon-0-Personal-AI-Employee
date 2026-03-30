# Quick Start - Gold Tier Development

## TL;DR - Start Working Now

```bash
# Navigate to active workspace
cd Gold-Tier

# Start all watchers
python run_all_watchers.py

# Or start individually in separate terminals:
python Watchers/gmail_watcher.py          # Terminal 1
python Watchers/whatsapp_watcher.py       # Terminal 2  
python Watchers/approved_watcher.py       # Terminal 3

# Run scheduler (optional)
python schedulers/daily_runner.py         # Terminal 4
```

## Daily Workflow

### 1. Morning Startup
```bash
cd Gold-Tier
python run_all_watchers.py
```

### 2. Check Dashboard
```bash
cat Dashboard.md
```

### 3. Review Pending Items
```bash
# Check what needs approval
ls Pending_Approval/

# Review a file
cat Pending_Approval/email_send_*.md

# Edit if needed
nano Pending_Approval/email_send_*.md

# Approve by moving to Approved/
mv Pending_Approval/email_send_*.md Approved/
```

### 4. Monitor Activity
```bash
# Watch logs in real-time
tail -f Logs/email_sender.log

# Check what's been processed
cat Logs/approved_processed.txt

# View completed items
ls Approved/Done/
```

## Common Tasks

### Send an Email
```bash
# 1. Create draft
cat > Pending_Approval/email_test.md << 'EOF'
to: recipient@example.com
subject: Test Email

Hello,

This is a test email from the Gold-Tier system.

Best regards
EOF

# 2. Review and approve
nano Pending_Approval/email_test.md

# 3. Move to Approved/
mv Pending_Approval/email_test.md Approved/

# 4. Watcher will detect and send automatically (within 30 seconds)
```

### Post to LinkedIn
```bash
# 1. Generate post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])"

# 2. Review in Pending_Approval/
cat Pending_Approval/linkedin_post_*.md

# 3. Approve
mv Pending_Approval/linkedin_post_*.md Approved/

# 4. Watcher will post automatically
```

### Check Email Inbox
```bash
# View new emails
ls Needs_Action/

# Read an email
cat Needs_Action/email_*.md

# Process with email processor
python Skills/email_processor.py
```

## Folder Structure Quick Reference

```
Gold-Tier/
├── Watchers/              # All watchers (gmail, whatsapp, linkedin, approved)
├── Skills/                # All skills (00-10)
├── actions/               # Email sender
├── schedulers/            # Daily runner
├── Pending_Approval/      # 👀 Review items here
├── Approved/              # ✅ Move approved items here
│   └── Done/              # ✓ Completed items
├── Needs_Action/          # 📧 New emails/messages
├── Plans/                 # 📋 Generated plans
├── Logs/                  # 📝 All logs
├── Dashboard.md           # 📊 Current status
└── Company_Handbook.md    # 📚 Reference
```

## Configuration

### SMTP Settings (.env)
```bash
# Edit root .env file
nano ../.env

# Or copy to Gold-Tier
cp ../.env .env
nano .env
```

Required variables:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=your_app_password
FROM_EMAIL=your.email@gmail.com
```

### Gmail API
- Credentials: `../credentials.json`
- Token: `../token.json`
- First run will prompt for OAuth

### WhatsApp
- Session: `Watchers/whatsapp_session/`
- First run will show QR code to scan

### LinkedIn
- Session: `Watchers/linkedin_session/`
- First run will prompt for login

## Monitoring

### Watch All Logs
```bash
# Terminal 1: Email sender
tail -f Logs/email_sender.log

# Terminal 2: Gmail watcher
tail -f Logs/gmail_watcher.log

# Terminal 3: WhatsApp watcher
tail -f Logs/whatsapp_watcher.log

# Terminal 4: LinkedIn poster
tail -f Logs/linkedin_poster.log
```

### Check Status
```bash
# Active watchers
ps aux | grep watcher

# Pending approvals
ls -la Pending_Approval/

# Approved (waiting to process)
ls -la Approved/

# Completed
ls -la Approved/Done/

# Failed (needs attention)
ls -la Needs_Action/
```

## Troubleshooting

### Watcher Not Running
```bash
# Check if running
ps aux | grep watcher

# Start if not running
python Watchers/approved_watcher.py
```

### Email Not Sending
```bash
# Check logs
cat Logs/email_sender.log

# Verify SMTP config
cat ../.env | grep SMTP

# Test email sender directly
python actions/email_sender.py --file Approved/email_test.md
```

### Import Errors
```bash
# Verify dependencies exist
ls Watchers/base_watcher.py
ls Watchers/gmail_watcher.py

# Re-run fix script if needed
cd ..
python fix_import_paths.py
cd Gold-Tier
```

### Missing Folders
```bash
# Create all required folders
mkdir -p Pending_Approval Approved/Done Needs_Action Plans Logs
```

## Development Tips

### Test Email Workflow
```bash
# 1. Create test email to yourself
cat > Approved/email_test.md << 'EOF'
to: your.email@gmail.com
subject: Test

Test email
EOF

# 2. Run watcher once
python Watchers/approved_watcher.py

# 3. Check your inbox
```

### Debug Mode
```bash
# Run watcher with verbose output
python Watchers/approved_watcher.py --verbose

# Or add debug prints to code
```

### Stop All Watchers
```bash
# Find all watcher processes
ps aux | grep watcher

# Kill all
pkill -f watcher

# Or kill individually
kill <PID>
```

## Git Workflow

### Commit Changes
```bash
cd ..  # Go to root

# Check status
git status

# Add changes
git add Gold-Tier/

# Commit
git commit -m "Update Gold-Tier: [your changes]"

# Push
git push origin main
```

### Quick Push Script
```bash
# Use the push script
./push_to_github.sh "Your commit message"
```

## Performance Tips

### Reduce Polling Frequency
Edit watcher files to change intervals:
```python
# In Watchers/gmail_watcher.py
watcher = GmailWatcher(interval=300)  # 5 minutes (default)

# In Watchers/whatsapp_watcher.py
watcher = WhatsAppWatcher(interval=60)  # 1 minute (default)

# In Watchers/approved_watcher.py
watcher = ApprovedWatcher(interval=30)  # 30 seconds (default)
```

### Reduce Resource Usage
```bash
# Run only essential watchers
python Watchers/gmail_watcher.py &
python Watchers/approved_watcher.py &

# Skip WhatsApp/LinkedIn if not needed
```

## Backup

### Backup Important Files
```bash
# Backup approved items
cp -r Approved/ Approved_backup_$(date +%Y%m%d)/

# Backup logs
cp -r Logs/ Logs_backup_$(date +%Y%m%d)/

# Backup plans
cp -r Plans/ Plans_backup_$(date +%Y%m%d)/
```

### Restore from Backup
```bash
# Restore approved items
cp -r Approved_backup_20260323/ Approved/

# Restore logs
cp -r Logs_backup_20260323/ Logs/
```

## Useful Commands

```bash
# Count pending approvals
ls Pending_Approval/ | wc -l

# Count completed items
ls Approved/Done/ | wc -l

# Find recent emails
find Needs_Action/ -name "email_*.md" -mtime -1

# Search logs for errors
grep -i error Logs/*.log

# Check disk usage
du -sh Gold-Tier/

# Clean old archives
find Approved/Done/ -name "*.md" -mtime +30 -delete
```

## Next Steps

1. ✅ Start watchers: `python run_all_watchers.py`
2. ✅ Check dashboard: `cat Dashboard.md`
3. ✅ Test email workflow: Create test email → Approve → Send
4. ✅ Monitor logs: `tail -f Logs/email_sender.log`
5. ✅ Review completed items: `ls Approved/Done/`

## Support

- Bronze Tier docs: `../Bronze-Tier/README_TIER.md`
- Silver Tier docs: `../Silver-Tier/README.md`
- Gold Tier docs: `README.md`
- Troubleshooting: `TEST_EMAIL_SENDER.md`
- Full summary: `../REORGANIZATION_SUMMARY.md`

---

**You're ready to work in Gold-Tier!** 🚀
