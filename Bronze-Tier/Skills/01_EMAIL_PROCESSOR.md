# Skill: Email Processor

## Overview
This skill processes emails from the Needs_Action folder, analyzes their content and priority, creates actionable plans in the Plans folder, and updates the Dashboard.

## Prerequisites
- Gmail Watcher has created email files in Needs_Action/
- Python 3.13+
- Required dependencies installed

## Input
- Email markdown files in Needs_Action/ folder with YAML frontmatter

## Process
1. List all files in Needs_Action/
2. Read each email markdown file
3. Analyze content, sender, subject, and priority
4. Create structured plan in Plans/ folder
5. Update Dashboard.md with summary
6. Move processed files to Done/ folder with <COMPLETE> status

## Implementation

```python
import os
import glob
import yaml
import re
from datetime import datetime
from pathlib import Path

def process_emails():
    """
    Process all email files in Needs_Action folder
    """
    print("Starting email processing...")

    # Get all email files in Needs_Action
    email_files = glob.glob("Needs_Action/email_*.md")

    if not email_files:
        print("No emails to process")
        return

    print(f"Found {len(email_files)} emails to process")

    processed_count = 0
    for email_file in email_files:
        try:
            # Read the email file
            with open(email_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Separate YAML frontmatter from content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_frontmatter = parts[1]
                    email_body = parts[2]

                    # Load YAML data
                    email_data = yaml.safe_load(yaml_frontmatter)

                    # Create a plan based on the email
                    create_plan_from_email(email_data, email_body, email_file)

                    # Move the file to Done
                    move_to_done(email_file)

                    processed_count += 1
                    print(f"Processed: {email_file}")

        except Exception as e:
            print(f"Error processing {email_file}: {e}")

    # Update dashboard
    update_dashboard(len(email_files), processed_count)

    print(f"Email processing complete. Processed {processed_count} emails.")


def create_plan_from_email(email_data, email_body, original_file):
    """
    Create a plan in Plans/ folder based on email content
    """
    # Extract information from email
    subject = email_data.get('subject', 'No Subject')
    sender = email_data.get('sender', 'Unknown Sender')
    priority = email_data.get('priority', 'medium')
    date_received = email_data.get('date_received', 'Unknown Date')

    # Generate plan filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_filename = f"plan_{timestamp}_{subject[:30].replace(' ', '_').replace('/', '_')}.md"
    plan_path = Path("Plans") / plan_filename

    # Determine next steps based on email content
    next_steps = determine_next_steps(email_body, subject)

    # Create plan content
    plan_content = f"""---
title: "Plan for: {subject}"
created: "{datetime.now().isoformat()}"
status: pending
priority: {priority}
source: "{original_file}"
sender: "{sender}"
original_date: "{date_received}"
---

# Action Plan: {subject}

## Email Details
- **From:** {sender}
- **Subject:** {subject}
- **Received:** {date_received}
- **Priority:** {priority}
- **Source File:** {original_file}

## Summary
{extract_summary(email_body)}

## Next Steps
{next_steps}

## Required Actions
1. [ ] Assess priority and urgency
2. [ ] Determine appropriate response
3. [ ] Execute action plan
4. [ ] Follow up as needed

## Notes
- Action item extracted from email processing
- Refer to original email for complete context

---
*Created by Email Processor Skill at {datetime.now().isoformat()}*
"""

    # Write the plan file
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

    print(f"Created plan: {plan_path}")


def determine_next_steps(email_body, subject):
    """
    Determine appropriate next steps based on email content
    """
    # Simple keyword-based analysis
    body_lower = email_body.lower()
    subject_lower = subject.lower()

    next_steps = []

    # Check for common request types
    if any(keyword in body_lower or keyword in subject_lower for keyword in ['meeting', 'schedule', 'appointment', 'calendar']):
        next_steps.append("- Schedule requested meeting")
        next_steps.append("- Confirm availability")

    if any(keyword in body_lower or keyword in subject_lower for keyword in ['report', 'data', 'information', 'details']):
        next_steps.append("- Gather requested information")
        next_steps.append("- Prepare response")

    if any(keyword in body_lower or keyword in subject_lower for keyword in ['urgent', 'asap', 'immediately', 'critical']):
        next_steps.append("- Prioritize for immediate attention")
        next_steps.append("- Escalate if needed")

    if any(keyword in body_lower or keyword in subject_lower for keyword in ['follow up', 'check', 'status', 'update']):
        next_steps.append("- Check status of referenced items")
        next_steps.append("- Provide requested update")

    if not next_steps:
        # Default next steps
        next_steps = [
            "- Review email content",
            "- Determine appropriate response",
            "- Take necessary action",
            "- Respond if required"
        ]

    # Format as numbered list
    return "\n".join([f"{i+1}. {step}" for i, step in enumerate(next_steps)])


def extract_summary(email_body):
    """
    Extract a summary from the email body
    """
    # Remove extra whitespace and get first few sentences
    clean_body = re.sub(r'\s+', ' ', email_body.strip())

    # Get first 200 characters or first sentence, whichever is longer
    if len(clean_body) <= 200:
        return clean_body
    else:
        # Find first sentence ending
        first_period = clean_body.find('.', 100)
        if first_period != -1:
            return clean_body[:first_period+1]
        else:
            return clean_body[:200] + "..."


def move_to_done(file_path):
    """
    Move processed file to Done/ folder
    """
    filename = Path(file_path).name
    new_path = Path("Done") / filename

    # Read the content and add completion marker
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add completion marker if not already present
    if '<COMPLETE>' not in content:
        content += f"\n\n<COMPLETE>\nProcessed by Email Processor at {datetime.now().isoformat()}\n</COMPLETE>\n"

    # Write to Done folder
    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Remove original file
    os.remove(file_path)


def update_dashboard(total_emails, processed_count):
    """
    Update Dashboard.md with processing summary
    """
    # Read current dashboard
    with open('Dashboard.md', 'r', encoding='utf-8') as f:
        dashboard_content = f.read()

    # Update the dashboard with new information
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Replace placeholder for recent activity
    activity_entry = f"[{timestamp}] Processed {processed_count} of {total_emails} emails in Needs_Action\n"

    if "{{recent_activity}}" in dashboard_content:
        # Simple replacement for now
        updated_dashboard = dashboard_content.replace("{{recent_activity}}", activity_entry + "{{recent_activity}}")
    else:
        updated_dashboard = dashboard_content.replace(
            "---\n*Dashboard automatically updated by AI Employee System*",
            f"```\n{{recent_activity}}\n{activity_entry}\n```\n\n---\n*Dashboard automatically updated by AI Employee System*"
        )

    # Write updated dashboard
    with open('Dashboard.md', 'w', encoding='utf-8') as f:
        f.write(updated_dashboard)


if __name__ == "__main__":
    process_emails()
    print("\n<COMPLETE>")
    print("Email Processor skill completed. All emails from Needs_Action have been processed into Plans/ and moved to Done/. Dashboard updated.")
    print("</COMPLETE>")
```

## Execution
To execute this skill, run:
```bash
python -m Skills.email_processor
```

## Expected Outcomes
- All emails in Needs_Action/ are processed
- Actionable plans are created in Plans/
- Dashboard.md is updated with processing summary
- Processed emails are moved to Done/ with completion markers
- System maintains <COMPLETE> promise for Ralph Wiggum pattern

## Error Handling
- Files that fail to process remain in Needs_Action/
- Errors are logged for debugging
- Processing continues with other files if one fails

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations