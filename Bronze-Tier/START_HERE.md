# 🚀 START HERE - Silver Tier Complete Setup

## Welcome to Your AI Employee - Silver Tier!

This guide will get you up and running in 10 minutes.

## Prerequisites ✅

You should already have:
- Python 3.13+
- UV package manager
- Playwright installed
- Gmail watcher working
- WhatsApp watcher working

## New in Silver Tier 🆕

- ✅ LinkedIn post generation
- ✅ Automated LinkedIn posting
- ✅ HITL approval workflow
- ✅ Task scheduling
- ✅ Multi-source orchestration

## 3-Step Quick Start

### Step 1: Install (2 minutes)
```bash
# Install schedule library
uv pip install schedule --system

# Create folders
mkdir -p Pending_Approval Approved Briefings schedulers

# Verify installation
python -c "import schedule; print('✅ Ready!')"
```

### Step 2: Setup LinkedIn (5 minutes)
```bash
# First-time LinkedIn setup
python Watchers/linkedin_poster.py

# What happens:
# 1. Browser opens to LinkedIn
# 2. You login (ONE TIME ONLY)
# 3. Session saved automatically
# 4. Test post (optional)
```

### Step 3: Test Everything (3 minutes)
```bash
# Generate a LinkedIn post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('\`\`\`python')[1].split('\`\`\`')[0])"

# Check it was created
ls Pending_Approval/

# Review the post
cat Pending_Approval/linkedin_post_*.md

# Approve it
mv Pending_Approval/linkedin_post_*.md Approved/

# Post it manually (or wait for approved watcher)
python Watchers/linkedin_poster.py Approved/linkedin_post_*.md

# Check LinkedIn - your post should be live!
```

## Running the System

### Option 1: All-in-One (Recommended)
```bash
# Start everything at once
python run_all_watchers.py

# This starts:
# - Gmail Watcher
# - WhatsApp Watcher  
# - Approved Watcher
# - Scheduler

# Press Ctrl+C to stop all
```

### Option 2: Individual Components
```bash
# Terminal 1: Gmail watcher
python -m Watchers.gmail_watcher

# Terminal 2: WhatsApp watcher
python -m Watchers.whatsapp_watcher

# Terminal 3: Approved watcher
python Watchers/approved_watcher.py

# Terminal 4: Scheduler
python schedulers/daily_runner.py
```

### Option 3: Background (Windows)
```bash
# Run in background
start /B python run_all_watchers.py

# Check it's running
tasklist | findstr python
```

## Daily Workflow

### Morning (Automated at 9 AM)
1. Ralph loop processes overnight messages
2. LinkedIn post generated
3. Saved to Pending_Approval/

### Your Action (When Convenient)
1. Check Pending_Approval/
2. Review posts/replies
3. Edit if needed
4. Move to Approved/

### Automatic (Within 30 seconds)
1. Approved watcher detects file
2. Posts to LinkedIn
3. Moves to Done/
4. Logs success

### Evening (Automated at 6 PM)
1. Ralph loop processes day's messages
2. Weekly briefing generated
3. Dashboard updated

## Monitoring

### Check Status
```bash
# View all logs
ls -lh Logs/

# Recent activity
tail -n 20 Logs/master_runner.log

# Folder status
echo "Pending: $(ls Pending_Approval/ | wc -l)"
echo "Approved: $(ls Approved/ | wc -l)"
echo "Done: $(ls Done/ | wc -l)"
```

### View Dashboard
```bash
cat Dashboard.md
```

## Troubleshooting

### "LinkedIn won't login"
```bash
# Make sure headless=False (already set)
# Try logging in to LinkedIn in regular browser first
# Check for 2FA requirements
```

### "Approved watcher not working"
```bash
# Check it's running
ps aux | grep approved_watcher

# Check logs
cat Logs/approved_watcher.log

# Restart it
python Watchers/approved_watcher.py
```

### "Post not appearing on LinkedIn"
```bash
# Check screenshots
ls Logs/linkedin_*.png

# View the screenshot
open Logs/linkedin_post_success_*.png

# Verify on LinkedIn
open https://www.linkedin.com/feed/
```

### "Import errors"
```bash
# Make sure you're in the right directory
pwd
# Should be: .../Bronze-Tier/

# Reinstall dependencies
uv pip install -e . --system
```

## What Each Component Does

### Gmail Watcher
- Monitors Gmail every 5 minutes
- Creates .md files in Needs_Action/
- Marks emails as read

### WhatsApp Watcher
- Monitors WhatsApp Web every 60 seconds
- Extracts unread messages
- Creates .md files in Needs_Action/

### Main Orchestrator
- Routes files by source
- Calls appropriate processor
- Updates dashboard

### LinkedIn Post Generator
- Creates professional posts
- 5 different types
- Saves to Pending_Approval/

### Approved Watcher
- Monitors Approved/ every 30 seconds
- Detects LinkedIn posts
- Calls linkedin_poster.py
- Moves to Done/

### LinkedIn Poster
- Opens LinkedIn in browser
- Posts content automatically
- Takes screenshots
- Handles errors

### Scheduler
- Runs tasks at set times
- Morning/afternoon/evening routines
- Weekly briefings
- Log cleanup

## File Locations

```
Needs_Action/          → New messages from watchers
Pending_Approval/      → Drafts awaiting your review
Approved/              → Approved content ready to post
Done/                  → Completed items
Plans/                 → Action plans and drafts
Briefings/             → Weekly summaries
Logs/                  → All system logs
Watchers/linkedin_session/  → LinkedIn session (gitignored)
Watchers/whatsapp_session/  → WhatsApp session (gitignored)
```

## Scheduled Tasks

- **9:00 AM** - Morning routine + LinkedIn post
- **2:00 PM** - Afternoon check
- **6:00 PM** - Evening routine + briefing
- **Every 2 hours** - Ralph loop (8 AM - 6 PM)
- **Monday 8 AM** - Weekly routine + cleanup

## Security Notes

- LinkedIn session stored locally (never committed)
- All posts require human approval
- Sensitive content auto-flagged
- Credentials never logged
- Screenshots for verification

## Next Steps

1. ✅ Complete this setup
2. ✅ Test the workflow
3. ✅ Let it run for a week
4. ✅ Review the results
5. 🚀 Move to Gold Tier!

## Need Help?

Check these files:
- `QUICK_REFERENCE.md` - Quick commands
- `INSTALL_AND_TEST.md` - Detailed testing
- `SILVER_TIER_FINAL_SETUP.md` - Complete setup
- `SILVER_TIER_ACHIEVEMENT.md` - What you built
- `Logs/*.log` - System logs

## Congratulations! 🎉

You've completed Silver Tier! Your AI Employee can now:
- Handle Gmail and WhatsApp
- Generate LinkedIn posts
- Post automatically (with approval)
- Run on a schedule
- Track everything

Enjoy your automated business operations! 🚀

---

**Quick Start**: `python run_all_watchers.py`
**Generate Post**: See QUICK_REFERENCE.md
**Check Status**: `cat Dashboard.md`
