# Skill 20: Vault Sync Manager

## Purpose

Manages bidirectional synchronization of the Vault folder between Cloud VM and Local machine using Git or Syncthing. Ensures task files, updates, and signals are synced while protecting secrets.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│            Vault Sync Manager                            │
│         (Git or Syncthing)                               │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Cloud VM    │    │   GitHub     │    │Local Machine │
│              │    │   (Remote)   │    │              │
│ Vault/       │◄──►│              │◄──►│ Vault/       │
│ (Push)       │    │  Repository  │    │ (Pull)       │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## When to Use

- **Always**: Vault must be synced for hybrid architecture to work
- **Cloud pushes**: After creating drafts, updates, signals
- **Local pulls**: Before checking for pending approvals
- **Local pushes**: After executing tasks, updating status
- **Cloud pulls**: Before claiming new tasks

## When NOT to Use

- Syncing secrets (.env, credentials, sessions)
- Syncing large binary files
- Syncing local-only files (Dashboard.md)

---

## Sync Methods

### Option 1: Git (Recommended)

**Advantages:**
- ✅ Version control and history
- ✅ Conflict resolution
- ✅ Easy to audit changes
- ✅ Works with GitHub/GitLab
- ✅ Free and widely supported

**Disadvantages:**
- ❌ Requires manual push/pull
- ❌ Potential merge conflicts
- ❌ Slight delay in sync

### Option 2: Syncthing

**Advantages:**
- ✅ Automatic bidirectional sync
- ✅ Real-time updates
- ✅ No manual intervention
- ✅ Conflict handling built-in

**Disadvantages:**
- ❌ No version history
- ❌ Requires Syncthing setup
- ❌ More complex configuration

---

## Git Sync Implementation

### Repository Setup

```bash
# 1. Create Git repository
cd Platinum-Tier/Vault
git init

# 2. Add remote (GitHub)
git remote add origin https://github.com/your-username/platinum-vault.git

# 3. Create .gitignore
cat > .gitignore << 'EOF'
# Secrets (NEVER sync)
*.env
.env.*
*_secrets.json
credentials.json
tokens/
*_session/
*.session
banking_creds/
payment_tokens/

# Local-only files
../Dashboard.md
../local_state.json

# Temporary files
*.tmp
*.lock
.DS_Store
Thumbs.db
EOF

# 4. Initial commit
git add .
git commit -m "Initial Vault setup"
git push -u origin main
```

### Cloud Push Function

```python
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def cloud_push_vault(message: str = None):
    """
    Push Vault changes from Cloud to Git remote.
    
    Args:
        message: Optional commit message
    
    Returns:
        True if push successful, False otherwise
    """
    try:
        # 1. Change to Vault directory
        vault_path = "/home/ubuntu/Platinum-Tier/Vault"
        
        # 2. Add all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 3. Check if there are changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )
        
        if not status.stdout.strip():
            logger.info("No changes to push")
            return True
        
        # 4. Commit changes
        if not message:
            message = f"Cloud update: {datetime.now().isoformat()}"
        
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 5. Push to remote
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        logger.info(f"✅ Cloud pushed to Git: {message}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Cloud push failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Cloud push error: {e}")
        return False
```

### Cloud Pull Function

```python
def cloud_pull_vault():
    """
    Pull Vault changes from Git remote to Cloud.
    
    Returns:
        True if pull successful, False otherwise
    """
    try:
        # 1. Change to Vault directory
        vault_path = "/home/ubuntu/Platinum-Tier/Vault"
        
        # 2. Fetch changes
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 3. Check if pull needed
        local_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=vault_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote_commit = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=vault_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if local_commit == remote_commit:
            logger.info("Vault already up to date")
            return True
        
        # 4. Pull changes (with rebase to avoid merge commits)
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        logger.info("✅ Cloud pulled from Git")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Cloud pull failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Cloud pull error: {e}")
        return False
```

### Local Push Function

```python
def local_push_vault(message: str = None):
    """
    Push Vault changes from Local to Git remote.
    
    Args:
        message: Optional commit message
    
    Returns:
        True if push successful, False otherwise
    """
    try:
        # 1. Change to Vault directory
        vault_path = "/Users/user/Platinum-Tier/Vault"  # Adjust for Windows/Mac/Linux
        
        # 2. Add all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 3. Check if there are changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )
        
        if not status.stdout.strip():
            logger.info("No changes to push")
            return True
        
        # 4. Commit changes
        if not message:
            message = f"Local update: {datetime.now().isoformat()}"
        
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 5. Push to remote
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        logger.info(f"✅ Local pushed to Git: {message}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Local push failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Local push error: {e}")
        return False
```

### Local Pull Function

```python
def local_pull_vault():
    """
    Pull Vault changes from Git remote to Local.
    
    Returns:
        True if pull successful, False otherwise
    """
    try:
        # 1. Change to Vault directory
        vault_path = "/Users/user/Platinum-Tier/Vault"  # Adjust for Windows/Mac/Linux
        
        # 2. Fetch changes
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        # 3. Check if pull needed
        local_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=vault_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote_commit = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=vault_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if local_commit == remote_commit:
            logger.info("Vault already up to date")
            return True
        
        # 4. Pull changes (with rebase to avoid merge commits)
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=vault_path,
            check=True,
            capture_output=True
        )
        
        logger.info("✅ Local pulled from Git")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Local pull failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Local pull error: {e}")
        return False
```

---

## Sync Workflow

### Cloud Workflow

```python
def cloud_sync_workflow():
    """
    Cloud agent sync workflow.
    """
    # 1. Pull before claiming tasks
    cloud_pull_vault()
    
    # 2. Scan for new tasks
    new_tasks = scan_needs_action()
    
    # 3. Process tasks
    for task in new_tasks:
        process_cloud_task(task)
    
    # 4. Push after creating drafts
    cloud_push_vault("Cloud: Created drafts")
```

### Local Workflow

```python
def local_sync_workflow():
    """
    Local executive sync workflow.
    """
    # 1. Pull before checking approvals
    local_pull_vault()
    
    # 2. Scan for pending approvals
    pending_tasks = scan_pending_approval()
    
    # 3. Present for approval and execute
    for task in pending_tasks:
        if human_approves(task):
            execute_local_task(task)
    
    # 4. Push after executing tasks
    local_push_vault("Local: Executed tasks")
```

---

## Conflict Resolution

### Detect Conflicts

```python
def detect_git_conflicts(vault_path: str) -> List[str]:
    """
    Detect Git merge conflicts in Vault.
    
    Returns:
        List of files with conflicts
    """
    try:
        # Check for conflict markers
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )
        
        conflicts = result.stdout.strip().split('\n')
        conflicts = [f for f in conflicts if f]  # Remove empty strings
        
        if conflicts:
            logger.warning(f"⚠️ Git conflicts detected: {conflicts}")
        
        return conflicts
        
    except Exception as e:
        logger.error(f"❌ Conflict detection error: {e}")
        return []
```

### Resolve Conflicts

```python
def resolve_git_conflicts(vault_path: str, strategy: str = "remote"):
    """
    Resolve Git conflicts automatically.
    
    Args:
        vault_path: Path to Vault directory
        strategy: "remote" (keep Cloud) or "local" (keep Local)
    """
    try:
        conflicts = detect_git_conflicts(vault_path)
        
        if not conflicts:
            return True
        
        for conflict_file in conflicts:
            if strategy == "remote":
                # Keep remote (Cloud) version
                subprocess.run(
                    ["git", "checkout", "--theirs", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Resolved conflict (kept remote): {conflict_file}")
                
            elif strategy == "local":
                # Keep local version
                subprocess.run(
                    ["git", "checkout", "--ours", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Resolved conflict (kept local): {conflict_file}")
        
        # Stage resolved files
        subprocess.run(
            ["git", "add", "."],
            cwd=vault_path,
            check=True
        )
        
        # Continue rebase
        subprocess.run(
            ["git", "rebase", "--continue"],
            cwd=vault_path,
            check=True
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Conflict resolution error: {e}")
        return False
```

### Smart Conflict Resolution

```python
def smart_resolve_conflicts(vault_path: str):
    """
    Smart conflict resolution based on file location.
    
    Rules:
    - In_Progress/cloud/ → Keep Cloud version
    - In_Progress/local/ → Keep Local version
    - Pending_Approval/ → Keep Cloud version (drafts)
    - Done/ → Keep newer version
    """
    try:
        conflicts = detect_git_conflicts(vault_path)
        
        for conflict_file in conflicts:
            if "In_Progress/cloud/" in conflict_file:
                # Cloud owns this
                subprocess.run(
                    ["git", "checkout", "--theirs", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Kept Cloud version: {conflict_file}")
                
            elif "In_Progress/local/" in conflict_file:
                # Local owns this
                subprocess.run(
                    ["git", "checkout", "--ours", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Kept Local version: {conflict_file}")
                
            elif "Pending_Approval/" in conflict_file:
                # Cloud creates drafts, keep Cloud version
                subprocess.run(
                    ["git", "checkout", "--theirs", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Kept Cloud draft: {conflict_file}")
                
            else:
                # Default: keep newer version
                subprocess.run(
                    ["git", "checkout", "--theirs", conflict_file],
                    cwd=vault_path,
                    check=True
                )
                logger.info(f"✅ Kept newer version: {conflict_file}")
        
        # Stage and continue
        subprocess.run(["git", "add", "."], cwd=vault_path, check=True)
        subprocess.run(["git", "rebase", "--continue"], cwd=vault_path, check=True)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Smart conflict resolution error: {e}")
        return False
```

---

## Syncthing Implementation (Alternative)

### Setup Syncthing

```bash
# Install Syncthing
# Ubuntu/Debian
sudo apt install syncthing

# macOS
brew install syncthing

# Windows
# Download from https://syncthing.net/

# Start Syncthing
syncthing
```

### Configure Syncthing

```python
def configure_syncthing():
    """
    Configure Syncthing for Vault sync.
    """
    config = {
        'folder': {
            'id': 'platinum-vault',
            'path': '/path/to/Platinum-Tier/Vault',
            'devices': ['cloud-device-id', 'local-device-id'],
            'rescanIntervalS': 60,  # Scan every 60 seconds
            'fsWatcherEnabled': True,  # Watch for changes
            'ignorePerms': False
        },
        'ignore': [
            '*.env',
            '.env.*',
            '*_secrets.json',
            'credentials.json',
            'tokens/',
            '*_session/',
            '*.session',
            'banking_creds/',
            'payment_tokens/',
            '../Dashboard.md',
            '../local_state.json'
        ]
    }
    
    # Write Syncthing config
    # (Syncthing uses XML config, this is pseudocode)
    write_syncthing_config(config)
```

### Syncthing Monitoring

```python
def monitor_syncthing_sync():
    """
    Monitor Syncthing sync status.
    """
    import requests
    
    # Syncthing REST API
    api_url = "http://localhost:8384/rest/db/status"
    api_key = os.getenv('SYNCTHING_API_KEY')
    
    headers = {'X-API-Key': api_key}
    
    try:
        response = requests.get(
            f"{api_url}?folder=platinum-vault",
            headers=headers
        )
        
        status = response.json()
        
        logger.info(f"Syncthing status: {status['state']}")
        logger.info(f"Files in sync: {status['inSyncFiles']}")
        logger.info(f"Bytes in sync: {status['inSyncBytes']}")
        
        return status['state'] == 'idle'
        
    except Exception as e:
        logger.error(f"❌ Syncthing monitoring error: {e}")
        return False
```

---

## Security

### Validate .gitignore

```python
def validate_gitignore():
    """
    Ensure .gitignore protects secrets.
    """
    required_patterns = [
        '*.env',
        '.env.*',
        '*_secrets.json',
        'credentials.json',
        'tokens/',
        '*_session/',
        '*.session',
        'banking_creds/',
        'payment_tokens/'
    ]
    
    gitignore_path = "Platinum-Tier/Vault/.gitignore"
    
    try:
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        missing = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing.append(pattern)
        
        if missing:
            logger.error(f"❌ .gitignore missing patterns: {missing}")
            return False
        
        logger.info("✅ .gitignore validated")
        return True
        
    except Exception as e:
        logger.error(f"❌ .gitignore validation error: {e}")
        return False
```

### Scan for Secrets

```python
def scan_for_secrets_in_vault():
    """
    Scan Vault for accidentally committed secrets.
    """
    import re
    
    secret_patterns = [
        r'password\s*=\s*["\'].*["\']',
        r'api_key\s*=\s*["\'].*["\']',
        r'token\s*=\s*["\'].*["\']',
        r'secret\s*=\s*["\'].*["\']',
        r'sk-[a-zA-Z0-9]{32,}',  # OpenAI API key
        r'ghp_[a-zA-Z0-9]{36}',  # GitHub token
    ]
    
    vault_path = "Platinum-Tier/Vault"
    
    violations = []
    
    for root, dirs, files in os.walk(vault_path):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.md') or file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        violations.append({
                            'file': filepath,
                            'pattern': pattern,
                            'matches': matches
                        })
    
    if violations:
        logger.error(f"❌ Secrets found in Vault: {violations}")
        return False
    
    logger.info("✅ No secrets found in Vault")
    return True
```

---

## Monitoring

### Sync Health Check

```python
def sync_health_check():
    """
    Check Vault sync health.
    """
    health = {
        'timestamp': datetime.now().isoformat(),
        'git_status': 'unknown',
        'last_sync': 'unknown',
        'conflicts': [],
        'uncommitted_changes': False,
        'secrets_protected': False
    }
    
    try:
        vault_path = "Platinum-Tier/Vault"
        
        # 1. Check Git status
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )
        
        health['uncommitted_changes'] = bool(status.stdout.strip())
        
        # 2. Check for conflicts
        health['conflicts'] = detect_git_conflicts(vault_path)
        
        # 3. Check last sync time
        last_commit = subprocess.run(
            ["git", "log", "-1", "--format=%cd"],
            cwd=vault_path,
            capture_output=True,
            text=True
        )
        health['last_sync'] = last_commit.stdout.strip()
        
        # 4. Validate .gitignore
        health['secrets_protected'] = validate_gitignore()
        
        # 5. Overall status
        if health['conflicts'] or not health['secrets_protected']:
            health['git_status'] = 'unhealthy'
        else:
            health['git_status'] = 'healthy'
        
        return health
        
    except Exception as e:
        logger.error(f"❌ Sync health check error: {e}")
        health['git_status'] = 'error'
        return health
```

---

## Automation

### Auto-Sync on Cloud

```python
def cloud_auto_sync_loop():
    """
    Cloud auto-sync loop (runs continuously).
    """
    while True:
        try:
            # 1. Pull changes
            cloud_pull_vault()
            
            # 2. Wait for processing
            time.sleep(30)
            
            # 3. Push changes
            cloud_push_vault()
            
            # 4. Sleep
            time.sleep(30)  # Sync every 60 seconds total
            
        except Exception as e:
            logger.error(f"❌ Cloud auto-sync error: {e}")
            time.sleep(60)
```

### Auto-Sync on Local

```python
def local_auto_sync_loop():
    """
    Local auto-sync loop (runs periodically).
    """
    while True:
        try:
            # 1. Pull changes
            local_pull_vault()
            
            # 2. Wait for processing
            time.sleep(300)  # 5 minutes
            
            # 3. Push changes
            local_push_vault()
            
            # 4. Sleep
            time.sleep(300)  # Sync every 10 minutes total
            
        except Exception as e:
            logger.error(f"❌ Local auto-sync error: {e}")
            time.sleep(300)
```

---

## Testing

### Test Sync

```bash
# Cloud VM
cd Platinum-Tier/Vault
echo "Test from Cloud" > test_sync.md
git add test_sync.md
git commit -m "Test sync from Cloud"
git push

# Local Machine
cd Platinum-Tier/Vault
git pull
cat test_sync.md  # Should show "Test from Cloud"

# Local Machine
echo "Test from Local" > test_sync_local.md
git add test_sync_local.md
git commit -m "Test sync from Local"
git push

# Cloud VM
git pull
cat test_sync_local.md  # Should show "Test from Local"
```

---

## Success Indicators

✅ Vault syncs bidirectionally  
✅ No secrets in Git repository  
✅ .gitignore protects sensitive files  
✅ Conflicts resolved automatically  
✅ Sync health monitoring works  
✅ Auto-sync runs reliably  
✅ No data loss during sync  
✅ Sync latency < 2 minutes  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Hybrid System  
**Dependencies:** Skill 19 (Claim-by-Move), Skill 21 (Security Isolation)  
**Safety Level:** 🟡 MODERATE (Must protect secrets)  
**Critical:** YES (Core infrastructure for hybrid architecture)
