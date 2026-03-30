#!/usr/bin/env python3
"""
Reorganize AI Employee codebase into Bronze/Silver/Gold tiers
"""
import os
import shutil
from pathlib import Path

# Current structure: everything in Bronze-Tier/
# Target: Bronze-Tier/, Silver-Tier/, Gold-Tier/ at root level

ROOT = Path(".")
BRONZE_SRC = ROOT / "Bronze-Tier"
SILVER_DST = ROOT / "Silver-Tier"
GOLD_DST = ROOT / "Gold-Tier"

# Classification of files by tier
BRONZE_FILES = {
    # Core Bronze watchers
    "Watchers/gmail_watcher.py",
    "Watchers/base_watcher.py",
    "Watchers/__init__.py",
    
    # Bronze skills (01-07)
    "Skills/01_EMAIL_PROCESSOR.md",
    "Skills/02_EMAIL_REPLY_DRAFTER.md",
    "Skills/03_TASK_EXTRACTOR.md",
    "Skills/04_PRIORITY_SCORER.md",
    "Skills/05_DASHBOARD_UPDATER.md",
    "Skills/06_ARCHIVE_CLEANER.md",
    "Skills/email_processor.py",
    
    # Bronze docs
    "START_HERE.md",
    "INSTALL_AND_TEST.md",
    "TROUBLESHOOTING.md",
    "demo_guide.md",
    
    # Debug scripts (Bronze era)
    "debug_gmail.py",
    "debug_unread_detection.py",
    "test_gmail_query.py",
}

SILVER_FILES = {
    # Silver watchers
    "Watchers/whatsapp_watcher.py",
    "Watchers/linkedin_poster.py",
    
    # Silver skills
    "Skills/00_MAIN_ORCHESTRATOR.md",
    "Skills/08_LINKEDIN_POST_GENERATOR.md",
    "Skills/09_WHATSAPP_PROCESSOR.md",
    
    # Silver docs
    "BRONZE_VS_SILVER.md",
    "SILVER_TIER_ACHIEVEMENT.md",
    "SILVER_TIER_COMPLETE.md",
    "SILVER_TIER_FINAL_SETUP.md",
    "SILVER_TIER_MULTI_SOURCE_GUIDE.md",
    "SILVER_TIER_README.md",
    "SILVER_TIER_SETUP.md",
    "QUICK_START_SILVER.md",
    "VERIFY_SILVER_TIER.md",
    
    # WhatsApp docs
    "WHATSAPP_TROUBLESHOOTING.md",
    "WHATSAPP_UNREAD_MANUAL_CHECK.md",
    "WHATSAPP_WATCHER_FIX.md",
    "WHATSAPP_WATCHER_SUMMARY.md",
    "FIX_WHATSAPP_NOW.md",
    
    # LinkedIn docs
    "LINKEDIN_SETUP_MANUAL.md",
    "setup_linkedin.py",
    
    # Silver scripts
    "orchestrator.py",
    "run_both_watchers.py",
    "test_multi_source.py",
    "test_silver_tier.py",
    "test_whatsapp_simple.py",
    "test_whatsapp_unread.py",
    "fix_whatsapp_detection.py",
    "debug_whatsapp_live.py",
    "debug_whatsapp_selectors.py",
    "setup_silver_tier.sh",
}

GOLD_FILES = {
    # Gold actions
    "actions/email_sender.py",
    
    # Gold skills
    "Skills/10_EMAIL_SENDER.md",
    
    # Gold watcher (enhanced version)
    "Watchers/approved_watcher.py",
    
    # Gold docs
    "GOLD_TIER_AUTO_EMAIL_WORKFLOW.md",
    "GOLD_TIER_EMAIL_SENDER_COMPLETE.md",
    "TEST_EMAIL_SENDER.md",
    "DO_THIS_NOW.md",
}

# Shared files (copy to all tiers or keep at root)
SHARED_FILES = {
    "Dashboard.md",
    "Company_Handbook.md",
    "QUICK_REFERENCE.md",
    "CLAUDE.md",
    "GITHUB_PUSH_GUIDE.md",
    "push_to_github.sh",
    "README.md",
    "README_LOCAL.md",
}

# Root-only files
ROOT_FILES = {
    ".env",
    ".env.example",
    ".gitignore",
    "credentials.json",
    "token.json",
    "pyproject.toml",
    "uv.lock",
    "LICENSE",
}

# Shared folders (copy to Gold, reference from others)
SHARED_FOLDERS = {
    "Plans",
    "Logs",
}

# Tier-specific folders
BRONZE_FOLDERS = {
    "Inbox",
    "Needs_Action",
    "Done",
    "Archive_Feb16",
}

SILVER_FOLDERS = {
    "Briefings",
}

GOLD_FOLDERS = {
    "Pending_Approval",
    "Approved",
}


def create_tier_structure():
    """Create folder structure for each tier"""
    print("Creating tier folder structures...")
    
    # Bronze structure
    for folder in ["Watchers", "Skills", "Inbox", "Needs_Action", "Done", "Archive_Feb16", "Plans", "Logs"]:
        (BRONZE_SRC / folder).mkdir(parents=True, exist_ok=True)
    
    # Silver structure
    for folder in ["Watchers", "Skills", "Briefings", "Plans", "Logs"]:
        (SILVER_DST / folder).mkdir(parents=True, exist_ok=True)
    
    # Gold structure
    for folder in ["Watchers", "Skills", "actions", "Pending_Approval", "Approved", "Approved/Done", "Plans", "Logs", "schedulers"]:
        (GOLD_DST / folder).mkdir(parents=True, exist_ok=True)
    
    print("✓ Folder structures created")


def copy_file_safe(src, dst):
    """Copy file if it exists, create parent dirs"""
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False


def move_to_silver():
    """Move Silver-specific files to Silver-Tier"""
    print("\nMoving Silver Tier files...")
    moved = 0
    
    for file_path in SILVER_FILES:
        src = BRONZE_SRC / file_path
        dst = SILVER_DST / file_path
        if copy_file_safe(src, dst):
            print(f"  ✓ {file_path}")
            moved += 1
    
    # Copy session folders if they exist
    for session_folder in ["Watchers/whatsapp_session", "Watchers/linkedin_session"]:
        src = BRONZE_SRC / session_folder
        dst = SILVER_DST / session_folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✓ {session_folder}/")
            moved += 1
    
    print(f"✓ Moved {moved} Silver items")


def move_to_gold():
    """Move Gold-specific files to Gold-Tier"""
    print("\nMoving Gold Tier files...")
    moved = 0
    
    for file_path in GOLD_FILES:
        src = BRONZE_SRC / file_path
        dst = GOLD_DST / file_path
        if copy_file_safe(src, dst):
            print(f"  ✓ {file_path}")
            moved += 1
    
    # Copy schedulers
    src = BRONZE_SRC / "schedulers"
    dst = GOLD_DST / "schedulers"
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"  ✓ schedulers/")
        moved += 1
    
    # Copy run_all_watchers.py
    src = BRONZE_SRC / "run_all_watchers.py"
    dst = GOLD_DST / "run_all_watchers.py"
    if copy_file_safe(src, dst):
        print(f"  ✓ run_all_watchers.py")
        moved += 1
    
    print(f"✓ Moved {moved} Gold items")


def copy_shared_files():
    """Copy shared files to Gold (active workspace)"""
    print("\nCopying shared files to Gold-Tier...")
    copied = 0
    
    for file_path in SHARED_FILES:
        src = BRONZE_SRC / file_path
        dst = GOLD_DST / file_path
        if copy_file_safe(src, dst):
            print(f"  ✓ {file_path}")
            copied += 1
    
    # Copy shared folders to Gold
    for folder in SHARED_FOLDERS:
        src = BRONZE_SRC / folder
        dst = GOLD_DST / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✓ {folder}/")
            copied += 1
    
    print(f"✓ Copied {copied} shared items to Gold")


def copy_root_files():
    """Copy root-level config files to project root"""
    print("\nCopying root configuration files...")
    copied = 0
    
    for file_path in ROOT_FILES:
        src = BRONZE_SRC / file_path
        dst = ROOT / file_path
        if src.exists() and not dst.exists():  # Don't overwrite existing
            shutil.copy2(src, dst)
            print(f"  ✓ {file_path}")
            copied += 1
    
    print(f"✓ Copied {copied} root files")


def create_readmes():
    """Create README files for each tier"""
    print("\nCreating tier README files...")
    
    # Bronze README
    bronze_readme = """# Bronze Tier - Email-Only Automation

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
"""
    
    # Silver README
    silver_readme = """# Silver Tier - Multi-Source Automation

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
"""
    
    # Gold README
    gold_readme = """# Gold Tier - Automated Email Workflow (Active Workspace)

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
"""
    
    # Root README
    root_readme = """# AI Employee Vault - Multi-Tier Architecture

## Project Structure

This project is organized into three progressive tiers:

### Bronze Tier - Email-Only Automation
Basic email monitoring, processing, and reply drafting.
- **Location**: `Bronze-Tier/`
- **Status**: Complete ✅
- **Features**: Gmail watcher, email processor, task extraction

### Silver Tier - Multi-Source Automation
Adds WhatsApp and LinkedIn automation.
- **Location**: `Silver-Tier/`
- **Status**: Complete ✅
- **Features**: WhatsApp watcher, LinkedIn poster, multi-source orchestration

### Gold Tier - Automated Email Workflow
Complete automation with email sending and advanced workflows.
- **Location**: `Gold-Tier/` (Active Workspace)
- **Status**: In Development 🚧
- **Features**: Email sender, approval workflow, scheduling

## Quick Start

### For Development (Gold Tier)
```bash
cd Gold-Tier
python run_all_watchers.py
```

### For Testing Bronze Features
```bash
cd Bronze-Tier
python Watchers/gmail_watcher.py
```

### For Testing Silver Features
```bash
cd Silver-Tier
python Watchers/whatsapp_watcher.py
```

## Configuration

Root-level configuration files:
- `.env` - SMTP and API credentials
- `.env.example` - Template for credentials
- `credentials.json` - Gmail API credentials
- `token.json` - Gmail OAuth token
- `pyproject.toml` - Python dependencies

## Installation

```bash
# Install dependencies
uv pip install -e . --system

# Install Playwright (for Silver/Gold)
playwright install chromium
```

## Documentation

Each tier has its own README with specific instructions:
- `Bronze-Tier/README.md`
- `Silver-Tier/README.md`
- `Gold-Tier/README.md`

## Git Workflow

```bash
# Push changes
./push_to_github.sh "Your commit message"
```

## Support

See tier-specific documentation for troubleshooting:
- Bronze: `Bronze-Tier/TROUBLESHOOTING.md`
- Silver: `Silver-Tier/WHATSAPP_TROUBLESHOOTING.md`
- Gold: `Gold-Tier/TEST_EMAIL_SENDER.md`
"""
    
    # Write READMEs with UTF-8 encoding
    (BRONZE_SRC / "README_TIER.md").write_text(bronze_readme, encoding='utf-8')
    (SILVER_DST / "README.md").write_text(silver_readme, encoding='utf-8')
    (GOLD_DST / "README.md").write_text(gold_readme, encoding='utf-8')
    (ROOT / "README_TIERS.md").write_text(root_readme, encoding='utf-8')
    
    print("✓ Created README files for all tiers")


def main():
    """Execute reorganization"""
    print("=" * 60)
    print("AI Employee Vault - Tier Reorganization")
    print("=" * 60)
    
    # Step 1: Create structure
    create_tier_structure()
    
    # Step 2: Move Silver files
    move_to_silver()
    
    # Step 3: Move Gold files
    move_to_gold()
    
    # Step 4: Copy shared files
    copy_shared_files()
    
    # Step 5: Copy root files
    copy_root_files()
    
    # Step 6: Create READMEs
    create_readmes()
    
    print("\n" + "=" * 60)
    print("✅ Reorganization Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the new structure")
    print("2. Update import paths in code (see path_fixes.py)")
    print("3. Test each tier independently")
    print("4. Work in Gold-Tier/ as active workspace")
    print("\nFolder structure:")
    print("  Bronze-Tier/  - Original email-only system")
    print("  Silver-Tier/  - Multi-source automation")
    print("  Gold-Tier/    - Active workspace with email sending")


if __name__ == "__main__":
    main()
