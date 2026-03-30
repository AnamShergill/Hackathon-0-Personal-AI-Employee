# Silver Tier - Installation & Testing Guide

## Quick Start - Complete Silver Tier Setup

### Step 1: Install Dependencies
```bash
# Install the schedule library
uv pip install schedule --system

# Verify all dependencies
python -c "import schedule; print('✅ schedule installed')"
python -c "from playwright.sync_api import sync_playwright; print('✅ playwright installed')"
```

### Step 2: Create Required Folders
```bash
# Create all necessary folders
mkdir -p Pending_Approval
mkdir -p Approved
mkdir -p Briefings
mkdir -p schedulers
```

### Step 3: Verify File Structure
```bash
# Check all new files exist
ls Skills/08_LINKEDIN_POST_GENERATOR.md
ls Watchers/linkedin_poster.py
ls Watchers/approved_watcher.py
ls schedulers/daily_runner.py
ls run_all_watchers.py
```

## Testing Each Component

### Test 1: LinkedIn Post Generator ✅
```bash
# Generate a LinkedIn post
python -c "
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'\`\`\`python\n(.*?)\n\`\`\`', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"

# Check output
ls Pending_Approval/
cat Pending_Approval/linkedin_post_*.md
```

**Expected Result**: 
- New file in `Pending_Approval/` folder
- Contains professional LinkedIn post text
- Includes hashtags and CTA
- Character count shown

### Test 2: LinkedIn Poster (First Time Setup) ✅
```bash
# Run LinkedIn poster interactively
python Watchers/linkedin_poster.py
```

**What happens**:
1. Browser opens to LinkedIn
2. You'll be asked to login (ONE TIME ONLY)
3. Session is saved to `Watchers/linkedin_session/`
4. You can test posting a message
5. Future runs will reuse the session

**Expected Result**:
- Browser opens
- Login successful
- Session saved
- Test post appears on LinkedIn (if you confirm)

### Test 3: HITL Workflow (Manual) ✅
```bash
# Step 1: Generate a post
python -c "
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'\`\`\`python\n(.*?)\n\`\`\`', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"

# Step 2: Review the post
cat Pending_Approval/linkedin_post_*.md

# Step 3: Approve it (move to Approved/)
mv Pending_Approval/linkedin_post_*.md Approved/

# Step 4: Post manually
python Watchers/linkedin_poster.py Approved/linkedin_post_*.md
```

**Expected Result**:
- Post generated in Pending_Approval/
- You review and edit if needed
- Move to Approved/
- LinkedIn poster publishes it
- File moved to Done/ with timestamp

### Test 4: Approved Watcher (Automated HITL) ✅
```bash
# Terminal 1: Start the approved watcher
python Watchers/approved_watcher.py

# Terminal 2: Generate and approve a post
python -c "
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'\`\`\`python\n(.*?)\n\`\`\`', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"

# Wait a moment, then approve
sleep 5
mv Pending_Approval/linkedin_post_*.md Approved/

# Watch Terminal 1 - should detect and post automatically within 30 seconds
```

**Expected Result**:
- Watcher detects new file in Approved/
- Calls linkedin_poster.py automatically
- Post appears on LinkedIn
- File moved to Done/
- Logs show success

### Test 5: Scheduler ✅
```bash
# Test individual scheduler functions
python -c "
import sys
sys.path.insert(0, '.')
from schedulers.daily_runner import generate_linkedin_post
generate_linkedin_post()
"

# Test briefing generation
python -c "
import sys
sys.path.insert(0, '.')
from schedulers.daily_runner import generate_weekly_briefing
generate_weekly_briefing()
"

# Check outputs
ls Pending_Approval/  # Should have new LinkedIn post
ls Briefings/         # Should have briefing file
```

**Expected Result**:
- LinkedIn post generated
- Briefing created in Briefings/
- Dashboard updated

### Test 6: Run Full Scheduler ✅
```bash
# Run the scheduler (will execute tasks at scheduled times)
python schedulers/daily_runner.py

# Or run in background (Windows)
start /B python schedulers/daily_runner.py

# Check logs
tail -f Logs/scheduler.log
```

**Expected Result**:
- Scheduler starts
- Shows configured schedule
- Runs tasks at specified times
- Logs all activity

### Test 7: Master Runner (All Components) ✅
```bash
# Start everything at once
python run_all_watchers.py

# This starts:
# - Gmail Watcher (300s interval)
# - WhatsApp Watcher (60s interval)
# - Approved Watcher (30s interval)
# - Scheduler (daily tasks)
```

**Expected Result**:
- All 4 components start
- Each runs in separate thread
- Logs to Logs/master_runner.log
- Press Ctrl+C to stop all

## Complete End-to-End Test

### Scenario: Generate and Post LinkedIn Content

```bash
# 1. Start the approved watcher
python Watchers/approved_watcher.py &

# 2. Generate a LinkedIn post
python -c "
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'\`\`\`python\n(.*?)\n\`\`\`', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"

# 3. Review the generated post
cat Pending_Approval/linkedin_post_*.md

# 4. Edit if needed (optional)
nano Pending_Approval/linkedin_post_*.md

# 5. Approve by moving to Approved/
mv Pending_Approval/linkedin_post_*.md Approved/

# 6. Wait for approved watcher to detect and post (max 30 seconds)
# Watch the logs or check LinkedIn

# 7. Verify post on LinkedIn
# Open https://www.linkedin.com/feed/

# 8. Check Done/ folder for completed file
ls Done/
cat Done/linkedin_post_*.md
```

## Verification Checklist

After testing, verify:

- [ ] LinkedIn post generator creates posts in Pending_Approval/
- [ ] LinkedIn poster can login and save session
- [ ] LinkedIn poster can publish posts
- [ ] Approved watcher detects files in Approved/
- [ ] Approved watcher triggers linkedin_poster.py
- [ ] Posts appear on LinkedIn
- [ ] Files move to Done/ after posting
- [ ] Scheduler runs tasks at correct times
- [ ] Dashboard tracks LinkedIn activity
- [ ] Logs capture all activity

## Troubleshooting

### Issue: LinkedIn login fails
```bash
# Solution: Run in non-headless mode
# Edit linkedin_poster.py line: headless=False (already set)
# Try manual login in regular browser first
```

### Issue: Approved watcher not detecting files
```bash
# Check watcher is running
ps aux | grep approved_watcher

# Check logs
cat Logs/approved_watcher.log

# Verify file naming
ls Approved/
```

### Issue: Scheduler not running tasks
```bash
# Check system time
date

# Test individual functions
python -c "from schedulers.daily_runner import morning_routine; morning_routine()"

# Check logs
cat Logs/scheduler.log
```

### Issue: Import errors
```bash
# Ensure you're in the correct directory
pwd

# Should be: .../Bronze-Tier/

# Reinstall dependencies
uv pip install -e . --system
```

## Production Deployment

### Option 1: Run as Background Services (Linux/Mac)
```bash
# Create systemd service files or use screen/tmux
screen -S ai-employee
python run_all_watchers.py
# Ctrl+A, D to detach
```

### Option 2: Windows Task Scheduler
```batch
# Create start_ai_employee.bat:
@echo off
cd /d C:\Users\Bruno\Desktop\projects\Hackathon-0\Bronze-Tier
python run_all_watchers.py

# Add to Task Scheduler:
# - Trigger: At startup
# - Action: Run start_ai_employee.bat
```

### Option 3: Docker (Future)
```dockerfile
# TODO: Create Dockerfile for containerized deployment
```

## Monitoring

### Check System Status
```bash
# Check all logs
ls -lh Logs/

# View recent activity
tail -n 50 Logs/master_runner.log
tail -n 50 Logs/linkedin_poster.log
tail -n 50 Logs/approved_watcher.log
tail -n 50 Logs/scheduler.log

# Check folder status
echo "Needs Action: $(ls Needs_Action/ | wc -l) files"
echo "Pending Approval: $(ls Pending_Approval/ | wc -l) files"
echo "Approved: $(ls Approved/ | wc -l) files"
echo "Done: $(ls Done/ | wc -l) files"
echo "Plans: $(ls Plans/ | wc -l) files"
```

### Dashboard Updates
```bash
# View dashboard
cat Dashboard.md

# Should show:
# - LinkedIn posts drafted
# - LinkedIn posts published
# - Recent activity with timestamps
```

## Silver Tier Completion Checklist

- [x] Multi-source automation (Gmail + WhatsApp)
- [x] LinkedIn post generation (5 types)
- [x] LinkedIn posting automation (Playwright MCP)
- [x] HITL approval workflow (Pending → Approved → Done)
- [x] Approved watcher (automated posting)
- [x] Scheduling system (daily/weekly tasks)
- [x] Dashboard tracking
- [x] Error handling and logging
- [x] Session persistence
- [x] Security and privacy

## Next Steps - Gold Tier

1. **MCP Gmail Send**: Actually send approved email replies
2. **MCP WhatsApp Send**: Send approved WhatsApp replies
3. **Odoo Integration**: Sync with CRM/ERP
4. **CEO Briefings**: Weekly executive summaries
5. **Analytics Dashboard**: Track metrics and ROI
6. **Image Generation**: Auto-generate images for posts
7. **A/B Testing**: Test different post variations
8. **Multi-language Support**: Handle multiple languages

## Summary

Silver Tier is now 100% complete! 🎉

You have:
- ✅ Automated LinkedIn posting
- ✅ MCP integration (Playwright-based)
- ✅ HITL approval workflow
- ✅ Scheduling system
- ✅ Multi-source message handling
- ✅ Complete logging and monitoring

Ready to move to Gold Tier! 🚀
