# Skill 18: Local Executive (Execution-Only Zone)

## Purpose

Local-based AI agent that runs periodically on the user's machine. Handles all execution, approval, and final actions. **NEVER drafts** - only executes approved tasks from Cloud.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│        Local Executive (Runs Periodically)               │
│              User's Local Machine                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Email Executor│    │Social Executor│   │ Odoo Executor│
│              │    │              │    │              │
│ - Approve    │    │ - Approve    │    │ - Approve    │
│ - Send       │    │ - Post       │    │ - Record     │
│ - HITL       │    │ - HITL       │    │ - HITL       │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │    Vault/Done/        │
                │  Dashboard.md         │
                └───────────────────────┘
```

---

## When to Use

- **Periodically**: Local executive runs every 5 minutes (or on-demand)
- **Approval needed**: Present drafts to human for approval
- **Final execution**: Send emails, post to social, record payments
- **Dashboard updates**: Merge updates from Cloud
- **WhatsApp operations**: All WhatsApp interactions
- **Banking operations**: All payment executions

## When NOT to Use

- Drafting (Cloud only)
- 24/7 monitoring (Cloud only)
- Automated triage (Cloud only)
- Read-only analysis (Cloud only)

---

## Allowed Operations (Execution-Only)

### ✅ Permitted Actions

1. **Email Operations**
   - Send emails via SMTP
   - Access SMTP credentials
   - Final email delivery
   - Email signature injection

2. **Social Media Operations**
   - Post to LinkedIn
   - Post to Facebook
   - Access social media sessions
   - Final post publishing

3. **Odoo Operations**
   - Create invoices
   - Record payments
   - Modify partners
   - All write operations

4. **Payment Operations**
   - Execute payments
   - Access banking credentials
   - Record transactions

5. **WhatsApp Operations**
   - Access WhatsApp session
   - Send WhatsApp messages
   - Read WhatsApp messages

6. **Local Operations**
   - Update Dashboard.md
   - Access local secrets
   - Modify local state
   - Merge Cloud updates

7. **HITL Operations**
   - Present drafts for approval
   - Collect human feedback
   - Execute approved actions
   - Reject/modify drafts

### ❌ Forbidden Actions

1. **Drafting Operations**
   - ❌ Draft email replies (Cloud does this)
   - ❌ Draft social posts (Cloud does this)
   - ❌ Generate briefings (Cloud does this)
   - ❌ Automated triage (Cloud does this)

2. **24/7 Operations**
   - ❌ Continuous monitoring (Cloud does this)
   - ❌ Always-on watchers (Cloud does this)

---

## Local Executive Workflow

### Main Loop (Periodic)

```python
def local_executive_main_loop():
    """
    Local executive main loop - runs periodically.
    """
    logger.info("Local Executive starting periodic check...")
    
    while True:
        try:
            # 1. Scan for pending approvals
            pending_tasks = scan_pending_approval()
            
            # 2. Present to human for approval
            if pending_tasks:
                approved_tasks = present_for_approval(pending_tasks)
                
                # 3. Execute approved tasks
                for task in approved_tasks:
                    execute_local_task(task)
            
            # 4. Check for updates from Cloud
            process_cloud_updates()
            
            # 5. Update Dashboard
            update_dashboard()
            
            # 6. Check for signals from Cloud
            process_signals()
            
            # 7. Health check
            if time_for_health_check():
                perform_health_check()
            
            # 8. Sleep
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Local executive error: {e}")
            time.sleep(60)  # Wait longer on error
```

### Task Execution

```python
def execute_local_task(task_path: str):
    """
    Execute a single approved task in Local zone.
    """
    # 1. Claim task
    if not claim_task(task_path, 'local'):
        logger.info(f"Task already claimed: {task_path}")
        return
    
    # 2. Classify task
    classification = classify_task(task_path)
    action_type = classification['action_type']
    
    # 3. Route to appropriate executor
    if action_type == 'email_send':
        execute_email_send(task_path)
    elif action_type == 'social_post':
        execute_social_post(task_path)
    elif action_type == 'odoo_payment':
        execute_odoo_payment(task_path)
    elif action_type == 'odoo_invoice':
        execute_odoo_invoice(task_path)
    else:
        logger.warning(f"Unknown action type: {action_type}")
        release_task(task_path)
```

---

## HITL Approval Interface

### Approval Presentation

```python
def present_for_approval(pending_tasks: List[str]) -> List[str]:
    """
    Present pending tasks to human for approval.
    """
    approved_tasks = []
    
    for task in pending_tasks:
        # 1. Read task details
        task_data = read_task_file(task)
        
        # 2. Display to human
        print("\n" + "="*60)
        print(f"APPROVAL REQUIRED: {task_data['type']}")
        print("="*60)
        print(f"\nTask: {task_data['title']}")
        print(f"Domain: {task_data['domain']}")
        print(f"Drafted by: {task_data['drafted_by']}")
        print(f"Drafted at: {task_data['drafted_at']}")
        print("\n" + "-"*60)
        print("CONTENT:")
        print("-"*60)
        print(task_data['content'])
        print("-"*60)
        
        # 3. Get human decision
        decision = input("\nApprove? (y/n/e for edit): ").lower()
        
        if decision == 'y':
            # Approved - add to execution queue
            approved_tasks.append(task)
            logger.info(f"✅ Approved: {task}")
            
        elif decision == 'e':
            # Edit - open in editor
            edited_task = edit_task_in_editor(task)
            approved_tasks.append(edited_task)
            logger.info(f"✏️ Edited and approved: {task}")
            
        else:
            # Rejected - move back to Needs_Action
            reject_task(task, "Human rejected")
            logger.info(f"❌ Rejected: {task}")
    
    return approved_tasks
```

### Interactive Approval UI

```python
def interactive_approval_ui():
    """
    Rich interactive UI for approvals (using rich library).
    """
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
    
    console = Console()
    
    # 1. Scan pending approvals
    pending = scan_pending_approval()
    
    if not pending:
        console.print("[green]✅ No pending approvals[/green]")
        return []
    
    # 2. Display table
    table = Table(title="Pending Approvals")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Domain", style="yellow")
    table.add_column("Drafted", style="green")
    
    for idx, task in enumerate(pending, 1):
        data = read_task_file(task)
        table.add_row(
            str(idx),
            data['type'],
            data['domain'],
            data['drafted_at']
        )
    
    console.print(table)
    
    # 3. Get selection
    selection = Prompt.ask(
        "Select task to review (number) or 'all' to approve all",
        default="1"
    )
    
    # 4. Process selection
    if selection == 'all':
        return approve_all_tasks(pending)
    else:
        task_idx = int(selection) - 1
        return [approve_single_task(pending[task_idx])]
```

---

## Email Execution

### Send Email

```python
def execute_email_send(task_path: str):
    """
    Execute email send action.
    """
    # 1. Read email draft
    email_data = read_email_draft(task_path)
    
    # 2. Use Gold Tier email sender
    from gold_tier.actions import EmailSender
    
    sender = EmailSender()
    
    # 3. Send email (with retry logic)
    success, message_id, error = sender.send_email(
        to_email=email_data['to'],
        subject=email_data['subject'],
        body=email_data['body'],
        cc=email_data.get('cc'),
        bcc=email_data.get('bcc'),
        attachments=email_data.get('attachments')
    )
    
    # 4. Handle result
    if success:
        logger.info(f"✅ Email sent: {message_id}")
        
        # Update Dashboard
        update_dashboard_email_sent(email_data, message_id)
        
        # Move to Done
        move_to_done(task_path, f"Sent: {message_id}")
        
    else:
        logger.error(f"❌ Email send failed: {error}")
        
        # Move back to Pending_Approval
        move_to_pending_approval(task_path, f"Failed: {error}")
        
        # Notify human
        notify_human(f"Email send failed: {error}")
```

---

## Social Media Execution

### Post to Social Media

```python
def execute_social_post(task_path: str):
    """
    Execute social media post action.
    """
    # 1. Read post draft
    post_data = read_social_draft(task_path)
    platform = post_data['platform']
    
    # 2. Use Gold Tier social poster
    if platform == 'linkedin':
        from gold_tier.actions import LinkedInPoster
        poster = LinkedInPoster()
    elif platform == 'facebook':
        from gold_tier.actions import FacebookPoster
        poster = FacebookPoster()
    else:
        logger.error(f"Unknown platform: {platform}")
        return
    
    # 3. Post content
    success, post_id, error = poster.post(
        content=post_data['content'],
        image=post_data.get('image'),
        visibility=post_data.get('visibility', 'public')
    )
    
    # 4. Handle result
    if success:
        logger.info(f"✅ Posted to {platform}: {post_id}")
        
        # Update Dashboard
        update_dashboard_social_posted(post_data, post_id)
        
        # Move to Done
        move_to_done(task_path, f"Posted: {post_id}")
        
    else:
        logger.error(f"❌ Post failed: {error}")
        
        # Move back to Pending_Approval
        move_to_pending_approval(task_path, f"Failed: {error}")
        
        # Notify human
        notify_human(f"Social post failed: {error}")
```

---

## Odoo Execution

### Record Payment

```python
def execute_odoo_payment(task_path: str):
    """
    Execute Odoo payment recording action.
    """
    # 1. Read payment action
    payment_data = read_payment_action(task_path)
    
    # 2. Use Gold Tier payment reconciliation
    from gold_tier.actions import PaymentReconciliation
    
    reconciler = PaymentReconciliation()
    
    # 3. Connect to Odoo (full access)
    odoo_client = get_full_odoo_client()
    
    # 4. Record payment
    success, payment_id, error = reconciler.record_payment(
        odoo_client,
        payment_data['amount'],
        payment_data['date'],
        payment_data['partner_id'],
        payment_data['invoice_id'],
        payment_data['reference']
    )
    
    # 5. Handle result
    if success:
        logger.info(f"✅ Payment recorded: {payment_id}")
        
        # Update Dashboard
        update_dashboard_payment_recorded(payment_data, payment_id)
        
        # Move to Done
        move_to_done(task_path, f"Recorded: {payment_id}")
        
    else:
        logger.error(f"❌ Payment recording failed: {error}")
        
        # Move back to Pending_Approval
        move_to_pending_approval(task_path, f"Failed: {error}")
        
        # Notify human
        notify_human(f"Payment recording failed: {error}")
```

### Create Invoice

```python
def execute_odoo_invoice(task_path: str):
    """
    Execute Odoo invoice creation action.
    """
    # 1. Read invoice action
    invoice_data = read_invoice_action(task_path)
    
    # 2. Use Gold Tier Odoo RPC
    from gold_tier.actions import OdooRPCClient
    
    odoo_client = OdooRPCClient()
    
    # 3. Create invoice
    success, invoice_id, error = odoo_client.create_invoice(
        partner_id=invoice_data['partner_id'],
        invoice_lines=invoice_data['lines'],
        invoice_date=invoice_data['date'],
        payment_term=invoice_data.get('payment_term')
    )
    
    # 4. Handle result
    if success:
        logger.info(f"✅ Invoice created: {invoice_id}")
        
        # Update Dashboard
        update_dashboard_invoice_created(invoice_data, invoice_id)
        
        # Move to Done
        move_to_done(task_path, f"Created: {invoice_id}")
        
    else:
        logger.error(f"❌ Invoice creation failed: {error}")
        
        # Move back to Pending_Approval
        move_to_pending_approval(task_path, f"Failed: {error}")
        
        # Notify human
        notify_human(f"Invoice creation failed: {error}")
```

---

## Dashboard Updates

### Merge Cloud Updates

```python
def process_cloud_updates():
    """
    Process updates from Cloud and merge into Dashboard.
    """
    # 1. Scan Updates folder
    updates = scan_vault("Updates/")
    
    for update_file in updates:
        # 2. Read update
        update_data = read_update_file(update_file)
        
        # 3. Merge into Dashboard
        merge_to_dashboard(update_data)
        
        # 4. Archive update
        move_to_done(update_file, "Merged to Dashboard")
        
        logger.info(f"✅ Merged update: {update_file}")
```

### Update Dashboard

```python
def update_dashboard():
    """
    Update Dashboard.md with latest status.
    """
    # 1. Read current Dashboard
    dashboard = read_dashboard()
    
    # 2. Collect metrics
    metrics = {
        'emails_sent_today': count_emails_sent_today(),
        'social_posts_today': count_social_posts_today(),
        'payments_recorded_today': count_payments_recorded_today(),
        'pending_approvals': count_pending_approvals(),
        'tasks_in_progress': count_tasks_in_progress('local'),
        'last_sync': get_last_sync_time(),
        'cloud_status': get_cloud_health_status()
    }
    
    # 3. Update Dashboard sections
    dashboard = update_dashboard_metrics(dashboard, metrics)
    dashboard = update_dashboard_recent_activity(dashboard)
    dashboard = update_dashboard_system_health(dashboard)
    
    # 4. Write Dashboard
    write_dashboard(dashboard)
    
    logger.info("✅ Dashboard updated")
```

### Dashboard Format

```markdown
# Personal AI Employee Dashboard

**Last Updated:** 2026-04-13 14:30:00  
**System Status:** 🟢 Healthy

---

## Today's Activity

- **Emails Sent:** 5
- **Social Posts:** 2
- **Payments Recorded:** 1
- **Pending Approvals:** 3

---

## System Health

### Cloud Zone
- **Status:** 🟢 Online
- **Uptime:** 72 hours
- **Tasks Processed:** 127
- **Last Sync:** 2 minutes ago

### Local Zone
- **Status:** 🟢 Online
- **Tasks Pending:** 3
- **Last Check:** Just now

---

## Recent Activity

### Emails (Last 5)
1. ✅ Reply to john@example.com - Sent at 14:25
2. ✅ Reply to jane@example.com - Sent at 13:10
3. ✅ Reply to support@client.com - Sent at 11:45

### Social Media (Last 3)
1. ✅ LinkedIn post about AI - Posted at 12:00
2. ✅ Facebook update - Posted at 10:30

### Odoo (Last 3)
1. ✅ Payment recorded: $3,750 - TechCorp - 14:00
2. ✅ Invoice created: INV/2026/0042 - 11:30

---

## Pending Approvals

1. 📧 Email reply to client@example.com (Drafted 5 min ago)
2. 📱 LinkedIn post about product launch (Drafted 15 min ago)
3. 💰 Payment recording: $1,200 - DesignCo (Drafted 30 min ago)

---

## Week Summary

- **Total Emails:** 47
- **Total Social Posts:** 12
- **Total Payments:** 8
- **Total Revenue:** $45,230

---

**Next Briefing:** Sunday, April 20, 2026 at 8:00 PM
```

---

## WhatsApp Operations

### WhatsApp Monitoring

```python
def monitor_whatsapp():
    """
    Monitor WhatsApp for new messages (Local only).
    """
    # Use Gold Tier WhatsApp watcher
    from gold_tier.watchers import WhatsAppWatcher
    
    watcher = WhatsAppWatcher()
    
    # 1. Check for new messages
    new_messages = watcher.check_new_messages()
    
    # 2. Process each message
    for message in new_messages:
        # 3. Create task in Vault
        create_whatsapp_task(message)
        
        logger.info(f"📱 New WhatsApp message: {message['from']}")
```

### WhatsApp Sending

```python
def send_whatsapp_message(task_path: str):
    """
    Send WhatsApp message (Local only).
    """
    # 1. Read message draft
    message_data = read_whatsapp_draft(task_path)
    
    # 2. Use Gold Tier WhatsApp sender
    from gold_tier.actions import WhatsAppSender
    
    sender = WhatsAppSender()
    
    # 3. Send message
    success, error = sender.send_message(
        to=message_data['to'],
        message=message_data['message']
    )
    
    # 4. Handle result
    if success:
        logger.info(f"✅ WhatsApp sent to {message_data['to']}")
        move_to_done(task_path, "Sent")
    else:
        logger.error(f"❌ WhatsApp send failed: {error}")
        notify_human(f"WhatsApp send failed: {error}")
```

---

## Security Enforcement

### Environment Validation

```python
def validate_local_environment():
    """
    Ensure Local environment has all required secrets.
    """
    required_vars = [
        'SMTP_USER',
        'SMTP_PASS',
        'ODOO_URL',
        'ODOO_USERNAME',
        'ODOO_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise ConfigError(f"Missing required secrets: {missing}")
    
    logger.info("✅ Local environment validated - all secrets present")
```

### Odoo Full Access

```python
def get_full_odoo_client():
    """
    Get Odoo client with full write access (Local only).
    """
    from gold_tier.actions import OdooRPCClient
    
    # Use full-access credentials
    client = OdooRPCClient()
    client.username = os.getenv('ODOO_USERNAME')
    client.password = os.getenv('ODOO_PASSWORD')
    
    # Validate connection
    if not client.test_connection():
        raise ConnectionError("Cannot connect to Odoo")
    
    return client
```

---

## Health Monitoring

### Local Health Check

```python
def perform_health_check():
    """
    Perform Local executive health check.
    """
    health = {
        'timestamp': datetime.now().isoformat(),
        'zone': 'local',
        'status': 'healthy',
        'tasks_pending_approval': count_pending_approvals(),
        'tasks_in_progress': count_tasks_in_progress('local'),
        'tasks_completed_today': count_tasks_completed_today(),
        'last_sync': get_last_sync_time(),
        'vault_accessible': test_vault_access(),
        'smtp_connection': test_smtp_connection(),
        'odoo_connection': test_odoo_connection(),
        'whatsapp_session': test_whatsapp_session(),
        'dashboard_writable': test_dashboard_writable()
    }
    
    # Write health status
    save_file('Vault/Updates/local_health.json', json.dumps(health, indent=2))
    
    # Alert if unhealthy
    if health['status'] != 'healthy':
        notify_human(f"Local unhealthy: {health}")
    
    return health
```

---

## Error Handling

### Execution Errors

```python
def handle_local_error(task: str, error: Exception):
    """
    Handle Local executive errors gracefully.
    """
    logger.error(f"Local error executing {task}: {error}")
    
    # 1. Classify error severity
    severity = classify_error_severity(error)
    
    if severity == 'critical':
        # Critical error - notify human immediately
        notify_human(f"CRITICAL: Task {task} failed: {error}")
        
        # Move to manual review
        move_to_manual_review(task)
        
    elif severity == 'high':
        # High severity - move back to Pending_Approval
        move_to_pending_approval(task, f"Failed: {error}")
        
        # Notify human
        notify_human(f"Task {task} failed: {error}")
        
    else:
        # Low severity - retry once
        schedule_retry(task, delay=60)
    
    # 2. Update Dashboard with error
    update_dashboard_error(task, error)
```

---

## Configuration

### Local Executive Config

```python
LOCAL_EXECUTIVE_CONFIG = {
    'zone': 'local',
    'mode': 'execute_only',
    'vault_path': '/Users/user/Platinum-Tier/Vault',
    'scan_interval': 300,  # 5 minutes
    'health_check_interval': 600,  # 10 minutes
    'max_concurrent_tasks': 3,
    'retry_attempts': 3,
    'retry_delay': 60,  # seconds
    'odoo_full_access': True,
    'allowed_operations': [
        'send', 'post', 'execute', 'payment', 'write', 'approve'
    ],
    'forbidden_operations': [
        'draft', 'triage', 'analyze'  # Cloud does these
    ]
}
```

---

## Deployment (Local Machine)

### Setup

```bash
# Local machine (Windows/Mac/Linux)

# 1. Clone repository
git clone https://github.com/your-repo/Platinum-Tier.git
cd Platinum-Tier

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp Config/local.env.example .env
nano .env  # Edit with Local credentials

# 4. Start Local executive
python Actions/local_executive.py

# Or run as scheduled task (cron/Task Scheduler)
# Every 5 minutes:
# */5 * * * * cd /path/to/Platinum-Tier && python Actions/local_executive.py
```

---

## Success Indicators

✅ Local executive runs without crashes  
✅ All approvals presented correctly  
✅ All executions complete successfully  
✅ Dashboard updates correctly  
✅ WhatsApp operations work  
✅ Odoo write operations succeed  
✅ Security validation passes  
✅ Health checks report healthy status  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Local Zone  
**Dependencies:** Skill 16 (Hybrid Orchestrator), Skill 19 (Claim-by-Move), Gold Tier Actions  
**Safety Level:** 🔴 CRITICAL (Executes final actions)  
**Deployment:** User's Local Machine
