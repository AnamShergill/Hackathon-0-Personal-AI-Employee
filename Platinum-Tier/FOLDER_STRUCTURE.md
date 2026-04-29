# Platinum Tier - Folder Structure

## Overview

Platinum Tier implements a hybrid Cloud + Local architecture with a synced Vault for communication between zones.

---

## Complete Structure

```
Platinum-Tier/
├── Skills/                          # Platinum-specific skills
│   ├── 16_HYBRID_ORCHESTRATOR.md   # Central routing for hybrid mode
│   ├── 17_CLOUD_AGENT.md           # Cloud zone draft-only agent
│   ├── 18_LOCAL_EXECUTIVE.md       # Local zone execution agent
│   ├── 19_CLAIM_BY_MOVE.md         # Task claiming protocol
│   ├── 20_VAULT_SYNC_MANAGER.md    # Git/Syncthing sync management
│   └── 21_SECURITY_ISOLATION.md    # Security and secret protection
│
├── Actions/                         # Platinum-specific actions
│   ├── cloud_drafter.py            # Cloud drafting engine
│   ├── local_executor.py           # Local execution engine
│   ├── vault_sync.py               # Vault synchronization
│   └── claim_manager.py            # Task claiming logic
│
├── MCPs/                            # Model Context Protocols
│   ├── hybrid_orchestrator_mcp.py  # Hybrid routing MCP
│   ├── vault_manager_mcp.py        # Vault operations MCP
│   └── security_guard_mcp.py       # Security validation MCP
│
├── Watchers/                        # Zone-specific watchers
│   ├── cloud_watcher.py            # Cloud zone monitoring
│   ├── local_watcher.py            # Local zone monitoring
│   └── vault_watcher.py            # Vault sync monitoring
│
├── Schedulers/                      # Scheduled tasks
│   ├── cloud_runner.py             # Cloud 24/7 scheduler
│   └── local_runner.py             # Local periodic scheduler
│
├── Logs/                            # Separate logs per zone
│   ├── cloud/                      # Cloud zone logs
│   └── local/                      # Local zone logs
│
├── Vault/                           # SYNCED COMMUNICATION VAULT
│   │
│   ├── Needs_Action/               # Incoming tasks (entry point)
│   │   ├── email/                  # Email-related tasks
│   │   ├── social/                 # Social media tasks
│   │   └── odoo/                   # Odoo/accounting tasks
│   │
│   ├── Plans/                      # Task plans by domain
│   │   ├── email/                  # Email plans
│   │   ├── social/                 # Social media plans
│   │   └── odoo/                   # Odoo plans
│   │
│   ├── Pending_Approval/           # Awaiting HITL approval
│   │   ├── email/                  # Email drafts for approval
│   │   ├── social/                 # Social posts for approval
│   │   └── odoo/                   # Odoo actions for approval
│   │
│   ├── In_Progress/                # Claimed tasks by agent
│   │   ├── cloud/                  # Cloud agent working
│   │   └── local/                  # Local agent working
│   │
│   ├── Updates/                    # Status updates (Cloud → Local)
│   │   └── *.md                    # Update files
│   │
│   ├── Signals/                    # Control signals
│   │   └── *.signal                # Signal files
│   │
│   ├── Done/                       # Completed tasks
│   │   └── *.md                    # Archived completed tasks
│   │
│   └── Briefings/                  # Weekly briefings
│       └── *.md                    # Generated briefings
│
├── Config/                          # Configuration files
│   ├── cloud.env.example           # Cloud environment template
│   ├── local.env.example           # Local environment template
│   └── vault_sync.conf             # Sync configuration
│
├── Deployment/                      # Deployment scripts
│   ├── cloud_setup.sh              # Cloud VM setup
│   ├── local_setup.sh              # Local setup
│   └── oracle_cloud_guide.md       # Oracle Cloud deployment
│
├── .gitignore                       # Protect secrets
├── README.md                        # Platinum Tier documentation
└── PLATINUM_ARCHITECTURE.md         # Architecture overview
```

---

## Vault Communication Protocol

### Work Zones

**Cloud Zone (Draft-Only)**
- Monitors: `Vault/Needs_Action/`
- Claims: Moves to `Vault/In_Progress/cloud/`
- Outputs: `Vault/Pending_Approval/`, `Vault/Updates/`
- Never: Executes final actions, accesses secrets

**Local Zone (Execution-Only)**
- Monitors: `Vault/Pending_Approval/`, `Vault/Updates/`
- Claims: Moves to `Vault/In_Progress/local/`
- Outputs: `Vault/Done/`, Dashboard updates
- Only: Executes final actions, HITL approval

### Claim-by-Move Rule

1. Task arrives in `Vault/Needs_Action/<domain>/task.md`
2. First agent to move it to `Vault/In_Progress/<agent>/task.md` owns it
3. Agent processes and outputs to appropriate folder
4. Completed tasks move to `Vault/Done/task.md`

### Single-Writer Rules

- **Dashboard.md**: Only Local zone writes
- **Secrets**: Never synced, never in Vault
- **Updates**: Cloud writes to `Updates/`, Local merges

---

## Security Boundaries

### NEVER Synced (Protected by .gitignore)

```
# Secrets
*.env
.env.*
*_secrets.json
credentials.json
tokens/

# Sessions
*_session/
*.session
whatsapp_session/

# Banking/Payment
banking_creds/
payment_tokens/

# Local-only
Dashboard.md
local_state.json
```

### Always Synced (Vault only)

```
# Task files
Vault/**/*.md
Vault/**/*.json (state only)
Vault/**/*.signal

# Logs (optional)
Logs/**/*.log
```

---

## Data Flow Examples

### Example 1: Email Draft (Cloud → Local)

```
1. Email arrives → Vault/Needs_Action/email/email_20260413.md
2. Cloud claims → Vault/In_Progress/cloud/email_20260413.md
3. Cloud drafts → Vault/Pending_Approval/email/email_reply_20260413.md
4. Local approves → Vault/In_Progress/local/email_reply_20260413.md
5. Local sends → Vault/Done/email_reply_20260413.md
```

### Example 2: Payment Reconciliation (Cloud → Local)

```
1. Payment email → Vault/Needs_Action/odoo/payment_20260413.md
2. Cloud claims → Vault/In_Progress/cloud/payment_20260413.md
3. Cloud matches invoice → Vault/Pending_Approval/odoo/payment_action_20260413.md
4. Local reviews → Vault/In_Progress/local/payment_action_20260413.md
5. Local records in Odoo → Vault/Done/payment_action_20260413.md
```

### Example 3: Weekly Briefing (Cloud → Local)

```
1. Sunday 8 PM → Cloud generates briefing
2. Cloud writes → Vault/Briefings/Weekly_Report_20260413.md
3. Cloud signals → Vault/Updates/briefing_ready_20260413.md
4. Local reads and displays
```

---

## Sync Methods

### Option 1: Git (Recommended)

```bash
# Cloud pushes
cd Platinum-Tier/Vault
git add .
git commit -m "Cloud: Draft email reply"
git push

# Local pulls
cd Platinum-Tier/Vault
git pull
```

### Option 2: Syncthing

```bash
# Bidirectional sync
# Cloud: ~/Platinum-Tier/Vault
# Local: ~/Platinum-Tier/Vault
# Auto-sync every 60 seconds
```

---

## Deployment Zones

### Cloud VM (Oracle Free Tier)

**Runs 24/7:**
- `cloud_watcher.py` - Monitors Vault/Needs_Action/
- `cloud_runner.py` - Scheduled tasks
- `cloud_drafter.py` - Drafting engine
- Odoo (read-only access)

**Never Runs:**
- Email sender (SMTP)
- WhatsApp watcher
- Payment executor
- Final approval actions

### Local Machine

**Runs Periodically:**
- `local_watcher.py` - Monitors Vault/Pending_Approval/
- `local_runner.py` - Scheduled tasks
- `local_executor.py` - Execution engine
- HITL approval interface

**Exclusive Access:**
- WhatsApp session
- Banking credentials
- Payment execution
- Dashboard.md updates

---

## Status: ✅ STRUCTURE COMPLETE

All folders created and ready for Platinum Tier implementation.

**Next Steps:**
1. Create core Platinum skills (16-21)
2. Implement Python agents
3. Setup Git sync
4. Deploy to Oracle Cloud
5. Test minimum viable demo

---

**Created**: April 13, 2026  
**Version**: Platinum Tier v0.1  
**Architecture**: Hybrid Cloud + Local
