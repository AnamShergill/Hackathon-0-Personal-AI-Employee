"""
WhatsApp Watcher - Silver Tier
Monitors WhatsApp Web for new/unread messages and creates structured markdown files
in the Needs_Action folder for processing by the AI Employee.

Uses Playwright to automate WhatsApp Web with persistent session (QR code scan once).
"""

import os
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout

from Watchers.base_watcher import BaseWatcher

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'whatsapp_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp watcher that monitors WhatsApp Web for new messages and creates
    structured markdown files in the Needs_Action folder.
    
    Features:
    - Persistent browser session (QR code scan only once)
    - Polls for unread messages every 60 seconds
    - Extracts sender, message text, timestamp
    - Priority detection based on keywords
    - Creates markdown files compatible with email processor
    """
    
    # Urgent keywords for priority detection
    URGENT_KEYWORDS = [
        'urgent', 'asap', 'immediately', 'now', 'emergency', 'critical',
        'important', 'help', 'please', 'quick', 'fast', 'hurry'
    ]
    
    # WhatsApp Web selectors (2026 - using robust fallback strategies)
    SELECTORS = {
        'qr_code': 'canvas[aria-label*="Scan"]',  # More flexible QR detection
        'search_box': 'div[contenteditable="true"][data-tab="3"]',
        # Chat list - multiple fallback options (checked in order)
        'chat_list_primary': '[data-testid="chat-list"]',  # Primary: data-testid
        'chat_list_role': 'div[role="grid"]',  # Fallback: role-based
        'chat_list_side': '#pane-side',  # Fallback: ID-based (stable)
        'chat_item': 'div[role="row"]',  # Updated from listitem to row (grid structure)
        'message_container': 'div[data-testid="conversation-panel-body"]',
        'message_text': 'span.selectable-text',
        'chat_header': 'header[data-testid="conversation-header"]',
        'contact_name': 'span[data-testid="conversation-info-header-chat-title"]',
    }

    def __init__(self, interval: int = 60, headless: bool = False, scan_all: bool = False):
        """
        Initialize WhatsApp watcher.
        
        Args:
            interval: Polling interval in seconds (default: 60)
            headless: Run browser in headless mode (default: False for QR scan)
            scan_all: If True, scan ALL chats (not just unread) for debugging (default: False)
        """
        super().__init__("WhatsApp Watcher", interval)
        self.headless = headless
        self.scan_all = scan_all
        self.session_dir = Path("Watchers/whatsapp_session")
        self.session_dir.mkdir(exist_ok=True)
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.processed_messages = set()  # Track processed message IDs
        self._load_processed_messages()
        
        logger.info(f"Initializing {self.name} with {interval}s interval")
        self._initialize_browser()

    def _load_processed_messages(self):
        """Load previously processed message IDs from file"""
        processed_file = self.session_dir / 'processed_messages.txt'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_messages = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.processed_messages)} processed message IDs")

    def _save_processed_message(self, message_id: str):
        """Save processed message ID to file"""
        self.processed_messages.add(message_id)
        processed_file = self.session_dir / 'processed_messages.txt'
        with open(processed_file, 'a') as f:
            f.write(f"{message_id}\n")
    
    def _debug_page_state(self, context: str = ""):
        """Debug helper to log current page state"""
        try:
            logger.debug(f"=== DEBUG: {context} ===")
            logger.debug(f"URL: {self.page.url}")
            logger.debug(f"Title: {self.page.title()}")
            
            # Check for common elements
            elements_to_check = [
                ('Search box', 'div[contenteditable="true"]'),
                ('Chat items (row)', 'div[role="row"]'),
                ('Chat items (listitem)', 'div[role="listitem"]'),
                ('Side pane', '#pane-side'),
                ('Chat list testid', '[data-testid="chat-list"]'),
            ]
            
            for name, selector in elements_to_check:
                count = len(self.page.query_selector_all(selector))
                logger.debug(f"{name}: {count} found")
                
        except Exception as e:
            logger.debug(f"Debug failed: {e}")

    def _initialize_browser(self):
        """Initialize Playwright browser with persistent context"""
        try:
            logger.info("Launching Playwright browser...")
            self.playwright = sync_playwright().start()
            
            # Launch Chromium with persistent context for session persistence
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ],
                viewport={'width': 1280, 'height': 720},
            )
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            
            logger.info("Browser launched successfully")
            self._navigate_to_whatsapp()
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def _navigate_to_whatsapp(self):
        """Navigate to WhatsApp Web and handle QR code if needed"""
        try:
            logger.info("Navigating to WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
            
            # Wait for network to settle after initial load
            logger.info("Waiting for network idle...")
            try:
                self.page.wait_for_load_state('networkidle', timeout=30000)
            except PlaywrightTimeout:
                logger.warning("Network idle timeout - continuing anyway")
            
            # Additional buffer for dynamic content
            time.sleep(3)
            
            # Check if QR code is present (first time login)
            try:
                qr_canvas = self.page.wait_for_selector(
                    self.SELECTORS['qr_code'],
                    timeout=5000
                )
                if qr_canvas:
                    logger.warning("=" * 80)
                    logger.warning("QR CODE DETECTED - FIRST TIME SETUP")
                    logger.warning("=" * 80)
                    logger.warning("Please scan the QR code in the browser window with your phone")
                    logger.warning("1. Open WhatsApp on your phone")
                    logger.warning("2. Go to Settings → Linked Devices")
                    logger.warning("3. Tap 'Link a Device'")
                    logger.warning("4. Scan the QR code displayed in the browser")
                    logger.warning("=" * 80)
                    
                    # Wait for QR code to disappear (successful login)
                    logger.info("Waiting for QR code scan... (timeout: 120 seconds)")
                    self.page.wait_for_selector(
                        self.SELECTORS['qr_code'],
                        state='detached',
                        timeout=120000
                    )
                    logger.info("✅ QR code scanned successfully! Session saved.")
                    
                    # Wait for page to reload after QR scan
                    time.sleep(5)
                    
            except PlaywrightTimeout:
                # QR code not found - already logged in
                logger.info("Already logged in (no QR code detected)")
            
            # Wait for chat list to load - try multiple strategies
            logger.info("Waiting for WhatsApp chat interface to load...")
            chat_list_loaded = False
            
            # Strategy 1: Try data-testid (most reliable in 2026)
            try:
                logger.info("Strategy 1: Looking for chat list by data-testid...")
                self.page.wait_for_selector(
                    self.SELECTORS['chat_list_primary'],
                    state='visible',
                    timeout=20000
                )
                chat_list_loaded = True
                logger.info("✅ Chat list found via data-testid")
            except PlaywrightTimeout:
                logger.warning("Strategy 1 failed - trying fallback...")
            
            # Strategy 2: Try role-based selector
            if not chat_list_loaded:
                try:
                    logger.info("Strategy 2: Looking for chat list by role...")
                    self.page.wait_for_selector(
                        self.SELECTORS['chat_list_role'],
                        state='visible',
                        timeout=20000
                    )
                    chat_list_loaded = True
                    logger.info("✅ Chat list found via role attribute")
                except PlaywrightTimeout:
                    logger.warning("Strategy 2 failed - trying fallback...")
            
            # Strategy 3: Try ID-based selector (most stable)
            if not chat_list_loaded:
                try:
                    logger.info("Strategy 3: Looking for side pane by ID...")
                    self.page.wait_for_selector(
                        self.SELECTORS['chat_list_side'],
                        state='visible',
                        timeout=20000
                    )
                    chat_list_loaded = True
                    logger.info("✅ Side pane found via ID")
                except PlaywrightTimeout:
                    logger.warning("Strategy 3 failed - trying text-based fallback...")
            
            # Strategy 4: Look for search box (always present when logged in)
            if not chat_list_loaded:
                try:
                    logger.info("Strategy 4: Looking for search box...")
                    search_locator = self.page.locator('div[contenteditable="true"]').first
                    search_locator.wait_for(state='visible', timeout=20000)
                    chat_list_loaded = True
                    logger.info("✅ Search box found - interface loaded")
                except PlaywrightTimeout:
                    logger.warning("Strategy 4 failed")
            
            if not chat_list_loaded:
                # Debug: Take screenshot and log page info
                logger.error("All strategies failed - taking debug screenshot...")
                debug_path = Path("Logs") / f"whatsapp_load_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(debug_path))
                logger.error(f"Screenshot saved to: {debug_path}")
                logger.error(f"Page title: {self.page.title()}")
                logger.error(f"Page URL: {self.page.url}")
                
                # Try one more reload
                logger.info("Attempting page reload...")
                self.page.reload(wait_until='networkidle', timeout=60000)
                time.sleep(5)
                
                # Final attempt with any visible element
                try:
                    self.page.wait_for_selector('div[role="row"]', state='visible', timeout=20000)
                    chat_list_loaded = True
                    logger.info("✅ Chat interface loaded after reload")
                except PlaywrightTimeout:
                    raise Exception("Failed to load WhatsApp chat interface after all attempts")
            
            logger.info("✅ WhatsApp Web loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to navigate to WhatsApp Web: {e}")
            # Take final debug screenshot
            try:
                debug_path = Path("Logs") / f"whatsapp_fatal_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(debug_path))
                logger.error(f"Fatal error screenshot: {debug_path}")
            except:
                pass
            raise

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread messages in WhatsApp Web.
        
        Returns:
            List of message dictionaries with sender, text, timestamp, etc.
        """
        messages = []
        
        try:
            # Don't reload on every check - just wait for content to update
            logger.info("Checking for unread messages...")
            time.sleep(2)  # Wait for any dynamic updates
            
            # Find all chat items - try multiple selectors
            chat_items = self.page.query_selector_all(self.SELECTORS['chat_item'])
            
            # Fallback if no items found with primary selector
            if not chat_items:
                logger.warning("No chat items found with primary selector, trying fallback...")
                chat_items = self.page.query_selector_all('div[role="listitem"]')
            
            if not chat_items:
                logger.warning("No chat items found with fallback selector, trying generic...")
                chat_items = self.page.query_selector_all('[data-testid^="cell-frame-container"]')
            
            logger.info(f"Found {len(chat_items)} chat items")
            
            # Debug mode: log details of first 5 chats
            if self.scan_all or len(messages) == 0:
                logger.info("=== DEBUG: Analyzing first 5 chats ===")
                for idx, chat_item in enumerate(chat_items[:5]):
                    try:
                        # Get chat name
                        title_elem = chat_item.query_selector('span[title]')
                        chat_name = title_elem.get_attribute('title') if title_elem else "Unknown"
                        
                        # Check all unread indicators
                        has_badge = chat_item.query_selector('span[data-testid="icon-unread-count"]') is not None
                        has_aria = chat_item.query_selector('div[aria-label*="unread" i]') is not None
                        has_bold = len(chat_item.query_selector_all('strong')) > 0
                        has_icon = len(chat_item.query_selector_all('span[data-icon*="unread"]')) > 0
                        
                        # NEW: Check for recent timestamp (today's messages)
                        time_elem = chat_item.query_selector('span[data-testid="last-msg-time"]')
                        timestamp = time_elem.inner_text() if time_elem else "N/A"
                        
                        logger.info(f"  Chat #{idx+1}: {chat_name[:30]} | Badge:{has_badge} Aria:{has_aria} Bold:{has_bold} Icon:{has_icon} | Time:{timestamp}")
                    except Exception as e:
                        logger.error(f"  Error analyzing chat #{idx+1}: {e}")
            
            # NEW STRATEGY: If scan_all mode, check first 3 chats regardless of unread status
            if self.scan_all and len(messages) == 0:
                logger.info("=== SCAN_ALL MODE: Checking first 3 chats for new messages ===")
                for idx in range(min(3, len(chat_items))):
                    try:
                        chat_item = chat_items[idx]
                        
                        # Get chat name for logging
                        title_elem = chat_item.query_selector('span[title]')
                        chat_name = title_elem.get_attribute('title') if title_elem else "Unknown"
                        
                        logger.info(f"Opening chat #{idx+1}: {chat_name}")
                        
                        # Click to open
                        chat_item.click()
                        time.sleep(2)
                        
                        # Extract message
                        message_data = self._extract_message_from_chat()
                        
                        if message_data:
                            # Check if already processed
                            if message_data['id'] not in self.processed_messages:
                                messages.append(message_data)
                                logger.info(f"✅ Found message from: {message_data['sender']}")
                            else:
                                logger.info(f"⏭️  Already processed: {message_data['id']}")
                        
                        # Go back
                        self.page.keyboard.press('Escape')
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error in scan_all for chat #{idx+1}: {e}")
            
            unread_count = 0
            for idx, chat_item in enumerate(chat_items):
                try:
                    # Multiple strategies to detect unread messages
                    is_unread = False
                    unread_reason = ""
                    
                    # Strategy 1: Check for unread badge with count (multiple messages)
                    unread_badge = chat_item.query_selector('span[data-testid="icon-unread-count"]')
                    if unread_badge:
                        is_unread = True
                        unread_reason = f"badge count: {unread_badge.inner_text()}"
                    
                    # Strategy 2: Check for unread dot indicator (single message or no count)
                    if not is_unread:
                        unread_dot = chat_item.query_selector('div[aria-label*="unread" i]')
                        if unread_dot:
                            is_unread = True
                            unread_reason = "unread aria-label"
                    
                    # Strategy 3: Check for green dot or unread marker by class/style
                    if not is_unread:
                        # Look for common unread indicators
                        unread_markers = chat_item.query_selector_all('span[data-icon="unread-count"], span[data-icon="status-unread"]')
                        if unread_markers and len(unread_markers) > 0:
                            is_unread = True
                            unread_reason = "unread icon marker"
                    
                    # Strategy 4: Check for bold text (unread chats have bold sender names)
                    if not is_unread:
                        bold_elements = chat_item.query_selector_all('span[title] strong, div strong')
                        if bold_elements and len(bold_elements) > 0:
                            # Additional check: look for message preview that's also bold
                            message_preview = chat_item.query_selector('span[title]')
                            if message_preview:
                                is_unread = True
                                unread_reason = "bold text (likely unread)"
                    
                    if is_unread:
                        unread_count += 1
                        logger.info(f"Unread chat #{unread_count} detected ({unread_reason})")
                        
                        # Click on the chat to open it
                        chat_item.click()
                        time.sleep(1.5)  # Wait for chat to open
                        
                        # Extract message details
                        message_data = self._extract_message_from_chat()
                        
                        if message_data and message_data['id'] not in self.processed_messages:
                            messages.append(message_data)
                            logger.info(f"✅ New message from: {message_data['sender']}")
                        else:
                            if message_data:
                                logger.info(f"⏭️  Message already processed: {message_data['id']}")
                            else:
                                logger.warning("Failed to extract message data")
                        
                        # Go back to chat list
                        self.page.keyboard.press('Escape')
                        time.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"Error processing chat item #{idx}: {e}")
                    continue
            
            logger.info(f"Found {unread_count} unread chats, extracted {len(messages)} new messages")
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
        
        return messages

    def _extract_message_from_chat(self) -> Optional[Dict[str, Any]]:
        """
        Extract message details from currently open chat.
        
        Returns:
            Dictionary with message data or None if extraction fails
        """
        try:
            # Wait a moment for chat to fully load
            time.sleep(1)
            
            # Get contact name from header - try multiple selectors
            sender = "Unknown Contact"
            
            # Try primary selector
            contact_element = self.page.query_selector(self.SELECTORS['contact_name'])
            if contact_element:
                sender = contact_element.inner_text()
            else:
                # Try alternative selectors
                alt_selectors = [
                    'header span[dir="auto"]',  # Common pattern
                    'header h1',
                    'header [data-testid="conversation-info-header"]',
                    'div[data-testid="conversation-info-header"] span',
                ]
                for selector in alt_selectors:
                    elem = self.page.query_selector(selector)
                    if elem and elem.inner_text():
                        sender = elem.inner_text()
                        break
            
            logger.info(f"Extracting messages from: {sender}")
            
            # Get message container - try multiple selectors
            message_container = None
            container_selectors = [
                self.SELECTORS['message_container'],  # Primary
                'div[data-testid="conversation-panel-messages"]',  # Alternative 1
                'div[data-testid="conversation-panel-body"]',  # Alternative 2
                'div[role="application"]',  # Alternative 3
                'div.copyable-area',  # Alternative 4 (older WhatsApp)
            ]
            
            for selector in container_selectors:
                message_container = self.page.query_selector(selector)
                if message_container:
                    logger.info(f"Found message container with selector: {selector}")
                    break
            
            if not message_container:
                logger.error("Could not find message container with any selector")
                # Take a screenshot for debugging
                try:
                    screenshot_path = Path("Logs") / f"no_container_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.page.screenshot(path=str(screenshot_path))
                    logger.error(f"Screenshot saved: {screenshot_path}")
                except:
                    pass
                return None
            
            # Get message bubbles - try multiple selectors
            message_bubbles = message_container.query_selector_all('div[data-testid="msg-container"]')
            
            if not message_bubbles:
                logger.warning("No message bubbles found with primary selector - trying alternatives")
                # Try alternative selectors
                alt_bubble_selectors = [
                    'div.message-in, div.message-out',
                    'div[class*="message"]',
                    'div[data-testid^="msg"]',
                    'span.selectable-text',  # Just get text spans
                ]
                for selector in alt_bubble_selectors:
                    message_bubbles = message_container.query_selector_all(selector)
                    if message_bubbles:
                        logger.info(f"Found {len(message_bubbles)} bubbles with: {selector}")
                        break
            
            if not message_bubbles:
                logger.error(f"No messages found in chat with {sender}")
                return None
            
            logger.info(f"Found {len(message_bubbles)} message bubbles")
            
            # Get last 5 messages (or all if less than 5)
            recent_messages = message_bubbles[-5:] if len(message_bubbles) > 5 else message_bubbles
            
            # Extract text from messages
            message_texts = []
            timestamps = []
            
            for bubble in recent_messages:
                # Check if it's an incoming message (not sent by us)
                # Try multiple ways to detect incoming messages
                is_incoming = False
                
                # Method 1: Check class attribute
                class_attr = bubble.get_attribute('class') or ''
                if 'message-in' in class_attr or 'msg-in' in class_attr:
                    is_incoming = True
                
                # Method 2: Check for incoming data-testid
                if not is_incoming and bubble.query_selector('[data-testid*="incoming"]'):
                    is_incoming = True
                
                # Method 3: If we can't determine, assume it's incoming (better to capture too much than miss)
                # Check if it's NOT outgoing
                if not is_incoming:
                    if 'message-out' not in class_attr and 'msg-out' not in class_attr:
                        # Might be incoming, let's check for text
                        text_check = bubble.query_selector_all('span.selectable-text, span[dir="ltr"]')
                        if text_check and len(text_check) > 0:
                            is_incoming = True  # Has text and not marked as outgoing
                
                if is_incoming:
                    # Extract message text
                    text_elements = bubble.query_selector_all(self.SELECTORS['message_text'])
                    if not text_elements:
                        # Try alternative text selectors
                        text_elements = bubble.query_selector_all('span[dir="ltr"], span.copyable-text')
                    
                    text = ' '.join([el.inner_text() for el in text_elements if el.inner_text()])
                    
                    if text:
                        message_texts.append(text)
                        logger.info(f"  Extracted text: {text[:50]}...")
                        
                        # Try to extract timestamp
                        time_element = bubble.query_selector('span[data-testid="msg-meta"]')
                        if not time_element:
                            time_element = bubble.query_selector('span[class*="time"], div[class*="time"]')
                        if time_element:
                            timestamps.append(time_element.inner_text())
            
            # If no incoming messages found, just get the LAST message regardless of direction
            if not message_texts:
                logger.warning("No incoming messages detected - extracting last message regardless")
                last_bubble = recent_messages[-1] if recent_messages else None
                if last_bubble:
                    text_elements = last_bubble.query_selector_all('span.selectable-text, span[dir="ltr"]')
                    text = ' '.join([el.inner_text() for el in text_elements if el.inner_text()])
                    if text:
                        message_texts.append(text)
                        logger.info(f"  Extracted last message: {text[:50]}...")
            
            if not message_texts:
                logger.warning("No messages could be extracted from chat")
                return None
            
            # Combine messages
            full_message = '\n\n'.join(message_texts)
            timestamp = timestamps[-1] if timestamps else datetime.now().strftime('%H:%M')
            
            # Generate unique message ID
            message_id = hashlib.md5(
                f"{sender}_{full_message[:50]}_{timestamp}".encode()
            ).hexdigest()[:16]
            
            # Detect priority based on keywords
            priority = self._detect_priority(full_message, sender)
            
            return {
                'id': message_id,
                'sender': sender,
                'message': full_message,
                'timestamp': timestamp,
                'priority': priority,
                'date_received': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error extracting message: {e}")
            return None

    def _detect_priority(self, message: str, sender: str) -> str:
        """
        Detect message priority based on keywords and sender.
        
        Args:
            message: Message text
            sender: Sender name
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        message_lower = message.lower()
        
        # Check for urgent keywords
        urgent_count = sum(1 for keyword in self.URGENT_KEYWORDS if keyword in message_lower)
        
        # Check for financial keywords
        financial_keywords = ['payment', 'pay', 'money', 'invoice', '$', '€', '£', 'rs', 'pkr']
        financial_count = sum(1 for keyword in financial_keywords if keyword in message_lower)
        
        # Calculate priority score
        score = urgent_count * 3 + financial_count * 2
        
        if score >= 5:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a WhatsApp message by creating a structured markdown file.
        
        Args:
            event: Message event dictionary
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Create markdown filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"whatsapp_{timestamp}_{event['id']}.md"
            filepath = Path("Needs_Action") / filename
            
            # Create YAML frontmatter with message metadata
            markdown_content = f"""---
source: "WhatsApp"
sender: "{event['sender']}"
date_received: "{event['date_received']}"
timestamp: "{event['timestamp']}"
message_id: "{event['id']}"
priority: {event['priority']}
status: new
processed: false
---

# WhatsApp Message from: {event['sender']}

**Received:** {event['timestamp']}

**Priority:** {event['priority'].upper()}

**Message ID:** {event['id']}

## Message Content

{event['message']}

---

*Processed by WhatsApp Watcher at {datetime.now().isoformat()}*
"""
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"✅ Created message file: {filepath}")
            
            # Mark as processed
            self._save_processed_message(event['id'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message {event['id']}: {e}")
            return False

    def run_once(self) -> int:
        """
        Run one cycle of checking and processing WhatsApp messages.
        
        Returns:
            Number of messages processed
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"{self.name} running WhatsApp check at {current_time}...")
        
        try:
            # Check if page is still valid
            if not self.page or self.page.is_closed():
                logger.warning("Page closed, reinitializing browser...")
                self._initialize_browser()
            
            # Check for new messages
            events = self.check_for_updates()
            logger.info(f"{self.name} found {len(events)} new messages")
            
            processed_count = 0
            for event in events:
                if self.process_event(event):
                    processed_count += 1
            
            self.last_run = time.time()
            logger.info(f"{self.name} completed cycle, processed {processed_count} messages")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error in {self.name} run cycle: {e}")
            # Try to recover
            try:
                logger.info("Attempting to recover browser session...")
                self._initialize_browser()
            except:
                logger.error("Failed to recover browser session")
            return 0

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page and not self.page.is_closed():
                self.page.close()
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def main():
    """
    Main entry point for WhatsApp watcher.
    Run this script to start monitoring WhatsApp Web.
    """
    logger.info("=" * 80)
    logger.info("WhatsApp Watcher - Silver Tier")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Starting WhatsApp Web monitoring...")
    logger.info("This will open a browser window for WhatsApp Web")
    logger.info("")
    logger.info("First time setup:")
    logger.info("1. Browser will open to WhatsApp Web")
    logger.info("2. Scan QR code with your phone")
    logger.info("3. Session will be saved for future runs")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)
    logger.info("")
    
    watcher = None
    try:
        # Create watcher (headless=False for first run to scan QR)
        # Change to headless=True after QR code is scanned once
        watcher = WhatsAppWatcher(interval=60, headless=False)
        
        # Run forever
        watcher.run_forever()
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 80)
        logger.info("WhatsApp Watcher stopped by user")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if watcher:
            watcher.cleanup()


if __name__ == "__main__":
    main()
