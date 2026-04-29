"""
Local Executive - Execution-Only Agent

Runs periodically on Local machine to present drafts for HITL approval
and execute approved actions.

Author: Platinum Tier
Version: 1.0
Date: 2026-04-13
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PlatinumConfig, AgentMode
from Actions.hybrid_orchestrator import HybridOrchestrator

# Configure logging
logger = logging.getLogger(__name__)


class LocalExecutive:
    """
    Local Executive - Execution-only operation.
    
    Responsibilities:
    - Monitor Vault/Pending_Approval/ periodically
    - Present drafts to human for approval (HITL)
    - Execute approved actions (send, post, payment)
    - Update Dashboard.md
    - Merge updates from Cloud
    
    Permissions:
    - Full SMTP access (send emails)
    - Full social media access (post)
    - Full Odoo write access
    - WhatsApp session access
    - Banking/payment access
    """
    
    def __init__(self):
        """Initialize Local Executive."""
        
        # Force Local mode
        os.environ['AGENT_MODE'] = 'local'
        
        # Load configuration
        self.config = PlatinumConfig()
        
        # Validate we're in Local mode
        if self.config.agent_mode != AgentMode.LOCAL:
            raise RuntimeError("LocalExecutive must run in LOCAL mode")
        
        # Initialize orchestrator
        self.orchestrator = HybridOrchestrator(self.config)
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'tasks_processed': 0,
            'emails_sent': 0,
            'posts_published': 0,
            'payments_recorded': 0,
            'errors': 0
        }
        
        logger.info("🏠 Local Executive initialized")
        logger.info(f"📁 Vault: {self.config.vault_path}")
        logger.info(f"⏱️  Scan interval: {self.config.scan_interval}s")
    
    def run(self):
        """
        Run Local Executive in periodic loop.
        
        This is the main entry point for periodic operation.
        """
        logger.info("\n" + "="*60)
        logger.info("🏠 Starting Local Executive (Periodic Operation)")
        logger.info("="*60 + "\n")
        
        try:
            # Run orchestrator loop
            self.orchestrator.run_loop()
        
        except KeyboardInterrupt:
            logger.info("\n⏹️  Local Executive stopped by user")
            self._print_stats()
        
        except Exception as e:
            logger.error(f"❌ Local Executive fatal error: {e}")
            self._print_stats()
            raise
    
    def run_once(self):
        """
        Run one iteration (for testing or manual execution).
        """
        logger.info("🏠 Running Local Executive (single iteration)")
        self.orchestrator.run_once()
        self._print_stats()
    
    def present_for_approval(self) -> List[Dict]:
        """
        Present pending tasks for human approval.
        
        This is a placeholder for HITL approval interface.
        In production, this would show a UI or CLI prompt.
        
        Returns:
            List of approved tasks
        """
        # Scan Pending_Approval
        pending_path = self.config.vault_path / "Pending_Approval"
        pending_tasks = []
        
        for domain in ['email', 'social', 'odoo']:
            domain_path = pending_path / domain
            if domain_path.exists():
                pending_tasks.extend(domain_path.glob("*.md"))
        
        if not pending_tasks:
            logger.info("✅ No tasks pending approval")
            return []
        
        logger.info(f"\n📋 {len(pending_tasks)} tasks pending approval:")
        for i, task in enumerate(pending_tasks, 1):
            logger.info(f"  {i}. {task.name}")
        
        # TODO: Implement actual HITL approval interface
        # For now, just log
        logger.info("\n⚠️  HITL approval interface not yet implemented")
        logger.info("Tasks will be processed automatically in this version")
        
        return []
    
    def update_dashboard(self):
        """
        Update Dashboard.md with latest status.
        
        This is a placeholder for Dashboard update logic.
        """
        dashboard_path = self.config.vault_path.parent / "Dashboard.md"
        
        # TODO: Implement Dashboard update logic
        # For now, just log
        logger.info(f"📊 Dashboard update: {dashboard_path}")
    
    def _print_stats(self):
        """Print agent statistics."""
        uptime = datetime.now() - self.stats['start_time']
        
        logger.info("\n" + "="*60)
        logger.info("📊 Local Executive Statistics")
        logger.info("="*60)
        logger.info(f"Uptime: {uptime}")
        logger.info(f"Tasks processed: {self.stats['tasks_processed']}")
        logger.info(f"Emails sent: {self.stats['emails_sent']}")
        logger.info(f"Posts published: {self.stats['posts_published']}")
        logger.info(f"Payments recorded: {self.stats['payments_recorded']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("="*60 + "\n")


def main():
    """Main entry point for Local Executive."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Platinum Tier Local Executive (Execution-Only)')
    parser.add_argument('--once', action='store_true', help='Run once and exit (for testing)')
    parser.add_argument('--vault', help='Vault path (overrides VAULT_PATH env var)')
    parser.add_argument('--approve', action='store_true', help='Show approval interface')
    
    args = parser.parse_args()
    
    # Override vault path if provided
    if args.vault:
        os.environ['VAULT_PATH'] = args.vault
    
    # Initialize Local Executive
    executive = LocalExecutive()
    
    if args.approve:
        # Show approval interface
        executive.present_for_approval()
    elif args.once:
        # Run once
        executive.run_once()
    else:
        # Run continuous loop
        executive.run()


if __name__ == "__main__":
    main()
