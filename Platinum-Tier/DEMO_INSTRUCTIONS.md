# Platinum Tier - Demo Testing Instructions

Complete step-by-step guide for testing the Platinum Tier Minimum Viable Demo.

---

## Demo Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATINUM TIER DEMO FLOW                      │
└─────────────────────────────────────────────────────────────────┘

1. Email Arrives (Local Offline)
   └─> Needs_Action/email/demo_test_*.json

2. Cloud Agent Detects & Drafts Reply
   └─> In_Progress/cloud/demo_test_*.json (claimed)
   └─> Pending_Approval/demo_test_*.json (draft created)

3. Local Comes Online & User Reviews
   └─> User approves draft
   └─> Needs_Action/email/demo_test_*_approved.json

4. Local Executive Executes Send
   └─> In_Progress/local/demo_test_*_approved.json (claimed)
   └─> Done/demo_test_*.json (completed)

5. Verification
   └─> Needs_Action: Empty ✅
   └─> Pending_Approval: Empty ✅
   └─> In_Progress: Empty ✅
   └─> Done: Has completed task ✅
```

---

## Prerequisites

### 1. Python Environment

```bash
# Ensure Python 3.9+ is installed
python --version

# Install dependencies
cd Platinum-Tier
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example config
cp Config/local.env.example .env

# Edit .env with your settings
nano .env
```

**Minimum .env configuration for demo:**

```bash
# Agent Mode (will be overridden by demo script)
AGENT_MODE=local

# Vault Path
VAULT_PATH=./Vault

# Email Settings (for actual sending - optional for demo)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Git Settings (optional for demo)
GIT_REPO_URL=https://github.com/your-username/platinum-vault.git
```

### 3. Vault Structure

```bash
# Ensure Vault directories exist
mkdir -p Vault/Needs_Action/email
mkdir -p Vault/Pending_Approval
mkdir -p Vault/In_Progress/cloud
mkdir -p Vault/In_Progress/local
mkdir -p Vault/Done
```

---

## Running the Demo

### Option 1: Automated Demo Script (Recommended)

```bash
cd Platinum-Tier

# Run the complete automated demo
python demo_test.py
```

**Expected Output:**

```
================================================================================
PLATINUM TIER - MINIMUM VIABLE DEMO
================================================================================

[14:30:00] ✅ Setup
           Test environment ready

[14:30:01] ✅ Step 1
           Email task created: demo_test_20260414_143001.json

[14:30:02] ✅ Step 2
           Draft created: demo_test_20260414_143001.json

[14:30:04] ✅ Step 3
           Draft approved and ready for execution

[14:30:05] ✅ Step 4
           Email sent and moved to Done: demo_test_20260414_143001.json

[14:30:06] ✅ Verification
           All tasks completed and archived correctly

================================================================================
TEST SUMMARY
================================================================================

Total Tests: 6
Passed: 6 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 ALL TESTS PASSED - PLATINUM TIER DEMO SUCCESSFUL!

================================================================================
```

---

### Option 2: Manual Step-by-Step Demo

For a deeper understanding, run each step manually:

#### Step 1: Create Incoming Email Task

```bash
cd Platinum-Tier

# Create test email
cat > Vault/Needs_Action/email/demo_manual_$(date +%Y%m%d_%H%M%S).json << 'EOF'
{
  "task_id": "demo_manual_001",
  "type": "email",
  "action": "draft_reply",
  "priority": "normal",
  "created_at": "2026-04-14T14:30:00",
  "email": {
    "from": "customer@example.com",
    "to": "ceo@company.com",
    "subject": "Question about your services",
    "body": "Hi, I would like to know more about your consulting services. Can you provide pricing and availability?",
    "received_at": "2026-04-14T14:30:00"
  },
  "instructions": "Draft a professional reply with pricing information"
}
EOF

# Verify file created
ls -la Vault/Needs_Action/email/
```

#### Step 2: Run Cloud Agent (Simulate Local Offline)

```bash
# Set Cloud mode
export AGENT_MODE=cloud

# Run Cloud Agent once
python Actions/cloud_agent.py --once

# Check Pending_Approval for draft
ls -la Vault/Pending_Approval/
cat Vault/Pending_Approval/demo_manual_*.json
```

**Expected:** Draft email in `Pending_Approval/`

#### Step 3: Approve Draft (Simulate User Review)

```bash
# View the draft
cat Vault/Pending_Approval/demo_manual_*.json

# Approve by modifying and moving
python << 'EOF'
import json
from pathlib import Path
from datetime import datetime

# Find draft
drafts = list(Path("Vault/Pending_Approval").glob("demo_manual_*.json"))
if drafts:
    draft_file = drafts[0]
    
    # Read draft
    with open(draft_file, 'r') as f:
        draft = json.load(f)
    
    # Add approval
    draft['approved_at'] = datetime.now().isoformat()
    draft['approved_by'] = 'manual_user'
    draft['action'] = 'send_email'
    
    # Move to Needs_Action
    approved_file = Path("Vault/Needs_Action/email") / f"{draft_file.stem}_approved.json"
    with open(approved_file, 'w') as f:
        json.dump(draft, f, indent=2)
    
    # Remove from Pending_Approval
    draft_file.unlink()
    
    print(f"✅ Approved: {approved_file.name}")
else:
    print("❌ No draft found")
EOF

# Verify approval
ls -la Vault/Needs_Action/email/
```

#### Step 4: Run Local Executive (Simulate Local Online)

```bash
# Set Local mode
export AGENT_MODE=local

# Run Local Executive once
python Actions/local_executive.py --once

# Check Done folder
ls -la Vault/Done/
cat Vault/Done/demo_manual_*.json
```

**Expected:** Completed task in `Done/`

#### Step 5: Verify Final State

```bash
# Check all folders
echo "=== Needs_Action ==="
ls -la Vault/Needs_Action/email/

echo "=== Pending_Approval ==="
ls -la Vault/Pending_Approval/

echo "=== In_Progress ==="
ls -la Vault/In_Progress/cloud/
ls -la Vault/In_Progress/local/

echo "=== Done ==="
ls -la Vault/Done/
```

**Expected:**
- `Needs_Action/`: Empty ✅
- `Pending_Approval/`: Empty ✅
- `In_Progress/`: Empty ✅
- `Done/`: Has completed task ✅

---

## Simulating "Local Offline"

### Method 1: Environment Variable

```bash
# Cloud mode (Local offline)
export AGENT_MODE=cloud
python Actions/cloud_agent.py --once

# Local mode (Local online)
export AGENT_MODE=local
python Actions/local_executive.py --once
```

### Method 2: Separate Terminals

**Terminal 1 (Cloud VM):**
```bash
export AGENT_MODE=cloud
python Actions/cloud_agent.py  # Runs continuously
```

**Terminal 2 (Local Machine):**
```bash
# Wait a few minutes (simulate offline)
sleep 300

# Then start Local
export AGENT_MODE=local
python Actions/local_executive.py --once
```

### Method 3: Docker (Production Simulation)

**Cloud VM:**
```bash
docker-compose up -d cloud-agent
docker-compose logs -f cloud-agent
```

**Local Machine:**
```bash
# Wait for Cloud to process
sleep 60

# Then run Local
export AGENT_MODE=local
python Actions/local_executive.py --once
```

---

## Troubleshooting

### Issue: No draft created by Cloud

**Check:**
```bash
# Verify task file exists
ls -la Vault/Needs_Action/email/

# Check Cloud logs
export AGENT_MODE=cloud
python Actions/cloud_agent.py --once --verbose

# Verify action is allowed in Cloud mode
python -c "from config import PlatinumConfig; c = PlatinumConfig(); print(c.validate_action('draft_reply'))"
```

### Issue: Local doesn't execute

**Check:**
```bash
# Verify approved task exists
ls -la Vault/Needs_Action/email/

# Check Local logs
export AGENT_MODE=local
python Actions/local_executive.py --once --verbose

# Verify action is allowed in Local mode
python -c "from config import PlatinumConfig; import os; os.environ['AGENT_MODE']='local'; c = PlatinumConfig(); print(c.validate_action('send_email'))"
```

### Issue: File locking errors

**Solution:**
```bash
# Clean up any stuck locks
find Vault/In_Progress -name "*.json" -delete

# Restart demo
python demo_test.py
```

### Issue: Import errors

**Solution:**
```bash
# Ensure all __init__.py files exist
touch Platinum-Tier/__init__.py
touch Platinum-Tier/Actions/__init__.py

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Success Criteria

✅ **Demo is successful if:**

1. Email task created in `Needs_Action/email/`
2. Cloud Agent drafts reply → `Pending_Approval/`
3. User approves draft → `Needs_Action/email/*_approved.json`
4. Local Executive sends email → `Done/`
5. All intermediate folders are empty
6. No errors in logs
7. Task lifecycle is complete

---

## Next Steps After Successful Demo

1. **Test with Real Email Integration:**
   - Configure actual SMTP settings
   - Test with real Gmail/Outlook account
   - Verify email actually sends

2. **Test Git Synchronization:**
   - Set up GitHub repository
   - Test Cloud → Local sync
   - Test Local → Cloud sync
   - Verify conflict resolution

3. **Deploy to Cloud VM:**
   - Follow `GIT_SETUP.md` for deployment
   - Use Docker Compose for production
   - Set up systemd services
   - Monitor logs

4. **Add More Task Types:**
   - Social media posting
   - Odoo data extraction
   - Payment reconciliation
   - Weekly briefings

5. **Production Hardening:**
   - Add monitoring and alerts
   - Implement retry logic
   - Add health checks
   - Set up log aggregation

---

## Demo Video Script

If recording a demo video, follow this script:

1. **Introduction (30 seconds)**
   - "This is the Platinum Tier hybrid AI system"
   - "Cloud drafts, Local executes"
   - "Let's see it in action"

2. **Show Initial State (30 seconds)**
   - Show empty Vault folders
   - Show Cloud and Local agents ready

3. **Incoming Email (1 minute)**
   - Create email task
   - Show file in Needs_Action/
   - Explain: "Local is offline, Cloud will handle this"

4. **Cloud Processing (1 minute)**
   - Run Cloud Agent
   - Show draft in Pending_Approval/
   - Show draft content

5. **User Approval (1 minute)**
   - Review draft
   - Approve
   - Show approved task in Needs_Action/

6. **Local Execution (1 minute)**
   - "Local comes online"
   - Run Local Executive
   - Show task in Done/

7. **Verification (30 seconds)**
   - Show all folders empty except Done/
   - Show completed task
   - "Demo successful!"

8. **Conclusion (30 seconds)**
   - Recap the flow
   - Mention production deployment
   - Thank you

**Total Time:** ~6 minutes

---

**Created:** April 14, 2026  
**Version:** 1.0  
**Status:** Ready for Testing ✅
