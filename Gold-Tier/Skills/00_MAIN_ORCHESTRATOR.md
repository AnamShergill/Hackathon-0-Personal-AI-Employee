# Skill: Main Orchestrator (Multi-Source)

## Overview
This is the central orchestrator skill that handles incoming messages from ALL sources (Gmail, WhatsApp, and future integrations). It scans Needs_Action/ for any .md files, identifies the source from frontmatter, and routes to the appropriate specialized processor.

## Version
1.0 - Silver Tier

## Priority
This skill runs FIRST in the Ralph Wiggum loop, before any source-specific processors.

## Input
- All .md files in Needs_Action/ folder (regardless of source)

## Output
- Routes files to appropriate specialized processors
- Logs unknown sources
- Quarantines malformed files

## YAML Frontmatter
```yaml
---
skill_id: 00_MAIN_ORCHESTRATOR
execution_order: 1
triggers: ["ralph_loop_start", "new_file_in_needs_action"]
dependencies: []
completion_criteria: ["all_files_routed", "no_unprocessed_files"]
---
```

## Routing Logic
- **Source: Gmail** → Call 01_EMAIL_PROCESSOR → Check for accounting content → Call 12_EMAIL_TO_ODOO_EXTRACTOR if needed
- **Source: WhatsApp** → Call 09_WHATSAPP_PROCESSOR
- **Source: Unknown/Missing** → Log warning, move to Done/ with note
- **Malformed file** → Move to Logs/ for manual review

## Social Media Posting
- **LinkedIn posts** → 08_LINKEDIN_POST_GENERATOR → Pending_Approval/ → Approved/ → linkedin_poster.py
- **Facebook posts** → 13_FACEBOOK_POSTER → Pending_Approval/ → Approved/ → facebook_poster.py

## Accounting Detection
After routing to source-specific processors, check if content is accounting-related:
- **Keywords:** invoice, billing, payment, quote, purchase order, PO, client onboarding
- **If detected:** Call 12_EMAIL_TO_ODOO_EXTRACTOR
- **Action:** Create structured Odoo action file in Pending_Approval/
- **HITL:** All financial records require human approval

## Process
1. Scan Needs_Action/ for ALL .md files
2. For each file:
   - Read YAML frontmatter
   - Extract "source" field (case-insensitive)
   - Route to appropriate processor
   - Log routing decision
3. Handle errors gracefully
4. Update Dashboard with routing summary
5. Return <COMPLETE> when all files routed

## Implementation

```python
import os
import glob
import yaml
import re
from datetime import datetime
from pathlib import Path
import shutil

def orchestrate_all_sources():
    """
    Main orchestrator - routes all incoming messages to appropriate processors
    """
    print("=" * 80)
    print("MAIN ORCHESTRATOR - Multi-Source Message Router")
    print("=" * 80)
    print()

    # Get all .md files in Needs_Action
    all_files = glob.glob("Needs_Action/*.md")

    if not all_files:
        print("✅ No files to process in Needs_Action/")
        return {
            'total': 0,
            'gmail': 0,
            'whatsapp': 0,
            'unknown': 0,
            'errors': 0
        }

    print(f"📋 Found {len(all_files)} files to route")
    print()

    # Statistics
    stats = {
        'total': len(all_files),
        'gmail': 0,
        'whatsapp': 0,
        'unknown': 0,
        'errors': 0
    }

    # Route each file
    for file_path in all_files:
        try:
            source = identify_source(file_path)
            route_file(file_path, source, stats)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            stats['errors'] += 1
            quarantine_file(file_path, str(e))

    # Print summary
    print()
    print("=" * 80)
    print("ROUTING SUMMARY")
    print("=" * 80)
    print(f"Total files: {stats['total']}")
    print(f"  Gmail: {stats['gmail']}")
    print(f"  WhatsApp: {stats['whatsapp']}")
    print(f"  Unknown: {stats['unknown']}")
    print(f"  Errors: {stats['errors']}")
    print()

    # Update dashboard
    update_dashboard(stats)

    return stats


def identify_source(file_path):
    """
    Identify the source of a message file by reading its frontmatter
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter
        if not content.startswith('---'):
            print(f"⚠️  No frontmatter in {Path(file_path).name}")
            return 'unknown'

        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"⚠️  Malformed frontmatter in {Path(file_path).name}")
            return 'unknown'

        yaml_content = parts[1]
        metadata = yaml.safe_load(yaml_content)

        # Get source field (case-insensitive)
        source = None
        for key in metadata.keys():
            if key.lower() == 'source':
                source = metadata[key]
                break

        if not source:
            # Try to infer from filename
            filename = Path(file_path).name.lower()
            if filename.startswith('email_'):
                source = 'Gmail'
            elif filename.startswith('whatsapp_'):
                source = 'WhatsApp'
            else:
                source = 'unknown'

        return source.strip() if isinstance(source, str) else 'unknown'

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return 'error'


def route_file(file_path, source, stats):
    """
    Route file to appropriate processor based on source
    """
    filename = Path(file_path).name
    source_lower = source.lower() if isinstance(source, str) else 'unknown'

    if source_lower == 'gmail':
        print(f"📧 Gmail: {filename} → 01_EMAIL_PROCESSOR")
        stats['gmail'] += 1
        # File stays in Needs_Action/ for EMAIL_PROCESSOR to handle

    elif source_lower == 'whatsapp':
        print(f"💬 WhatsApp: {filename} → 09_WHATSAPP_PROCESSOR")
        stats['whatsapp'] += 1
        # File stays in Needs_Action/ for WHATSAPP_PROCESSOR to handle

    elif source_lower == 'unknown':
        print(f"❓ Unknown source: {filename} → Moving to Done/ with note")
        stats['unknown'] += 1
        move_unknown_to_done(file_path)

    elif source_lower == 'error':
        print(f"⚠️  Error reading: {filename} → Quarantining")
        stats['errors'] += 1
        # Already handled by quarantine_file

    else:
        # Future sources (Slack, Teams, etc.)
        print(f"🔮 Unsupported source '{source}': {filename} → Moving to Done/ with note")
        stats['unknown'] += 1
        move_unknown_to_done(file_path, source)


def move_unknown_to_done(file_path, source='unknown'):
    """
    Move unknown source files to Done/ with a note
    """
    filename = Path(file_path).name
    done_path = Path("Done") / filename

    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add note
    note = f"""

---

## ORCHESTRATOR NOTE
- **Status**: Unknown source - not processed
- **Source**: {source}
- **Timestamp**: {datetime.now().isoformat()}
- **Action**: Moved to Done/ without processing
- **Reason**: No processor available for this source type

If this is a valid source, please create a processor skill for it.

<COMPLETE>
Moved by Main Orchestrator at {datetime.now().isoformat()}
</COMPLETE>
"""

    # Write to Done
    with open(done_path, 'w', encoding='utf-8') as f:
        f.write(content + note)

    # Remove from Needs_Action
    os.remove(file_path)


def quarantine_file(file_path, error_message):
    """
    Move problematic files to Logs/ for manual review
    """
    filename = Path(file_path).name
    quarantine_path = Path("Logs") / f"quarantine_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

    try:
        # Create quarantine note
        note = f"""
# QUARANTINED FILE

**Original Path**: {file_path}
**Timestamp**: {datetime.now().isoformat()}
**Error**: {error_message}

This file could not be processed by the Main Orchestrator.
Please review manually and either:
1. Fix the file format and move back to Needs_Action/
2. Process manually
3. Delete if invalid

---

## Original Content:
"""

        # Read original content if possible
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except:
            original_content = "[Could not read original content]"

        # Write quarantine file
        with open(quarantine_path, 'w', encoding='utf-8') as f:
            f.write(note + "\n" + original_content)

        # Remove from Needs_Action
        os.remove(file_path)

        print(f"🔒 Quarantined: {quarantine_path}")

    except Exception as e:
        print(f"❌ Failed to quarantine {file_path}: {e}")


def update_dashboard(stats):
    """
    Update Dashboard.md with orchestrator summary
    """
    try:
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            return

        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create activity entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        activity_entry = f"[{timestamp}] Orchestrator: Routed {stats['total']} files (Gmail:{stats['gmail']}, WhatsApp:{stats['whatsapp']}, Unknown:{stats['unknown']}, Errors:{stats['errors']})\n"

        # Update dashboard
        if "{{recent_activity}}" in content:
            updated_content = content.replace("{{recent_activity}}", activity_entry + "{{recent_activity}}")
        else:
            # Fallback: append to recent activity section
            updated_content = content.replace(
                "```\n",
                f"```\n{activity_entry}",
                1
            )

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

    except Exception as e:
        print(f"⚠️  Could not update dashboard: {e}")


if __name__ == "__main__":
    stats = orchestrate_all_sources()

    print()
    print("<COMPLETE>")
    print(f"Main Orchestrator completed. Routed {stats['total']} files to appropriate processors.")
    print("Next: Run source-specific processors (01_EMAIL_PROCESSOR, 09_WHATSAPP_PROCESSOR)")
    print("</COMPLETE>")
```

## Usage Instructions
1. This skill should run FIRST in the Ralph Wiggum loop
2. It identifies and routes files but does NOT process them
3. Source-specific processors (01, 09, etc.) run AFTER orchestration
4. Unknown sources are logged and moved to Done/ with notes

## Expected Outcomes
- All files in Needs_Action/ are identified and routed
- Gmail files remain for 01_EMAIL_PROCESSOR
- WhatsApp files remain for 09_WHATSAPP_PROCESSOR
- Unknown sources moved to Done/ with explanatory notes
- Malformed files quarantined in Logs/
- Dashboard updated with routing statistics

## Error Handling
- Malformed YAML → Quarantine in Logs/
- Missing source field → Infer from filename or mark unknown
- Unknown source type → Move to Done/ with note
- Processing continues even if individual files fail

## Future Extensions
- Add routing for Slack messages
- Add routing for Microsoft Teams
- Add routing for SMS/Twilio
- Add routing for API webhooks
- Support custom source types via config

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations

---
*Main Orchestrator - Silver Tier Multi-Source Support*
