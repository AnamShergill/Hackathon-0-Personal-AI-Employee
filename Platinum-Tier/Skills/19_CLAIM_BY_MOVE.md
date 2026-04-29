# Skill 19: Claim-by-Move Protocol

## Purpose

Atomic task claiming protocol that prevents duplicate processing in the hybrid Cloud + Local architecture. Uses filesystem move operations to ensure only one agent can claim and process a task.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Claim-by-Move Protocol                      │
│         (Atomic Filesystem Operations)                   │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Cloud Agent  │    │  Vault/      │    │ Local Agent  │
│              │    │  Needs_      │    │              │
│ Tries claim  │◄──►│  Action/     │◄──►│ Tries claim  │
│              │    │              │    │              │
│ First wins   │    │ (Unclaimed)  │    │ Second fails │
└──────────────┘    └──────────────┘    └──────────────┘
        │                                       │
        ▼                                       ▼
┌──────────────┐                        ┌──────────────┐
│In_Progress/  │                        │ (Claim       │
│cloud/        │                        │  failed)     │
│task.md       │                        └──────────────┘
└──────────────┘
```

---

## When to Use

- **Always**: Every task must be claimed before processing
- **Cloud agent**: Claims tasks from Needs_Action/
- **Local agent**: Claims tasks from Pending_Approval/
- **Concurrent access**: Multiple agents trying to claim same task
- **Distributed system**: Cloud and Local running simultaneously

## When NOT to Use

- Single-agent systems (no concurrency)
- Manual file operations (human moving files)
- Read-only operations (no claiming needed)

---

## Protocol Rules

### Rule 1: Atomic Move

**Principle:** Use filesystem `rename()` operation which is atomic on the same filesystem.

```python
# Atomic claim
try:
    os.rename(source_path, target_path)
    # SUCCESS: You own the task
except FileNotFoundError:
    # FAILURE: Someone else claimed it first
```

**Why atomic?**
- `rename()` is atomic at the OS level
- Either succeeds completely or fails completely
- No partial states or race conditions
- Works across processes and machines (with proper sync)

### Rule 2: First Mover Wins

**Principle:** The first agent to successfully move the file owns the task.

```python
# Cloud tries to claim
cloud_target = "In_Progress/cloud/task.md"
success = atomic_move("Needs_Action/email/task.md", cloud_target)

# Local tries to claim (at same time)
local_target = "In_Progress/local/task.md"
success = atomic_move("Needs_Action/email/task.md", local_target)

# Only ONE will succeed - the first one
```

### Rule 3: No Retry on Claim Failure

**Principle:** If claim fails, the task is already being processed. Do not retry.

```python
if not claim_task(task_path, agent_name):
    logger.info(f"Task already claimed by another agent: {task_path}")
    return  # Move on to next task
```

### Rule 4: Release on Error

**Principle:** If processing fails, release the task back to the queue.

```python
try:
    process_task(task_path)
except Exception as e:
    logger.error(f"Processing failed: {e}")
    release_task(task_path)  # Move back to Needs_Action
```

### Rule 5: Complete to Done

**Principle:** Successfully processed tasks move to Done/ folder.

```python
# After successful processing
move_to_done(task_path, completion_message)
```

---

## Implementation

### Core Claim Function

```python
import os
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def claim_task(task_path: str, agent_name: str) -> Tuple[bool, Optional[str]]:
    """
    Atomically claim a task by moving it to agent's In_Progress folder.
    
    Args:
        task_path: Path to task file (e.g., "Vault/Needs_Action/email/task.md")
        agent_name: Name of claiming agent ("cloud" or "local")
    
    Returns:
        (success: bool, claimed_path: Optional[str])
        - (True, path) if claim successful
        - (False, None) if already claimed
    
    Example:
        success, path = claim_task("Vault/Needs_Action/email/task.md", "cloud")
        if success:
            process_task(path)
    """
    try:
        # 1. Validate task exists
        if not os.path.exists(task_path):
            logger.warning(f"Task does not exist: {task_path}")
            return False, None
        
        # 2. Build target path
        task_filename = Path(task_path).name
        target_path = f"Vault/In_Progress/{agent_name}/{task_filename}"
        
        # 3. Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 4. Atomic move (claim)
        os.rename(task_path, target_path)
        
        # 5. Success
        logger.info(f"✅ Claimed by {agent_name}: {task_filename}")
        return True, target_path
        
    except FileNotFoundError:
        # Task was already moved by another agent
        logger.info(f"⚠️ Already claimed by another agent: {task_path}")
        return False, None
        
    except Exception as e:
        # Unexpected error
        logger.error(f"❌ Claim error: {e}")
        return False, None
```

### Release Task

```python
def release_task(task_path: str, reason: str = "Processing failed") -> bool:
    """
    Release a claimed task back to Needs_Action queue.
    
    Args:
        task_path: Path to claimed task (e.g., "Vault/In_Progress/cloud/task.md")
        reason: Reason for release
    
    Returns:
        True if released successfully, False otherwise
    
    Example:
        release_task("Vault/In_Progress/cloud/task.md", "Odoo connection failed")
    """
    try:
        # 1. Determine original location
        task_filename = Path(task_path).name
        
        # Extract domain from filename or metadata
        domain = extract_domain_from_task(task_path)
        
        # 2. Build target path
        target_path = f"Vault/Needs_Action/{domain}/{task_filename}"
        
        # 3. Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 4. Move back to Needs_Action
        os.rename(task_path, target_path)
        
        # 5. Log reason
        logger.info(f"🔄 Released: {task_filename} - Reason: {reason}")
        
        # 6. Write release metadata
        write_release_metadata(target_path, reason)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Release error: {e}")
        return False
```

### Complete Task

```python
def complete_task(task_path: str, result: str) -> bool:
    """
    Mark task as complete and move to Done folder.
    
    Args:
        task_path: Path to claimed task (e.g., "Vault/In_Progress/local/task.md")
        result: Completion result message
    
    Returns:
        True if completed successfully, False otherwise
    
    Example:
        complete_task("Vault/In_Progress/local/email.md", "Email sent: msg-123")
    """
    try:
        # 1. Build target path
        task_filename = Path(task_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_filename = f"{timestamp}_{task_filename}"
        target_path = f"Vault/Done/{target_filename}"
        
        # 2. Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 3. Write completion metadata
        write_completion_metadata(task_path, result)
        
        # 4. Move to Done
        os.rename(task_path, target_path)
        
        # 5. Log completion
        logger.info(f"✅ Completed: {task_filename} - Result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Completion error: {e}")
        return False
```

---

## Task Lifecycle

### State Diagram

```
┌─────────────────┐
│  Needs_Action/  │  ← New task arrives
└────────┬────────┘
         │
         │ claim_task()
         ▼
┌─────────────────┐
│  In_Progress/   │  ← Agent processing
│  <agent>/       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ Done/  │  │Needs_  │  ← release_task()
│        │  │Action/ │     (on error)
└────────┘  └────────┘
    ▲
    │
    └─ complete_task()
       (on success)
```

### State Transitions

| Current State | Action | Next State | Who |
|--------------|--------|------------|-----|
| Needs_Action/ | claim_task() | In_Progress/<agent>/ | Cloud or Local |
| In_Progress/<agent>/ | complete_task() | Done/ | Same agent |
| In_Progress/<agent>/ | release_task() | Needs_Action/ | Same agent |
| Done/ | (archive) | (deleted after 30 days) | System |

---

## Concurrency Scenarios

### Scenario 1: Both Agents Try to Claim

```python
# Time: T0 - Task exists
# File: Vault/Needs_Action/email/task.md

# Time: T1 - Cloud tries to claim
cloud_success = claim_task("Vault/Needs_Action/email/task.md", "cloud")
# Result: True (Cloud wins)

# Time: T1 - Local tries to claim (same time)
local_success = claim_task("Vault/Needs_Action/email/task.md", "local")
# Result: False (File already moved by Cloud)

# Time: T2 - Only Cloud processes
# File: Vault/In_Progress/cloud/task.md
```

### Scenario 2: Claim, Process, Complete

```python
# 1. Cloud claims task
success, path = claim_task("Vault/Needs_Action/email/task.md", "cloud")
# path = "Vault/In_Progress/cloud/task.md"

# 2. Cloud processes task
try:
    result = process_email_draft(path)
    
    # 3. Cloud completes task
    complete_task(path, f"Draft created: {result}")
    # File moved to: Vault/Done/20260413_143000_task.md
    
except Exception as e:
    # 4. On error, release task
    release_task(path, str(e))
    # File moved back to: Vault/Needs_Action/email/task.md
```

### Scenario 3: Claim, Sync, Claim Again

```python
# Cloud VM
# Time: T0
cloud_success = claim_task("Vault/Needs_Action/email/task.md", "cloud")
# Result: True
# File: Vault/In_Progress/cloud/task.md

# Git sync happens
# Time: T1
git_push()  # Cloud pushes to Git

# Local Machine
# Time: T2
git_pull()  # Local pulls from Git
# File appears: Vault/In_Progress/cloud/task.md

# Local tries to claim
# Time: T3
local_success = claim_task("Vault/Needs_Action/email/task.md", "local")
# Result: False (File doesn't exist in Needs_Action anymore)

# Local sees Cloud is processing
# Time: T4
logger.info("Task already claimed by cloud")
```

---

## Metadata Tracking

### Claim Metadata

```python
def write_claim_metadata(task_path: str, agent_name: str):
    """
    Write claim metadata to task file.
    """
    metadata = {
        'claimed_by': agent_name,
        'claimed_at': datetime.now().isoformat(),
        'claim_id': generate_claim_id()
    }
    
    # Append to task file
    with open(task_path, 'a') as f:
        f.write(f"\n\n---\n## Claim Metadata\n")
        f.write(f"- **Claimed by:** {metadata['claimed_by']}\n")
        f.write(f"- **Claimed at:** {metadata['claimed_at']}\n")
        f.write(f"- **Claim ID:** {metadata['claim_id']}\n")
```

### Release Metadata

```python
def write_release_metadata(task_path: str, reason: str):
    """
    Write release metadata to task file.
    """
    metadata = {
        'released_at': datetime.now().isoformat(),
        'release_reason': reason,
        'retry_count': get_retry_count(task_path) + 1
    }
    
    # Append to task file
    with open(task_path, 'a') as f:
        f.write(f"\n\n---\n## Release Metadata\n")
        f.write(f"- **Released at:** {metadata['released_at']}\n")
        f.write(f"- **Reason:** {metadata['release_reason']}\n")
        f.write(f"- **Retry count:** {metadata['retry_count']}\n")
```

### Completion Metadata

```python
def write_completion_metadata(task_path: str, result: str):
    """
    Write completion metadata to task file.
    """
    metadata = {
        'completed_at': datetime.now().isoformat(),
        'result': result,
        'processing_time': calculate_processing_time(task_path)
    }
    
    # Append to task file
    with open(task_path, 'a') as f:
        f.write(f"\n\n---\n## Completion Metadata\n")
        f.write(f"- **Completed at:** {metadata['completed_at']}\n")
        f.write(f"- **Result:** {metadata['result']}\n")
        f.write(f"- **Processing time:** {metadata['processing_time']} seconds\n")
```

---

## Error Handling

### Claim Failures

```python
def handle_claim_failure(task_path: str, agent_name: str):
    """
    Handle claim failure gracefully.
    """
    logger.info(f"Claim failed for {task_path} by {agent_name}")
    
    # 1. Check if task is being processed
    if is_task_in_progress(task_path):
        logger.info("Task is being processed by another agent")
        return
    
    # 2. Check if task was completed
    if is_task_completed(task_path):
        logger.info("Task was already completed")
        return
    
    # 3. Check if task was deleted
    if not task_exists_anywhere(task_path):
        logger.warning("Task disappeared - possible sync issue")
        return
```

### Stale Claims

```python
def detect_stale_claims(max_age_minutes: int = 30):
    """
    Detect and release stale claims (tasks stuck in In_Progress).
    """
    in_progress_tasks = scan_vault("In_Progress/")
    
    for task in in_progress_tasks:
        # Check age
        age_minutes = get_task_age_minutes(task)
        
        if age_minutes > max_age_minutes:
            logger.warning(f"Stale claim detected: {task} (age: {age_minutes} min)")
            
            # Release back to queue
            release_task(task, f"Stale claim (age: {age_minutes} min)")
```

### Orphaned Tasks

```python
def detect_orphaned_tasks():
    """
    Detect tasks that are claimed but agent is offline.
    """
    # Check Cloud tasks
    cloud_tasks = scan_vault("In_Progress/cloud/")
    if cloud_tasks and not is_cloud_agent_alive():
        logger.warning(f"Cloud agent offline with {len(cloud_tasks)} claimed tasks")
        for task in cloud_tasks:
            release_task(task, "Cloud agent offline")
    
    # Check Local tasks
    local_tasks = scan_vault("In_Progress/local/")
    if local_tasks and not is_local_agent_alive():
        logger.warning(f"Local agent offline with {len(local_tasks)} claimed tasks")
        for task in local_tasks:
            release_task(task, "Local agent offline")
```

---

## Sync Considerations

### Git Sync

```python
def sync_before_claim():
    """
    Sync Vault before attempting to claim tasks.
    """
    # 1. Pull latest changes
    git_pull()
    
    # 2. Wait for sync to complete
    time.sleep(1)
    
    # 3. Now safe to claim
    return True
```

### Sync Conflicts

```python
def handle_sync_conflict(task_path: str):
    """
    Handle Git sync conflicts on task files.
    """
    # 1. Check conflict markers
    if has_conflict_markers(task_path):
        logger.error(f"Sync conflict detected: {task_path}")
        
        # 2. Resolve by keeping remote (Cloud) version
        resolve_conflict_keep_remote(task_path)
        
        # 3. Commit resolution
        git_add(task_path)
        git_commit(f"Resolved conflict: {task_path}")
        git_push()
```

---

## Testing

### Test Concurrent Claims

```python
def test_concurrent_claims():
    """
    Test that only one agent can claim a task.
    """
    import threading
    
    # Create test task
    task_path = "Vault/Needs_Action/email/test_task.md"
    create_test_task(task_path)
    
    # Results
    results = {'cloud': False, 'local': False}
    
    # Cloud thread
    def cloud_claim():
        results['cloud'] = claim_task(task_path, 'cloud')[0]
    
    # Local thread
    def local_claim():
        results['local'] = claim_task(task_path, 'local')[0]
    
    # Start both threads simultaneously
    t1 = threading.Thread(target=cloud_claim)
    t2 = threading.Thread(target=local_claim)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Verify only one succeeded
    assert results['cloud'] != results['local'], "Both agents claimed task!"
    assert results['cloud'] or results['local'], "Neither agent claimed task!"
    
    print(f"✅ Test passed: Cloud={results['cloud']}, Local={results['local']}")
```

### Test Release and Reclaim

```python
def test_release_and_reclaim():
    """
    Test that released tasks can be reclaimed.
    """
    # 1. Create and claim task
    task_path = "Vault/Needs_Action/email/test_task.md"
    create_test_task(task_path)
    
    success, claimed_path = claim_task(task_path, 'cloud')
    assert success, "Initial claim failed"
    
    # 2. Release task
    release_success = release_task(claimed_path, "Test release")
    assert release_success, "Release failed"
    
    # 3. Verify task is back in Needs_Action
    assert os.path.exists(task_path), "Task not in Needs_Action"
    
    # 4. Reclaim task
    success2, claimed_path2 = claim_task(task_path, 'local')
    assert success2, "Reclaim failed"
    
    print("✅ Test passed: Release and reclaim works")
```

---

## Best Practices

### 1. Always Sync Before Claiming

```python
# Good
git_pull()
success, path = claim_task(task_path, agent_name)

# Bad
success, path = claim_task(task_path, agent_name)  # May claim stale task
```

### 2. Always Release on Error

```python
# Good
try:
    process_task(claimed_path)
    complete_task(claimed_path, result)
except Exception as e:
    release_task(claimed_path, str(e))

# Bad
try:
    process_task(claimed_path)
    complete_task(claimed_path, result)
except Exception as e:
    pass  # Task stuck in In_Progress forever!
```

### 3. Check Claim Success

```python
# Good
success, path = claim_task(task_path, agent_name)
if success:
    process_task(path)
else:
    logger.info("Task already claimed")

# Bad
claim_task(task_path, agent_name)
process_task(task_path)  # May not exist!
```

### 4. Monitor Stale Claims

```python
# Run periodically
def cleanup_stale_claims():
    detect_stale_claims(max_age_minutes=30)
    detect_orphaned_tasks()

# Schedule every 10 minutes
schedule.every(10).minutes.do(cleanup_stale_claims)
```

---

## Success Indicators

✅ No duplicate processing of tasks  
✅ Claim failures handled gracefully  
✅ Stale claims detected and released  
✅ Orphaned tasks recovered  
✅ Sync conflicts resolved automatically  
✅ Metadata tracking complete  
✅ Concurrent claims work correctly  
✅ Release and reclaim works  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Hybrid System  
**Dependencies:** Skill 16 (Hybrid Orchestrator), Skill 20 (Vault Sync Manager)  
**Safety Level:** 🟢 SAFE (Prevents duplicate processing)  
**Critical:** YES (Core protocol for hybrid architecture)
