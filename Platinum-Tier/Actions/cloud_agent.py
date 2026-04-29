"""
Cloud Agent - 24/7 Draft-Only Agent

Runs continuously on Cloud VM (Oracle Free Tier) to monitor for new tasks,
draft replies, and prepare actions for Local approval.

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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PlatinumConfig, AgentMode
from Actions.hybrid_orchestrator import HybridOrchestrator

# Configure logging
logger = logging.getLogger(__name__)


class CloudAgent:
    """
    Cloud Agent - 24/7 draft-only operation.
    
    Responsibilities:
    - Monitor Vault/Needs_Action/ continuously
    - Draft email replies
    - Draft social media posts
    - Extract Odoo data (read-only)
    - Generate weekly briefings
    - Create approval files in Vault/Pending_Approval/
    
    Restrictions:
    - NO final execution (send, post, payment)
    - NO access to secrets (SMTP, WhatsApp, banking)
    - Read-only Odoo access
    """
    
    def __init__(self):
        """Initialize Cloud Agent."""
        
        # Force Cloud mode
        os.environ['AGENT_MODE'] = 'cloud'
        
        # Load configuration
        self.config = PlatinumConfig()
        
        # Validate we're in Cloud mode
        if self.config.agent_mode != AgentMode.CLOUD:
            raise RuntimeError("CloudAgent must run in CLOUD mode")
        
        # Initialize orchestrator
        self.orchestrator = HybridOrchestrator(self.config)
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'tasks_processed': 0,
            'drafts_created': 0,
            'errors': 0
        }
        
        logger.info("☁️ Cloud Agent initialized")
        logger.info(f"📁 Vault: {self.config.vault_path}")
        logger.info(f"⏱️  Scan interval: {self.config.scan_interval}s")
    
    def run(self):
        """
        Run Cloud Agent in continuous loop.
        
        This is the main entry point for 24/7 operation.
        """
        logger.info("\n" + "="*60)
        logger.info("☁️ Starting Cloud Agent (24/7 Operation)")
        logger.info("="*60 + "\n")
        
        try:
            # Run orchestrator loop
            self.orchestrator.run_loop()
        
        except KeyboardInterrupt:
            logger.info("\n⏹️  Cloud Agent stopped by user")
            self._print_stats()
        
        except Exception as e:
            logger.error(f"❌ Cloud Agent fatal error: {e}")
            self._print_stats()
            raise
    
    def run_once(self):
        """
        Run one iteration (for testing).
        """
        logger.info("☁️ Running Cloud Agent (single iteration)")
        self.orchestrator.run_once()
        self._print_stats()
    
    def _print_stats(self):
        """Print agent statistics."""
        uptime = datetime.now() - self.stats['start_time']
        
        logger.info("\n" + "="*60)
        logger.info("📊 Cloud Agent Statistics")
        logger.info("="*60)
        logger.info(f"Uptime: {uptime}")
        logger.info(f"Tasks processed: {self.stats['tasks_processed']}")
        logger.info(f"Drafts created: {self.stats['drafts_created']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("="*60 + "\n")


def main():
    """Main entry point for Cloud Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Platinum Tier Cloud Agent (24/7 Draft-Only)')
    parser.add_argument('--once', action='store_true', help='Run once and exit (for testing)')
    parser.add_argument('--vault', help='Vault path (overrides VAULT_PATH env var)')
    
    args = parser.parse_args()
    
    # Override vault path if provided
    if args.vault:
        os.environ['VAULT_PATH'] = args.vault
    
    # Initialize and run Cloud Agent
    agent = CloudAgent()
    
    if args.once:
        agent.run_once()
    else:
        agent.run()


if __name__ == "__main__":
    main()
