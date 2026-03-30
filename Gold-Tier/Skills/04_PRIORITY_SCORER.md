# Skill: Priority Scorer

## Overview
This skill reads email files from Needs_Action/ and assigns priority levels (High/Medium/Low/Ignore) based on keywords, sender domain, and subject urgency. It updates each file with priority information and creates a summary for dashboard display.

## Version
1.0

## Input
- Reads all email .md files from Needs_Action/ folder
- Analyzes content, sender, subject, and other metadata

## Output
- Updates each email file with priority score and reason
- Creates priority_summary.md in Plans/ folder with overall priorities
- Updates Dashboard.md with priority counts

## YAML Frontmatter
```yaml
---
skill_id: 04_PRIORITY_SCORER
triggers: ["new_email_arrives", "priority_review_needed"]
dependencies: ["01_EMAIL_PROCESSOR"]
completion_criteria: ["priorities_assigned", "dashboard_updated"]
---
```

## Process
1. Scan all files in Needs_Action/
2. Analyze each file for priority indicators
3. Assign priority based on defined criteria
4. Update each file with priority information
5. Create summary file with priorities
6. Update Dashboard.md with priority counts

## Implementation

```python
import os
import yaml
import re
import glob
from datetime import datetime
from pathlib import Path

def score_priorities():
    """
    Score priorities for all emails in Needs_Action/
    """
    print("Scoring priorities for emails in Needs_Action/")

    # Get all email files in Needs_Action
    email_files = glob.glob("Needs_Action/email_*.md")

    if not email_files:
        print("No emails found in Needs_Action/")
        return

    print(f"Found {len(email_files)} emails to score")

    priorities = {
        'High': [],
        'Medium': [],
        'Low': [],
        'Ignore': []
    }

    for email_file in email_files:
        priority, reason = analyze_priority(email_file)

        # Update the email file with priority info
        update_email_file_with_priority(email_file, priority, reason)

        # Add to priority list
        priorities[priority].append((email_file, reason))

    # Create summary file
    create_priority_summary(priorities)

    # Update dashboard
    update_dashboard(priorities)

    print(f"Priority scoring complete. High: {len(priorities['High'])}, Medium: {len(priorities['Medium'])}, Low: {len(priorities['Low'])}, Ignore: {len(priorities['Ignore'])}")


def analyze_priority(email_file_path):
    """
    Analyze an email and assign priority with reason
    """
    with open(email_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Separate YAML frontmatter from content
    yaml_frontmatter = ""
    email_body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_frontmatter = parts[1]
            email_body = parts[2]

    # Load YAML data if available
    email_data = {}
    if yaml_frontmatter:
        email_data = yaml.safe_load(yaml_frontmatter)

    subject = email_data.get('subject', '').lower()
    sender = email_data.get('sender', '').lower()
    email_content = email_body.lower()

    # Initialize scores
    urgency_score = 0
    financial_score = 0
    deadline_score = 0
    sender_score = 0

    # Urgency keywords
    urgency_keywords = [
        'urgent', 'asap', 'immediately', 'now', 'today', 'within', 'by',
        'critical', 'emergency', 'important', 'high priority', 'attention',
        'deadline', 'due', 'expires', 'expiring', 'last chance'
    ]

    # Financial keywords
    financial_keywords = [
        'payment', 'pay', 'invoice', 'cost', 'price', 'charge', 'fee',
        'bill', 'money', 'funds', 'budget', 'purchase', 'order', 'transaction',
        'reimbursement', 'expense', 'receipt', 'statement', 'financial'
    ]

    # Deadline keywords
    deadline_keywords = [
        'deadline', 'due', 'expires', 'expiring', 'by', 'before',
        'next', 'soon', 'week', 'day', 'month', 'hours', 'minutes'
    ]

    # Sender importance
    important_senders = [
        'manager', 'ceo', 'director', 'executive', 'admin', 'boss',
        'supervisor', 'lead', 'president', 'founder', 'cofounder'
    ]

    # Calculate scores
    urgency_score = sum(1 for word in urgency_keywords if word in subject or word in email_content)
    financial_score = sum(1 for word in financial_keywords if word in subject or word in email_content)
    deadline_score = sum(1 for word in deadline_keywords if word in subject or word in email_content)
    sender_score = sum(1 for word in important_senders if word in sender)

    # Check for sender domain importance
    if 'company.com' in sender or 'client.com' in sender:  # Placeholder for real domain check
        sender_score += 2

    # Total score
    total_score = urgency_score * 3 + financial_score * 2 + deadline_score * 2 + sender_score * 2

    # Determine priority based on total score
    if total_score >= 10:
        priority = 'High'
        reason = f"High urgency ({urgency_score}) or financial ({financial_score}) or important sender ({sender_score})"
    elif total_score >= 5:
        priority = 'Medium'
        reason = f"Moderate urgency ({urgency_score}) or deadline ({deadline_score})"
    elif total_score >= 1:
        priority = 'Low'
        reason = f"Minor urgency ({urgency_score}) or reference ({deadline_score})"
    else:
        priority = 'Ignore'
        reason = "No urgency indicators found"

    return priority, reason


def update_email_file_with_priority(email_file_path, priority, reason):
    """
    Update the email file with priority information
    """
    with open(email_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if priority info already exists
    if 'priority_score:' in content:
        # Update existing priority info
        import re
        content = re.sub(r'priority_score: .*\n', f'priority_score: {priority}\n', content)
        content = re.sub(r'priority_reason: .*\n', f'priority_reason: "{reason}"\n', content)
        content = re.sub(r'priority_assigned: .*\n', f'priority_assigned: "{datetime.now().isoformat()}"\n', content)
    else:
        # Add priority info after YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_frontmatter = parts[1]
                email_body = parts[2]

                # Add priority fields to YAML frontmatter
                yaml_lines = yaml_frontmatter.split('\n')
                yaml_lines.append(f'priority_score: {priority}')
                yaml_lines.append(f'priority_reason: "{reason}"')
                yaml_lines.append(f'priority_assigned: "{datetime.now().isoformat()}"')
                updated_yaml = '\n'.join(yaml_lines)

                content = f'---\n{updated_yaml}\n---{email_body}'

    # Write updated content
    with open(email_file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_priority_summary(priorities):
    """
    Create a summary file with priority information
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f"priority_summary_{timestamp}.md"
    summary_path = Path("Plans") / summary_filename

    summary_content = f"""---
title: "Priority Summary"
created: "{datetime.now().isoformat()}"
---

# Priority Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## High Priority Items ({len(priorities['High'])})
{chr(10).join([f"- {file}: {reason}" for file, reason in priorities['High']]) if priorities['High'] else 'No high priority items'}

## Medium Priority Items ({len(priorities['Medium'])})
{chr(10).join([f"- {file}: {reason}" for file, reason in priorities['Medium']]) if priorities['Medium'] else 'No medium priority items'}

## Low Priority Items ({len(priorities['Low'])})
{chr(10).join([f"- {file}: {reason}" for file, reason in priorities['Low']]) if priorities['Low'] else 'No low priority items'}

## Items to Ignore ({len(priorities['Ignore'])})
{chr(10).join([f"- {file}: {reason}" for file, reason in priorities['Ignore']]) if priorities['Ignore'] else 'No items to ignore'}

## Priority Scoring Summary
- Total items processed: {sum(len(items) for items in priorities.values())}
- High priority: {len(priorities['High'])}
- Medium priority: {len(priorities['Medium'])}
- Low priority: {len(priorities['Low'])}
- Ignore: {len(priorities['Ignore'])}

---
*Created by Priority Scorer Skill at {datetime.now().isoformat()}*
"""

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)


def update_dashboard(priorities):
    """
    Update Dashboard.md with priority counts
    """
    # Read current dashboard
    dashboard_path = Path("Dashboard.md")
    if not dashboard_path.exists():
        return

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update priority counts
    content = re.sub(r'\{\{high_priority_count\}\}', str(len(priorities['High'])), content)
    content = re.sub(r'\{\{medium_priority_count\}\}', str(len(priorities['Medium'])), content)
    content = re.sub(r'\{\{low_priority_count\}\}', str(len(priorities['Low'])), content)

    # Add defaults if placeholders don't exist
    if '{{high_priority_count}}' not in content:
        content = content.replace('{{high_priority_count}}', str(len(priorities['High'])))
    if '{{medium_priority_count}}' not in content:
        content = content.replace('{{medium_priority_count}}', str(len(priorities['Medium'])))
    if '{{low_priority_count}}' not in content:
        content = content.replace('{{low_priority_count}}', str(len(priorities['Low'])))

    # Add to recent activity
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_processed = sum(len(items) for items in priorities.values())
    activity_entry = f"[{timestamp}] Scored {total_processed} emails by priority (High: {len(priorities['High'])}, Med: {len(priorities['Medium'])}, Low: {len(priorities['Low'])})\n"

    # Insert activity in recent activity section
    if "{{recent_activity}}" in content:
        updated_content = content.replace("{{recent_activity}}", activity_entry + "{{recent_activity}}")
    else:
        updated_content = content.replace(
            "---\n*Dashboard automatically updated by AI Employee System*",
            f"```\n{{recent_activity}}\n{activity_entry}\n```\n\n---\n*Dashboard automatically updated by AI Employee System*"
        )

    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)


if __name__ == "__main__":
    score_priorities()

    print("\n<COMPLETE>")
    print("Priority Scorer skill completed. All emails in Needs_Action have been prioritized.")
    print("</COMPLETE>")
```

## Usage Instructions
1. Run the skill to score all emails: `python Skills/04_PRIORITY_SCORER.py`
2. The skill will analyze all files in Needs_Action/ folder
3. Each file will be updated with priority information
4. A priority summary will be created in Plans/ folder
5. Dashboard.md will be updated with priority counts

## References
- Follows Company_Handbook.md priority guidelines
- Implements urgency and importance assessment patterns

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations