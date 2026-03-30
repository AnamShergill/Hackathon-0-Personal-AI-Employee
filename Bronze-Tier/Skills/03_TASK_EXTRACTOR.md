# Skill: Task Extractor

## Overview
This skill parses email content from Needs_Action/ files to extract action items, deadlines, and people mentioned. It creates or updates Plan.md files in the Plans/ folder with checklist format and updates Dashboard.md with pending tasks.

## Version
1.0

## Input
- Path to an email .md file in Needs_Action/ folder containing YAML frontmatter and email content

## Output
- Action items extracted and added to appropriate Plan.md in Plans/ folder
- Dashboard.md updated with new pending tasks
- Checklist format used for clarity and progress tracking

## YAML Frontmatter
```yaml
---
skill_id: 03_TASK_EXTRACTOR
triggers: ["email_processed", "task_identified"]
dependencies: ["01_EMAIL_PROCESSOR"]
completion_criteria: ["tasks_extracted", "dashboard_updated"]
---
```

## Process
1. Read email file from Needs_Action/
2. Parse content for action items, deadlines, and people mentioned
3. Create/update Plan.md with extracted tasks in checklist format
4. Update Dashboard.md with new pending tasks
5. Mark original email as processed

## Implementation

```python
import os
import yaml
import re
from datetime import datetime, timedelta
from pathlib import Path

def extract_tasks(email_file_path):
    """
    Extract tasks from an email and create/update Plan.md
    """
    print(f"Extracting tasks from: {email_file_path}")

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

    # Extract tasks from email content
    tasks = extract_action_items(email_body)
    deadlines = extract_deadlines(email_body)
    people = extract_people(email_body)

    if not tasks:
        print("No tasks found in email")
        return

    # Create/update Plan.md with tasks
    plan_path = create_task_plan(email_file_path, subject, tasks, deadlines, people)

    # Update Dashboard.md with pending tasks
    update_dashboard(tasks)

    print(f"Task extraction completed. Plan created: {plan_path}")


def extract_action_items(email_content):
    """
    Extract action items from email content using pattern matching
    """
    # Common action item patterns
    patterns = [
        r'please\s+(?P<action>\w+(?:\s+\w+)*)',
        r'need\s+to\s+(?P<action>\w+(?:\s+\w+)*)',
        r'should\s+(?P<action>\w+(?:\s+\w+)*)',
        r'could\s+you\s+(?P<action>\w+(?:\s+\w+)*)',
        r'can\s+you\s+(?P<action>\w+(?:\s+\w+)*)',
        r'would\s+you\s+(?P<action>\w+(?:\s+\w+)*)',
        r'help\s+me\s+(?P<action>\w+(?:\s+\w+)*)',
        r'assist\s+with\s+(?P<action>\w+(?:\s+\w+)*)',
        r'follow\s+up\s+on\s+(?P<action>\w+(?:\s+\w+)*)',
        r'review\s+(?P<action>\w+(?:\s+\w+)*)',
        r'prepare\s+(?P<action>\w+(?:\s+\w+)*)',
        r'schedule\s+(?P<action>\w+(?:\s+\w+)*)',
        r'research\s+(?P<action>\w+(?:\s+\w+)*)',
        r'investigate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'analyze\s+(?P<action>\w+(?:\s+\w+)*)',
        r'draft\s+(?P<action>\w+(?:\s+\w+)*)',
        r'create\s+(?P<action>\w+(?:\s+\w+)*)',
        r'send\s+(?P<action>\w+(?:\s+\w+)*)',
        r'update\s+(?P<action>\w+(?:\s+\w+)*)',
        r'check\s+(?P<action>\w+(?:\s+\w+)*)',
        r'look\s+into\s+(?P<action>\w+(?:\s+\w+)*)',
        r'get\s+(?P<action>\w+(?:\s+\w+)*)',
        r'find\s+(?P<action>\w+(?:\s+\w+)*)',
        r'locate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'obtain\s+(?P<action>\w+(?:\s+\w+)*)',
        r'gather\s+(?P<action>\w+(?:\s+\w+)*)',
        r'collect\s+(?P<action>\w+(?:\s+\w+)*)',
        r'compile\s+(?P<action>\w+(?:\s+\w+)*)',
        r'organize\s+(?P<action>\w+(?:\s+\w+)*)',
        r'coordinate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'arrange\s+(?P<action>\w+(?:\s+\w+)*)',
        r'contact\s+(?P<action>\w+(?:\s+\w+)*)',
        r'notify\s+(?P<action>\w+(?:\s+\w+)*)',
        r'inform\s+(?P<action>\w+(?:\s+\w+)*)',
        r'report\s+(?P<action>\w+(?:\s+\w+)*)',
        r'present\s+(?P<action>\w+(?:\s+\w+)*)',
        r'demonstrate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'measure\s+(?P<action>\w+(?:\s+\w+)*)',
        r'evaluate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'assess\s+(?P<action>\w+(?:\s+\w+)*)',
        r'determine\s+(?P<action>\w+(?:\s+\w+)*)',
        r'establish\s+(?P<action>\w+(?:\s+\w+)*)',
        r'develop\s+(?P<action>\w+(?:\s+\w+)*)',
        r'design\s+(?P<action>\w+(?:\s+\w+)*)',
        r'implement\s+(?P<action>\w+(?:\s+\w+)*)',
        r'estimate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'calculate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'confirm\s+(?P<action>\w+(?:\s+\w+)*)',
        r'verify\s+(?P<action>\w+(?:\s+\w+)*)',
        r'validate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'ensure\s+(?P<action>\w+(?:\s+\w+)*)',
        r'guarantee\s+(?P<action>\w+(?:\s+\w+)*)',
        r'maintain\s+(?P<action>\w+(?:\s+\w+)*)',
        r'preserve\s+(?P<action>\w+(?:\s+\w+)*)',
        r'protect\s+(?P<action>\w+(?:\s+\w+)*)',
        r'secure\s+(?P<action>\w+(?:\s+\w+)*)',
        r'defend\s+(?P<action>\w+(?:\s+\w+)*)',
        r'enhance\s+(?P<action>\w+(?:\s+\w+)*)',
        r'improve\s+(?P<action>\w+(?:\s+\w+)*)',
        r'upgrade\s+(?P<action>\w+(?:\s+\w+)*)',
        r'optimize\s+(?P<action>\w+(?:\s+\w+)*)',
        r'reduce\s+(?P<action>\w+(?:\s+\w+)*)',
        r'minimize\s+(?P<action>\w+(?:\s+\w+)*)',
        r'eliminate\s+(?P<action>\w+(?:\s+\w+)*)',
        r'remove\s+(?P<action>\w+(?:\s+\w+)*)',
        r'delete\s+(?P<action>\w+(?:\s+\w+)*)',
        r'solve\s+(?P<action>\w+(?:\s+\w+)*)',
        r'resolve\s+(?P<action>\w+(?:\s+\w+)*)',
        r'fix\s+(?P<action>\w+(?:\s+\w+)*)',
        r'correct\s+(?P<action>\w+(?:\s+\w+)*)',
        r'identify\s+(?P<action>\w+(?:\s+\w+)*)',
        r'detect\s+(?P<action>\w+(?:\s+\w+)*)',
        r'discover\s+(?P<action>\w+(?:\s+\w+)*)',
        r'recognize\s+(?P<action>\w+(?:\s+\w+)*)',
        r'recruit\s+(?P<action>\w+(?:\s+\w+)*)',
        r'hire\s+(?P<action>\w+(?:\s+\w+)*)',
        r'advertise\s+(?P<action>\w+(?:\s+\w+)*)',
        r'recruit\s+(?P<action>\w+(?:\s+\w+)*)',
        r'hire\s+(?P<action>\w+(?:\s+\w+)*)',
    ]

    tasks = []
    for pattern in patterns:
        matches = re.finditer(pattern, email_content, re.IGNORECASE)
        for match in matches:
            action = match.group('action').strip()
            if len(action) > 2:  # Filter out very short matches
                tasks.append(action)

    # Remove duplicates while preserving order
    unique_tasks = []
    seen = set()
    for task in tasks:
        task_lower = task.lower()
        if task_lower not in seen:
            seen.add(task_lower)
            unique_tasks.append(task)

    return unique_tasks


def extract_deadlines(email_content):
    """
    Extract potential deadlines from email content
    """
    # Patterns for dates and deadlines
    date_patterns = [
        r'(?:by|on|before|no later than|deadline|due)\s+(?:the\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:by|on|before|no later than|deadline|due)\s+(?:the\s+)?(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
        r'(?:by|on|before|no later than|deadline|due)\s+(?:the\s+)?(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})',
        r'(?:in|within)\s+(\d+)\s+(?:day|days|week|weeks|month|months)',
        r'today|tomorrow|ASAP|urgent|immediately|right away',
    ]

    deadlines = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, email_content, re.IGNORECASE)
        for match in matches:
            deadline = match.group(0).strip()
            deadlines.append(deadline)

    return deadlines


def extract_people(email_content):
    """
    Extract people mentioned in the email content
    """
    # Simple pattern to catch names (words with capital letters)
    # This is a basic approach - real implementation would use NLP
    name_patterns = [
        r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Two capitalized words
    ]

    people = []
    for pattern in name_patterns:
        matches = re.finditer(pattern, email_content)
        for match in matches:
            person = match.group(0 if len(match.groups()) == 0 else 1).strip()
            if len(person) > 2:
                people.append(person)

    # Remove duplicates while preserving order
    unique_people = []
    seen = set()
    for person in people:
        person_lower = person.lower()
        if person_lower not in seen:
            seen.add(person_lower)
            unique_people.append(person)

    return unique_people


def create_task_plan(email_file_path, subject, tasks, deadlines, people):
    """
    Create or update a Plan.md file with extracted tasks in checklist format
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_filename = f"plan_{timestamp}_tasks_from_{Path(email_file_path).stem}.md"
    plan_path = Path("Plans") / plan_filename

    # Create checklist format
    task_items = []
    for i, task in enumerate(tasks, 1):
        task_items.append(f"{i}. [ ] {task}")

    task_list = "\n".join(task_items)

    # Create plan content
    plan_content = f"""---
title: "Task Plan: {subject}"
created: "{datetime.now().isoformat()}"
status: pending
source: "{email_file_path}"
---

# Task Plan from: {subject}

## Extracted Tasks
{task_list if task_list else 'No tasks identified'}

## Related Deadlines
{chr(10).join(f"- {deadline}" for deadline in deadlines) if deadlines else 'No deadlines identified'}

## People Involved
{chr(10).join(f"- {person}" for person in people) if people else 'No people identified'}

## Next Steps
1. [ ] Review extracted tasks for accuracy
2. [ ] Prioritize tasks based on urgency
3. [ ] Assign or execute tasks as appropriate
4. [ ] Update status as tasks are completed

## Notes
- Tasks extracted by Task Extractor skill
- Refer to original email for full context

---
*Created by Task Extractor Skill at {datetime.now().isoformat()}*
"""

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

    return plan_path


def update_dashboard(tasks):
    """
    Update Dashboard.md with pending tasks
    """
    if not tasks:
        return

    # Read current dashboard
    dashboard_path = Path("Dashboard.md")
    if not dashboard_path.exists():
        return

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update pending tasks count
    # Count current pending tasks by looking for unchecked items
    pending_pattern = r'\[ \]'
    current_pending_count = len(re.findall(pending_pattern, content))

    # Add the new tasks to the count
    new_pending_count = current_pending_count + len(tasks)

    # Update the count in dashboard
    import re
    content = re.sub(r'\{\{pending_tasks_count\}\}', str(new_pending_count), content)
    if '{{pending_tasks_count}}' not in content:
        content = content.replace('{{pending_tasks_count}}', str(new_pending_count))

    # Add to recent activity
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_entry = f"[{timestamp}] Extracted {len(tasks)} tasks from email\n"

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

    extract_tasks(email_file_path)

    print("\n<COMPLETE>")
    print("Task Extractor skill completed. Tasks extracted and added to Plans folder.")
    print("</COMPLETE>")
```

## Usage Instructions
1. Call this skill with the path to an email file: `python Skills/03_TASK_EXTRACTOR.py Needs_Action/email_file.md`
2. The skill will extract tasks and create a Plan.md file in the Plans/ folder
3. Dashboard.md will be updated with new pending tasks
4. Tasks will be formatted in checklist format for easy tracking

## References
- Follows Company_Handbook.md task management guidelines
- Uses checklist format for clear progress tracking

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations