# Silver Tier - Quick Reference Card

## 🚀 Quick Start Commands

### Install Dependencies
```bash
uv pip install schedule --system
```

### Generate LinkedIn Post
```bash
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('\`\`\`python')[1].split('\`\`\`')[0])"
```

### Setup LinkedIn (First Time)
```bash
python Watchers/linkedin_poster.py
# Login when prompted, session saved automatically
```

### Start All Watchers
```bash
python run_all_watchers.py
```

### Start Individual Components
```bash
# Gmail watcher
python -m Watchers.gmail_watcher

# WhatsApp watcher
python -m Watchers.whatsapp_watcher

# Approved watcher
python Watchers/approved_watcher.py

# Scheduler
python schedulers/daily_runner.py
```

## 📁 Folder Structure

```
Needs_Action/     → New messages (Gmail, WhatsApp)
Pending_Approval/ → Drafts awaiting human review
Approved/         → Approved content ready to send
Done/             → Completed items
Plans/            → Action plans and drafts
Briefings/        → Weekly summaries
Logs/             → All system logs
```

## 🔄 HITL Workflow

```
1. Generate → Pending_Approval/
2. Review → Edit if needed
3. Approve → Move to Approved/
4. Auto-post → Approved watcher detects
5. Complete → Moved to Done/
```

## 📊 Check Status

```bash
# View logs
tail -f Logs/master_runner.log

# Check folders
ls Needs_Action/ Pending_Approval/ Approved/ Done/

# View dashboard
cat Dashboard.md
```

## 🛠️ Troubleshooting

### LinkedIn won't login
```bash
# Run in visible mode (already default)
python Watchers/linkedin_poster.py
```

### Watcher not running
```bash
# Check process
ps aux | grep watcher

# Check logs
cat Logs/approved_watcher.log
```

### Post not appearing
```bash
# Check screenshots
ls Logs/linkedin_*.png

# Verify on LinkedIn
open https://www.linkedin.com/feed/
```

## 📝 Post Types

1. **business_update** - Milestones, achievements
2. **industry_insight** - Tips, trends, lessons
3. **problem_solution** - Pain points + solutions
4. **behind_the_scenes** - Tech stack, process
5. **call_to_action** - Direct sales pitch

## ⏰ Schedule

- **9:00 AM** - Morning routine + LinkedIn post
- **2:00 PM** - Afternoon check
- **6:00 PM** - Evening routine + briefing
- **Every 2h** - Ralph loop (8 AM - 6 PM)
- **Monday 8 AM** - Weekly routine

## 🔐 Security

- LinkedIn session: `Watchers/linkedin_session/` (gitignored)
- WhatsApp session: `Watchers/whatsapp_session/` (gitignored)
- All posts require HITL approval
- Sensitive content auto-flagged

## 📞 Support

Check these files for details:
- `INSTALL_AND_TEST.md` - Full testing guide
- `SILVER_TIER_FINAL_SETUP.md` - Complete setup
- `SILVER_TIER_COMPLETE.md` - Architecture overview
- `Logs/*.log` - System logs
