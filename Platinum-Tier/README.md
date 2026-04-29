# Platinum Tier - Hybrid Cloud + Local AI Employee

**Status:** Phase 1 Complete (Skills & Architecture) ✅  
**Next:** Phase 2 (Python Implementation)  
**Version:** v0.1  
**Date:** April 13, 2026

---

## Overview

Platinum Tier is the production-grade evolution of the Personal AI Employee, featuring a **hybrid Cloud + Local architecture** that enables 24/7 operation while maintaining strict security boundaries.

### Key Features

- 🌐 **Always-On Cloud VM** - Runs 24/7 on Oracle Cloud Free Tier
- 🔒 **Security Isolation** - Secrets never leave Local machine
- 📁 **Vault Communication** - File-based sync via Git/Syncthing
- ⚡ **Claim-by-Move** - Atomic task claiming prevents duplicates
- 👤 **HITL Approval** - Human-in-the-loop for all final actions
- 📊 **Work-Zone Specialization** - Cloud drafts, Local executes

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Platinum Tier Architecture                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Cloud Zone  │    │    Vault     │    │  Local Zone  │
│  (24/7 VM)   │◄──►│   (Synced)   │◄──►│  (Periodic)  │
│              │    │              │    │              │
│ Draft-Only   │    │ Git/Syncthing│    │ Execute-Only │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Cloud Zone (Draft-Only)
- ✅ Email triage + draft replies
- ✅ Social post drafting
- ✅ Odoo extraction (read-only)
- ✅ Weekly briefing generation
- ❌ NO final execution
- ❌ NO secrets access

### Local Zone (Execution-Only)
- ✅ HITL approval interface
- ✅ Final email sending
- ✅ Final social posting
- ✅ Odoo write operations
- ✅ Payment execution
- ✅ WhatsApp operations
- ✅ Dashboard updates

---

## Folder Structure

```
Platinum-Tier/
├── Skills/                          # Core Platinum skills
│   ├── 16_HYBRID_ORCHESTRATOR.md   # Central routing
│   ├── 17_CLOUD_AGENT.md           # Cloud zone agent
│   ├── 18_LOCAL_EXECUTIVE.md       # Local zone agent
│   ├── 19_CLAIM_BY_MOVE.md         # Task claiming protocol
│   ├── 20_VAULT_SYNC_MANAGER.md    # Sync management
│   └── 21_SECURITY_ISOLATION.md    # Security enforcement
│
├── Actions/                         # Python implementations (Phase 2)
│   ├── cloud_agent.py              # Cloud orchestrator
│   ├── local_executive.py          # Local executor
│   ├── vault_sync.py               # Vault synchronization
│   └── claim_manager.py            # Task claiming logic
│
├── Vault/                           # SYNCED COMMUNICATION VAULT
│   ├── Needs_Action/<domain>/      # Entry point for new tasks
│   ├── Plans/<domain>/             # Task plans
│   ├── Pending_Approval/<domain>/  # Awaiting HITL approval
│   ├── In_Progress/<agent>/        # Claimed tasks
│   ├── Updates/                    # Cloud → Local updates
│   ├── Signals/                    # Control signals
│   ├── Done/                       # Completed tasks
│   └── Briefings/                  # Weekly reports
│
├── Config/                          # Configuration files
│   ├── cloud.env.example           # Cloud environment template
│   ├── local.env.example           # Local environment template
│   └── vault_sync.conf             # Sync configuration
│
├── Deployment/                      # Deployment scripts
│   ├── cloud_setup.sh              # Cloud VM setup
│   ├── local_setup.sh              # Local setup
│   └── oracle_cloud_guide.md       # Deployment guide
│
├── FOLDER_STRUCTURE.md              # Complete structure documentation
├── PHASE_1_COMPLETE.md              # Phase 1 completion summary
└── README.md                        # This file
```

---

## Core Skills

### Skill 16: Hybrid Orchestrator
Central routing and coordination system for hybrid architecture.

**Key Features:**
- Task classification and routing
- Work-zone specialization enforcement
- Claim-by-move integration
- Health monitoring
- Update protocol (Cloud → Local)
- Signal protocol (bidirectional)

**File:** `Skills/16_HYBRID_ORCHESTRATOR.md`

### Skill 17: Cloud Agent
24/7 Cloud VM agent for drafting and analysis (draft-only).

**Key Features:**
- Always-on operation
- Email triage and drafting
- Social media drafting
- Odoo read-only operations
- Weekly briefing generation
- Security enforcement

**File:** `Skills/17_CLOUD_AGENT.md`

### Skill 18: Local Executive
Local machine agent for execution and approval (execute-only).

**Key Features:**
- Periodic execution
- HITL approval interface
- Email sending (SMTP)
- Social media posting
- Odoo write operations
- Payment execution
- Dashboard updates

**File:** `Skills/18_LOCAL_EXECUTIVE.md`

### Skill 19: Claim-by-Move Protocol
Atomic task claiming to prevent duplicate processing.

**Key Features:**
- Atomic filesystem operations
- First-mover-wins protocol
- Stale claim detection
- Orphaned task recovery
- Metadata tracking

**File:** `Skills/19_CLAIM_BY_MOVE.md`

### Skill 20: Vault Sync Manager
Bidirectional Vault synchronization via Git or Syncthing.

**Key Features:**
- Git sync (recommended)
- Syncthing alternative
- Conflict resolution
- Secret scanning
- Sync health monitoring

**File:** `Skills/20_VAULT_SYNC_MANAGER.md`

### Skill 21: Security Isolation
Enforce security boundaries between zones.

**Key Features:**
- Environment validation
- File access control
- Operation validation
- API access control
- Secret scanning
- Audit logging

**File:** `Skills/21_SECURITY_ISOLATION.md`

---

## Security Model

### Secret Protection

**NEVER Synced:**
```
*.env
.env.*
*_secrets.json
credentials.json
tokens/
*_session/
*.session
banking_creds/
payment_tokens/
Dashboard.md
local_state.json
```

**Always Synced:**
```
Vault/**/*.md
Vault/**/*.json (state only)
Vault/**/*.signal
```

### Zone Restrictions

**Cloud Cannot:**
- ❌ Send emails
- ❌ Post to social media
- ❌ Write to Odoo
- ❌ Execute payments
- ❌ Access WhatsApp
- ❌ Access banking
- ❌ Update Dashboard

**Local Cannot:**
- ❌ Draft (Cloud does this)
- ❌ Run 24/7 (Cloud does this)

---

## Communication Protocol

### Vault Workflow

1. **Task Arrives** → `Vault/Needs_Action/<domain>/task.md`
2. **Cloud Claims** → `Vault/In_Progress/cloud/task.md` (atomic move)
3. **Cloud Drafts** → `Vault/Pending_Approval/<domain>/draft.md`
4. **Local Pulls** → Syncs Vault via Git
5. **Human Approves** → HITL approval interface
6. **Local Claims** → `Vault/In_Progress/local/draft.md` (atomic move)
7. **Local Executes** → Sends email/posts/records payment
8. **Local Completes** → `Vault/Done/task.md`

### Claim-by-Move Rule

**Protocol:**
- First agent to move file to `In_Progress/<agent>/` owns it
- Atomic filesystem operation prevents duplicates
- If move fails, task already claimed
- Agent must release on error
- Agent must complete to Done on success

---

## Minimum Viable Demo

**Scenario:** Email arrives while Local is offline

1. ✅ Email arrives → Cloud detects in Gmail
2. ✅ Cloud creates task → `Vault/Needs_Action/email/task.md`
3. ✅ Cloud claims task → `Vault/In_Progress/cloud/task.md`
4. ✅ Cloud drafts reply → `Vault/Pending_Approval/email/draft.md`
5. ✅ Cloud pushes to Git
6. ✅ Local comes online → Pulls from Git
7. ✅ Local presents draft → HITL approval interface
8. ✅ Human approves
9. ✅ Local claims draft → `Vault/In_Progress/local/draft.md`
10. ✅ Local sends email → SMTP
11. ✅ Local completes → `Vault/Done/task.md`
12. ✅ Local pushes to Git

---

## Deployment

### Cloud VM (Oracle Free Tier)

**Specs:**
- VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM)
- Ubuntu 22.04 LTS
- Always-on 24/7

**Runs:**
- Cloud agent (24/7)
- Cloud watcher (24/7)
- Cloud scheduler (24/7)
- Odoo (read-only access)

**Never Runs:**
- Email sender
- WhatsApp watcher
- Payment executor
- Final approval actions

### Local Machine

**Specs:**
- Windows/Mac/Linux
- Runs periodically (every 5 minutes)

**Runs:**
- Local executive (periodic)
- Local watcher (periodic)
- HITL approval interface
- Email sender (SMTP)
- WhatsApp watcher
- Payment executor
- Dashboard updates

---

## Development Status

### Phase 1: Skills & Architecture ✅ COMPLETE

- [x] Folder structure created
- [x] 6 core skills documented (9,000+ lines)
- [x] Architecture defined
- [x] Security model specified
- [x] Communication protocol designed

### Phase 2: Python Implementation (NEXT)

- [ ] Core Python agents
- [ ] Watchers and schedulers
- [ ] Configuration files
- [ ] Deployment scripts
- [ ] Testing suite

### Phase 3: Deployment (FUTURE)

- [ ] Oracle Cloud VM setup
- [ ] Git repository configuration
- [ ] Minimum viable demo
- [ ] End-to-end testing
- [ ] Production deployment

---

## Quick Start (After Phase 2)

### Cloud Setup

```bash
# Oracle Cloud VM
git clone https://github.com/your-repo/Platinum-Tier.git
cd Platinum-Tier
cp Config/cloud.env.example .env
nano .env  # Edit with Cloud credentials
pip install -r requirements.txt
python Actions/cloud_agent.py
```

### Local Setup

```bash
# Local Machine
git clone https://github.com/your-repo/Platinum-Tier.git
cd Platinum-Tier
cp Config/local.env.example .env
nano .env  # Edit with Local credentials
pip install -r requirements.txt
python Actions/local_executive.py
```

---

## Key Innovations

### 1. Claim-by-Move Protocol
Uses atomic filesystem operations to prevent duplicate processing without complex locking.

### 2. Work-Zone Specialization
Strict separation of drafting (Cloud) and execution (Local) based on security boundaries.

### 3. Vault Communication
File-based communication via synced Vault folder instead of API calls.

### 4. Smart Conflict Resolution
Automatic conflict resolution based on folder ownership rules.

---

## Documentation

- **FOLDER_STRUCTURE.md** - Complete folder structure
- **PHASE_1_COMPLETE.md** - Phase 1 completion summary
- **Skills/16_HYBRID_ORCHESTRATOR.md** - Central routing
- **Skills/17_CLOUD_AGENT.md** - Cloud zone agent
- **Skills/18_LOCAL_EXECUTIVE.md** - Local zone agent
- **Skills/19_CLAIM_BY_MOVE.md** - Task claiming protocol
- **Skills/20_VAULT_SYNC_MANAGER.md** - Sync management
- **Skills/21_SECURITY_ISOLATION.md** - Security enforcement

**Total:** 9,000+ lines of comprehensive documentation

---

## Support

For questions or issues:
1. Check the skill documentation in `Skills/`
2. Review `FOLDER_STRUCTURE.md` for architecture
3. See `PHASE_1_COMPLETE.md` for status

---

## License

Same as Gold Tier (see parent LICENSE file)

---

## Changelog

### v0.1 (April 13, 2026)
- ✅ Phase 1 complete: Skills and architecture
- ✅ 6 core skills documented
- ✅ Complete folder structure
- ✅ Security model defined
- ✅ Communication protocol specified

---

**Created:** April 13, 2026  
**Version:** v0.1  
**Status:** Phase 1 Complete ✅  
**Next:** Phase 2 - Python Implementation 🚀
