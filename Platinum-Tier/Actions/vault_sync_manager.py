"""
Vault Sync Manager - Git-based Vault Synchronization

Manages bidirectional synchronization of the Vault folder between Cloud VM
and Local machine using Git.

Author: Platinum Tier
Version: 1.0
Date: 2026-04-13
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Tuple, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PlatinumConfig

# Configure logging
logger = logging.getLogger(__name__)


class VaultSyncManager:
    """
    Manages Git-based synchronization of the Vault folder.
    
    Features:
    - Automatic push/pull
    - Conflict resolution
    - Secret protection validation
    - Sync health monitoring
    """
    
    def __init__(self, config: Optional[PlatinumConfig] = None):
        """
        Initialize Vault Sync Manager.
        
        Args:
            config: Optional PlatinumConfig instance
        """
        self.config = config or PlatinumConfig()
        self.vault_path = self.config.vault_path
        self.git_repo_url = self.config.git_repo_url
        
        # Validate vault is a git repository
        self.git_dir = self.vault_path / '.git'
        
        logger.info(f"VaultSyncManager initialized")
        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Git repo: {self.git_repo_url or 'Not configured'}")
    
    def is_git_repo(self) -> bool:
        """
        Check if Vault is a Git repository.
        
        Returns:
            True if Git repository exists
        """
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def init_repo(self) -> Tuple[bool, str]:
        """
        Initialize Git repository in Vault.
        
        Returns:
            (success, message)
        """
        try:
            if self.is_git_repo():
                return True, "Git repository already initialized"
            
            # Initialize git
            result = subprocess.run(
                ['git', 'init'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Git repository initialized")
            return True, "Git repository initialized successfully"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Git init failed: {e.stderr}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Git init error: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def add_remote(self, remote_url: str, remote_name: str = 'origin') -> Tuple[bool, str]:
        """
        Add Git remote.
        
        Args:
            remote_url: Git repository URL
            remote_name: Remote name (default: origin)
        
        Returns:
            (success, message)
        """
        try:
            # Check if remote already exists
            result = subprocess.run(
                ['git', 'remote', 'get-url', remote_name],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Remote exists, update URL
                subprocess.run(
                    ['git', 'remote', 'set-url', remote_name, remote_url],
                    cwd=str(self.vault_path),
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"✅ Git remote '{remote_name}' updated")
                return True, f"Remote '{remote_name}' updated"
            else:
                # Add new remote
                subprocess.run(
                    ['git', 'remote', 'add', remote_name, remote_url],
                    cwd=str(self.vault_path),
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"✅ Git remote '{remote_name}' added")
                return True, f"Remote '{remote_name}' added"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Git remote failed: {e.stderr}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Git remote error: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def pull(self, remote: str = 'origin', branch: str = 'main') -> Tuple[bool, str]:
        """
        Pull changes from remote.
        
        Args:
            remote: Remote name
            branch: Branch name
        
        Returns:
            (success, message)
        """
        try:
            if not self.is_git_repo():
                return False, "Not a Git repository"
            
            # Fetch changes
            subprocess.run(
                ['git', 'fetch', remote, branch],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if pull needed
            local_commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            ).stdout.strip()
            
            remote_commit = subprocess.run(
                ['git', 'rev-parse', f'{remote}/{branch}'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            ).stdout.strip()
            
            if local_commit == remote_commit:
                logger.info("✅ Vault already up to date")
                return True, "Already up to date"
            
            # Pull with rebase
            result = subprocess.run(
                ['git', 'pull', '--rebase', remote, branch],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✅ Pulled from Git successfully")
            return True, "Pulled successfully"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Git pull failed: {e.stderr}"
            logger.error(f"❌ {error_msg}")
            
            # Check for conflicts
            if 'conflict' in e.stderr.lower():
                self._resolve_conflicts()
            
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Git pull error: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def push(self, message: Optional[str] = None, remote: str = 'origin', branch: str = 'main') -> Tuple[bool, str]:
        """
        Push changes to remote.
        
        Args:
            message: Commit message (auto-generated if None)
            remote: Remote name
            branch: Branch name
        
        Returns:
            (success, message)
        """
        try:
            if not self.is_git_repo():
                return False, "Not a Git repository"
            
            # Add all changes
            subprocess.run(
                ['git', 'add', '.'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if there are changes
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            )
            
            if not status.stdout.strip():
                logger.info("✅ No changes to push")
                return True, "No changes to push"
            
            # Commit changes
            if not message:
                message = f"{self.config.agent_mode.value.capitalize()} update: {datetime.now().isoformat()}"
            
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Push to remote
            subprocess.run(
                ['git', 'push', remote, branch],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"✅ Pushed to Git: {message}")
            return True, f"Pushed: {message}"
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Git push failed: {e.stderr}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Git push error: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def sync(self) -> Tuple[bool, str]:
        """
        Full sync: pull then push.
        
        Returns:
            (success, message)
        """
        # Pull first
        pull_success, pull_msg = self.pull()
        if not pull_success:
            return False, f"Pull failed: {pull_msg}"
        
        # Then push
        push_success, push_msg = self.push()
        if not push_success:
            return False, f"Push failed: {push_msg}"
        
        return True, "Sync completed successfully"
    
    def _resolve_conflicts(self):
        """
        Automatically resolve Git conflicts using smart rules.
        
        Rules:
        - In_Progress/cloud/ → Keep Cloud version (theirs)
        - In_Progress/local/ → Keep Local version (ours)
        - Pending_Approval/ → Keep Cloud version (theirs)
        - Done/ → Keep newer version (theirs)
        """
        try:
            # Get conflicted files
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=U'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            )
            
            conflicts = [f for f in result.stdout.strip().split('\n') if f]
            
            if not conflicts:
                return
            
            logger.warning(f"⚠️ Resolving {len(conflicts)} conflicts")
            
            for conflict_file in conflicts:
                if 'In_Progress/cloud/' in conflict_file:
                    # Cloud owns this, keep theirs
                    subprocess.run(
                        ['git', 'checkout', '--theirs', conflict_file],
                        cwd=str(self.vault_path),
                        check=True
                    )
                    logger.info(f"✅ Kept Cloud version: {conflict_file}")
                
                elif 'In_Progress/local/' in conflict_file:
                    # Local owns this, keep ours
                    subprocess.run(
                        ['git', 'checkout', '--ours', conflict_file],
                        cwd=str(self.vault_path),
                        check=True
                    )
                    logger.info(f"✅ Kept Local version: {conflict_file}")
                
                elif 'Pending_Approval/' in conflict_file:
                    # Cloud creates drafts, keep theirs
                    subprocess.run(
                        ['git', 'checkout', '--theirs', conflict_file],
                        cwd=str(self.vault_path),
                        check=True
                    )
                    logger.info(f"✅ Kept Cloud draft: {conflict_file}")
                
                else:
                    # Default: keep newer version (theirs)
                    subprocess.run(
                        ['git', 'checkout', '--theirs', conflict_file],
                        cwd=str(self.vault_path),
                        check=True
                    )
                    logger.info(f"✅ Kept newer version: {conflict_file}")
            
            # Stage resolved files
            subprocess.run(
                ['git', 'add', '.'],
                cwd=str(self.vault_path),
                check=True
            )
            
            # Continue rebase
            subprocess.run(
                ['git', 'rebase', '--continue'],
                cwd=str(self.vault_path),
                check=True
            )
            
            logger.info("✅ Conflicts resolved automatically")
        
        except Exception as e:
            logger.error(f"❌ Conflict resolution failed: {e}")
    
    def validate_gitignore(self) -> Tuple[bool, List[str]]:
        """
        Validate .gitignore protects secrets.
        
        Returns:
            (is_valid, missing_patterns)
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
        
        gitignore_path = self.vault_path / '.gitignore'
        
        try:
            if not gitignore_path.exists():
                logger.warning("⚠️ .gitignore not found")
                return False, required_patterns
            
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            missing = []
            for pattern in required_patterns:
                if pattern not in gitignore_content:
                    missing.append(pattern)
            
            if missing:
                logger.warning(f"⚠️ .gitignore missing patterns: {missing}")
                return False, missing
            
            logger.info("✅ .gitignore validated")
            return True, []
        
        except Exception as e:
            logger.error(f"❌ .gitignore validation error: {e}")
            return False, required_patterns
    
    def get_status(self) -> Dict:
        """
        Get Git status information.
        
        Returns:
            Status dictionary
        """
        try:
            if not self.is_git_repo():
                return {'error': 'Not a Git repository'}
            
            # Get current branch
            branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get last commit
            last_commit = subprocess.run(
                ['git', 'log', '-1', '--format=%H %s'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get uncommitted changes
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True
            ).stdout.strip()
            
            return {
                'branch': branch,
                'last_commit': last_commit,
                'uncommitted_changes': bool(status),
                'changes_count': len(status.split('\n')) if status else 0
            }
        
        except Exception as e:
            return {'error': str(e)}


def main():
    """Main entry point for Vault Sync Manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Platinum Tier Vault Sync Manager')
    parser.add_argument('action', choices=['init', 'pull', 'push', 'sync', 'status'], help='Sync action')
    parser.add_argument('--message', '-m', help='Commit message (for push)')
    parser.add_argument('--remote', default='origin', help='Git remote name')
    parser.add_argument('--branch', default='main', help='Git branch name')
    parser.add_argument('--url', help='Git repository URL (for init)')
    
    args = parser.parse_args()
    
    # Initialize sync manager
    sync_manager = VaultSyncManager()
    
    # Execute action
    if args.action == 'init':
        success, msg = sync_manager.init_repo()
        if success and args.url:
            success, msg = sync_manager.add_remote(args.url)
        print(msg)
    
    elif args.action == 'pull':
        success, msg = sync_manager.pull(args.remote, args.branch)
        print(msg)
    
    elif args.action == 'push':
        success, msg = sync_manager.push(args.message, args.remote, args.branch)
        print(msg)
    
    elif args.action == 'sync':
        success, msg = sync_manager.sync()
        print(msg)
    
    elif args.action == 'status':
        status = sync_manager.get_status()
        print("Git Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
