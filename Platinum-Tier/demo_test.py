"""
Platinum Tier - Minimum Viable Demo Test Script

Simulates the complete end-to-end flow:
1. Email arrives while Local is offline
2. Cloud detects and drafts reply
3. Draft placed in Pending_Approval/
4. Local comes online
5. User reviews and approves
6. Local executes send
7. Task moves to Done/

Author: Platinum Tier
Version: 1.0
Date: 2026-04-14
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import PlatinumConfig, AgentMode
from Actions.claim_by_move import ClaimByMove
from Actions.hybrid_orchestrator import HybridOrchestrator


class DemoTestRunner:
    """
    Runs the Platinum Tier minimum viable demo.
    """
    
    def __init__(self):
        """Initialize demo test runner."""
        self.vault_path = Path(__file__).parent / "Vault"
        self.test_email_id = f"demo_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = []
        
        print("=" * 80)
        print("PLATINUM TIER - MINIMUM VIABLE DEMO")
        print("=" * 80)
        print()
    
    def log_step(self, step: str, status: str, details: str = ""):
        """Log a test step."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            'timestamp': timestamp,
            'step': step,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        print(f"[{timestamp}] {status_icon} {step}")
        if details:
            print(f"           {details}")
        print()
    
    def setup_test_environment(self):
        """Set up clean test environment."""
        self.log_step("Setup", "⏳", "Preparing test environment...")
        
        try:
            # Ensure Vault directories exist
            needs_action = self.vault_path / "Needs_Action" / "email"
            pending_approval = self.vault_path / "Pending_Approval"
            in_progress_cloud = self.vault_path / "In_Progress" / "cloud"
            in_progress_local = self.vault_path / "In_Progress" / "local"
            done = self.vault_path / "Done"
            
            for directory in [needs_action, pending_approval, in_progress_cloud, 
                            in_progress_local, done]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Clean up any existing test files
            for test_file in self.vault_path.rglob(f"*{self.test_email_id}*"):
                test_file.unlink()
            
            self.log_step("Setup", "PASS", "Test environment ready")
            return True
        
        except Exception as e:
            self.log_step("Setup", "FAIL", f"Error: {e}")
            return False
    
    def simulate_incoming_email(self):
        """Simulate an incoming email that needs a reply."""
        self.log_step("Step 1", "⏳", "Simulating incoming email...")
        
        try:
            # Create test email task
            email_task = {
                'task_id': self.test_email_id,
                'type': 'email',
                'action': 'draft_reply',
                'priority': 'normal',
                'created_at': datetime.now().isoformat(),
                'email': {
                    'from': 'customer@example.com',
                    'to': 'ceo@company.com',
                    'subject': 'Question about your services',
                    'body': 'Hi, I would like to know more about your consulting services. Can you provide pricing and availability?',
                    'received_at': datetime.now().isoformat()
                },
                'instructions': 'Draft a professional reply with pricing information'
            }
            
            # Write to Needs_Action/email/
            task_file = self.vault_path / "Needs_Action" / "email" / f"{self.test_email_id}.json"
            with open(task_file, 'w') as f:
                json.dump(email_task, f, indent=2)
            
            self.log_step("Step 1", "PASS", f"Email task created: {task_file.name}")
            return True
        
        except Exception as e:
            self.log_step("Step 1", "FAIL", f"Error: {e}")
            return False
    
    def run_cloud_agent(self):
        """Simulate Cloud Agent processing (Local is offline)."""
        self.log_step("Step 2", "⏳", "Cloud Agent processing (Local offline)...")
        
        try:
            # Initialize Cloud mode orchestrator
            os.environ['AGENT_MODE'] = 'cloud'
            config = PlatinumConfig()
            orchestrator = HybridOrchestrator(config)
            
            # Process tasks
            print("           [CLOUD] Scanning for tasks...")
            orchestrator.process_tasks()
            
            # Check if draft was created
            time.sleep(1)  # Give it a moment
            
            # Look in Pending_Approval/email/ subdirectory
            pending_files = list((self.vault_path / "Pending_Approval" / "email").glob(f"*{self.test_email_id}*"))
            
            if pending_files:
                self.log_step("Step 2", "PASS", f"Draft created: {pending_files[0].name}")
                return True
            else:
                self.log_step("Step 2", "FAIL", "No draft found in Pending_Approval/email/")
                return False
        
        except Exception as e:
            self.log_step("Step 2", "FAIL", f"Error: {e}")
            return False
    
    def simulate_user_approval(self):
        """Simulate user reviewing and approving the draft."""
        self.log_step("Step 3", "⏳", "User reviewing draft...")
        
        try:
            # Find the draft in Pending_Approval/email/
            pending_files = list((self.vault_path / "Pending_Approval" / "email").glob(f"*{self.test_email_id}*"))
            
            if not pending_files:
                self.log_step("Step 3", "FAIL", "No draft found to approve")
                return False
            
            draft_file = pending_files[0]
            
            # Read draft
            with open(draft_file, 'r') as f:
                draft = json.load(f)
            
            print(f"           📧 Draft Preview:")
            print(f"           To: {draft.get('email', {}).get('to', 'N/A')}")
            print(f"           Subject: {draft.get('email', {}).get('subject', 'N/A')}")
            print(f"           Body: {draft.get('email', {}).get('body', 'N/A')[:100]}...")
            print()
            
            # Simulate approval by adding approval metadata
            draft['approved_at'] = datetime.now().isoformat()
            draft['approved_by'] = 'demo_user'
            draft['action'] = 'send_email'  # Change action to send
            
            # Update the draft file in place (keep in Pending_Approval for Local to find)
            with open(draft_file, 'w') as f:
                json.dump(draft, f, indent=2)
            
            self.log_step("Step 3", "PASS", "Draft approved and ready for execution")
            return True
        
        except Exception as e:
            self.log_step("Step 3", "FAIL", f"Error: {e}")
            return False
    
    def run_local_executive(self):
        """Simulate Local Executive coming online and executing."""
        self.log_step("Step 4", "⏳", "Local Executive coming online...")
        
        try:
            # Initialize Local mode orchestrator
            os.environ['AGENT_MODE'] = 'local'
            config = PlatinumConfig()
            orchestrator = HybridOrchestrator(config)
            
            # Process tasks
            print("           [LOCAL] Scanning for approved tasks...")
            orchestrator.process_tasks()
            
            # Check if task was executed and moved to Done
            time.sleep(1)
            
            done_files = list((self.vault_path / "Done").glob(f"*{self.test_email_id}*"))
            
            if done_files:
                self.log_step("Step 4", "PASS", f"Email sent and moved to Done: {done_files[0].name}")
                return True
            else:
                self.log_step("Step 4", "FAIL", "Task not found in Done/")
                return False
        
        except Exception as e:
            self.log_step("Step 4", "FAIL", f"Error: {e}")
            return False
    
    def verify_final_state(self):
        """Verify the final state of the system."""
        self.log_step("Verification", "⏳", "Verifying final state...")
        
        try:
            # Check Needs_Action is empty
            needs_action_files = list((self.vault_path / "Needs_Action" / "email").glob(f"*{self.test_email_id}*"))
            
            # Check Pending_Approval is empty
            pending_files = list((self.vault_path / "Pending_Approval" / "email").glob(f"*{self.test_email_id}*"))
            
            # Check In_Progress is empty
            in_progress_files = list((self.vault_path / "In_Progress").rglob(f"*{self.test_email_id}*"))
            
            # Check Done has the completed task
            done_files = list((self.vault_path / "Done").glob(f"*{self.test_email_id}*"))
            
            issues = []
            if needs_action_files:
                issues.append(f"Needs_Action not empty: {len(needs_action_files)} files")
            if pending_files:
                issues.append(f"Pending_Approval not empty: {len(pending_files)} files")
            if in_progress_files:
                issues.append(f"In_Progress not empty: {len(in_progress_files)} files")
            if not done_files:
                issues.append("Done/ is empty - task not completed")
            
            if issues:
                self.log_step("Verification", "FAIL", "; ".join(issues))
                return False
            else:
                self.log_step("Verification", "PASS", "All tasks completed and archived correctly")
                return True
        
        except Exception as e:
            self.log_step("Verification", "FAIL", f"Error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = passed + failed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        print()
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED - PLATINUM TIER DEMO SUCCESSFUL!")
        else:
            print("⚠️ SOME TESTS FAILED - REVIEW LOGS ABOVE")
        
        print()
        print("=" * 80)
    
    def run_full_demo(self):
        """Run the complete demo flow."""
        print("Starting Platinum Tier Minimum Viable Demo...")
        print()
        
        # Step 0: Setup
        if not self.setup_test_environment():
            self.print_summary()
            return False
        
        # Step 1: Incoming email
        if not self.simulate_incoming_email():
            self.print_summary()
            return False
        
        time.sleep(1)
        
        # Step 2: Cloud processes (Local offline)
        if not self.run_cloud_agent():
            self.print_summary()
            return False
        
        time.sleep(2)
        
        # Step 3: User approves
        if not self.simulate_user_approval():
            self.print_summary()
            return False
        
        time.sleep(1)
        
        # Step 4: Local executes
        if not self.run_local_executive():
            self.print_summary()
            return False
        
        time.sleep(1)
        
        # Step 5: Verify
        if not self.verify_final_state():
            self.print_summary()
            return False
        
        # Print summary
        self.print_summary()
        
        return True


def main():
    """Main entry point."""
    demo = DemoTestRunner()
    success = demo.run_full_demo()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
