
import os
import pickle
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

from Watchers.base_watcher import BaseWatcher

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher that monitors for new emails and creates structured markdown files
    in the Needs_Action folder for processing.
    """

    def __init__(self, interval: int = 300):
        super().__init__("Gmail Watcher", interval)
        self.creds = None
        self.service = None
        self.gmail_authenticate()

    def gmail_authenticate(self):
        """
        Authenticate with Gmail API using credentials.json.
        Performs OAuth flow on first run and creates token.json.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists('token.json'):
            with open('token.json', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail authentication successful")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for unread emails that are starred OR marked important by Gmail.

        Returns:
            List of email message objects
        """
        try:
            # Calculate time for one day ago to limit search
            one_day_ago = (datetime.utcnow() - timedelta(days=1)).strftime('%Y/%m/%d')

            # Search for unread emails that are either starred OR marked important by Gmail
            # This catches both manually starred emails and Gmail's automatic importance markers
            query = f'is:unread (is:starred OR is:important) -in:sent after:{one_day_ago}'
            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Get full message details
            detailed_messages = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()

                # Extract relevant information
                email_data = self._extract_email_data(message)
                detailed_messages.append(email_data)

            logger.info(f"Found {len(detailed_messages)} new emails")
            return detailed_messages
        except Exception as e:
            logger.error(f"Error checking for Gmail updates: {e}")
            return []

    def _extract_email_data(self, message: Dict) -> Dict[str, Any]:
        """
        Extract relevant data from a Gmail message.

        Args:
            message: The Gmail message object

        Returns:
            Dictionary with extracted email data
        """
        email_data = {
            'id': message['id'],
            'threadId': message.get('threadId', ''),
            'subject': '',
            'sender': '',
            'date': '',
            'body': '',
            'labels': message.get('labelIds', []),
            'sizeEstimate': message.get('sizeEstimate', 0)
        }

        # Extract headers (subject, sender, date)
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')

            if name == 'subject':
                email_data['subject'] = value
            elif name == 'from':
                email_data['sender'] = value
            elif name == 'date':
                email_data['date'] = value

        # Extract body
        payload = message.get('payload', {})
        parts = payload.get('parts', [])

        if not parts and 'body' in payload:
            # Plain text email
            body_data = payload['body'].get('data', '')
            if body_data:
                import base64
                email_data['body'] = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            # Multi-part email - try to get text/plain part
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        import base64
                        email_data['body'] = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
                elif part.get('mimeType') == 'text/html' and not email_data['body']:
                    # Fallback to HTML if no plain text found
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        import base64
                        email_data['body'] = base64.urlsafe_b64decode(body_data).decode('utf-8')

        return email_data

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single email event by creating a structured markdown file in Needs_Action.

        Args:
            event: The email event to process

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Create a structured markdown file in Needs_Action
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{timestamp}_{event['id'][:8]}.md"
            filepath = Path("Needs_Action") / filename

            # Create YAML frontmatter with email metadata
            yaml_frontmatter = f"""---
subject: "{event['subject']}"
sender: "{event['sender']}"
date_received: "{event['date']}"
gmail_id: "{event['id']}"
thread_id: "{event['threadId']}"
labels: {event['labels']}
priority: medium
status: new
processed: false
---

# Email from: {event['sender']}

**Subject:** {event['subject']}

**Date:** {event['date']}

**Gmail ID:** {event['id']}

## Email Content

{event['body']}

---

*Processed by Gmail Watcher at {datetime.now().isoformat()}*
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(yaml_frontmatter)

            logger.info(f"Created email file: {filepath}")

            # Mark email as read to avoid duplicate processing
            self._mark_email_as_read(event['id'])

            return True
        except Exception as e:
            logger.error(f"Error processing email {event['id']}: {e}")
            return False

    def _mark_email_as_read(self, email_id: str):
        """
        Mark the email as read to avoid processing it again.

        Args:
            email_id: The ID of the email to mark as read
        """
        try:
            # Remove 'UNREAD' label to mark as read
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked email {email_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark email {email_id} as read: {e}")

    def run_once(self) -> int:
        """
        Run one cycle of checking and processing Gmail events.

        Returns:
            Number of emails processed
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"{self.name} running Gmail check at {current_time}...")
        try:
            events = self.check_for_updates()
            logger.info(f"{self.name} found {len(events)} new emails")

            processed_count = 0
            for event in events:
                if self.process_event(event):
                    processed_count += 1

            self.last_run = time.time()
            logger.info(f"{self.name} completed cycle, processed {processed_count} emails")
            return processed_count
        except Exception as e:
            logger.error(f"Error in {self.name} run cycle: {e}")
            return 0


if __name__ == "__main__":
    # Create and run the Gmail watcher
    watcher = GmailWatcher(interval=90)
    watcher.run_forever()