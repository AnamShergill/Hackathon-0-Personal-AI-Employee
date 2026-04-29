# Agent Mode Detection - Cloud vs Local

## Overview

The Platinum Tier system automatically determines whether it's running in **Cloud mode** or **Local mode** based on environment variables.

---

## Mode Detection Logic

### Method 1: Explicit AGENT_MODE Variable (Recommended)

Set the `AGENT_MODE` environment variable:

```bash
# Cloud VM
export AGENT_MODE=cloud

# Local Machine
export AGENT_MODE=local
```

### Method 2: Automatic Detection (Fallback)

If `AGENT_MODE` is not set, the system detects mode based on available credentials:

**Local Mode Detected If:**
- `SMTP_USER` environment variable exists
- `SMTP_PASS` environment variable exists

**Cloud Mode Detected If:**
- No SMTP credentials found
- Only read-only Odoo credentials present

---

## Environment Variables by Mode

### Cloud Mode (.env)

```bash
# Agent Mode
AGENT_MODE=cloud

# Vault Path
VAULT_PATH=/home/ubuntu/Platinum-Tier/Vault

# Odoo (Read-Only)
ODOO_URL=https://your-odoo.com
ODOO_READONLY_USER=readonly_user
ODOO_READONLY_PASS=readonly_password

# OpenAI
OPENAI_API_KEY=sk-cloud-key

# Logging
LOG_LEVEL=INFO
```

**What Cloud CANNOT Have:**
```bash
# ❌ FORBIDDEN in Cloud .env
SMTP_USER=...
SMTP_PASS=...
WHATSAPP_SESSION_PATH=...
BANKING_API_KEY=...
PAYMENT_TOKEN=...
```

### Local Mode (.env)

```bash
# Agent Mode
AGENT_MODE=local

# Vault Path
VAULT_PATH=/Users/user/Platinum-Tier/Vault

# SMTP (Required for Local)
SMTP_USER=user@example.com
SMTP_PASS=app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Odoo (Full Access)
ODOO_URL=http://localhost:8069
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password

# WhatsApp (Optional)
WHATSAPP_SESSION_PATH=/local/whatsapp_session/

# OpenAI
OPENAI_API_KEY=sk-local-key

# Logging
LOG_LEVEL=INFO
```

---

## Usage Examples

### Running in Cloud Mode

```bash
# Option 1: Set environment variable
export AGENT_MODE=cloud
python Platinum-Tier/Actions/hybrid_orchestrator.py

# Option 2: Command line argument
python Platinum-Tier/Actions/hybrid_orchestrator.py --mode cloud

# Option 3: Automatic detection (no SMTP credentials)
python Platinum-Tier/Actions/hybrid_orchestrator.py
```

### Running in Local Mode

```bash
# Option 1: Set environment variable
export AGENT_MODE=local
python Platinum-Tier/Actions/hybrid_orchestrator.py

# Option 2: Command line argument
python Platinum-Tier/Actions/hybrid_orchestrator.py --mode local

# Option 3: Automatic detection (SMTP credentials present)
python Platinum-Tier/Actions/hybrid_orchestrator.py
```

---

## Verification

### Check Current Mode

The orchestrator logs the detected mode on startup:

```
2026-04-13 14:30:00 - hybrid_orchestrator - INFO - 🚀 Hybrid Orchestrator initialized in CLOUD mode
2026-04-13 14:30:00 - hybrid_orchestrator - INFO - 📁 Vault path: Platinum-Tier/Vault
```

### Test Mode Detection

```python
from hybrid_orchestrator import HybridOrchestrator

orchestrator = HybridOrchestrator()
print(f"Mode: {orchestrator.mode.value}")
print(f"Config: {orchestrator.config}")
```

---

## Configuration by Mode

### Cloud Mode Configuration

```python
{
    'zone': 'cloud',
    'mode': 'draft_only',
    'scan_interval': 30,  # seconds (every 30 seconds)
    'max_concurrent_tasks': 5,
    'allowed_domains': ['email', 'social', 'odoo'],
    'forbidden_actions': ['send', 'post', 'execute', 'payment']
}
```

**Behavior:**
- Scans `Vault/Needs_Action/` every 30 seconds
- Drafts replies, posts, and actions
- Outputs to `Vault/Pending_Approval/`
- Never executes final actions

### Local Mode Configuration

```python
{
    'zone': 'local',
    'mode': 'execute_only',
    'scan_interval': 300,  # seconds (every 5 minutes)
    'max_concurrent_tasks': 3,
    'allowed_domains': ['email', 'social', 'odoo'],
    'allowed_actions': ['send', 'post', 'execute', 'payment']
}
```

**Behavior:**
- Scans `Vault/Pending_Approval/` every 5 minutes
- Presents drafts for HITL approval
- Executes approved actions
- Outputs to `Vault/Done/`

---

## Systemd Service Configuration

### Cloud Service

```ini
# /etc/systemd/system/platinum-cloud.service
[Unit]
Description=Platinum Tier Cloud Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Platinum-Tier
Environment="AGENT_MODE=cloud"
Environment="VAULT_PATH=/home/ubuntu/Platinum-Tier/Vault"
EnvironmentFile=/home/ubuntu/Platinum-Tier/.env
ExecStart=/usr/bin/python3 Actions/hybrid_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Local Service (Optional)

```ini
# /etc/systemd/system/platinum-local.service
[Unit]
Description=Platinum Tier Local Executive
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/Platinum-Tier
Environment="AGENT_MODE=local"
Environment="VAULT_PATH=/home/youruser/Platinum-Tier/Vault"
EnvironmentFile=/home/youruser/Platinum-Tier/.env
ExecStart=/usr/bin/python3 Actions/hybrid_orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Docker Configuration

### Cloud Docker Compose

```yaml
# docker-compose.cloud.yml
version: '3.8'

services:
  cloud-agent:
    build: .
    container_name: platinum-cloud
    environment:
      - AGENT_MODE=cloud
      - VAULT_PATH=/app/Vault
    env_file:
      - .env.cloud
    volumes:
      - ./Vault:/app/Vault
      - ./Logs:/app/Logs
    restart: always
    command: python Actions/hybrid_orchestrator.py
```

### Local Docker Compose

```yaml
# docker-compose.local.yml
version: '3.8'

services:
  local-executive:
    build: .
    container_name: platinum-local
    environment:
      - AGENT_MODE=local
      - VAULT_PATH=/app/Vault
    env_file:
      - .env.local
    volumes:
      - ./Vault:/app/Vault
      - ./Logs:/app/Logs
      - ./whatsapp_session:/app/whatsapp_session
    restart: always
    command: python Actions/hybrid_orchestrator.py
```

---

## Troubleshooting

### Issue: Wrong Mode Detected

**Problem:** System detects Cloud mode when it should be Local (or vice versa)

**Solution:**
```bash
# Explicitly set mode
export AGENT_MODE=local

# Or use command line
python Actions/hybrid_orchestrator.py --mode local
```

### Issue: Mode Not Detected

**Problem:** System fails to detect mode

**Solution:**
```bash
# Check environment variables
env | grep AGENT_MODE
env | grep SMTP

# Set explicitly
export AGENT_MODE=cloud
```

### Issue: Wrong Configuration Loaded

**Problem:** System loads wrong configuration for mode

**Solution:**
```bash
# Verify mode detection
python -c "from hybrid_orchestrator import HybridOrchestrator; o = HybridOrchestrator(); print(o.mode.value)"

# Check config
python -c "from hybrid_orchestrator import HybridOrchestrator; o = HybridOrchestrator(); print(o.config)"
```

---

## Best Practices

### 1. Always Set AGENT_MODE Explicitly

```bash
# Cloud VM
echo "AGENT_MODE=cloud" >> .env

# Local Machine
echo "AGENT_MODE=local" >> .env
```

### 2. Use Separate .env Files

```bash
# Cloud VM
cp Config/cloud.env.example .env

# Local Machine
cp Config/local.env.example .env
```

### 3. Validate Mode on Startup

```python
orchestrator = HybridOrchestrator()
assert orchestrator.mode == AgentMode.CLOUD, "Expected Cloud mode"
```

### 4. Use Systemd for Production

```bash
# Cloud VM
sudo systemctl enable platinum-cloud
sudo systemctl start platinum-cloud

# Local Machine (optional)
sudo systemctl enable platinum-local
sudo systemctl start platinum-local
```

---

## Summary

| Method | Priority | Use Case |
|--------|----------|----------|
| `AGENT_MODE` env var | 1 (Highest) | Explicit mode setting |
| Command line `--mode` | 2 | Testing, one-off runs |
| Auto-detection (SMTP) | 3 (Fallback) | Convenience |

**Recommendation:** Always set `AGENT_MODE` explicitly in production.

---

**Created:** April 13, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
