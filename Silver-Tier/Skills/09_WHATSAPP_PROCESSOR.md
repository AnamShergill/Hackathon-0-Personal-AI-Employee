# Skill: WhatsApp Processor

## Overview
This skill processes WhatsApp messages from the Needs_Action folder, analyzes their content and priority, creates actionable plans or reply drafts in the Plans folder, and updates the Dashboard. Designed for short-form, conversational messages with different tone requirements than email.

## Version
1.0 - Silver Tier

## Prerequisites
- WhatsApp Watcher has created message files in Needs_Action/
- Main Orchestrator (00) has identified WhatsApp messages
- Python 3.13+
- Required dependencies installed

## Input
- WhatsApp message markdown files in Needs_Action/ folder with YAML frontmatter
- Source field must be "WhatsApp"

## Output
- Action plans in Plans/ folder
- Reply drafts in Plans/ (WhatsApp-style: short, casual)
- HITL flags for sensitive content
- Processed files moved to Done/
- Dashboard updates

## YAML Frontmatter
```yaml
---
skill_id: 09_WHATSAPP_PROCESSOR
execution_order: 3
triggers: ["whatsapp_message_received", "orchestrator_routed"]
dependencies: ["00_MAIN_ORCHESTRATOR"]
completion_criteria: ["all_whatsapp_processed", "plans_created", "files_moved_to_done"]
---
```

## Process
1. List all WhatsApp files in Needs_Action/ (source: "WhatsApp")
2. Read each message file
3. Analyze content, sender, priority, and urgency
4. Determine action type:
   - **Reply needed**: Draft short WhatsApp-style response
   - **Task extraction**: Create action plan
   - **Information only**: Log and archive
5. Check for HITL requirements (money, personal info, contracts)
6. Create plans/drafts in Plans/ folder
7. Update Dashboard.md with summary
8. Move processed files to Done/ folder with <COMPLETE> status

## WhatsApp-Specific Handling
- **Tone**: More casual than email (but still professional)
- **Length**: Keep replies under 1000 characters
- **Format**: Short paragraphs, use emojis sparingly if appropriate
- **Urgency**: WhatsApp messages often expect faster response
- **Context**: May lack subject line - infer intent from message body

## Implementation

```python
import os
import glob
import yaml
import re
from datetime import datetime
from pathlib import Path

def process_whatsapp_messages():
    """
    Process all WhatsApp message files in Needs_Action folder
    """
    print("=" * 80)
    print("WHATSAPP PROCESSOR - Processing WhatsApp Messages")
    print("=" * 80)
    print()

    # Get all WhatsApp files in Needs_Action
    all_files = glob.glob("Needs_Action/whatsapp_*.md")

    # Also check for files with source: WhatsApp in frontmatter
    other_files = glob.glob("Needs_Action/*.md")
    for file_path in other_files:
        if file_path not in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'source: "WhatsApp"' in content or "source: 'WhatsApp'" in content or 'source: WhatsApp' in content:
                    all_files.append(file_path)
            except:
                pass

    if not all_files:
        print("✅ No WhatsApp messages to process")
        return

    print(f"📱 Found {len(all_files)} WhatsApp messages to process")
    print()

    processed_count = 0
    for message_file in all_files:
        try:
            # Read the message file
            with open(message_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Separate YAML frontmatter from content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_frontmatter = parts[1]
                    message_body = parts[2]

                    # Load YAML data
                    message_data = yaml.safe_load(yaml_frontmatter)

                    # Process the message
                    process_single_message(message_data, message_body, message_file)

                    # Move the file to Done
                    move_to_done(message_file)

                    processed_count += 1
                    print(f"✅ Processed: {Path(message_file).name}")
                    print()

        except Exception as e:
            print(f"❌ Error processing {message_file}: {e}")
            print()

    # Update dashboard
    update_dashboard(len(all_files), processed_count)

    print("=" * 80)
    print(f"WhatsApp processing complete. Processed {processed_count}/{len(all_files)} messages.")
    print("=" * 80)


def process_single_message(message_data, message_body, original_file):
    """
    Process a single WhatsApp message - determine action and create plan/draft
    """
    # Extract information from message
    sender = message_data.get('sender', 'Unknown Contact')
    message_text = extract_message_text(message_body)
    priority = message_data.get('priority', 'medium')
    timestamp = message_data.get('timestamp', 'Unknown')
    date_received = message_data.get('date_received', 'Unknown Date')
    message_id = message_data.get('message_id', 'unknown')

    print(f"📱 Processing message from: {sender}")
    print(f"   Priority: {priority.upper()}")
    print(f"   Length: {len(message_text)} chars")

    # Determine action type
    action_type = determine_action_type(message_text, sender, priority)
    print(f"   Action: {action_type}")

    # Check for HITL requirements
    hitl_required, hitl_reason = check_hitl_requirements(message_text, sender)
    if hitl_required:
        print(f"   ⚠️  HITL Required: {hitl_reason}")

    # Create appropriate output based on action type
    if action_type == 'reply_needed':
        create_reply_draft(message_data, message_text, original_file, hitl_required, hitl_reason)
    elif action_type == 'task_extraction':
        create_task_plan(message_data, message_text, original_file, hitl_required, hitl_reason)
    elif action_type == 'information_only':
        create_info_log(message_data, message_text, original_file)
    else:
        # Default: create a plan
        create_task_plan(message_data, message_text, original_file, hitl_required, hitl_reason)


def extract_message_text(message_body):
    """
    Extract clean message text from markdown body
    """
    # Remove markdown headers and formatting
    text = re.sub(r'^#+\s+.*$', '', message_body, flags=re.MULTILINE)
    text = re.sub(r'\*\*.*?\*\*:', '', text)
    text = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
    text = re.sub(r'\*Processed by.*?\*', '', text)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def determine_action_type(message_text, sender, priority):
    """
    Determine what action to take based on message content
    """
    text_lower = message_text.lower()

    # Check for question indicators
    question_indicators = ['?', 'how', 'what', 'when', 'where', 'why', 'who', 'can you', 'could you', 'please']
    has_question = any(indicator in text_lower for indicator in question_indicators)

    # Check for request indicators
    request_indicators = ['please', 'need', 'want', 'require', 'send', 'share', 'provide', 'help']
    has_request = any(indicator in text_lower for indicator in request_indicators)

    # Check for urgent/action indicators
    urgent_indicators = ['urgent', 'asap', 'immediately', 'now', 'quick', 'fast', 'hurry']
    is_urgent = any(indicator in text_lower for indicator in urgent_indicators)

    # Check for task indicators
    task_indicators = ['todo', 'task', 'action', 'complete', 'finish', 'deadline', 'by tomorrow', 'by today']
    has_task = any(indicator in text_lower for indicator in task_indicators)

    # Decision logic
    if has_question or has_request or is_urgent:
        return 'reply_needed'
    elif has_task or priority == 'high':
        return 'task_extraction'
    elif len(message_text) < 50 and not has_question:
        # Very short messages without questions are likely just info
        return 'information_only'
    else:
        # Default: extract task
        return 'task_extraction'


def check_hitl_requirements(message_text, sender):
    """
    Check if message requires Human-In-The-Loop approval
    Based on Company_Handbook.md authorization thresholds
    """
    text_lower = message_text.lower()

    # Check for financial mentions
    money_keywords = [
        'payment', 'pay', 'invoice', 'cost', 'price', 'charge', 'fee',
        'bill', 'money', 'funds', 'budget', 'purchase', 'order', 'transaction',
        '$', '€', '£', '¥', 'rs', 'pkr', 'amount', 'dollar', 'rupee'
    ]
    has_money = any(keyword in text_lower for keyword in money_keywords)

    # Check for personal/sensitive info
    sensitive_keywords = [
        'password', 'account', 'login', 'credit card', 'bank', 'ssn',
        'personal', 'confidential', 'private', 'secret', 'sensitive'
    ]
    has_sensitive = any(keyword in text_lower for keyword in sensitive_keywords)

    # Check for contract/legal
    legal_keywords = [
        'contract', 'agreement', 'legal', 'sign', 'signature', 'terms',
        'conditions', 'policy', 'compliance', 'regulation'
    ]
    has_legal = any(keyword in text_lower for keyword in legal_keywords)

    # Check for attachment requests
    attachment_keywords = [
        'attachment', 'attach', 'file', 'document', 'pdf', 'send file',
        'share file', 'upload', 'download'
    ]
    has_attachment = any(keyword in text_lower for keyword in attachment_keywords)

    # Determine HITL requirement
    if has_money:
        return True, "Financial transaction mentioned"
    elif has_sensitive:
        return True, "Sensitive personal information"
    elif has_legal:
        return True, "Legal/contract content"
    elif has_attachment:
        return True, "File attachment requested"
    else:
        return False, None


def create_reply_draft(message_data, message_text, original_file, hitl_required, hitl_reason):
    """
    Create a WhatsApp-style reply draft (short, casual, under 1000 chars)
    """
    sender = message_data.get('sender', 'Unknown Contact')
    priority = message_data.get('priority', 'medium')
    message_id = message_data.get('message_id', 'unknown')

    # Generate reply text
    reply_text = generate_whatsapp_reply(message_text, sender, priority)

    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reply_filename = f"REPLY_WhatsApp_{message_id}_{timestamp}.md"
    reply_path = Path("Plans") / reply_filename

    # Create reply draft file
    reply_content = f"""---
type: "whatsapp_reply_draft"
original_file: "{original_file}"
sender: "{sender}"
message_id: "{message_id}"
generated: "{datetime.now().isoformat()}"
requires_approval: {hitl_required}
approval_reason: "{hitl_reason if hitl_reason else 'N/A'}"
priority: {priority}
---

# WhatsApp Reply Draft

## To: {sender}

## Original Message
{message_text}

## Draft Reply
{reply_text}

## Processing Notes
- **HITL Required**: {'Yes' if hitl_required else 'No'}
- **Reason**: {hitl_reason if hitl_reason else 'Standard reply'}
- **Character Count**: {len(reply_text)}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Instructions
{'⚠️ This reply requires human approval before sending.' if hitl_required else '✅ This reply can be sent automatically if configured.'}

---
*Created by WhatsApp Processor at {datetime.now().isoformat()}*
"""

    with open(reply_path, 'w', encoding='utf-8') as f:
        f.write(reply_content)

    print(f"   📝 Reply draft created: {reply_filename}")


def generate_whatsapp_reply(message_text, sender, priority):
    """
    Generate a short, casual WhatsApp-style reply (under 1000 chars)
    """
    text_lower = message_text.lower()

    # Determine tone based on priority and content
    if priority == 'high' or 'urgent' in text_lower:
        greeting = "Got it!"
    else:
        greeting = "Hi!"

    # Generate contextual response
    reply_parts = [greeting]

    # Check message type and respond appropriately
    if '?' in message_text:
        # It's a question
        if 'when' in text_lower or 'time' in text_lower:
            reply_parts.append("Let me check on that timing and get back to you shortly.")
        elif 'how' in text_lower:
            reply_parts.append("I'll look into this and send you the details soon.")
        elif 'what' in text_lower or 'which' in text_lower:
            reply_parts.append("Good question! I'll find out and let you know.")
        else:
            reply_parts.append("Thanks for reaching out. I'll get you an answer on this.")

    elif any(word in text_lower for word in ['please', 'need', 'want', 'can you']):
        # It's a request
        reply_parts.append("Sure, I can help with that. Let me take care of it and update you.")

    elif any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'now']):
        # Urgent message
        reply_parts.append("I see this is urgent. I'm on it and will update you ASAP.")

    elif any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
        # Gratitude
        reply_parts.append("You're welcome! Happy to help. Let me know if you need anything else.")

    elif len(message_text) < 50:
        # Short message - acknowledge
        reply_parts.append("Noted! I'll take care of it.")

    else:
        # Default response
        reply_parts.append("Thanks for the message. I've noted this and will follow up as needed.")

    # Add closing if appropriate
    if priority == 'high':
        reply_parts.append("I'll prioritize this.")

    # Combine and ensure under 1000 chars
    reply = ' '.join(reply_parts)

    if len(reply) > 1000:
        reply = reply[:997] + "..."

    return reply


def create_task_plan(message_data, message_text, original_file, hitl_required, hitl_reason):
    """
    Create an action plan for WhatsApp message
    """
    sender = message_data.get('sender', 'Unknown Contact')
    priority = message_data.get('priority', 'medium')
    message_id = message_data.get('message_id', 'unknown')
    timestamp = message_data.get('timestamp', 'Unknown')

    # Generate plan filename
    plan_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create safe filename from sender
    safe_sender = re.sub(r'[^\w\s-]', '', sender)[:30].strip().replace(' ', '_')
    plan_filename = f"Plan_WhatsApp_{message_id}_{safe_sender}.md"
    plan_path = Path("Plans") / plan_filename

    # Extract action items
    action_items = extract_action_items(message_text)

    # Create plan content
    plan_content = f"""---
type: "whatsapp_action_plan"
source: "WhatsApp"
sender: "{sender}"
message_id: "{message_id}"
created: "{datetime.now().isoformat()}"
status: "pending"
priority: {priority}
requires_approval: {hitl_required}
approval_reason: "{hitl_reason if hitl_reason else 'N/A'}"
---

# WhatsApp Action Plan: {sender}

## Message Details
- **From**: {sender}
- **Received**: {timestamp}
- **Priority**: {priority.upper()}
- **Message ID**: {message_id}

## Original Message
```
{message_text}
```

## Summary
{extract_summary_whatsapp(message_text)}

## Action Items
{action_items}

## HITL Status
- **Required**: {'Yes' if hitl_required else 'No'}
- **Reason**: {hitl_reason if hitl_reason else 'Standard processing'}

## Next Steps
1. {'⚠️ Obtain human approval' if hitl_required else '✅ Proceed with action items'}
2. Execute planned actions
3. Send reply/update to sender
4. Mark as complete

## Notes
- Source: WhatsApp message
- Processing: Automated via WhatsApp Processor skill
- Refer to original file: {original_file}

---
*Created by WhatsApp Processor at {datetime.now().isoformat()}*
"""

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

    print(f"   📋 Action plan created: {plan_filename}")


def extract_action_items(message_text):
    """
    Extract actionable items from WhatsApp message
    """
    text_lower = message_text.lower()
    items = []

    # Check for explicit action requests
    if 'please' in text_lower or 'can you' in text_lower or 'could you' in text_lower:
        items.append("- Respond to sender's request")

    if '?' in message_text:
        items.append("- Answer question(s) from sender")

    if any(word in text_lower for word in ['send', 'share', 'provide']):
        items.append("- Provide requested information/files")

    if any(word in text_lower for word in ['urgent', 'asap', 'immediately']):
        items.append("- Prioritize for immediate action")

    if any(word in text_lower for word in ['meeting', 'call', 'schedule']):
        items.append("- Schedule/coordinate meeting or call")

    if not items:
        # Default action items
        items = [
            "- Review message content",
            "- Determine appropriate response",
            "- Take necessary action",
            "- Follow up with sender"
        ]

    return '\n'.join(items)


def extract_summary_whatsapp(message_text):
    """
    Create a brief summary of WhatsApp message
    """
    # For short messages, return as-is
    if len(message_text) <= 150:
        return message_text.strip()

    # For longer messages, get first 150 chars
    summary = message_text[:150].strip()

    # Try to end at a sentence
    last_period = summary.rfind('.')
    if last_period > 50:
        summary = summary[:last_period + 1]
    else:
        summary += "..."

    return summary


def create_info_log(message_data, message_text, original_file):
    """
    Create a simple log entry for information-only messages
    """
    sender = message_data.get('sender', 'Unknown Contact')
    message_id = message_data.get('message_id', 'unknown')

    # Create log filename
    log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"Log_WhatsApp_{message_id}.md"
    log_path = Path("Plans") / log_filename

    log_content = f"""---
type: "whatsapp_info_log"
sender: "{sender}"
message_id: "{message_id}"
logged: "{datetime.now().isoformat()}"
status: "logged"
---

# WhatsApp Info Log

## From: {sender}

## Message
{message_text}

## Action Taken
- Message logged for reference
- No reply or action required
- Archived automatically

---
*Logged by WhatsApp Processor at {datetime.now().isoformat()}*
"""

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)

    print(f"   📄 Info log created: {log_filename}")


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
        content += f"""

<COMPLETE>
Processed by WhatsApp Processor at {datetime.now().isoformat()}
</COMPLETE>
"""

    # Write to Done folder
    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Remove original file
    os.remove(file_path)


def update_dashboard(total_messages, processed_count):
    """
    Update Dashboard.md with WhatsApp processing summary
    """
    try:
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            return

        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create activity entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        activity_entry = f"[{timestamp}] WhatsApp Processor: Processed {processed_count}/{total_messages} messages\n"

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
    process_whatsapp_messages()

    print()
    print("<COMPLETE>")
    print("WhatsApp Processor skill completed. All WhatsApp messages processed.")
    print("Plans/drafts created in Plans/ folder. Processed messages moved to Done/.")
    print("</COMPLETE>")
```

## Usage Instructions
1. Run AFTER Main Orchestrator (00) has identified WhatsApp messages
2. Processes only files with source: "WhatsApp"
3. Creates reply drafts (short, casual tone)
4. Creates action plans for tasks
5. Flags sensitive content for HITL
6. Updates Dashboard with processing stats

## Expected Outcomes
- All WhatsApp messages in Needs_Action/ are processed
- Reply drafts created in Plans/ (under 1000 chars, casual tone)
- Action plans created for tasks
- HITL flags set for sensitive content (money, personal info, contracts)
- Processed messages moved to Done/ with completion markers
- Dashboard updated with WhatsApp processing summary

## Differences from Email Processor
- **Tone**: More casual, conversational
- **Length**: Shorter replies (under 1000 chars)
- **Format**: No subject line, simpler structure
- **Speed**: WhatsApp expects faster responses
- **Context**: Less formal, more direct

## Error Handling
- Files that fail to process remain in Needs_Action/
- Errors are logged for debugging
- Processing continues with other files if one fails

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Standard library for file operations
- Company_Handbook.md for HITL rules

---
*WhatsApp Processor - Silver Tier Multi-Source Support*
