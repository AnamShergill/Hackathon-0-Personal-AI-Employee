# Silver Tier - Final Setup & Testing Guide

## 🎉 Silver Tier Complete!

All Silver Tier requirements are now implemented:
- ✅ Multi-source automation (Gmail + WhatsApp)
- ✅ LinkedIn post generation and automation
- ✅ MCP integration (Playwright-based LinkedIn poster)
- ✅ Explicit HITL approval workflow
- ✅ Basic scheduling (cron-like with Python schedule)

## Installation

### 1. Install Dependencies
```bash
# Install schedule library
uv pip install schedule --system

# Or reinstall all dependencies
uv pip install -e . --system
```

### 2. Create Required Folders
```bash
# Create folders if they don't exist
mkdir -p Pending_Approval
mkdir -p Approved
mkdir -p Briefings
mkdir -p schedulers
```

### 3. Update .gitignore
Already updated to ignore:
- `Watchers/linkedin_session/` (LinkedIn browser session)
- `Logs/approved_processed.txt` (tracking file)

## Components Overview

### 1. LinkedIn Post Generator
**File**: `Skills/08_LINKEDIN_POST_GENERATOR.md`

**Purpose**: Generates professional, sales-oriented LinkedIn posts

**Features**:
- 5 post types: business_update, industry_insight, problem_solution, behind_the_scenes, call_to_action
- Optimized length (150-300 chars for engagement)
- Hashtags and CTAs included
- Image prompts for AI image generation
- Saves to Pending_Approval/ for HITL review

**Usage**:
```bash
# Generate random post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])"

# Or add to Ralph loop
```

### 2. LinkedIn Poster (MCP Integration)
**File**: `Watchers/linkedin_poster.py`

**Purpose**: Automates posting to LinkedIn using Playwright

**Features**:
- Persistent browser session (login once)
- Automated post creation
- Screenshot capture for verification
- Error handling and retries
- Session stored in `Watchers/linkedin_session/`

**First-Time Setup**:
```bash
# Run interactive test
python Watchers/linkedin_poster.py

# This will:
# 1. Open LinkedIn in browser
# 2. Ask you to login (one time only)
# 3. Save session for future use
# 4. Post a test message (if you confirm)
```

**Post Approved Content**:
```bash
# Post specific file
python Watchers/linkedin_poster.py Approved/linkedin_post_*.md
```

### 3. Approved Watcher (HITL Workflow)
**File**: `Watchers/approved_watcher.py`

**Purpose**: Monitors Approved/ folder and triggers actions

**Features**:
- Polls Approved/ every 30 seconds
- Detects LinkedIn posts, email replies, WhatsApp replies
- Calls appropriate poster/sender
- Tracks processed files
- Moves completed items to Done/

**Usage**:
```bash
# Run continuously
python Watchers/approved_watcher.py

# Or run in background (Windows)
start /B python Watchers/approved_watcher.py
```

### 4. Daily Runner (Scheduler)
**File**: `schedulers/daily_runner.py`

**Purpose**: Runs tasks on a schedule

**Schedule**:
- **9:00 AM**: Morning routine (Ralph loop + LinkedIn post)
- **2:00 PM**: Afternoon routine (Ralph loop)
- **6:00 PM**: Evening routine (Ralph loop + briefing)
- **Every 2 hours (8 AM - 6 PM)**: Ralph loop
- **Monday 8:00 AM**: Weekly routine (briefing + cleanup)

**Usage**:
```bash
# Run scheduler
python schedulers/daily_runner.py

# Or run in background
start /B python schedulers/daily_runner.py
```

## HITL Workflow

### Complete Flow:
```
1. Generate Content
   ├─ LinkedIn Post Generator → Pending_Approval/
   ├─ Email Reply Drafter → Pending_Approval/
   └─ WhatsApp Reply Drafter → Pending_Approval/

2. Human Reviews
   ├─ Open file in Pending_Approval/
   ├─ Edit if needed
   └─ Move to Approved/ when ready

3. Approved Watcher Detects
   ├─ Polls Approved/ every 30s
   ├─ Identifies file type
   └─ Triggers appropriate action

4. Action Executed
   ├─ LinkedIn → linkedin_poster.py
   ├─ Email → (future: MCP Gmail)
   └─ WhatsApp → (future: MCP WhatsApp)

5. Completion
   └─ File moved to Done/ with timestamp
```

## Testing Guide

### Test 1: Generate LinkedIn Post
```bash
# 1. Generate a post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])"

# 2. Check Pending_Approval/
ls Pending_Approval/

# 3. Review the post
cat Pending_Approval/linkedin_post_*.md

# 4. If approved, move to Approved/
mv Pending_Approval/linkedin_post_*.md Approved/
```

### Test 2: Post to LinkedIn (Manual)
```bash
# 1. Run LinkedIn poster interactively
python Watchers/linkedin_poster.py

# 2. Login when prompted (first time only)
# 3. Confirm test post
# 4. Verify post appears on LinkedIn
```

### Test 3: Full HITL Workflow
```bash
# Terminal 1: Start approved watcher
python Watchers/approved_watcher.py

# Terminal 2: Generate and approve post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])"
mv Pending_Approval/linkedin_post_*.md Approved/

# Watch Terminal 1 - should detect and post automatically
```

### Test 4: Scheduler
```bash
# Run scheduler (will execute tasks at scheduled times)
python schedulers/daily_runner.py

# Or test individual functions:
python -c "from schedulers.daily_runner import generate_linkedin_post; generate_linkedin_post()"
python -c "from schedulers.daily_runner import generate_weekly_briefing; generate_weekly_briefing()"
```

## Dashboard Updates

Update your Dashboard.md to track LinkedIn activity:

```markdown
## Active Watchers
- **Gmail Watcher**: `Running (300s interval)`
- **WhatsApp Watcher**: `Running (60s interval)`
- **Approved Watcher**: `Running (30s interval)`
- **Scheduler**: `Running (daily tasks)`

## Social Media Activity
- **LinkedIn Posts Drafted**: `5 this week`
- **LinkedIn Posts Published**: `3 this week`
- **Pending Approval**: `2 posts`

## Recent Activity Log
```
[2026-03-20 18:00:00] LinkedIn Post Generator: Created new post draft
[2026-03-20 18:05:00] Approved Watcher: Posted to LinkedIn successfully
[2026-03-20 18:05:05] File moved to Done/: linkedin_post_call_to_action_*.md
```
```

## Windows Task Scheduler Setup (Optional)

To run watchers and scheduler automatically on Windows:

### 1. Create Batch Files

**start_watchers.bat**:
```batch
@echo off
cd /d C:\Users\Bruno\Desktop\projects\Hackathon-0\Bronze-Tier
start "Gmail Watcher" python Watchers\gmail_watcher.py
start "WhatsApp Watcher" python Watchers\whatsapp_watcher.py
start "Approved Watcher" python Watchers\approved_watcher.py
start "Scheduler" python schedulers\daily_runner.py
```

### 2. Add to Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Name: "AI Employee Watchers"
4. Trigger: At startup
5. Action: Start a program
6. Program: `C:\path\to\start_watchers.bat`
7. Finish

## Troubleshooting

### LinkedIn Login Issues
**Problem**: Can't login to LinkedIn
**Solution**: 
- Run in non-headless mode: `headless=False`
- Check for 2FA requirements
- Verify credentials
- Try manual login in regular browser first

### Approved Watcher Not Detecting Files
**Problem**: Files in Approved/ not being processed
**Solution**:
- Check watcher is running: `ps aux | grep approved_watcher`
- Check file naming matches patterns
- Check logs: `cat Logs/approved_watcher.log`
- Verify file has correct frontmatter

### Scheduler Not Running Tasks
**Problem**: Scheduled tasks not executing
**Solution**:
- Check system time is correct
- Verify scheduler is running
- Check logs: `cat Logs/scheduler.log`
- Test individual functions manually

### LinkedIn Posting Fails
**Problem**: Post doesn't appear on LinkedIn
**Solution**:
- Check screenshots in Logs/
- Verify selectors are current (LinkedIn changes UI)
- Try manual posting in browser
- Check for LinkedIn rate limits

## Security Notes

1. **LinkedIn Session**: Stored locally in `Watchers/linkedin_session/`
   - Never commit to git (already in .gitignore)
   - Contains login cookies
   - Regenerate if compromised

2. **HITL Approval**: Always required for:
   - LinkedIn posts (public visibility)
   - Email replies (external communication)
   - WhatsApp replies (client communication)

3. **Sensitive Content**: Automatically flagged:
   - Financial mentions
   - Personal information
   - Contracts/legal content
   - File attachments

## Next Steps (Gold Tier)

1. **MCP Gmail Send**: Actually send approved email replies
2. **MCP WhatsApp Send**: Send approved WhatsApp replies
3. **Odoo Integration**: Sync with CRM/ERP
4. **CEO Briefings**: Weekly executive summaries
5. **Analytics Dashboard**: Track metrics and ROI
6. **Multi-language Support**: Handle multiple languages
7. **Image Generation**: Auto-generate images for posts
8. **A/B Testing**: Test different post variations

## Summary

Silver Tier is now 100% complete with:
- ✅ Multi-source automation (Gmail, WhatsApp)
- ✅ LinkedIn post generation (5 types)
- ✅ LinkedIn posting automation (Playwright MCP)
- ✅ HITL approval workflow (Pending → Approved → Done)
- ✅ Scheduling system (daily/weekly tasks)
- ✅ Dashboard tracking
- ✅ Error handling and logging
- ✅ Session persistence
- ✅ Security and privacy

Ready for Gold Tier! 🚀
