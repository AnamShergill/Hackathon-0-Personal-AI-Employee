#!/usr/bin/env python3
"""
Email Sender Action - Gold Tier Phase 1

Standalone script that sends emails from approved .md files.
Reads email metadata from markdown frontmatter, sends via SMTP,
and updates the file with send status.

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
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/email_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailSenderError(Exception):
    """Custom exception for email sending errors"""
    pass


class EmailSender:
    """
    Email sender that reads markdown files and sends emails via SMTP.
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
        
        logger.info(f"Email sender initialized with server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"Sending from: {self.from_email}")
    
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
    
    def send_email(self, email_data: Dict[str, str]) -> Optional[str]:
        """
        Send email via SMTP.
        
        Args:
            email_data: Dictionary with to, subject, body, cc, from
            
        Returns:
            Message ID if available, None otherwise
            
        Raises:
            EmailSenderError: If sending fails
        """
        logger.info("Preparing to send email...")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_data['from']
        msg['To'] = email_data['to']
        msg['Subject'] = email_data['subject']
        
        # Add CC if present
        if email_data['cc']:
            msg['Cc'] = email_data['cc']
        
        # Attach body as plain text
        msg.attach(MIMEText(email_data['body'], 'plain', 'utf-8'))
        
        # Build recipient list
        recipients = [email_data['to']]
        if email_data['cc']:
            # Split CC by comma and strip whitespace
            cc_list = [cc.strip() for cc in email_data['cc'].split(',') if cc.strip()]
            recipients.extend(cc_list)
        
        logger.info(f"Sending to {len(recipients)} recipient(s)")
        
        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                # Enable TLS
                server.starttls()
                
                # Login (don't log password)
                logger.info(f"Logging in as: {self.smtp_user}")
                server.login(self.smtp_user, self.smtp_pass)
                
                # Send email
                logger.info("Sending email...")
                server.send_message(msg)
                
                logger.info("✅ Email sent successfully!")
                
                # Try to get message ID
                message_id = msg.get('Message-ID')
                return message_id
                
        except smtplib.SMTPAuthenticationError as e:
            raise EmailSenderError(f"SMTP authentication failed: {e}")
        except smtplib.SMTPException as e:
            raise EmailSenderError(f"SMTP error: {e}")
        except Exception as e:
            raise EmailSenderError(f"Failed to send email: {e}")
    
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
            
            # Send email
            message_id = self.send_email(email_data)
            
            # Update file with success
            self.update_file_success(filepath, message_id)
            
            logger.info("=" * 80)
            logger.info("✅ EMAIL SENT SUCCESSFULLY")
            logger.info("=" * 80)
            return True
            
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
