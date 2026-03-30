"""
Approved Watcher - HITL Workflow Automation
Monitors Approved/ folder for human-approved content and triggers appropriate actions.
- LinkedIn posts → linkedin_poster.py
- Email replies → (future: MCP Gmail send)
- WhatsApp replies → (future: MCP WhatsApp send)
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import sys

from Watchers.base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovedWatcher(BaseWatcher):
    """
    Watcher that monitors Approved/ folder for human-approved content
    and triggers appropriate posting/sending actions.
    """

    def __init__(self, interval: int = 30):
        """
        Initialize Approved watcher.
        
        Args:
            interval: Polling interval in seconds (default: 30)
        """
        super().__init__("Approved Watcher", interval)
        self.approved_dir = Path("Approved")
        self.approved_dir.mkdir(exist_ok=True)
        
        self.processed_files = set()
        self._load_processed_files()
        
        logger.info(f"Initializing {self.name} with {interval}s interval")

    def _load_processed_files(self):
        """Load previously processed file names"""
        processed_file = Path("Logs") / 'approved_processed.txt'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_files = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.processed_files)} processed file records")

    def _save_processed_file(self, filename: str):
        """Save processed file name to tracking file"""
        self.processed_files.add(filename)
        processed_file = Path("Logs") / 'approved_processed.txt'
        with open(processed_file, 'a') as f:
            f.write(f"{filename}\n")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new approved files in Approved/ folder.
        
        Returns:
            List of approved file dictionaries
        """
        approved_items = []
        
        try:
            # Get all .md files in Approved/
            files = list(self.approved_dir.glob("*.md"))
            
            for file_path in files:
                filename = file_path.name
                
                # Skip if already processed
                if filename in self.processed_files:
                    continue
                
                # Determine type and action
                file_type = self._determine_file_type(file_path)
                
                if file_type:
                    approved_items.append({
                        'path': str(file_path),
                        'filename': filename,
                        'type': file_type,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"New approved item: {filename} (type: {file_type})")
            
        except Exception as e:
            logger.error(f"Error checking for approved items: {e}")
        
        return approved_items

    def _determine_file_type(self, file_path: Path) -> str:
        """
        Determine the type of approved file based on filename and content.
        
        Returns:
            File type: 'linkedin_post', 'email_send', 'email_reply', 'whatsapp_reply', or None
        """
        filename = file_path.name.lower()
        
        # Check filename patterns first
        if 'linkedin' in filename:
            return 'linkedin_post'
        elif filename.startswith('email_send_') or filename.startswith('email_'):
            # Check if it's a send action (not just a reply draft)
            return 'email_send'
        elif 'email' in filename and 'reply' in filename:
            return 'email_reply'
        elif 'whatsapp' in filename and 'reply' in filename:
            return 'whatsapp_reply'
        
        # Check content if filename is ambiguous
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Check for email send indicators
            # Look for "action: send_email" or presence of "to:" and "subject:" near top
            if 'action: send_email' in content or 'action:send_email' in content:
                return 'email_send'
            
            # Check if file has email headers (to: and subject: in first 500 chars)
            content_start = content[:500]
            if 'to:' in content_start and 'subject:' in content_start:
                return 'email_send'
            
            # Check frontmatter for type
            if 'type: "linkedin_post"' in content or "type: 'linkedin_post'" in content:
                return 'linkedin_post'
            elif 'type: "email_send"' in content or "type: 'email_send'" in content:
                return 'email_send'
            elif 'type: "email_reply"' in content or 'type: "email_reply_draft"' in content:
                return 'email_reply'
            elif 'type: "whatsapp_reply"' in content or 'type: "whatsapp_reply_draft"' in content:
                return 'whatsapp_reply'
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
        
        return None

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process an approved item by triggering the appropriate action.
        
        Args:
            event: Approved item event dictionary
            
        Returns:
            True if processing was successful, False otherwise
        """
        file_path = event['path']
        file_type = event['type']
        filename = event['filename']
        
        logger.info(f"Processing approved {file_type}: {filename}")
        
        try:
            if file_type == 'linkedin_post':
                success = self._post_to_linkedin(file_path)
            elif file_type == 'email_send':
                success = self._send_email(file_path)
            elif file_type == 'email_reply':
                success = self._send_email_reply(file_path)
            elif file_type == 'whatsapp_reply':
                success = self._send_whatsapp_reply(file_path)
            else:
                logger.warning(f"Unknown file type: {file_type}")
                success = False
            
            if success:
                self._save_processed_file(filename)
                logger.info(f"✅ Successfully processed: {filename}")
            else:
                logger.error(f"❌ Failed to process: {filename}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return False

    def _post_to_linkedin(self, file_path: str) -> bool:
        """
        Post approved content to LinkedIn using linkedin_poster.py
        """
        logger.info(f"Posting to LinkedIn: {file_path}")
        
        try:
            # Call linkedin_poster.py with the file path
            result = subprocess.run(
                [sys.executable, 'Watchers/linkedin_poster.py', file_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ LinkedIn post successful")
                return True
            else:
                logger.error(f"LinkedIn post failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("LinkedIn posting timeout")
            return False
        except Exception as e:
            logger.error(f"Error calling linkedin_poster: {e}")
            return False

    def _send_email(self, file_path: str) -> bool:
        """
        Send approved email using actions/email_sender.py
        
        Args:
            file_path: Path to approved email file
            
        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"[EMAIL_SENDER] Detected send action in {file_path}")
        
        try:
            # Call email_sender.py with the file path
            result = subprocess.run(
                [sys.executable, 'actions/email_sender.py', '--file', file_path],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            logger.info(f"[EMAIL_SENDER] ✅ Email sent successfully")
            logger.info(f"[EMAIL_SENDER] Output: {result.stdout}")
            
            # Note: email_sender.py moves the file to Approved/Done/ on success
            # So we don't need to do anything else here
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"[EMAIL_SENDER] ❌ Email sending failed with exit code {e.returncode}")
            logger.error(f"[EMAIL_SENDER] Error output: {e.stderr}")
            if e.stdout:
                logger.error(f"[EMAIL_SENDER] Stdout: {e.stdout}")
            
            # email_sender.py should have moved the file to Needs_Action/ on failure
            # and appended error details to the file
            return False
            
        except subprocess.TimeoutExpired:
            logger.error(f"[EMAIL_SENDER] ❌ Email sending timeout (>60s)")
            return False
            
        except Exception as e:
            logger.error(f"[EMAIL_SENDER] ❌ Error calling email_sender.py: {e}")
            return False

    def _send_email_reply(self, file_path: str) -> bool:
        """
        Send approved email reply (legacy - redirects to _send_email)
        """
        logger.info(f"Email reply approved: {file_path}")
        # Redirect to the new email sender
        return self._send_email(file_path)

    def _send_whatsapp_reply(self, file_path: str) -> bool:
        """
        Send approved WhatsApp reply (placeholder for MCP WhatsApp integration)
        """
        logger.info(f"WhatsApp reply approved: {file_path}")
        logger.warning("⚠️  WhatsApp sending not yet implemented (requires MCP WhatsApp server)")
        logger.info("   For now: File will remain in Approved/ for manual sending")
        
        # TODO: Implement MCP WhatsApp send
        # For now, just log and leave in Approved/
        return False

    def run_once(self) -> int:
        """
        Run one cycle of checking and processing approved items.
        
        Returns:
            Number of items processed
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"{self.name} running check at {current_time}...")
        
        try:
            events = self.check_for_updates()
            logger.info(f"{self.name} found {len(events)} new approved items")
            
            processed_count = 0
            for event in events:
                if self.process_event(event):
                    processed_count += 1
            
            self.last_run = time.time()
            logger.info(f"{self.name} completed cycle, processed {processed_count} items")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error in {self.name} run cycle: {e}")
            return 0


def main():
    """
    Main entry point for Approved watcher.
    Run this script to start monitoring Approved/ folder.
    """
    logger.info("=" * 80)
    logger.info("Approved Watcher - HITL Workflow Automation")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Monitoring Approved/ folder for human-approved content...")
    logger.info("Supported actions:")
    logger.info("  - LinkedIn posts → linkedin_poster.py")
    logger.info("  - Email sending → actions/email_sender.py (Gold Tier)")
    logger.info("  - WhatsApp replies → (future: MCP WhatsApp)")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)
    logger.info("")
    
    watcher = None
    try:
        # Create watcher (check every 30 seconds)
        watcher = ApprovedWatcher(interval=30)
        
        # Run forever
        watcher.run_forever()
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 80)
        logger.info("Approved Watcher stopped by user")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if watcher:
            watcher.stop()


if __name__ == "__main__":
    main()
