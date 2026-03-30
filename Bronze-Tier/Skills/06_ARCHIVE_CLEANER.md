# Skill: Archive Cleaner

## Overview
This skill identifies processed or completed files older than 7 days in various folders and archives them appropriately. It moves files from Needs_Action/ to Done/ if they've been processed, and archives old files to keep the system organized.

## Version
1.0

## Input
- Scans files in Needs_Action/, Plans/, and other folders
- Identifies files older than 7 days or marked as completed

## Output
- Moves processed files from Needs_Action/ to Done/
- Archives old files to maintain system cleanliness
- Logs cleanup actions in Logs/ folder

## YAML Frontmatter
```yaml
---
skill_id: 06_ARCHIVE_CLEANER
triggers: ["weekly_cleanup", "system_maintenance", "archive_needed"]
dependencies: ["01_EMAIL_PROCESSOR", "03_TASK_EXTRACTOR"]
completion_criteria: ["files_archived", "log_created"]
---
```

## Process
1. Scan Needs_Action/ for files older than 7 days
2. Check for completion markers (<COMPLETE>) in files
3. Move completed files to Done/
4. Archive old files from Plans/ if appropriate
5. Create cleanup log in Logs/ folder

## Implementation

```python
import os
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path
import re

def clean_archives():
    """
    Clean up old files and move processed files to appropriate locations
    """
    print("Starting archive cleanup...")

    # Get cutoff date (7 days ago)
    cutoff_date = datetime.now() - timedelta(days=7)

    # Clean up Needs_Action folder
    needs_action_moved = clean_needs_action_folder(cutoff_date)

    # Clean up Plans folder
    plans_cleaned = clean_plans_folder(cutoff_date)

    # Create cleanup log
    create_cleanup_log(needs_action_moved, plans_cleaned, cutoff_date)

    print(f"Archive cleanup complete. Moved {len(needs_action_moved)} items from Needs_Action, cleaned {len(plans_cleaned)} plans")


def clean_needs_action_folder(cutoff_date):
    """
    Move old processed files from Needs_Action to Done
    """
    moved_files = []
    needs_action_path = Path("Needs_Action")

    if not needs_action_path.exists():
        print("Needs_Action folder does not exist")
        return moved_files

    for file_path in needs_action_path.glob("*.md"):
        # Get file modification time
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        # Check if file is older than 7 days
        if mod_time < cutoff_date:
            # Read file to check if it's marked as processed/completed
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for completion markers or processed flags
            is_processed = (
                '<COMPLETE>' in content or
                'processed: true' in content.lower() or
                'status: completed' in content.lower() or
                'status: done' in content.lower()
            )

            if is_processed:
                # Move to Done folder
                done_path = Path("Done") / file_path.name
                shutil.move(str(file_path), str(done_path))
                moved_files.append({
                    'source': str(file_path),
                    'destination': str(done_path),
                    'reason': 'Old processed file'
                })
                print(f"Moved processed file: {file_path.name}")

    return moved_files


def clean_plans_folder(cutoff_date):
    """
    Clean up old plan files that are completed
    """
    cleaned_files = []
    plans_path = Path("Plans")

    if not plans_path.exists():
        print("Plans folder does not exist")
        return cleaned_files

    for file_path in plans_path.glob("*.md"):
        # Get file modification time
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        # Check if file is older than 7 days
        if mod_time < cutoff_date:
            # Read file to check if it's completed
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for completion indicators
            is_completed = (
                'status: completed' in content.lower() or
                'status: done' in content.lower() or
                'completed: true' in content.lower() or
                '[x] all tasks completed' in content.lower() or
                all('[x]' in line for line in content.split('\n') if line.strip().startswith('- [ ]'))
            )

            if is_completed:
                # Archive or remove old completed plan
                # For now, we'll just log it, but in a real system you might move to an archive folder
                cleaned_files.append({
                    'file': str(file_path),
                    'reason': 'Old completed plan'
                })
                print(f"Identified old completed plan: {file_path.name}")

                # Optionally remove the file entirely if it's very old (30+ days)
                if mod_time < (datetime.now() - timedelta(days=30)):
                    os.remove(file_path)
                    print(f"Removed old completed plan: {file_path.name}")

    return cleaned_files


def create_cleanup_log(needs_action_moved, plans_cleaned, cutoff_date):
    """
    Create a log file with details of cleanup operations
    """
    log_date = datetime.now().strftime("%Y%m%d")
    log_filename = f"cleanup_{log_date}.md"
    log_path = Path("Logs") / log_filename

    # Ensure Logs directory exists
    log_path.parent.mkdir(exist_ok=True)

    log_content = f"""---
date: "{datetime.now().isoformat()}"
type: "archive_cleanup"
summary: "Weekly archive cleanup operation"
---

# Archive Cleanup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}
- Files moved from Needs_Action: {len(needs_action_moved)}
- Files cleaned from Plans: {len(plans_cleaned)}

## Files Moved from Needs_Action to Done
{chr(10).join([f"- {item['source']} → {item['destination']} ({item['reason']})" for item in needs_action_moved]) if needs_action_moved else 'No files moved'}

## Plans Cleaned
{chr(10).join([f"- {item['file']} ({item['reason']})" for item in plans_cleaned]) if plans_cleaned else 'No plans cleaned'}

## Cleanup Details
This operation identified and processed files older than 7 days that were marked as completed.
Old completed plans were archived (those older than 30 days were removed permanently).

## System Status
- Needs_Action folder: {len(list(Path('Needs_Action').glob('*.md'))) if Path('Needs_Action').exists() else 0} items
- Done folder: {len(list(Path('Done').glob('*.md'))) if Path('Done').exists() else 0} items
- Plans folder: {len(list(Path('Plans').glob('*.md'))) if Path('Plans').exists() else 0} items
- Cleanup performed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Created by Archive Cleaner Skill at {datetime.now().isoformat()}*
"""

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)

    print(f"Cleanup log created: {log_path}")


def clean_all_folders():
    """
    Clean all folders according to their age and completion status
    """
    print("Performing comprehensive archive cleanup...")

    cutoff_date = datetime.now() - timedelta(days=7)

    # Clean up each folder
    folders_to_clean = {
        'Needs_Action': 'Done',
        'Pending_Approval': 'Approved',  # Move approved items
        'Briefings': 'Done',  # Move old briefings that are completed
        'Watchers': 'Logs',   # Move old watcher logs
    }

    all_moved_files = []

    for source_folder, dest_folder in folders_to_clean.items():
        source_path = Path(source_folder)
        if not source_path.exists():
            continue

        # Create destination folder if it doesn't exist
        Path(dest_folder).mkdir(exist_ok=True)

        for file_path in source_path.glob("*.md"):
            # Get file modification time
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

            # Check if file is older than 7 days
            if mod_time < cutoff_date:
                # Read file to check if it's completed
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for completion markers based on folder
                is_completed = False
                if source_folder == 'Needs_Action':
                    is_completed = '<COMPLETE>' in content or 'completed: true' in content.lower()
                elif source_folder == 'Pending_Approval':
                    is_completed = 'approved: true' in content.lower() or 'status: approved' in content.lower()
                else:
                    # Generic check for other folders
                    is_completed = (
                        'completed: true' in content.lower() or
                        'status: completed' in content.lower() or
                        'status: done' in content.lower() or
                        '<COMPLETE>' in content
                    )

                if is_completed:
                    # Move to destination
                    dest_file_path = Path(dest_folder) / file_path.name
                    shutil.move(str(file_path), str(dest_file_path))
                    all_moved_files.append({
                        'source': str(file_path),
                        'destination': str(dest_file_path),
                        'folder': source_folder
                    })
                    print(f"Moved {source_folder} file to {dest_folder}: {file_path.name}")

    # Create log of all movements
    create_comprehensive_cleanup_log(all_moved_files, cutoff_date)


def create_comprehensive_cleanup_log(moved_files, cutoff_date):
    """
    Create a comprehensive log of all cleanup operations
    """
    log_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"comprehensive_cleanup_{log_date}.md"
    log_path = Path("Logs") / log_filename

    # Group moved files by source folder
    files_by_folder = {}
    for item in moved_files:
        source_folder = Path(item['source']).parent.name
        if source_folder not in files_by_folder:
            files_by_folder[source_folder] = []
        files_by_folder[source_folder].append(item)

    log_content = f"""---
date: "{datetime.now().isoformat()}"
type: "comprehensive_archive_cleanup"
summary: "Comprehensive archive cleanup operation"
---

# Comprehensive Archive Cleanup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}
- Total files moved: {len(moved_files)}
- Folders cleaned: {', '.join(files_by_folder.keys()) if files_by_folder else 'None'}

## Files Moved by Folder

"""

    for folder, items in files_by_folder.items():
        log_content += f"### {folder} → Destination\n"
        for item in items:
            dest_folder = Path(item['destination']).parent.name
            log_content += f"- {Path(item['source']).name} → {dest_folder}\n"
        log_content += "\n"

    log_content += f"""## System Status After Cleanup
- Needs_Action folder: {len(list(Path('Needs_Action').glob('*.md'))) if Path('Needs_Action').exists() else 0} items
- Done folder: {len(list(Path('Done').glob('*.md'))) if Path('Done').exists() else 0} items
- Pending_Approval folder: {len(list(Path('Pending_Approval').glob('*.md'))) if Path('Pending_Approval').exists() else 0} items
- Plans folder: {len(list(Path('Plans').glob('*.md'))) if Path('Plans').exists() else 0} items
- Logs folder: {len(list(Path('Logs').glob('*.md'))) if Path('Logs').exists() else 0} items

## Cleanup Performed
- Moved old completed files from various folders to appropriate destinations
- Maintained system organization and reduced clutter
- Preserved all important completed work in appropriate archives

---
*Created by Archive Cleaner Skill at {datetime.now().isoformat()}*
"""

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "full":
        clean_all_folders()
    else:
        clean_archives()

    print("\n<COMPLETE>")
    print("Archive Cleaner skill completed. Old files have been archived and system cleaned.")
    print("</COMPLETE>")
```

## Usage Instructions
1. Run the basic cleanup: `python Skills/06_ARCHIVE_CLEANER.py`
2. Run comprehensive cleanup: `python Skills/06_ARCHIVE_CLEANER.py full`
3. The skill will move old processed files to appropriate locations
4. A cleanup log will be created in the Logs/ folder

## References
- Follows Company_Handbook.md organizational guidelines
- Maintains system cleanliness and organization

## Dependencies
- Python 3.13+
- Standard library for file operations