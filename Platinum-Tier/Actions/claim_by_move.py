"""
Claim-by-Move Protocol Implementation

Atomic task claiming using filesystem operations to prevent duplicate processing
in the hybrid Cloud + Local architecture.

Author: Platinum Tier
Version: 1.0
Date: 2026-04-13
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
from datetime import datetime
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class ClaimByMove:
    """
    Implements atomic task claiming using filesystem move operations.
    
    The claim-by-move protocol ensures only one agent can claim and process
    a task, preventing duplicate processing in distributed systems.
    """
    
    def __init__(self, vault_path: str, agent_name: str):
        """
        Initialize claim manager.
        
        Args:
            vault_path: Path to Vault directory (e.g., "Platinum-Tier/Vault")
            agent_name: Name of this agent ("cloud" or "local")
        """
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name
        self.in_progress_path = self.vault_path / "In_Progress" / agent_name
        
        # Ensure directories exist
        self.in_progress_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ClaimByMove initialized for agent: {agent_name}")
    
    def claim_task(self, task_path: str) -> Tuple[bool, Optional[str]]:
        """
        Atomically claim a task by moving it to agent's In_Progress folder.
        
        This uses os.rename() which is atomic on the same filesystem.
        
        Args:
            task_path: Path to task file (e.g., "Vault/Needs_Action/email/task.md")
        
        Returns:
            (success: bool, claimed_path: Optional[str])
            - (True, path) if claim successful
            - (False, None) if already claimed
        
        Example:
            success, path = claim_manager.claim_task("Vault/Needs_Action/email/task.md")
            if success:
                process_task(path)
        """
        try:
            # 1. Validate task exists
            task_path = Path(task_path)
            if not task_path.exists():
                logger.warning(f"Task does not exist: {task_path}")
                return False, None
            
            # 2. Build target path
            task_filename = task_path.name
            target_path = self.in_progress_path / task_filename
            
            # 3. Atomic move (claim)
            # os.rename() is atomic on the same filesystem
            os.rename(str(task_path), str(target_path))
            
            # 4. Write claim metadata
            self._write_claim_metadata(target_path)
            
            # 5. Success
            import re
            clean_msg = re.sub(r'[^\x00-\x7F]+', '', f"Claimed by {self.agent_name}: {task_filename}")
            logger.info(clean_msg)
            return True, str(target_path)
            
        except FileNotFoundError:
            # Task was already moved by another agent
            import re
            clean_msg = re.sub(r'[^\x00-\x7F]+', '', f"Already claimed by another agent: {task_path.name}")
            logger.info(clean_msg)
            return False, None
            
        except Exception as e:
            # Unexpected error
            import re
            clean_msg = re.sub(r'[^\x00-\x7F]+', '', f"Claim error: {e}")
            logger.error(clean_msg)
            return False, None
    
    def release_task(self, task_path: str, reason: str = "Processing failed") -> bool:
        """
        Release a claimed task back to Needs_Action queue.
        
        Args:
            task_path: Path to claimed task (e.g., "Vault/In_Progress/cloud/task.md")
            reason: Reason for release
        
        Returns:
            True if released successfully, False otherwise
        
        Example:
            release_task("Vault/In_Progress/cloud/task.md", "Odoo connection failed")
        """
        try:
            task_path = Path(task_path)
            
            # 1. Determine original location
            task_filename = task_path.name
            
            # Extract domain from metadata or filename
            domain = self._extract_domain_from_task(task_path)
            
            # 2. Build target path
            target_path = self.vault_path / "Needs_Action" / domain / task_filename
            
            # 3. Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 4. Write release metadata
            self._write_release_metadata(task_path, reason)
            
            # 5. Move back to Needs_Action
            shutil.move(str(task_path), str(target_path))
            
            # 6. Log reason
            import re
            clean_msg = re.sub(r'[^\x00-\x7F]+', '', f"Released: {task_filename} - Reason: {reason}")
            logger.info(clean_msg)
            
            return True
            
        except Exception as e:
            import re
            clean_msg = re.sub(r'[^\x00-\x7F]+', '', f"Release error: {e}")
            logger.error(clean_msg)
            return False
    
    def complete_task(self, task_path: str, result: str) -> bool:
        """
        Mark task as complete and move to Done folder.
        
        Args:
            task_path: Path to claimed task (e.g., "Vault/In_Progress/local/task.md")
            result: Completion result message
        
        Returns:
            True if completed successfully, False otherwise
        
        Example:
            complete_task("Vault/In_Progress/local/email.md", "Email sent: msg-123")
        """
        try:
            task_path = Path(task_path)
            
            # 1. Build target path with timestamp
            task_filename = task_path.name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_filename = f"{timestamp}_{task_filename}"
            target_path = self.vault_path / "Done" / target_filename
            
            # 2. Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 3. Write completion metadata
            self._write_completion_metadata(task_path, result)
            
            # 4. Move to Done
            shutil.move(str(task_path), str(target_path))
            
            # 5. Log completion
            logger.info(f"✅ Completed: {task_filename} - Result: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Completion error: {e}")
            return False
    
    def detect_stale_claims(self, max_age_minutes: int = 30) -> list:
        """
        Detect and release stale claims (tasks stuck in In_Progress).
        
        Args:
            max_age_minutes: Maximum age before considering claim stale
        
        Returns:
            List of released task paths
        """
        released = []
        
        try:
            # Scan In_Progress directory
            for task_path in self.in_progress_path.glob("*.md"):
                # Check age
                age_minutes = self._get_task_age_minutes(task_path)
                
                if age_minutes > max_age_minutes:
                    logger.warning(f"Stale claim detected: {task_path.name} (age: {age_minutes} min)")
                    
                    # Release back to queue
                    if self.release_task(str(task_path), f"Stale claim (age: {age_minutes} min)"):
                        released.append(str(task_path))
            
            if released:
                logger.info(f"Released {len(released)} stale claims")
            
            return released
            
        except Exception as e:
            logger.error(f"❌ Stale claim detection error: {e}")
            return []
    
    def get_claimed_tasks(self) -> list:
        """
        Get list of tasks currently claimed by this agent.
        
        Returns:
            List of task file paths
        """
        try:
            return [str(p) for p in self.in_progress_path.glob("*.md")]
        except Exception as e:
            logger.error(f"❌ Error getting claimed tasks: {e}")
            return []
    
    def _write_claim_metadata(self, task_path: Path):
        """Write claim metadata to task file."""
        try:
            metadata = {
                'claimed_by': self.agent_name,
                'claimed_at': datetime.now().isoformat(),
                'claim_id': f"{self.agent_name}_{int(time.time())}"
            }
            
            # Handle JSON vs Markdown files differently
            if task_path.suffix == '.json':
                # For JSON files, update the JSON object
                import json
                with open(task_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['_claim_metadata'] = metadata
                
                with open(task_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                # For Markdown files, append metadata
                with open(task_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n---\n## Claim Metadata\n")
                    f.write(f"- **Claimed by:** {metadata['claimed_by']}\n")
                    f.write(f"- **Claimed at:** {metadata['claimed_at']}\n")
                    f.write(f"- **Claim ID:** {metadata['claim_id']}\n")
        
        except Exception as e:
            logger.error(f"Error writing claim metadata: {e}")
    
    def _write_release_metadata(self, task_path: Path, reason: str):
        """Write release metadata to task file."""
        try:
            retry_count = self._get_retry_count(task_path) + 1
            
            metadata = {
                'released_at': datetime.now().isoformat(),
                'release_reason': reason,
                'retry_count': retry_count
            }
            
            # Handle JSON vs Markdown files differently
            if task_path.suffix == '.json':
                # For JSON files, update the JSON object
                import json
                with open(task_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['_release_metadata'] = metadata
                
                with open(task_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                # For Markdown files, append metadata
                with open(task_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n---\n## Release Metadata\n")
                    f.write(f"- **Released at:** {metadata['released_at']}\n")
                    f.write(f"- **Reason:** {metadata['release_reason']}\n")
                    f.write(f"- **Retry count:** {metadata['retry_count']}\n")
        
        except Exception as e:
            logger.error(f"Error writing release metadata: {e}")
    
    def _write_completion_metadata(self, task_path: Path, result: str):
        """Write completion metadata to task file."""
        try:
            processing_time = self._calculate_processing_time(task_path)
            
            metadata = {
                'completed_at': datetime.now().isoformat(),
                'completed_by': self.agent_name,
                'result': result,
                'processing_time': processing_time
            }
            
            # Handle JSON vs Markdown files differently
            if task_path.suffix == '.json':
                # For JSON files, update the JSON object
                import json
                with open(task_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['_completion_metadata'] = metadata
                
                with open(task_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                # For Markdown files, append metadata
                with open(task_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n---\n## Completion Metadata\n")
                    f.write(f"- **Completed at:** {metadata['completed_at']}\n")
                    f.write(f"- **Completed by:** {metadata['completed_by']}\n")
                f.write(f"- **Result:** {metadata['result']}\n")
                f.write(f"- **Processing time:** {metadata['processing_time']} seconds\n")
        
        except Exception as e:
            logger.error(f"Error writing completion metadata: {e}")
    
    def _extract_domain_from_task(self, task_path: Path) -> str:
        """Extract domain from task file."""
        try:
            # Try to read domain from file content
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for domain in frontmatter
                if 'domain:' in content:
                    for line in content.split('\n'):
                        if line.strip().startswith('domain:'):
                            return line.split(':', 1)[1].strip()
            
            # Default to email if not found
            return 'email'
            
        except Exception as e:
            logger.error(f"Error extracting domain: {e}")
            return 'email'
    
    def _get_retry_count(self, task_path: Path) -> int:
        """Get retry count from task file."""
        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count release metadata sections
                return content.count('## Release Metadata')
        
        except Exception as e:
            logger.error(f"Error getting retry count: {e}")
            return 0
    
    def _get_task_age_minutes(self, task_path: Path) -> float:
        """Get task age in minutes."""
        try:
            # Get file modification time
            mtime = task_path.stat().st_mtime
            age_seconds = time.time() - mtime
            return age_seconds / 60.0
        
        except Exception as e:
            logger.error(f"Error getting task age: {e}")
            return 0.0
    
    def _calculate_processing_time(self, task_path: Path) -> float:
        """Calculate processing time from claim to completion."""
        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find claimed_at timestamp
                for line in content.split('\n'):
                    if 'Claimed at:' in line:
                        claimed_at_str = line.split('**', 2)[2].strip()
                        claimed_at = datetime.fromisoformat(claimed_at_str)
                        
                        # Calculate difference
                        now = datetime.now()
                        delta = now - claimed_at
                        return delta.total_seconds()
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating processing time: {e}")
            return 0.0


# Utility functions for external use

def claim_task(vault_path: str, agent_name: str, task_path: str) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to claim a task.
    
    Args:
        vault_path: Path to Vault directory
        agent_name: Name of agent ("cloud" or "local")
        task_path: Path to task file
    
    Returns:
        (success, claimed_path)
    """
    manager = ClaimByMove(vault_path, agent_name)
    return manager.claim_task(task_path)


def release_task(vault_path: str, agent_name: str, task_path: str, reason: str) -> bool:
    """
    Convenience function to release a task.
    
    Args:
        vault_path: Path to Vault directory
        agent_name: Name of agent ("cloud" or "local")
        task_path: Path to claimed task
        reason: Reason for release
    
    Returns:
        True if successful
    """
    manager = ClaimByMove(vault_path, agent_name)
    return manager.release_task(task_path, reason)


def complete_task(vault_path: str, agent_name: str, task_path: str, result: str) -> bool:
    """
    Convenience function to complete a task.
    
    Args:
        vault_path: Path to Vault directory
        agent_name: Name of agent ("cloud" or "local")
        task_path: Path to claimed task
        result: Completion result
    
    Returns:
        True if successful
    """
    manager = ClaimByMove(vault_path, agent_name)
    return manager.complete_task(task_path, result)


if __name__ == "__main__":
    # Test the claim-by-move protocol
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    vault_path = "Platinum-Tier/Vault"
    agent_name = "cloud"
    
    manager = ClaimByMove(vault_path, agent_name)
    
    print(f"\n✅ ClaimByMove initialized for agent: {agent_name}")
    print(f"📁 Vault path: {vault_path}")
    print(f"📂 In Progress path: {manager.in_progress_path}")
    
    # Show claimed tasks
    claimed = manager.get_claimed_tasks()
    print(f"\n📋 Currently claimed tasks: {len(claimed)}")
    for task in claimed:
        print(f"  - {task}")
    
    # Detect stale claims
    print(f"\n🔍 Checking for stale claims...")
    stale = manager.detect_stale_claims(max_age_minutes=30)
    if stale:
        print(f"⚠️ Released {len(stale)} stale claims")
    else:
        print(f"✅ No stale claims detected")
