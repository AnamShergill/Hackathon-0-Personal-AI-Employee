# Platinum Tier - Git Setup Guide

Complete guide for setting up Git synchronization between Cloud VM and Local machine.

---

## Overview

The Vault folder is synced between Cloud and Local using Git:
- **Cloud VM:** Pushes drafts, updates, signals
- **Local Machine:** Pulls drafts, pushes completions
- **GitHub:** Central repository for synchronization

---

## Prerequisites

- GitHub account
- Git installed on both Cloud VM and Local machine
- SSH keys or Personal Access Token for authentication

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `platinum-vault` (or your choice)
3. Description: "Platinum Tier Vault - Task synchronization"
4. **Visibility:** Private (recommended for security)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### Option B: Using GitHub CLI

```bash
gh repo create platinum-vault --private --description "Platinum Tier Vault"
```

---

## Step 2: Initialize Vault on Cloud VM

### SSH into Cloud VM

```bash
ssh ubuntu@<your-cloud-vm-ip>
```

### Navigate to Platinum Tier

```bash
cd ~/Platinum-Tier/Vault
```

### Initialize Git Repository

```bash
# Initialize Git
git init

# Configure Git user
git config user.name "Platinum Cloud Agent"
git config user.email "cloud@your-domain.com"

# Add remote
git remote add origin https://github.com/your-username/platinum-vault.git

# Or use SSH (if you have SSH keys set up)
git remote add origin git@github.com:your-username/platinum-vault.git
```

### Create .gitignore (Already Created)

The `.gitignore` file is already in place at `Vault/.gitignore`.

Verify it exists:
```bash
cat .gitignore
```

### Initial Commit and Push

```bash
# Add all files
git add .

# Initial commit
git commit -m "Initial Vault setup"

# Create main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### Authentication

**Option A: HTTPS with Personal Access Token**

1. Generate token: https://github.com/settings/tokens
2. Select scopes: `repo` (full control)
3. Copy token
4. When prompted for password, use the token

**Option B: SSH Keys**

```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "cloud@your-domain.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: https://github.com/settings/keys
```

---

## Step 3: Clone Vault on Local Machine

### Navigate to Platinum Tier

```bash
cd ~/Platinum-Tier
```

### Remove Empty Vault (if exists)

```bash
rm -rf Vault
```

### Clone from GitHub

```bash
# Clone repository
git clone https://github.com/your-username/platinum-vault.git Vault

# Or use SSH
git clone git@github.com:your-username/platinum-vault.git Vault
```

### Configure Git User

```bash
cd Vault

git config user.name "Platinum Local Executive"
git config user.email "local@your-domain.com"
```

---

## Step 4: Test Synchronization

### Test Cloud → Local Flow

**On Cloud VM:**

```bash
cd ~/Platinum-Tier/Vault

# Create test file
echo "Test from Cloud" > Needs_Action/email/test_cloud.md

# Commit and push
git add .
git commit -m "Test: Cloud draft"
git push
```

**On Local Machine:**

```bash
cd ~/Platinum-Tier/Vault

# Pull changes
git pull

# Verify file exists
cat Needs_Action/email/test_cloud.md
# Should show: "Test from Cloud"
```

### Test Local → Cloud Flow

**On Local Machine:**

```bash
cd ~/Platinum-Tier/Vault

# Create test file
echo "Test from Local" > Done/test_local.md

# Commit and push
git add .
git commit -m "Test: Local completion"
git push
```

**On Cloud VM:**

```bash
cd ~/Platinum-Tier/Vault

# Pull changes
git pull

# Verify file exists
cat Done/test_local.md
# Should show: "Test from Local"
```

---

## Step 5: Automated Sync Setup

### Cloud VM - Systemd Timer (Recommended)

Create sync service:

```bash
sudo nano /etc/systemd/system/platinum-vault-sync.service
```

```ini
[Unit]
Description=Platinum Vault Git Sync
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/Platinum-Tier/Vault
ExecStart=/usr/bin/git pull --rebase
ExecStart=/usr/bin/git add .
ExecStart=/usr/bin/git commit -m "Cloud sync: %Y-%m-%d %H:%M:%S" || true
ExecStart=/usr/bin/git push

[Install]
WantedBy=multi-user.target
```

Create sync timer:

```bash
sudo nano /etc/systemd/system/platinum-vault-sync.timer
```

```ini
[Unit]
Description=Platinum Vault Git Sync Timer
Requires=platinum-vault-sync.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable platinum-vault-sync.timer
sudo systemctl start platinum-vault-sync.timer

# Check status
sudo systemctl status platinum-vault-sync.timer
```

### Local Machine - Cron Job (Optional)

```bash
# Edit crontab
crontab -e

# Add sync every 5 minutes
*/5 * * * * cd ~/Platinum-Tier/Vault && git pull --rebase && git add . && git commit -m "Local sync: $(date)" || true && git push
```

### Using Vault Sync Manager (Recommended)

**Cloud VM:**

```bash
# Run sync manager in background
nohup python ~/Platinum-Tier/Actions/vault_sync_manager.py sync &

# Or use systemd (see systemd section below)
```

**Local Machine:**

```bash
# Run sync manager periodically
while true; do
    python ~/Platinum-Tier/Actions/vault_sync_manager.py sync
    sleep 300  # 5 minutes
done
```

---

## Step 6: Systemd Services (Production)

### Cloud Agent Service

```bash
sudo nano /etc/systemd/system/platinum-cloud.service
```

```ini
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
ExecStart=/usr/bin/python3 Actions/cloud_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable platinum-cloud.service
sudo systemctl start platinum-cloud.service

# Check status
sudo systemctl status platinum-cloud.service

# View logs
sudo journalctl -u platinum-cloud.service -f
```

### Local Executive Service (Optional)

```bash
sudo nano /etc/systemd/system/platinum-local.service
```

```ini
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
ExecStart=/usr/bin/python3 Actions/local_executive.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Issue: Authentication Failed

**Solution:**

```bash
# For HTTPS, use Personal Access Token
git remote set-url origin https://<token>@github.com/your-username/platinum-vault.git

# For SSH, ensure keys are added
ssh -T git@github.com
```

### Issue: Merge Conflicts

**Solution:**

The Vault Sync Manager automatically resolves conflicts using smart rules:
- `In_Progress/cloud/` → Keep Cloud version
- `In_Progress/local/` → Keep Local version
- `Pending_Approval/` → Keep Cloud version
- `Done/` → Keep newer version

Manual resolution:

```bash
# View conflicts
git status

# Resolve using smart rules
python ~/Platinum-Tier/Actions/vault_sync_manager.py sync
```

### Issue: Secrets Accidentally Committed

**Solution:**

```bash
# Remove from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all

# Rotate compromised secrets immediately!
```

### Issue: Sync Not Working

**Solution:**

```bash
# Check Git status
cd ~/Platinum-Tier/Vault
git status

# Check remote
git remote -v

# Test connection
git fetch origin

# Check logs
python ~/Platinum-Tier/Actions/vault_sync_manager.py status
```

---

## Security Best Practices

### 1. Use Private Repository

Always use a private GitHub repository for the Vault.

### 2. Validate .gitignore

```bash
# Check .gitignore is working
cd ~/Platinum-Tier/Vault
python ~/Platinum-Tier/Actions/vault_sync_manager.py status

# Verify no secrets in Git
git ls-files | grep -E '\.env|secret|credential|token|session'
# Should return nothing
```

### 3. Regular Audits

```bash
# Audit committed files
git log --all --full-history --pretty=format: --name-only | sort -u

# Check for secrets
git log -p | grep -i 'password\|secret\|token\|key'
```

### 4. Use SSH Keys

SSH keys are more secure than HTTPS tokens for production.

### 5. Rotate Tokens

Rotate GitHub Personal Access Tokens every 90 days.

---

## Quick Reference

### Common Commands

```bash
# Pull changes
cd ~/Platinum-Tier/Vault && git pull

# Push changes
cd ~/Platinum-Tier/Vault && git add . && git commit -m "Update" && git push

# Full sync
python ~/Platinum-Tier/Actions/vault_sync_manager.py sync

# Check status
python ~/Platinum-Tier/Actions/vault_sync_manager.py status

# View logs
git log --oneline -10
```

### Sync Manager Commands

```bash
# Initialize repository
python Actions/vault_sync_manager.py init --url https://github.com/your-username/platinum-vault.git

# Pull only
python Actions/vault_sync_manager.py pull

# Push only
python Actions/vault_sync_manager.py push -m "Custom message"

# Full sync
python Actions/vault_sync_manager.py sync

# Check status
python Actions/vault_sync_manager.py status
```

---

## Success Checklist

- [ ] GitHub repository created (private)
- [ ] Cloud VM Vault initialized with Git
- [ ] Local Machine Vault cloned from GitHub
- [ ] Test sync Cloud → Local works
- [ ] Test sync Local → Cloud works
- [ ] .gitignore validated (no secrets)
- [ ] Automated sync configured
- [ ] Systemd services running (Cloud)
- [ ] Authentication working (SSH or token)
- [ ] Conflict resolution tested

---

**Created:** April 13, 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
