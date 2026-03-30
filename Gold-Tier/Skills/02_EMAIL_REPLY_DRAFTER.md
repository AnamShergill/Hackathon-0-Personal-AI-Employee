# Skill: Email Reply Drafter

## Overview
This skill drafts polite, professional reply emails based on incoming messages in Needs_Action/. The draft is saved as a markdown file in the Plans/ folder. If the reply involves sensitive topics (money, attachments, new recipients), the skill flags it for Human-In-The-Loop (HITL) approval.

## Version
1.0

## Input
- Path to an email .md file in Needs_Action/ folder containing YAML frontmatter and email content

## Output
- Draft reply text saved to Plans/REPLY_[original_filename].md
- HITL flag if sensitive topics detected

## YAML Frontmatter
```yaml
---
skill_id: 02_EMAIL_REPLY_DRAFTER
triggers: ["new_email_processed", "reply_requested"]
dependencies: ["01_EMAIL_PROCESSOR"]
completion_criteria: ["draft_created", "hitl_flagged_if_needed"]
---
```

## Process
1. Read the input email file from Needs_Action/
2. Parse email content and metadata
3. Generate appropriate draft reply based on content and tone guidelines
4. Check for sensitive topics requiring HITL
5. Save draft reply to Plans/ folder
6. Flag for HITL if needed
7. Update Dashboard.md with status

## Implementation

```python
import os
import yaml
import re
from datetime import datetime
from pathlib import Path

def draft_reply(email_file_path):
    """
    Draft a reply to an email based on the content and context
    """
    print(f"Drafting reply for: {email_file_path}")

    # Read the email file
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

    subject = email_data.get('subject', 'No Subject')
    sender = email_data.get('sender', 'Unknown Sender')
    email_content = email_body.strip()

    # Check for sensitive topics that require HITL
    hitl_required = check_for_hitl_topics(email_content)

    # Generate draft reply
    draft_reply_text = generate_reply_draft(email_content, subject, sender)

    # Create output filename
    original_filename = Path(email_file_path).name
    reply_filename = f"REPLY_{original_filename.replace('.md', '.md')}"
    reply_path = Path("Plans") / reply_filename

    # Create the draft reply file
    reply_content = f"""---
original_email: "{email_file_path}"
subject: "{subject}"
sender: "{sender}"
generated: "{datetime.now().isoformat()}"
requires_approval: {hitl_required}
approval_category: "reply_draft"
---

# Draft Reply to: {subject}

## Original Sender
{sender}

## Original Subject
{subject}

## Original Message
{email_content}

## Draft Reply
{draft_reply_text}

## Processing Notes
- HITL Required: {'Yes' if hitl_required else 'No'}
- Approval Category: reply_draft
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    with open(reply_path, 'w', encoding='utf-8') as f:
        f.write(reply_content)

    print(f"Draft reply created: {reply_path}")

    # Update dashboard
    update_dashboard(email_file_path, hitl_required)

    print(f"Email reply draft completed. HITL required: {hitl_required}")


def check_for_hitl_topics(email_content):
    """
    Check if the email content requires Human-In-The-Loop approval
    based on Company_Handbook.md authorization thresholds
    """
    content_lower = email_content.lower()

    # Check for money/financial mentions
    money_keywords = [
        'payment', 'pay', 'invoice', 'cost', 'price', 'charge', 'fee',
        'bill', 'money', 'funds', 'budget', 'purchase', 'order', 'transaction',
        '$', '€', '£', '¥', 'amount', 'dollar', 'euro', 'currency'
    ]

    # Check for attachment requests
    attachment_keywords = [
        'attachment', 'attach', 'file', 'document', 'pdf', 'doc', 'xls',
        'send', 'forward', 'include', 'find attached', 'as attachment'
    ]

    # Check for new recipient requests
    new_recipient_keywords = [
        'cc', 'bcc', 'send to', 'forward to', 'introduce to',
        'contact', 'someone', 'person', 'their email', 'their address'
    ]

    # Check if any sensitive topics exist in the content
    has_money = any(keyword in content_lower for keyword in money_keywords)
    has_attachments = any(keyword in content_lower for keyword in attachment_keywords)
    has_new_recipients = any(keyword in content_lower for keyword in new_recipient_keywords)

    return has_money or has_attachments or has_new_recipients


def generate_reply_draft(email_content, subject, sender):
    """
    Generate a professional draft reply based on email content
    """
    content_lower = email_content.lower()
    subject_lower = subject.lower()

    # Determine appropriate tone based on sentiment and urgency
    if any(keyword in content_lower or keyword in subject_lower for keyword in
           ['urgent', 'asap', 'immediately', 'critical', 'important']):
        tone = "professional and urgent"
    else:
        tone = "professional and polite"

    # Generate contextually appropriate reply
    reply_parts = ["Thank you for your message,"]

    # Add specific response based on email content
    if 'meeting' in content_lower or 'schedule' in content_lower or 'appointment' in subject_lower:
        reply_parts.append("I can help with scheduling. Let me check availability and get back to you shortly.")
    elif 'question' in content_lower or 'help' in content_lower or 'info' in content_lower:
        reply_parts.append("I'll research this and provide you with a detailed response.")
    elif 'follow up' in content_lower or 'checking' in content_lower:
        reply_parts.append("Thank you for the follow-up. I'll look into this for you.")
    elif 'thank' in content_lower:
        reply_parts.append("You're welcome! Please don't hesitate to reach out if you need anything else.")
    else:
        reply_parts.append("I've reviewed your message and will take the appropriate action.")
        reply_parts.append("I'll update you once I've completed the requested task.")

    # Add closing
    reply_parts.append("\nBest regards,\nAI Employee Assistant")

    return ' '.join(reply_parts)


def update_dashboard(email_file_path, hitl_required):
    """
    Update Dashboard.md with processing status
    """
    # Read current dashboard
    dashboard_path = Path("Dashboard.md")
    if not dashboard_path.exists():
        return

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add to recent activity
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_entry = f"[{timestamp}] Drafted reply for {Path(email_file_path).name} (HITL: {'Yes' if hitl_required else 'No'})\n"

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
    import sys

    if len(sys.argv) > 1:
        email_file_path = sys.argv[1]
    else:
        print("Error: Please provide path to email file as argument")
        sys.exit(1)

    draft_reply(email_file_path)

    print("\n<COMPLETE>")
    print("Email Reply Drafter skill completed. Draft reply created in Plans/ folder.")
    print("</COMPLETE>")
```

## Usage Instructions
1. Call this skill with the path to an email file: `python Skills/02_EMAIL_REPLY_DRAFTER.py Needs_Action/email_file.md`
2. The skill will generate a draft reply in the Plans/ folder
3. If sensitive topics are detected, the file will be flagged for HITL approval
4. The dashboard will be updated with processing status

## References
- Follows Company_Handbook.md politeness protocol and authorization thresholds
- Implements HITL requirements for sensitive topics (financial, attachments, new recipients)

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations