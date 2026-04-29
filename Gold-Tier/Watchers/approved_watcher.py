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
import re
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
            File type: 'linkedin_post', 'facebook_post', 'email_send', 'email_reply', 'whatsapp_reply', 'odoo_action', 'odoo_record_payment', or None
        """
        filename = file_path.name.lower()
        
        # Check filename patterns first
        if 'linkedin' in filename:
            return 'linkedin_post'
        elif 'facebook' in filename:
            return 'facebook_post'
        elif 'odoo_payment' in filename or 'payment' in filename:
            return 'odoo_record_payment'
        elif 'odoo' in filename:
            return 'odoo_action'
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
            
            # Check for payment recording
            if 'type: odoo_record_payment' in content or 'type: "odoo_record_payment"' in content:
                return 'odoo_record_payment'
            
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
            elif 'type: facebook_post' in content or 'type: "facebook_post"' in content or "type: 'facebook_post'" in content:
                return 'facebook_post'
            elif 'type: odoo_action' in content or 'type: "odoo_action"' in content or "type: 'odoo_action'" in content:
                return 'odoo_action'
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
            elif file_type == 'facebook_post':
                success = self._post_to_facebook(file_path)
            elif file_type == 'odoo_record_payment':
                success = self._record_payment_in_odoo(file_path)
            elif file_type == 'odoo_action':
                success = self._execute_odoo_action(file_path)
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

    def _post_to_facebook(self, file_path: str) -> bool:
        """
        Post approved content to Facebook using actions/facebook_poster.py
        """
        logger.info(f"[FACEBOOK] Posting to Facebook: {file_path}")
        
        try:
            # Call facebook_poster.py with the file path
            result = subprocess.run(
                [sys.executable, 'actions/facebook_poster.py', '--file', file_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Facebook post successful")
                return True
            else:
                logger.error(f"Facebook post failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Facebook posting timeout")
            return False
        except Exception as e:
            logger.error(f"Error calling facebook_poster: {e}")
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

    def _execute_odoo_action(self, file_path: str) -> bool:
        """
        Execute approved Odoo action using actions/odoo_rpc.py
        
        Args:
            file_path: Path to approved Odoo action file
            
        Returns:
            True if action executed successfully, False otherwise
        """
        logger.info(f"[ODOO] Executing Odoo action: {file_path}")
        
        try:
            # Parse file to extract action type and parameters
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract action from content
            action = None
            if 'action: create_partner' in content.lower():
                action = 'create_partner'
            elif 'action: create_invoice' in content.lower():
                action = 'create_invoice_from_data'
            elif 'action: query_invoices' in content.lower() or 'action: unpaid_invoices' in content.lower():
                action = 'unpaid_invoices'
            elif 'action: list_partners' in content.lower():
                action = 'list_partners'
            
            if not action:
                logger.error(f"[ODOO] Could not determine action type from file")
                return False
            
            # For create_invoice_from_data, parse structured data
            if action == 'create_invoice_from_data':
                import re
                import json
                
                # Extract partner info
                partner_name = None
                partner_email = None
                partner_phone = None
                line_items = []
                
                # Simple regex extraction (in production, use proper parser)
                name_match = re.search(r'Name:\s*(.+)', content)
                if name_match:
                    partner_name = name_match.group(1).strip()
                
                email_match = re.search(r'Email:\s*([^\s]+@[^\s]+)', content)
                if email_match:
                    partner_email = email_match.group(1).strip()
                
                phone_match = re.search(r'Phone:\s*(\+?[\d\-\(\)\s]+)', content)
                if phone_match:
                    partner_phone = phone_match.group(1).strip()
                
                # Extract line items
                line_pattern = r'(\d+)\.\s*(.+?):\s*(\d+(?:\.\d+)?)\s*(?:hours?|x)?\s*\$?(\d+(?:\.\d+)?)\s*=\s*\$?(\d+(?:\.\d+)?)'
                for match in re.finditer(line_pattern, content):
                    description = match.group(2).strip()
                    quantity = float(match.group(3))
                    price_unit = float(match.group(4))
                    line_items.append({
                        'description': description,
                        'quantity': quantity,
                        'price_unit': price_unit
                    })
                
                # If no structured line items, try to extract total amount
                if not line_items:
                    amount_match = re.search(r'(?:Total Amount|Amount):\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', content)
                    if amount_match:
                        amount_str = amount_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        line_items.append({
                            'description': 'Service',
                            'quantity': 1,
                            'price_unit': amount
                        })
                
                if not partner_name or not line_items:
                    logger.error(f"[ODOO] Missing required data: partner_name={partner_name}, line_items={len(line_items)}")
                    self._update_file_with_error(file_path, "Missing required data for invoice creation")
                    return False
                
                # Prepare data structure
                data = {
                    'partner_name': partner_name,
                    'partner_email': partner_email,
                    'partner_phone': partner_phone,
                    'line_items': line_items,
                    'is_company': True
                }
                
                # Call RPC with JSON data
                data_json = json.dumps(data)
                result = subprocess.run(
                    [sys.executable, 'actions/odoo_rpc.py', '--action', 'create_invoice_from_file', '--data', data_json, '--file', file_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=True
                )
                
                logger.info(f"[ODOO] ✅ Invoice created successfully")
                logger.info(f"[ODOO] Output: {result.stdout}")
                
                # Update file with result
                self._update_file_with_success(file_path, result.stdout)
                
                # Move to Done folder
                self._move_to_done(file_path)
                return True
            
            else:
                # For simple actions (list, query), just execute
                result = subprocess.run(
                    [sys.executable, 'actions/odoo_rpc.py', '--action', action],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=True
                )
                
                logger.info(f"[ODOO] ✅ Action executed successfully")
                logger.info(f"[ODOO] Output: {result.stdout}")
                
                # Update file with result
                self._update_file_with_success(file_path, result.stdout)
                
                # Move to Done folder
                self._move_to_done(file_path)
                return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"[ODOO] ❌ Action failed with exit code {e.returncode}")
            logger.error(f"[ODOO] Error output: {e.stderr}")
            
            # Update file with error
            self._update_file_with_error(file_path, e.stderr)
            
            # Move to Needs_Action for review
            self._move_to_needs_action(file_path)
            return False
            
        except subprocess.TimeoutExpired:
            logger.error(f"[ODOO] ❌ Action timeout (>60s)")
            self._update_file_with_error(file_path, "Timeout: Operation took longer than 60 seconds")
            return False
            
        except Exception as e:
            logger.error(f"[ODOO] ❌ Error executing action: {e}")
            self._update_file_with_error(file_path, str(e))
            return False
    
    def _update_file_with_success(self, file_path: str, output: str):
        """Update file with successful execution result"""
        timestamp = datetime.now().isoformat()
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n---\n\n**Execution Result**\n\n")
            f.write(f"status: completed\n")
            f.write(f"executed_at: {timestamp}\n\n")
            f.write(f"```\n{output}\n```\n")
    
    def _update_file_with_error(self, file_path: str, error: str):
        """Update file with error information"""
        timestamp = datetime.now().isoformat()
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n---\n\n**Execution Failed**\n\n")
            f.write(f"status: failed\n")
            f.write(f"attempted_at: {timestamp}\n")
            f.write(f"error: {error}\n")
    
    def _move_to_done(self, file_path: str):
        """Move file to Done folder"""
        done_dir = Path("Approved") / "Done"
        done_dir.mkdir(exist_ok=True)
        done_path = done_dir / Path(file_path).name
        Path(file_path).rename(done_path)
        logger.info(f"[ODOO] Moved to Done: {done_path}")
    
    def _move_to_needs_action(self, file_path: str):
        """Move file to Needs_Action for review"""
        needs_action_dir = Path("Needs_Action")
        needs_action_dir.mkdir(exist_ok=True)
        needs_action_path = needs_action_dir / Path(file_path).name
        Path(file_path).rename(needs_action_path)
        logger.info(f"[ODOO] Moved to Needs_Action: {needs_action_path}")
    
    def _record_payment_in_odoo(self, file_path: str) -> bool:
        """
        Record payment in Odoo from approved payment action file.
        
        Args:
            file_path: Path to approved payment action file
            
        Returns:
            True if payment recorded successfully
        """
        logger.info(f"[PAYMENT] Recording payment from: {file_path}")
        
        try:
            # Parse file to extract payment details
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract invoice_id
            invoice_id = None
            invoice_id_match = re.search(r'\*\*Invoice ID:\*\*\s*(\d+)', content)
            if invoice_id_match:
                invoice_id = int(invoice_id_match.group(1))
            else:
                # Check for manually entered invoice_id
                manual_match = re.search(r'invoice_id:\s*(\d+)', content)
                if manual_match:
                    invoice_id = int(manual_match.group(1))
            
            if not invoice_id:
                logger.error("[PAYMENT] No invoice_id found in action file")
                self._update_file_with_error(file_path, "Missing invoice_id - cannot proceed")
                return False
            
            # Extract payment amount
            amount_match = re.search(r'\*\*Amount:\*\*\s*\$([0-9,]+\.?\d*)', content)
            if not amount_match:
                logger.error("[PAYMENT] No payment amount found")
                self._update_file_with_error(file_path, "Missing payment amount")
                return False
            
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Extract payment date
            date_match = re.search(r'\*\*Payment Date:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
            payment_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
            
            # Extract reference
            ref_match = re.search(r'\*\*(?:Reference|Transaction ID):\*\*\s*(.+)', content)
            reference = ref_match.group(1).strip() if ref_match else None
            
            # Extract payment method
            method_match = re.search(r'\*\*Payment Method:\*\*\s*(\w+)', content)
            payment_method = method_match.group(1) if method_match else 'manual'
            
            logger.info(f"[PAYMENT] Recording ${amount} for invoice ID {invoice_id}")
            
            # Call Odoo RPC to record payment
            result = subprocess.run(
                [
                    sys.executable, 'actions/odoo_rpc.py',
                    '--action', 'record_payment',
                    '--invoice-id', str(invoice_id),
                    '--amount', str(amount),
                    '--payment-date', payment_date,
                    '--reference', reference or f'Payment for invoice {invoice_id}'
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            logger.info(f"[PAYMENT] ✅ Payment recorded successfully")
            logger.info(f"[PAYMENT] Output: {result.stdout}")
            
            # Update file with success
            self._update_file_with_success(file_path, result.stdout)
            
            # Move to Done
            self._move_to_done(file_path)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"[PAYMENT] ❌ Payment recording failed with exit code {e.returncode}")
            logger.error(f"[PAYMENT] Error output: {e.stderr}")
            
            # Update file with error
            self._update_file_with_error(file_path, e.stderr)
            
            # Move to Needs_Action for review
            self._move_to_needs_action(file_path)
            return False
            
        except subprocess.TimeoutExpired:
            logger.error(f"[PAYMENT] ❌ Payment recording timeout (>60s)")
            self._update_file_with_error(file_path, "Timeout: Operation took longer than 60 seconds")
            return False
            
        except Exception as e:
            logger.error(f"[PAYMENT] ❌ Error recording payment: {e}")
            self._update_file_with_error(file_path, str(e))
            return False

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
