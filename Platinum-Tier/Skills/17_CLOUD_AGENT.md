# Skill 17: Cloud Agent (Draft-Only Zone)

## Purpose

Cloud-based AI agent that runs 24/7 on Oracle Cloud Free Tier VM. Handles all drafting, triage, analysis, and read-only operations. **NEVER executes final actions** - only prepares drafts for Local approval.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Cloud Agent (Always-On 24/7)                   │
│         Oracle Cloud Free Tier VM                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Email Drafter │    │Social Drafter│    │ Odoo Drafter │
│              │    │              │    │              │
│ - Triage     │    │ - Schedule   │    │ - Extract    │
│ - Draft      │    │ - Draft      │    │ - Match      │
│ - Analyze    │    │ - Plan       │    │ - Analyze    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Vault/Pending_       │
                │  Approval/<domain>/   │
                └───────────────────────┘
```

---

## When to Use

- **Always**: Cloud agent runs 24/7 monitoring Vault/Needs_Action/
- **Email arrives**: Draft reply immediately
- **Payment notification**: Extract and match invoice
- **Social media request**: Draft post
- **Weekly briefing**: Generate report
- **Odoo query**: Extract data and analyze

## When NOT to Use

- Final email sending (Local only)
- Final social media posting (Local only)
- Odoo write operations (Local only)
- Payment execution (Local only)
- WhatsApp operations (Local only)
- Dashboard updates (Local only)

---

## Allowed Operations (Draft-Only)

### ✅ Permitted Actions

1. **Email Operations**
   - Read incoming emails
   - Triage and classify
   - Draft reply emails
   - Extract information
   - Analyze sentiment

2. **Social Media Operations**
   - Draft LinkedIn posts
   - Draft Facebook posts
   - Schedule post timing
   - Generate content ideas
   - Analyze engagement patterns

3. **Odoo Operations**
   - Read invoices (read-only)
   - Read partners (read-only)
   - Extract invoice data from emails
   - Match payments to invoices
   - Generate financial reports
   - Query account balances

4. **Analysis & Reporting**
   - Generate weekly briefings
   - Analyze business metrics
   - Create task plans
   - Provide recommendations

5. **Vault Operations**
   - Read from Needs_Action/
   - Write to Pending_Approval/
   - Write to Updates/
   - Write to Signals/
   - Write to Briefings/
   - Claim tasks to In_Progress/cloud/

### ❌ Forbidden Actions

1. **Email Operations**
   - ❌ Send emails via SMTP
   - ❌ Access SMTP credentials
   - ❌ Final email delivery

2. **Social Media Operations**
   - ❌ Post to LinkedIn
   - ❌ Post to Facebook
   - ❌ Access social media sessions
   - ❌ Final post publishing

3. **Odoo Operations**
   - ❌ Create invoices
   - ❌ Record payments
   - ❌ Modify partners
   - ❌ Any write operations

4. **Payment Operations**
   - ❌ Execute payments
   - ❌ Access banking credentials
   - ❌ Record transactions

5. **WhatsApp Operations**
   - ❌ Access WhatsApp session
   - ❌ Send WhatsApp messages
   - ❌ Read WhatsApp messages

6. **Local Operations**
   - ❌ Update Dashboard.md
   - ❌ Access local secrets
   - ❌ Modify local state

---

## Cloud Agent Workflow

### Main Loop (24/7)

```python
def cloud_agent_main_loop():
    """
    Cloud agent main loop - runs continuously.
    """
    logger.info("Cloud Agent starting 24/7 operation...")
    
    while True:
        try:
            # 1. Scan for new tasks
            new_tasks = scan_needs_action()
            
            # 2. Process each task
            for task in new_tasks:
                process_cloud_task(task)
            
            # 3. Check for signals from Local
            process_signals()
            
            # 4. Health check
            if time_for_health_check():
                perform_health_check()
            
            # 5. Weekly briefing (Sunday 8 PM)
            if time_for_weekly_briefing():
                generate_weekly_briefing()
            
            # 6. Sleep
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Cloud agent error: {e}")
            time.sleep(60)  # Wait longer on error
```

### Task Processing

```python
def process_cloud_task(task_path: str):
    """
    Process a single task in Cloud zone.
    """
    # 1. Claim task
    if not claim_task(task_path, 'cloud'):
        logger.info(f"Task already claimed: {task_path}")
        return
    
    # 2. Classify task
    classification = classify_task(task_path)
    domain = classification['domain']
    
    # 3. Route to appropriate drafter
    if domain == 'email':
        draft_email_reply(task_path)
    elif domain == 'social':
        draft_social_post(task_path)
    elif domain == 'odoo':
        draft_odoo_action(task_path)
    else:
        logger.warning(f"Unknown domain: {domain}")
        release_task(task_path)
```

---

## Email Drafting

### Email Triage

```python
def draft_email_reply(task_path: str):
    """
    Draft reply to incoming email.
    """
    # 1. Read email
    email_data = read_email_file(task_path)
    
    # 2. Classify email type
    email_type = classify_email(email_data)
    
    # 3. Determine if reply needed
    if not needs_reply(email_data):
        # Archive without reply
        move_to_done(task_path, "No reply needed")
        return
    
    # 4. Draft reply
    reply_draft = generate_reply_draft(email_data, email_type)
    
    # 5. Save to Pending_Approval
    save_draft_for_approval(reply_draft, 'email')
    
    # 6. Update status
    cloud_write_update('email_drafted', {
        'original': task_path,
        'draft': reply_draft['filename'],
        'type': email_type
    })
    
    # 7. Move original to Done
    move_to_done(task_path, "Draft created")
```

### Reply Generation

```python
def generate_reply_draft(email_data: Dict, email_type: str) -> Dict:
    """
    Generate draft reply using AI.
    """
    # Use Gold Tier email processor logic
    from gold_tier.skills import EMAIL_PROCESSOR
    
    # Generate draft
    draft = EMAIL_PROCESSOR.draft_reply(
        from_email=email_data['from'],
        subject=email_data['subject'],
        body=email_data['body'],
        email_type=email_type
    )
    
    # Add metadata
    draft['metadata'] = {
        'drafted_by': 'cloud',
        'drafted_at': datetime.now().isoformat(),
        'original_email': email_data['filename'],
        'requires_approval': True
    }
    
    return draft
```

---

## Social Media Drafting

### Post Drafting

```python
def draft_social_post(task_path: str):
    """
    Draft social media post.
    """
    # 1. Read request
    request_data = read_social_request(task_path)
    
    # 2. Determine platform
    platform = request_data.get('platform', 'linkedin')
    
    # 3. Generate post content
    post_draft = generate_post_content(request_data, platform)
    
    # 4. Check rate limits
    if exceeds_rate_limit(platform):
        # Schedule for later
        schedule_post(post_draft, platform)
        return
    
    # 5. Save to Pending_Approval
    save_draft_for_approval(post_draft, 'social')
    
    # 6. Update status
    cloud_write_update('social_drafted', {
        'platform': platform,
        'draft': post_draft['filename']
    })
    
    # 7. Move original to Done
    move_to_done(task_path, "Post drafted")
```

### Content Generation

```python
def generate_post_content(request: Dict, platform: str) -> Dict:
    """
    Generate social media post content.
    """
    # Use Gold Tier social poster logic
    from gold_tier.skills import LINKEDIN_POST_GENERATOR
    
    # Generate content
    content = LINKEDIN_POST_GENERATOR.generate_post(
        topic=request['topic'],
        tone=request.get('tone', 'professional'),
        length=request.get('length', 'medium')
    )
    
    # Add metadata
    post = {
        'platform': platform,
        'content': content,
        'image': request.get('image'),
        'visibility': request.get('visibility', 'public'),
        'metadata': {
            'drafted_by': 'cloud',
            'drafted_at': datetime.now().isoformat(),
            'requires_approval': True
        }
    }
    
    return post
```

---

## Odoo Drafting

### Invoice Extraction

```python
def draft_odoo_action(task_path: str):
    """
    Draft Odoo action (invoice creation or payment recording).
    """
    # 1. Read task
    task_data = read_odoo_task(task_path)
    
    # 2. Determine action type
    action_type = classify_odoo_action(task_data)
    
    # 3. Route to appropriate handler
    if action_type == 'invoice_creation':
        draft_invoice_creation(task_data)
    elif action_type == 'payment_recording':
        draft_payment_recording(task_data)
    else:
        logger.warning(f"Unknown Odoo action: {action_type}")
        release_task(task_path)
```

### Payment Matching

```python
def draft_payment_recording(task_data: Dict):
    """
    Draft payment recording action.
    """
    # Use Gold Tier payment reconciliation logic
    from gold_tier.actions import PaymentReconciliation
    
    reconciler = PaymentReconciliation()
    
    # 1. Extract payment details
    payment_details = reconciler.extract_payment_details(task_data['content'])
    
    # 2. Connect to Odoo (read-only)
    odoo_client = get_readonly_odoo_client()
    
    # 3. Find matching invoices
    matches, confidence = reconciler.find_matching_invoices(
        payment_details,
        odoo_client
    )
    
    # 4. Generate action file
    action_draft = reconciler.generate_action_file(
        payment_details,
        matches,
        confidence,
        task_data['filename']
    )
    
    # 5. Save to Pending_Approval
    save_draft_for_approval(action_draft, 'odoo')
    
    # 6. Update status
    cloud_write_update('payment_matched', {
        'amount': payment_details['amount'],
        'confidence': confidence,
        'matches': len(matches)
    })
```

---

## Weekly Briefing Generation

### Briefing Workflow

```python
def generate_weekly_briefing():
    """
    Generate weekly CEO briefing (Sunday 8 PM).
    """
    logger.info("Generating weekly briefing...")
    
    # Use Gold Tier briefing generator
    from gold_tier.actions import WeeklyBriefingGenerator
    
    generator = WeeklyBriefingGenerator()
    
    # 1. Collect data from Odoo (read-only)
    odoo_client = get_readonly_odoo_client()
    financial_data = generator.collect_financial_metrics(odoo_client)
    
    # 2. Collect data from Vault
    email_data = collect_email_metrics_from_vault()
    social_data = collect_social_metrics_from_vault()
    task_data = collect_task_metrics_from_vault()
    
    # 3. Generate report
    report = generator.generate_report(
        financial_data,
        email_data,
        social_data,
        task_data
    )
    
    # 4. Save to Briefings/
    filename = f"Weekly_Report_{datetime.now().strftime('%Y-%m-%d')}.md"
    save_file(f"Vault/Briefings/{filename}", report)
    
    # 5. Signal Local
    cloud_send_signal('briefing_ready', f"Weekly briefing: {filename}")
    
    logger.info(f"✅ Weekly briefing generated: {filename}")
```

---

## Security Enforcement

### Environment Validation

```python
def validate_cloud_environment():
    """
    Ensure Cloud environment has no forbidden secrets.
    """
    forbidden_vars = [
        'SMTP_USER',
        'SMTP_PASS',
        'WHATSAPP_SESSION',
        'BANKING_CREDS',
        'PAYMENT_TOKEN'
    ]
    
    for var in forbidden_vars:
        if os.getenv(var):
            raise SecurityError(f"Forbidden secret in Cloud environment: {var}")
    
    logger.info("✅ Cloud environment validated - no forbidden secrets")
```

### File Access Validation

```python
def validate_file_access(filepath: str, operation: str):
    """
    Validate Cloud agent can access file.
    """
    forbidden_patterns = [
        '*.env',
        '*_secrets.json',
        'whatsapp_session/',
        'banking_creds/',
        'Dashboard.md'
    ]
    
    for pattern in forbidden_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            raise SecurityError(f"Cloud cannot {operation} forbidden file: {filepath}")
    
    # Only allow Vault access
    if not filepath.startswith('Vault/'):
        raise SecurityError(f"Cloud can only access Vault/: {filepath}")
```

### Odoo Access Validation

```python
def get_readonly_odoo_client():
    """
    Get Odoo client with read-only access.
    """
    from gold_tier.actions import OdooRPCClient
    
    # Use read-only credentials
    client = OdooRPCClient()
    client.username = os.getenv('ODOO_READONLY_USER')
    client.password = os.getenv('ODOO_READONLY_PASS')
    
    # Validate read-only
    if not client.username.startswith('readonly_'):
        raise SecurityError("Cloud must use readonly Odoo user")
    
    return client
```

---

## Health Monitoring

### Cloud Health Check

```python
def perform_health_check():
    """
    Perform Cloud agent health check.
    """
    health = {
        'timestamp': datetime.now().isoformat(),
        'zone': 'cloud',
        'status': 'healthy',
        'uptime': get_uptime_seconds(),
        'tasks_processed_today': count_tasks_processed_today(),
        'tasks_in_progress': count_tasks_in_progress('cloud'),
        'vault_accessible': test_vault_access(),
        'odoo_connection': test_odoo_readonly_connection(),
        'disk_space': get_disk_space(),
        'memory_usage': get_memory_usage(),
        'cpu_usage': get_cpu_usage()
    }
    
    # Write health status
    save_file('Vault/Updates/cloud_health.json', json.dumps(health, indent=2))
    
    # Alert if unhealthy
    if health['status'] != 'healthy':
        cloud_send_signal('health_alert', f"Cloud unhealthy: {health}")
    
    return health
```

---

## Error Handling

### Graceful Degradation

```python
def handle_cloud_error(task: str, error: Exception):
    """
    Handle Cloud agent errors gracefully.
    """
    logger.error(f"Cloud error processing {task}: {error}")
    
    # 1. Classify error severity
    severity = classify_error_severity(error)
    
    if severity == 'critical':
        # Critical error - signal Local immediately
        cloud_send_signal('critical_error', f"Task: {task}, Error: {error}")
        
        # Pause Cloud operations
        pause_cloud_operations()
        
    elif severity == 'high':
        # High severity - retry with backoff
        schedule_retry(task, delay=300)  # 5 minutes
        
    else:
        # Low severity - move back to Needs_Action
        release_task(task)
    
    # 2. Write error update
    cloud_write_update('error', {
        'task': task,
        'error': str(error),
        'severity': severity,
        'timestamp': datetime.now().isoformat()
    })
```

---

## Configuration

### Cloud Agent Config

```python
CLOUD_AGENT_CONFIG = {
    'zone': 'cloud',
    'mode': 'draft_only',
    'vault_path': '/home/ubuntu/Platinum-Tier/Vault',
    'scan_interval': 30,  # seconds
    'health_check_interval': 300,  # 5 minutes
    'max_concurrent_tasks': 5,
    'retry_attempts': 3,
    'retry_delay': 60,  # seconds
    'odoo_readonly': True,
    'allowed_operations': [
        'read', 'draft', 'analyze', 'extract', 'match', 'generate'
    ],
    'forbidden_operations': [
        'send', 'post', 'execute', 'payment', 'write', 'delete'
    ]
}
```

---

## Deployment (Oracle Cloud)

### VM Setup

```bash
# Oracle Cloud Free Tier
# VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM)
# Ubuntu 22.04 LTS

# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip git

# 2. Clone repository
git clone https://github.com/your-repo/Platinum-Tier.git
cd Platinum-Tier

# 3. Install Python packages
pip3 install -r requirements.txt

# 4. Configure environment
cp Config/cloud.env.example .env
nano .env  # Edit with Cloud credentials

# 5. Start Cloud agent
nohup python3 Actions/cloud_agent.py > Logs/cloud/agent.log 2>&1 &

# 6. Verify running
ps aux | grep cloud_agent
tail -f Logs/cloud/agent.log
```

### Systemd Service

```ini
# /etc/systemd/system/cloud-agent.service
[Unit]
Description=Platinum Tier Cloud Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Platinum-Tier
ExecStart=/usr/bin/python3 Actions/cloud_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Success Indicators

✅ Cloud agent runs 24/7 without crashes  
✅ All drafts created within 60 seconds  
✅ No forbidden operations attempted  
✅ Security validation passes  
✅ Health checks report healthy status  
✅ Weekly briefings generated on schedule  
✅ Odoo read-only access working  
✅ Vault sync functioning correctly  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Cloud Zone  
**Dependencies:** Skill 16 (Hybrid Orchestrator), Skill 19 (Claim-by-Move), Skill 21 (Security Isolation)  
**Safety Level:** 🟢 SAFE (Draft-only, no execution)  
**Deployment:** Oracle Cloud Free Tier VM
