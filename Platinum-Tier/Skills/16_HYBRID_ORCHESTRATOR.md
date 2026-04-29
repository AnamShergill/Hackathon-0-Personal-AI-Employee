# Skill 16: Hybrid Orchestrator

## Purpose

Central routing and coordination system for Platinum Tier's hybrid Cloud + Local architecture. Routes tasks between Cloud (draft-only) and Local (execution-only) zones based on work-zone specialization rules.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Hybrid Orchestrator                         │
│         (Runs on both Cloud and Local)                   │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Cloud Zone  │    │    Vault     │    │  Local Zone  │
│ (Draft-Only) │◄──►│   (Synced)   │◄──►│ (Exec-Only)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## When to Use

- **Always**: This is the entry point for all Platinum Tier operations
- **Cloud Mode**: Routes incoming tasks to Cloud drafting agents
- **Local Mode**: Routes approved tasks to Local execution agents
- **Hybrid Mode**: Coordinates between both zones via Vault

## When NOT to Use

- Direct Gold Tier operations (use Gold Tier orchestrator)
- Single-zone operations (use zone-specific agents)
- Manual file operations (use direct file access)

---

## Work-Zone Specialization

### Cloud Zone Responsibilities (Draft-Only)

**Allowed:**
- ✅ Email triage and draft replies
- ✅ Social post drafting and scheduling
- ✅ Odoo data extraction and draft actions
- ✅ Weekly briefing generation
- ✅ Task planning and analysis
- ✅ Read-only Odoo queries

**Forbidden:**
- ❌ Final email sending (SMTP)
- ❌ Final social media posting
- ❌ Odoo write operations
- ❌ Payment execution
- ❌ WhatsApp access
- ❌ Banking operations
- ❌ Dashboard.md updates

### Local Zone Responsibilities (Execution-Only)

**Allowed:**
- ✅ HITL approval interface
- ✅ Final email sending
- ✅ Final social media posting
- ✅ Odoo write operations
- ✅ Payment execution
- ✅ WhatsApp session access
- ✅ Banking operations
- ✅ Dashboard.md updates

**Forbidden:**
- ❌ Drafting (use Cloud for this)
- ❌ 24/7 monitoring (Cloud handles this)
- ❌ Automated triage (Cloud handles this)

---

## Routing Logic

### Task Classification

```python
def classify_task(task_file: str) -> Dict[str, str]:
    """
    Classify task and determine routing.
    
    Returns:
        {
            'domain': 'email' | 'social' | 'odoo',
            'type': 'draft' | 'execute' | 'approve',
            'zone': 'cloud' | 'local' | 'both',
            'priority': 'high' | 'medium' | 'low'
        }
    """
```

### Routing Rules

| Task Type | Current Location | Cloud Action | Local Action |
|-----------|-----------------|--------------|--------------|
| New email | Needs_Action/email/ | Draft reply → Pending_Approval/email/ | - |
| Draft reply | Pending_Approval/email/ | - | Approve → Execute → Done/ |
| Payment email | Needs_Action/odoo/ | Match invoice → Pending_Approval/odoo/ | - |
| Payment action | Pending_Approval/odoo/ | - | Approve → Record → Done/ |
| Social draft | Needs_Action/social/ | Draft post → Pending_Approval/social/ | - |
| Social post | Pending_Approval/social/ | - | Approve → Post → Done/ |
| Weekly briefing | Scheduled | Generate → Briefings/ | Read and display |

---

## Vault Communication Protocol

### Folder Structure

```
Vault/
├── Needs_Action/<domain>/     # Entry point for new tasks
├── Plans/<domain>/             # Task plans
├── Pending_Approval/<domain>/  # Awaiting HITL approval
├── In_Progress/<agent>/        # Claimed by agent
├── Updates/                    # Status updates (Cloud → Local)
├── Signals/                    # Control signals
├── Done/                       # Completed tasks
└── Briefings/                  # Generated briefings
```

### Claim-by-Move Rule

**Protocol:**
1. Task appears in `Needs_Action/<domain>/task.md`
2. Agent checks if task is unclaimed
3. Agent moves to `In_Progress/<agent>/task.md` (atomic claim)
4. If move fails, task is already claimed by another agent
5. Agent processes task
6. Agent outputs to appropriate folder
7. Agent moves to `Done/task.md` when complete

**Implementation:**
```python
def claim_task(task_path: str, agent_name: str) -> bool:
    """
    Atomically claim a task by moving it.
    
    Returns:
        True if claim successful, False if already claimed
    """
    try:
        target = f"In_Progress/{agent_name}/{task_path.name}"
        os.rename(task_path, target)  # Atomic on same filesystem
        return True
    except FileNotFoundError:
        # Already claimed by another agent
        return False
```

---

## Cloud Orchestrator Workflow

### Initialization

```python
# Cloud orchestrator runs 24/7
while True:
    # 1. Scan Needs_Action for new tasks
    new_tasks = scan_vault("Needs_Action/")
    
    # 2. Classify and route each task
    for task in new_tasks:
        classification = classify_task(task)
        
        if classification['zone'] == 'cloud':
            # 3. Claim task
            if claim_task(task, 'cloud'):
                # 4. Route to appropriate Cloud agent
                route_to_cloud_agent(task, classification)
    
    # 5. Check for signals from Local
    process_signals()
    
    # 6. Sleep and repeat
    time.sleep(30)  # Check every 30 seconds
```

### Cloud Agent Routing

```python
def route_to_cloud_agent(task: str, classification: Dict):
    """Route task to appropriate Cloud agent"""
    
    domain = classification['domain']
    
    if domain == 'email':
        # Email drafting agent
        cloud_email_drafter(task)
    
    elif domain == 'social':
        # Social media drafting agent
        cloud_social_drafter(task)
    
    elif domain == 'odoo':
        # Odoo extraction agent
        cloud_odoo_extractor(task)
    
    else:
        logger.warning(f"Unknown domain: {domain}")
```

---

## Local Orchestrator Workflow

### Initialization

```python
# Local orchestrator runs periodically (e.g., every 5 minutes)
while True:
    # 1. Scan Pending_Approval for tasks needing approval
    pending_tasks = scan_vault("Pending_Approval/")
    
    # 2. Present to human for approval
    for task in pending_tasks:
        if human_approves(task):
            # 3. Claim task
            if claim_task(task, 'local'):
                # 4. Route to appropriate Local executor
                route_to_local_executor(task)
    
    # 3. Check Updates from Cloud
    process_updates()
    
    # 4. Update Dashboard
    update_dashboard()
    
    # 5. Sleep and repeat
    time.sleep(300)  # Check every 5 minutes
```

### Local Executor Routing

```python
def route_to_local_executor(task: str):
    """Route approved task to appropriate Local executor"""
    
    task_type = detect_task_type(task)
    
    if task_type == 'email_send':
        # Email sender (Gold Tier)
        local_email_sender(task)
    
    elif task_type == 'social_post':
        # Social media poster (Gold Tier)
        local_social_poster(task)
    
    elif task_type == 'odoo_payment':
        # Payment recorder (Gold Tier)
        local_payment_recorder(task)
    
    elif task_type == 'odoo_invoice':
        # Invoice creator (Gold Tier)
        local_invoice_creator(task)
    
    else:
        logger.warning(f"Unknown task type: {task_type}")
```

---

## Security Isolation

### Cloud Zone Restrictions

**Environment Variables (Cloud):**
```env
# Cloud can only access:
ODOO_URL=https://cloud-odoo.example.com
ODOO_USERNAME=readonly_user
ODOO_PASSWORD=readonly_pass
OPENAI_API_KEY=sk-cloud-key

# Cloud CANNOT access:
# SMTP_USER (not in cloud .env)
# SMTP_PASS (not in cloud .env)
# WHATSAPP_SESSION (not synced)
# BANKING_CREDS (not synced)
```

**File Access (Cloud):**
```python
# Cloud can read/write:
ALLOWED_PATHS = [
    "Vault/Needs_Action/",
    "Vault/Plans/",
    "Vault/Pending_Approval/",
    "Vault/In_Progress/cloud/",
    "Vault/Updates/",
    "Vault/Signals/",
    "Vault/Briefings/"
]

# Cloud CANNOT access:
FORBIDDEN_PATHS = [
    "*.env",
    "*_secrets.json",
    "whatsapp_session/",
    "banking_creds/",
    "Dashboard.md"
]
```

### Local Zone Restrictions

**Environment Variables (Local):**
```env
# Local has full access:
SMTP_USER=user@example.com
SMTP_PASS=app_password
ODOO_URL=http://localhost:8069
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_pass
WHATSAPP_SESSION_PATH=/local/whatsapp_session/
BANKING_CREDS_PATH=/local/banking_creds/
```

**File Access (Local):**
```python
# Local can read/write:
ALLOWED_PATHS = [
    "Vault/**/*",  # Full Vault access
    "Dashboard.md",
    "local_state.json",
    "*.env"
]

# Local should not modify:
READONLY_PATHS = [
    "Vault/In_Progress/cloud/",  # Cloud's working directory
]
```

---

## Update Protocol (Cloud → Local)

### Cloud Writes Updates

```python
def cloud_write_update(update_type: str, data: Dict):
    """
    Cloud writes status update for Local to consume.
    """
    timestamp = datetime.now().isoformat()
    filename = f"update_{update_type}_{timestamp}.md"
    
    content = f"""---
type: {update_type}
timestamp: {timestamp}
source: cloud
---

# Update: {update_type}

{format_update_data(data)}
"""
    
    write_file(f"Vault/Updates/{filename}", content)
```

### Local Merges Updates

```python
def local_merge_updates():
    """
    Local reads and merges updates from Cloud.
    """
    updates = scan_vault("Updates/")
    
    for update in updates:
        data = parse_update(update)
        
        # Merge into Dashboard
        merge_to_dashboard(data)
        
        # Archive update
        move_to_done(update)
```

---

## Signal Protocol (Bidirectional)

### Signal Types

```python
SIGNAL_TYPES = {
    'pause': 'Pause Cloud operations',
    'resume': 'Resume Cloud operations',
    'sync_now': 'Force immediate sync',
    'health_check': 'Request health status',
    'shutdown': 'Graceful shutdown'
}
```

### Cloud Sends Signal

```python
def cloud_send_signal(signal_type: str, message: str = ""):
    """Cloud sends signal to Local"""
    timestamp = datetime.now().isoformat()
    filename = f"{signal_type}_{timestamp}.signal"
    
    content = f"""---
signal: {signal_type}
timestamp: {timestamp}
source: cloud
---

{message}
"""
    
    write_file(f"Vault/Signals/{filename}", content)
```

### Local Sends Signal

```python
def local_send_signal(signal_type: str, message: str = ""):
    """Local sends signal to Cloud"""
    timestamp = datetime.now().isoformat()
    filename = f"{signal_type}_{timestamp}.signal"
    
    content = f"""---
signal: {signal_type}
timestamp: {timestamp}
source: local
---

{message}
"""
    
    write_file(f"Vault/Signals/{filename}", content)
```

---

## Error Handling

### Cloud Zone Errors

```python
def handle_cloud_error(task: str, error: Exception):
    """
    Handle errors in Cloud zone.
    """
    logger.error(f"Cloud error processing {task}: {error}")
    
    # 1. Write error update
    cloud_write_update('error', {
        'task': task,
        'error': str(error),
        'zone': 'cloud'
    })
    
    # 2. Move task to Needs_Action for retry
    move_file(task, "Vault/Needs_Action/")
    
    # 3. Signal Local if critical
    if is_critical_error(error):
        cloud_send_signal('error', f"Critical error: {error}")
```

### Local Zone Errors

```python
def handle_local_error(task: str, error: Exception):
    """
    Handle errors in Local zone.
    """
    logger.error(f"Local error processing {task}: {error}")
    
    # 1. Update Dashboard with error
    update_dashboard_error(task, error)
    
    # 2. Move task back to Pending_Approval
    move_file(task, "Vault/Pending_Approval/")
    
    # 3. Notify human
    notify_human(f"Task {task} failed: {error}")
```

---

## Health Monitoring

### Cloud Health Check

```python
def cloud_health_check() -> Dict:
    """
    Cloud zone health status.
    """
    return {
        'zone': 'cloud',
        'status': 'healthy',
        'uptime': get_uptime(),
        'tasks_processed': count_tasks_processed(),
        'tasks_in_progress': count_tasks_in_progress(),
        'last_sync': get_last_sync_time(),
        'odoo_connection': test_odoo_connection(),
        'vault_accessible': test_vault_access()
    }
```

### Local Health Check

```python
def local_health_check() -> Dict:
    """
    Local zone health status.
    """
    return {
        'zone': 'local',
        'status': 'healthy',
        'tasks_pending_approval': count_pending_approval(),
        'tasks_in_progress': count_tasks_in_progress(),
        'last_sync': get_last_sync_time(),
        'smtp_connection': test_smtp_connection(),
        'whatsapp_session': test_whatsapp_session(),
        'vault_accessible': test_vault_access()
    }
```

---

## Configuration

### Cloud Configuration

```python
CLOUD_CONFIG = {
    'zone': 'cloud',
    'mode': 'draft_only',
    'vault_path': '/home/ubuntu/Platinum-Tier/Vault',
    'scan_interval': 30,  # seconds
    'max_concurrent_tasks': 5,
    'allowed_domains': ['email', 'social', 'odoo'],
    'forbidden_actions': ['send', 'post', 'execute', 'payment']
}
```

### Local Configuration

```python
LOCAL_CONFIG = {
    'zone': 'local',
    'mode': 'execute_only',
    'vault_path': '/Users/user/Platinum-Tier/Vault',
    'scan_interval': 300,  # seconds (5 minutes)
    'max_concurrent_tasks': 3,
    'allowed_domains': ['email', 'social', 'odoo'],
    'allowed_actions': ['send', 'post', 'execute', 'payment']
}
```

---

## Testing

### Test Cloud Orchestrator

```bash
# Start Cloud orchestrator
python Platinum-Tier/Actions/cloud_orchestrator.py

# Create test task
echo "Test email task" > Vault/Needs_Action/email/test_email.md

# Verify Cloud claims and drafts
ls Vault/In_Progress/cloud/
ls Vault/Pending_Approval/email/
```

### Test Local Orchestrator

```bash
# Start Local orchestrator
python Platinum-Tier/Actions/local_orchestrator.py

# Approve test task
mv Vault/Pending_Approval/email/test_email.md Vault/Pending_Approval/email/approved_test_email.md

# Verify Local executes
ls Vault/In_Progress/local/
ls Vault/Done/
```

---

## Success Indicators

✅ Cloud orchestrator runs 24/7 without crashes  
✅ Local orchestrator processes approvals correctly  
✅ Claim-by-move prevents duplicate processing  
✅ Security isolation maintained (no secret leaks)  
✅ Updates flow correctly (Cloud → Local)  
✅ Signals work bidirectionally  
✅ Health checks report accurate status  
✅ Error handling is graceful  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Hybrid System  
**Dependencies:** Skill 17 (Cloud Agent), Skill 18 (Local Executive), Skill 19 (Claim-by-Move)  
**Safety Level:** 🔴 CRITICAL (Coordinates all operations)
