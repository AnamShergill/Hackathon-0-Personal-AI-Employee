"""
Platinum Tier Configuration

Centralized configuration management for Cloud and Local modes.

Author: Platinum Tier
Version: 1.0
Date: 2026-04-13
"""

import os
from pathlib import Path
from typing import Dict, Optional
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load from Platinum-Tier/.env
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try parent directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, use system environment only
    pass


class AgentMode(Enum):
    """Agent operating mode."""
    CLOUD = "cloud"
    LOCAL = "local"


class PlatinumConfig:
    """
    Centralized configuration for Platinum Tier.
    
    Loads configuration from environment variables with sensible defaults.
    """
    
    def __init__(self):
        """Initialize configuration from environment."""
        
        # Agent Mode
        self.agent_mode = self._get_agent_mode()
        
        # Paths
        self.vault_path = Path(os.getenv('VAULT_PATH', './Vault'))
        self.log_path = Path(os.getenv('LOG_PATH', f'./Logs/{self.agent_mode.value}'))
        
        # Ensure directories exist
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # Scan Intervals
        if self.agent_mode == AgentMode.CLOUD:
            self.scan_interval = int(os.getenv('SCAN_INTERVAL', '30'))  # 30 seconds
        else:
            self.scan_interval = int(os.getenv('SCAN_INTERVAL', '300'))  # 5 minutes
        
        # Task Processing
        self.max_concurrent_tasks = int(os.getenv('MAX_CONCURRENT_TASKS', '5' if self.agent_mode == AgentMode.CLOUD else '3'))
        self.stale_claim_threshold = int(os.getenv('STALE_CLAIM_THRESHOLD', '30'))  # minutes
        
        # Health Monitoring
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '300' if self.agent_mode == AgentMode.CLOUD else '600'))
        
        # Sync Configuration
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '60' if self.agent_mode == AgentMode.CLOUD else '300'))
        self.git_repo_url = os.getenv('GIT_REPO_URL', '')
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Mode-specific configuration
        self.mode_config = self._get_mode_config()
    
    def _get_agent_mode(self) -> AgentMode:
        """
        Determine agent mode from environment.
        
        Priority:
        1. AGENT_MODE environment variable
        2. Auto-detect from SMTP credentials
        3. Default to CLOUD
        """
        mode_str = os.getenv('AGENT_MODE', '').lower()
        
        if mode_str == 'cloud':
            return AgentMode.CLOUD
        elif mode_str == 'local':
            return AgentMode.LOCAL
        else:
            # Auto-detect based on SMTP credentials
            if os.getenv('SMTP_USER') and os.getenv('SMTP_PASS'):
                return AgentMode.LOCAL
            else:
                return AgentMode.CLOUD
    
    def _get_mode_config(self) -> Dict:
        """Get mode-specific configuration."""
        if self.agent_mode == AgentMode.CLOUD:
            return {
                'zone': 'cloud',
                'mode': 'draft_only',
                'allowed_domains': ['email', 'social', 'odoo'],
                'forbidden_actions': ['send', 'post', 'execute', 'payment'],
                'allowed_actions': ['draft', 'analyze', 'extract', 'match', 'triage']
            }
        else:  # LOCAL
            return {
                'zone': 'local',
                'mode': 'execute_only',
                'allowed_domains': ['email', 'social', 'odoo'],
                'allowed_actions': ['send', 'post', 'execute', 'payment', 'approve'],
                'forbidden_actions': []  # Local can do everything
            }
    
    def is_action_allowed(self, action: str) -> bool:
        """
        Check if an action is allowed in current mode.
        
        Args:
            action: Action name (e.g., 'send', 'draft', 'execute')
        
        Returns:
            True if allowed, False if forbidden
        """
        if action in self.mode_config['forbidden_actions']:
            return False
        return True
    
    def validate_action(self, action: str) -> None:
        """
        Validate action is allowed, raise error if not.
        
        Args:
            action: Action name
        
        Raises:
            PermissionError: If action is forbidden in current mode
        """
        if not self.is_action_allowed(action):
            raise PermissionError(
                f"Action '{action}' is FORBIDDEN in {self.agent_mode.value.upper()} mode. "
                f"Forbidden actions: {self.mode_config['forbidden_actions']}"
            )
    
    def get_odoo_config(self) -> Dict:
        """Get Odoo configuration based on mode."""
        if self.agent_mode == AgentMode.CLOUD:
            # Cloud: Read-only access
            return {
                'url': os.getenv('ODOO_URL', ''),
                'username': os.getenv('ODOO_READONLY_USER', ''),
                'password': os.getenv('ODOO_READONLY_PASS', ''),
                'database': os.getenv('ODOO_DATABASE', ''),
                'readonly': True
            }
        else:
            # Local: Full access
            return {
                'url': os.getenv('ODOO_URL', ''),
                'username': os.getenv('ODOO_USERNAME', ''),
                'password': os.getenv('ODOO_PASSWORD', ''),
                'database': os.getenv('ODOO_DATABASE', ''),
                'readonly': False
            }
    
    def get_smtp_config(self) -> Optional[Dict]:
        """Get SMTP configuration (Local only)."""
        if self.agent_mode == AgentMode.LOCAL:
            return {
                'user': os.getenv('SMTP_USER', ''),
                'password': os.getenv('SMTP_PASS', ''),
                'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'port': int(os.getenv('SMTP_PORT', '587'))
            }
        else:
            # Cloud cannot access SMTP
            return None
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PlatinumConfig(\n"
            f"  mode={self.agent_mode.value},\n"
            f"  vault_path={self.vault_path},\n"
            f"  scan_interval={self.scan_interval}s,\n"
            f"  max_concurrent_tasks={self.max_concurrent_tasks}\n"
            f")"
        )


# Global configuration instance
config = PlatinumConfig()


# Convenience functions
def get_config() -> PlatinumConfig:
    """Get global configuration instance."""
    return config


def is_cloud_mode() -> bool:
    """Check if running in Cloud mode."""
    return config.agent_mode == AgentMode.CLOUD


def is_local_mode() -> bool:
    """Check if running in Local mode."""
    return config.agent_mode == AgentMode.LOCAL


def validate_action(action: str) -> None:
    """Validate action is allowed in current mode."""
    config.validate_action(action)


if __name__ == "__main__":
    # Test configuration
    print("="*60)
    print("Platinum Tier Configuration")
    print("="*60)
    print(config)
    print("\nMode Config:")
    for key, value in config.mode_config.items():
        print(f"  {key}: {value}")
    print("\nOdoo Config:")
    odoo = config.get_odoo_config()
    print(f"  URL: {odoo['url']}")
    print(f"  Username: {odoo['username']}")
    print(f"  Read-only: {odoo['readonly']}")
    print("\nSMTP Config:")
    smtp = config.get_smtp_config()
    if smtp:
        print(f"  User: {smtp['user']}")
        print(f"  Server: {smtp['server']}:{smtp['port']}")
    else:
        print("  Not available (Cloud mode)")
