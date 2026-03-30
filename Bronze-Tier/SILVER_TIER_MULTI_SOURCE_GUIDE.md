# Silver Tier Multi-Source Integration Guide

## Overview
The system now supports multiple message sources (Gmail + WhatsApp) with a central orchestrator pattern. This guide explains the new architecture and required changes.

## New Architecture

### Flow Diagram
```
Watchers (Gmail, WhatsApp)
    ↓
Needs_Action/ (.md files)
    ↓
00_MAIN_ORCHESTRATOR (routes by source)
    ↓
├─→ 01_EMAIL_PROCESSOR (Gmail)
├─→ 09_WHATSAPP_PROCESSOR (WhatsApp)
└─→ Future processors (Slack, Teams, etc.)
    ↓
Plans/ (action plans, reply drafts)
    ↓
Dashboard updates
    ↓
Done/ (completed items)
```

## New Files Created

### 1. Skills/00_MAIN_ORCHESTRATOR.md
- **Purpose**: Central router for all incoming messages
- **Execution Order**: FIRST (before any source-specific processors)
- **Function**: Reads frontmatter "source" field, routes to appropriate processor
- **Handles**: Unknown sources, malformed files, quarantine

### 2. Skills/09_WHATSAPP_PROCESSOR.md
- **Purpose**: Process WhatsApp messages specifically
- **Execution Order**: AFTER orchestrator
- **Function**: Creates plans/drafts with WhatsApp-appropriate tone
- **Features**: Short replies (<1000 chars), casual tone, HITL for sensitive content

## Required Changes to Existing Files

### 1. Update Ralph Wiggum Loop Prompt

**File**: Your main orchestrator.py or wherever you run the Ralph loop

**OLD prompt** (example):
```
Process all files in Needs_Action/ using 01_EMAIL_PROCESSOR...
```

**NEW prompt**:
```
You are the autonomous Personal AI Employee (Silver Tier - Multi-Source).
Ralph Wiggum loop starting now.

Task:
Process all files currently in Needs_Action/ from ALL sources (Gmail, WhatsApp, etc.).

Execution Order:
1. FIRST: Run 00_MAIN_ORCHESTRATOR to identify and route all files by source
2. THEN: Run 01_EMAIL_PROCESSOR for Gmail messages
3. THEN: Run 09_WHATSAPP_PROCESSOR for WhatsApp messages
4. THEN: Run other skills as needed (priority scoring, task extraction, dashboard updates)

For each source:
- Read the .md file
- Use appropriate processor based on source type
- Create plans/drafts in Plans/
- Flag for HITL if needed (money, sensitive info, contracts)
- Move to Done/ when complete

Follow all rules in Company_Handbook.md and CLAUDE.md strictly.

Print short status after each processor completes.
Output <COMPLETE> only when Needs_Action/ is completely empty.

Start the loop now — show step-by-step progress.
```

### 2. Update Dashboard.md Format

**File**: Dashboard.md

**Add new section** after "Active Watchers":

```markdown
## Active Watchers
- **Gmail Watcher**: `Running (300s interval)`
- **WhatsApp Watcher**: `Running (60s interval)`
- **File Watcher**: `Not configured`
- **API Watcher**: `Not configured`

## Message Sources (Last 24h)
- **Gmail**: `5 messages processed`
- **WhatsApp**: `12 messages processed`
- **Total**: `17 messages processed`
```

**Update Recent Activity Log** to show source:

```markdown
## Recent Activity Log
```
[2026-03-20 18:00:00] Orchestrator: Routed 6 files (Gmail:2, WhatsApp:4, Unknown:0, Errors:0)
[2026-03-20 18:00:05] Email Processor: Processed 2/2 Gmail messages
[2026-03-20 18:00:10] WhatsApp Processor: Processed 4/4 WhatsApp messages
[2026-03-20 18:00:15] Created 6 action plans (3 HIGH, 2 MEDIUM, 1 LOW)
[2026-03-20 18:00:15] Drafted 3 replies (1 email, 2 WhatsApp)
{{recent_activity}}
```
```

### 3. Update Company_Handbook.md (Optional Enhancement)

**File**: Company_Handbook.md

**Add new section** after "Communication Standards":

```markdown
### 6. Multi-Source Communication Guidelines

#### Email (Gmail)
- **Tone**: Professional, formal
- **Length**: Detailed, comprehensive
- **Response Time**: Within 24 hours (standard), 2 hours (urgent)
- **Format**: Subject line, greeting, body, signature

#### WhatsApp
- **Tone**: Professional but casual, conversational
- **Length**: Brief, under 1000 characters
- **Response Time**: Within 2 hours (standard), 30 minutes (urgent)
- **Format**: Direct message, minimal formatting

#### General Rules
- Match the tone and style of the incoming message source
- Maintain professionalism across all channels
- Escalate to HITL for sensitive content regardless of source
- Log all communications in Dashboard
```

### 4. Update orchestrator.py (Main Script)

**File**: orchestrator.py

**Add multi-source support**:

```python
# OLD (Bronze Tier)
def run_ralph_loop():
    """Run the Ralph Wiggum autonomous loop"""
    # Process emails only
    run_skill("01_EMAIL_PROCESSOR")
    # ...

# NEW (Silver Tier)
def run_ralph_loop():
    """Run the Ralph Wiggum autonomous loop - Multi-Source"""
    print("Starting Ralph Wiggum Loop - Silver Tier Multi-Source")
    
    # Step 1: Route all messages by source
    print("\n=== STEP 1: Main Orchestrator ===")
    stats = run_skill("00_MAIN_ORCHESTRATOR")
    
    # Step 2: Process Gmail messages
    if stats.get('gmail', 0) > 0:
        print("\n=== STEP 2: Email Processor ===")
        run_skill("01_EMAIL_PROCESSOR")
    
    # Step 3: Process WhatsApp messages
    if stats.get('whatsapp', 0) > 0:
        print("\n=== STEP 3: WhatsApp Processor ===")
        run_skill("09_WHATSAPP_PROCESSOR")
    
    # Step 4: Other skills (priority, tasks, dashboard)
    print("\n=== STEP 4: Additional Processing ===")
    run_skill("04_PRIORITY_SCORER")
    run_skill("03_TASK_EXTRACTOR")
    run_skill("05_DASHBOARD_UPDATER")
    
    print("\n<COMPLETE>")
```

## Testing the Multi-Source System

### Test Scenario 1: Mixed Messages
1. Send yourself a Gmail (starred/important)
2. Send yourself a WhatsApp message
3. Run Ralph loop
4. Verify:
   - Orchestrator routes both correctly
   - Email processor handles Gmail
   - WhatsApp processor handles WhatsApp
   - Both create appropriate plans in Plans/
   - Both moved to Done/

### Test Scenario 2: WhatsApp with HITL
1. Send WhatsApp message with "payment $500"
2. Run Ralph loop
3. Verify:
   - WhatsApp processor detects money keyword
   - Plan flagged with `requires_approval: true`
   - Dashboard shows HITL required

### Test Scenario 3: Unknown Source
1. Manually create a .md file with `source: "Slack"`
2. Run Ralph loop
3. Verify:
   - Orchestrator logs unknown source
   - File moved to Done/ with note
   - Dashboard updated

## File Naming Conventions

### Gmail Messages
- Format: `email_YYYYMMDD_HHMMSS_<gmail_id>.md`
- Source: `Gmail`
- Created by: Gmail Watcher

### WhatsApp Messages
- Format: `whatsapp_YYYYMMDD_HHMMSS_<message_id>.md`
- Source: `WhatsApp`
- Created by: WhatsApp Watcher

### Plans/Drafts
- Email reply: `REPLY_email_<id>.md`
- WhatsApp reply: `REPLY_WhatsApp_<id>_<timestamp>.md`
- Email plan: `plan_<timestamp>_<subject>.md`
- WhatsApp plan: `Plan_WhatsApp_<id>_<sender>.md`

## Benefits of Multi-Source Architecture

1. **Scalability**: Easy to add new sources (Slack, Teams, SMS)
2. **Separation of Concerns**: Each processor handles its source's specifics
3. **Consistent Routing**: Central orchestrator ensures no messages missed
4. **Source-Appropriate Responses**: Email vs WhatsApp tone/length
5. **Unified HITL**: Same rules apply across all sources
6. **Dashboard Visibility**: See all sources in one place

## Future Extensions

### Planned Sources (Gold Tier+)
- **Slack**: Team messaging, threads, reactions
- **Microsoft Teams**: Enterprise messaging
- **SMS/Twilio**: Text messages
- **Discord**: Community/server messages
- **Telegram**: Secure messaging
- **API Webhooks**: Custom integrations

### Adding a New Source
1. Create watcher: `Watchers/<source>_watcher.py`
2. Create processor: `Skills/XX_<SOURCE>_PROCESSOR.md`
3. Update orchestrator routing logic
4. Add to Dashboard tracking
5. Test end-to-end flow

## Troubleshooting

### Issue: Orchestrator not routing correctly
- Check frontmatter has `source:` field
- Verify source name matches exactly (case-sensitive)
- Check orchestrator logs in console output

### Issue: WhatsApp processor not finding files
- Ensure filename starts with `whatsapp_`
- OR ensure frontmatter has `source: "WhatsApp"`
- Check file is in Needs_Action/ not Done/

### Issue: HITL not triggering
- Review Company_Handbook.md rules
- Check keyword lists in processor code
- Verify `requires_approval` field in plan

## Summary

The Silver Tier multi-source system is now complete with:
- ✅ Central orchestrator (00_MAIN_ORCHESTRATOR)
- ✅ WhatsApp processor (09_WHATSAPP_PROCESSOR)
- ✅ Source-appropriate tone and formatting
- ✅ Unified HITL across all sources
- ✅ Dashboard tracking for all sources
- ✅ Scalable architecture for future sources

Next steps: Test with real messages, refine tone/responses, add more sources!
