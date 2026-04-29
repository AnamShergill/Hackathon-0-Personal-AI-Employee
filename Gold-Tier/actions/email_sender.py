#!/usr/bin/env python3
"""
Email Sender Action - Gold Tier Phase 1

Standalone script that sends emails from approved .md files.
Reads email metadata from markdown frontmatter, sends via SMTP,
and updates the file with send status.

Features:
- Retry logic with exponential backoff (3 attempts)
- HTML email support (auto-detect)
- Professional signature injection
- Graceful error handling
- Comprehensive logging

Usage:
    python actions/email_sender.py --file Approved/email_send_20260321_abc123.md

Requirements:
    - .env file with SMTP configuration
    - Email file in Approved/ folder with proper frontmatter
    - python-dotenv package installed

Environment Variables:
    SMTP_SERVER: SMTP server hostname (default: smtp.gmail.com)
    SMTP_PORT: SMTP port (default: 587)
    SMTP_USER: SMTP username/email
    SMTP_PASS: SMTP password or app password
    FROM_EMAIL: Default sender email (fallback to SMTP_USER)
"""

import argparse
import logging
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv

# Configure logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/email_sender.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds
BACKOFF_MULTIPLIER = 2


class EmailSenderError(Exception):
    """Custom exception for email sending errors"""
    pass


class EmailSender:
    """
    Email sender that reads markdown files and sends emails via SMTP.
    Includes retry logic, HTML support, and signature injection.
    """
    
    def __init__(self):
        """Initialize email sender with configuration from environment"""
        # Load environment variables
        load_dotenv()
        
        # Get SMTP configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        
        # Validate required configuration
        if not self.smtp_user:
            raise EmailSenderError("SMTP_USER not configured in .env file")
        if not self.smtp_pass:
            raise EmailSenderError("SMTP_PASS not configured in .env file")
        if not self.from_email:
            raise EmailSenderError("FROM_EMAIL not configured in .env file")
        
        # Load professional signature
        self.signature = self._load_signature()
        
        logger.info(f"Email sender initialized with server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"Sending from: {self.from_email}")
    
    def _load_signature(self) -> str:
        """
        Load professional email signature from Company_Handbook.md
        
        Returns:
            Email signature string
        """
        try:
            handbook_path = Path("Company_Handbook.md")
            if handbook_path.exists():
                with open(handbook_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract company name and basic info
                    # Simple extraction - can be enhanced
                    return "\n\n---\nBest regards,\nAI Employee System\nGold Tier"
            else:
                return "\n\n---\nBest regards"
        except Exception as e:
            logger.warning(f"Could not load signature: {e}")
            return "\n\n---\nBest regards"
    
    def _is_html_content(self, body: str) -> bool:
        """
        Detect if email body contains HTML.
        
        Args:
            body: Email body text
            
        Returns:
            True if HTML detected
        """
        html_indicators = ['<html', '<body', '<div', '<p>', '<br>', '<table', '<h1', '<h2']
        body_lower = body.lower()
        return any(indicator in body_lower for indicator in html_indicators)
    
    def parse_email_file(self, filepath: Path) -> Dict[str, str]:
        """
        Parse email metadata and body from markdown file.
        
        Expected format:
            to: recipient@example.com
            subject: Email Subject
            cc: optional@example.com
            from: optional_sender@example.com
            
            Email body starts here...
            Multiple lines supported.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            Dictionary with email fields: to, subject, body, cc, from
            
        Raises:
            EmailSenderError: If required fields are missing or file is invalid
        """
        logger.info(f"Parsing email file: {filepath}")
        
        if not filepath.exists():
            raise EmailSenderError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise EmailSenderError(f"Failed to read file: {e}")
        
        # Parse headers and body
        lines = content.split('\n')
        headers = {}
        body_lines = []
        in_body = False
        
        for line in lines:
            # Skip YAML frontmatter delimiters
            if line.strip() == '---':
                continue
            
            # Check if we've hit a blank line (end of headers)
            if not in_body and line.strip() == '':
                in_body = True
                continue
            
            # Parse header lines (key: value)
            if not in_body and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Only capture email-related headers
                if key in ['to', 'subject', 'cc', 'from', 'body']:
                    headers[key] = value
            else:
                # Everything else is body
                if in_body or not line.strip().startswith('#'):
                    body_lines.append(line)
        
        # Join body lines
        body = '\n'.join(body_lines).strip()
        
        # If body was specified in headers, use that
        if 'body' in headers and not body:
            body = headers['body']
        
        # Validate required fields
        if 'to' not in headers:
            raise EmailSenderError("Missing required field: 'to'")
        if 'subject' not in headers:
            raise EmailSenderError("Missing required field: 'subject'")
        if not body:
            raise EmailSenderError("Missing required field: 'body'")
        
        # Build email data
        email_data = {
            'to': headers['to'],
            'subject': headers['subject'],
            'body': body,
            'cc': headers.get('cc', ''),
            'from': headers.get('from', self.from_email)
        }
        
        logger.info(f"Parsed email - To: {email_data['to']}, Subject: {email_data['subject']}")
        if email_data['cc']:
            logger.info(f"CC: {email_data['cc']}")
        
        return email_data
    
    def send_email(self, email_data: Dict[str, str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send email via SMTP with retry logic and exponential backoff.
        
        Args:
            email_data: Dictionary with to, subject, body, cc, from
            
        Returns:
            Tuple of (success, message_id, error_message)
            
        Raises:
            EmailSenderError: If all retry attempts fail
        """
        logger.info("Preparing to send email...")
        
        # Inject signature if not already present
        body = email_data['body']
        if self.signature and self.signature not in body:
            body += self.signature
        
        # Detect if HTML
        is_html = self._is_html_content(body)
        content_type = 'html' if is_html else 'plain'
        
        logger.info(f"Email format: {content_type.upper()}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = email_data['from']
        msg['To'] = email_data['to']
        msg['Subject'] = email_data['subject']
        
        # Add CC if present
        if email_data['cc']:
            msg['Cc'] = email_data['cc']
        
        # Attach body
        msg.attach(MIMEText(body, content_type, 'utf-8'))
        
        # Build recipient list
        recipients = [email_data['to']]
        if email_data['cc']:
            # Split CC by comma and strip whitespace
            cc_list = [cc.strip() for cc in email_data['cc'].split(',') if cc.strip()]
            recipients.extend(cc_list)
        
        logger.info(f"Sending to {len(recipients)} recipient(s)")
        
        # Retry logic with exponential backoff
        last_error = None
        retry_delay = INITIAL_RETRY_DELAY
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Attempt {attempt}/{MAX_RETRIES}...")
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    # Enable TLS
                    server.starttls()
                    
                    # Login (don't log password)
                    logger.info(f"Logging in as: {self.smtp_user}")
                    server.login(self.smtp_user, self.smtp_pass)
                    
                    # Send email
                    logger.info("Sending email...")
                    server.send_message(msg)
                    
                    logger.info(f"✅ Email sent successfully on attempt {attempt}!")
                    
                    # Try to get message ID
                    message_id = msg.get('Message-ID')
                    return (True, message_id, None)
                    
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP authentication failed: {e}"
                logger.error(error_msg)
                # Don't retry auth errors
                return (False, None, error_msg)
                
            except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= BACKOFF_MULTIPLIER
                else:
                    error_msg = f"All {MAX_RETRIES} attempts failed. Last error: {last_error}"
                    logger.error(error_msg)
                    return (False, None, error_msg)
                    
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(error_msg)
                return (False, None, error_msg)
        
        # Should not reach here, but just in case
        return (False, None, f"Failed after {MAX_RETRIES} attempts")
    
    def update_file_success(self, filepath: Path, message_id: Optional[str] = None):
        """
        Update markdown file with successful send status and move to Done/.
        
        Args:
            filepath: Path to original markdown file
            message_id: Optional message ID from email server
        """
        logger.info("Updating file with success status...")
        
        # Prepare success metadata
        timestamp = datetime.now().isoformat()
        success_block = f"\n\n---\n\n**Send Result**\n\n"
        success_block += f"status: sent\n"
        success_block += f"sent_at: {timestamp}\n"
        if message_id:
            success_block += f"message_id: {message_id}\n"
        
        # Append to file
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(success_block)
            logger.info("✅ File updated with success status")
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
            # Don't raise - email was sent successfully
        
        # Move to Done/ folder
        try:
            # Get parent directory (should be Approved/)
            parent_dir = filepath.parent
            done_dir = parent_dir / 'Done'
            done_dir.mkdir(exist_ok=True)
            
            # Move file
            dest_path = done_dir / filepath.name
            filepath.rename(dest_path)
            
            logger.info(f"✅ File moved to: {dest_path}")
        except Exception as e:
            logger.error(f"Failed to move file to Done/: {e}")
            # Don't raise - email was sent successfully
    
    def update_file_failure(self, filepath: Path, error_message: str):
        """
        Update markdown file with failure status and move to Needs_Action/.
        
        Args:
            filepath: Path to original markdown file
            error_message: Error message to append
        """
        logger.info("Updating file with failure status...")
        
        # Prepare failure metadata
        timestamp = datetime.now().isoformat()
        failure_block = f"\n\n---\n\n**Send Result**\n\n"
        failure_block += f"status: failed\n"
        failure_block += f"error: {error_message}\n"
        failure_block += f"attempted_at: {timestamp}\n"
        
        # Append to file
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(failure_block)
            logger.info("File updated with failure status")
        except Exception as e:
            logger.error(f"Failed to update file: {e}")
        
        # Move to Needs_Action/ folder
        try:
            needs_action_dir = Path('Needs_Action')
            needs_action_dir.mkdir(exist_ok=True)
            
            # Move file
            dest_path = needs_action_dir / filepath.name
            
            # If file already exists, add timestamp to avoid overwrite
            if dest_path.exists():
                stem = filepath.stem
                suffix = filepath.suffix
                timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest_path = needs_action_dir / f"{stem}_retry_{timestamp_str}{suffix}"
            
            filepath.rename(dest_path)
            
            logger.info(f"File moved to: {dest_path}")
        except Exception as e:
            logger.error(f"Failed to move file to Needs_Action/: {e}")
    
    def process_email_file(self, filepath: str) -> bool:
        """
        Process email file: parse, send, and update status.
        
        Args:
            filepath: Path to email markdown file
            
        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)
        
        logger.info("=" * 80)
        logger.info(f"Processing email file: {filepath}")
        logger.info("=" * 80)
        
        try:
            # Parse email file
            email_data = self.parse_email_file(filepath)
            
            # Send email with retry logic
            success, message_id, error_msg = self.send_email(email_data)
            
            if success:
                # Update file with success
                self.update_file_success(filepath, message_id)
                
                logger.info("=" * 80)
                logger.info("✅ EMAIL SENT SUCCESSFULLY")
                logger.info("=" * 80)
                return True
            else:
                # Update file with failure
                self.update_file_failure(filepath, error_msg or "Unknown error")
                
                logger.info("=" * 80)
                logger.info("❌ EMAIL SENDING FAILED")
                logger.info("=" * 80)
                return False
            
        except EmailSenderError as e:
            logger.error(f"❌ Email sending failed: {e}")
            
            # Update file with failure
            try:
                self.update_file_failure(filepath, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update file with error: {update_error}")
            
            logger.info("=" * 80)
            logger.info("❌ EMAIL SENDING FAILED")
            logger.info("=" * 80)
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            
            # Try to update file with failure
            try:
                self.update_file_failure(filepath, f"Unexpected error: {e}")
            except:
                pass
            
            return False


def main():
    """Main entry point for email sender script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Send email from approved markdown file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python actions/email_sender.py --file Approved/email_send_20260321_abc123.md

The markdown file should contain:
    to: recipient@example.com
    subject: Email Subject
    cc: optional@example.com (optional)
    from: sender@example.com (optional)
    
    Email body starts here...
    Multiple lines supported.
        """
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to email markdown file'
    )
    
    args = parser.parse_args()
    
    # Ensure Logs directory exists
    Path('Logs').mkdir(exist_ok=True)
    
    try:
        # Initialize sender
        sender = EmailSender()
        
        # Process email file
        success = sender.process_email_file(args.file)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except EmailSenderError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
