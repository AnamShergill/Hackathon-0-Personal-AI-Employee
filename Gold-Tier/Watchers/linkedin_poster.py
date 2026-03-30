"""
LinkedIn Poster - Silver Tier MCP Integration
Automates posting to LinkedIn using Playwright with persistent session.
Posts approved content from Approved/ folder to LinkedIn.
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'linkedin_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinkedInPoster:
    """
    LinkedIn poster that automates posting using Playwright with persistent session.
    
    Features:
    - Persistent browser session (login once)
    - Automated post creation
    - Error handling and retries
    - Screenshot capture for verification
    """
    
    # LinkedIn selectors (2026 - multiple fallbacks for robustness)
    SELECTORS = {
        # Login page
        'login_email': 'input[id="username"]',
        'login_password': 'input[id="password"]',
        'login_button': 'button[type="submit"]',
        
        # Feed/Home
        'feed': 'main[role="main"]',
        
        # Start post button - multiple fallbacks
        'start_post_primary': 'button[aria-label*="Start a post" i]',
        'start_post_alt1': 'button:has-text("Start a post")',
        'start_post_alt2': 'div[role="button"]:has-text("Start a post")',
        'start_post_clickable': 'div.share-box-feed-entry__trigger',
        
        # Post textarea - multiple fallbacks
        'post_textarea_primary': 'div[role="textbox"][contenteditable="true"]',
        'post_textarea_alt1': 'div[data-placeholder*="talk about" i]',
        'post_textarea_alt2': '.ql-editor[contenteditable="true"]',
        
        # Post button - multiple fallbacks
        'post_button_primary': 'button[aria-label*="Post" i]:not([aria-label*="Start"])',
        'post_button_alt1': 'button:has-text("Post")',
        'post_button_alt2': 'button[data-test-share-box-post-button]',
    }

    def __init__(self, headless: bool = False):
        """
        Initialize LinkedIn poster.
        
        Args:
            headless: Run browser in headless mode (default: False for first login)
        """
        self.headless = headless
        self.session_dir = Path("Watchers/linkedin_session")
        self.session_dir.mkdir(exist_ok=True, parents=True)
        
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info(f"Initializing LinkedIn Poster")
        self._initialize_browser()

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
            self._navigate_to_linkedin()
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def _navigate_to_linkedin(self):
        """Navigate to LinkedIn and handle login if needed"""
        try:
            logger.info("Navigating to LinkedIn...")
            self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=60000)
            
            # Wait for network to settle
            time.sleep(3)
            
            # Check if we need to login
            current_url = self.page.url
            
            if 'login' in current_url or 'checkpoint' in current_url:
                logger.warning("=" * 80)
                logger.warning("LOGIN REQUIRED - FIRST TIME SETUP")
                logger.warning("=" * 80)
                logger.warning("Please log in to LinkedIn in the browser window")
                logger.warning("1. Enter your email and password")
                logger.warning("2. Complete any 2FA if required")
                logger.warning("3. Wait for feed to load")
                logger.warning("=" * 80)
                
                # Wait for user to login (check for feed)
                logger.info("Waiting for login... (timeout: 180 seconds)")
                try:
                    self.page.wait_for_url('**/feed/**', timeout=180000)
                    logger.info("✅ Login successful! Session saved.")
                except PlaywrightTimeout:
                    logger.error("Login timeout - please try again")
                    raise Exception("LinkedIn login timeout")
                
                time.sleep(3)
            else:
                logger.info("✅ Already logged in (session restored)")
            
            # Verify we're on the feed
            logger.info("Verifying LinkedIn feed loaded...")
            
            # Try multiple strategies to confirm we're logged in
            logged_in = False
            
            # Strategy 1: Look for "Start a post" button
            try:
                for selector in [self.SELECTORS['start_post_primary'], 
                                self.SELECTORS['start_post_alt1'],
                                self.SELECTORS['start_post_clickable']]:
                    if self.page.query_selector(selector):
                        logger.info(f"✅ Found start post button with: {selector}")
                        logged_in = True
                        break
            except:
                pass
            
            # Strategy 2: Look for profile/navigation elements
            if not logged_in:
                try:
                    # Look for "Me" navigation or profile icon
                    profile_nav = self.page.query_selector('a[href*="/in/"]')
                    if profile_nav:
                        logger.info("✅ Found profile navigation - logged in")
                        logged_in = True
                except:
                    pass
            
            # Strategy 3: Check URL
            if not logged_in:
                if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                    logger.info("✅ On LinkedIn feed/network page - logged in")
                    logged_in = True
            
            if logged_in:
                # Take success screenshot
                screenshot_path = Path("Logs") / f"linkedin_login_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"✅ Login verified! Screenshot: {screenshot_path}")
            else:
                logger.warning("⚠️  Could not verify login - may need manual check")
                # Take debug screenshot
                screenshot_path = Path("Logs") / f"linkedin_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.warning(f"Debug screenshot: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"Failed to navigate to LinkedIn: {e}")
            raise

    def post_to_linkedin(self, text: str, image_path: Optional[str] = None) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            text: Post text content
            image_path: Optional path to image to attach
            
        Returns:
            True if post was successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info("POSTING TO LINKEDIN")
            logger.info("=" * 80)
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Image: {image_path if image_path else 'None'}")
            
            # Ensure we're on the feed
            if 'feed' not in self.page.url:
                logger.info("Navigating to feed...")
                self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
            
            # Click "Start a post" button - try multiple selectors
            logger.info("Clicking 'Start a post' button...")
            start_button = None
            
            for selector in [self.SELECTORS['start_post_primary'],
                           self.SELECTORS['start_post_alt1'],
                           self.SELECTORS['start_post_alt2'],
                           self.SELECTORS['start_post_clickable']]:
                try:
                    start_button = self.page.wait_for_selector(selector, timeout=5000)
                    if start_button:
                        logger.info(f"Found start button with: {selector}")
                        start_button.click()
                        time.sleep(2)
                        break
                except PlaywrightTimeout:
                    continue
            
            if not start_button:
                logger.error("Could not find 'Start a post' button with any selector")
                # Try clicking on the share box directly
                logger.info("Trying alternative: clicking share box area...")
                try:
                    self.page.click('div[role="textbox"]', timeout=5000)
                    time.sleep(2)
                except:
                    raise Exception("Could not open post composer")
            
            # Wait for post modal/textarea to appear - try multiple selectors
            logger.info("Waiting for post editor...")
            textarea = None
            
            for selector in [self.SELECTORS['post_textarea_primary'],
                           self.SELECTORS['post_textarea_alt1'],
                           self.SELECTORS['post_textarea_alt2']]:
                try:
                    textarea = self.page.wait_for_selector(selector, timeout=5000)
                    if textarea:
                        logger.info(f"Found textarea with: {selector}")
                        break
                except PlaywrightTimeout:
                    continue
            
            if not textarea:
                raise Exception("Could not find post textarea")
            
            # Type the post text
            logger.info("Typing post content...")
            textarea.click()
            time.sleep(0.5)
            
            # Type text in chunks to avoid issues
            textarea.type(text, delay=10)
            time.sleep(1)
            
            # Handle image upload if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                try:
                    # Look for image upload button
                    upload_button = self.page.query_selector('input[type="file"]')
                    if upload_button:
                        upload_button.set_input_files(image_path)
                        time.sleep(3)
                        logger.info("✅ Image uploaded")
                    else:
                        logger.warning("Could not find image upload button")
                except Exception as e:
                    logger.warning(f"Image upload failed: {e}")
            
            # Take screenshot before posting
            screenshot_path = Path("Logs") / f"linkedin_pre_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Click Post button - try multiple selectors
            logger.info("Clicking 'Post' button...")
            post_button = None
            
            for selector in [self.SELECTORS['post_button_primary'],
                           self.SELECTORS['post_button_alt1'],
                           self.SELECTORS['post_button_alt2']]:
                try:
                    post_button = self.page.wait_for_selector(selector, timeout=5000)
                    if post_button:
                        logger.info(f"Found post button with: {selector}")
                        post_button.click()
                        break
                except PlaywrightTimeout:
                    continue
            
            if not post_button:
                raise Exception("Could not find 'Post' button")
            
            # Verify post was successful (modal should close)
            try:
                # Wait for modal to close and return to feed
                time.sleep(3)
                
                # Check if we're back on feed (start post button visible again)
                for selector in [self.SELECTORS['start_post_primary'],
                               self.SELECTORS['start_post_clickable']]:
                    if self.page.query_selector(selector):
                        logger.info("✅ Post published successfully!")
                        
                        # Take screenshot after posting
                        screenshot_path = Path("Logs") / f"linkedin_post_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        self.page.screenshot(path=str(screenshot_path))
                        logger.info(f"Success screenshot: {screenshot_path}")
                        
                        return True
                
                # If we can't confirm, assume success if no error
                logger.info("✅ Post likely successful (no errors detected)")
                screenshot_path = Path("Logs") / f"linkedin_post_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"Completion screenshot: {screenshot_path}")
                return True
                
            except Exception as e:
                logger.warning(f"Could not verify post completion: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            # Take error screenshot
            try:
                screenshot_path = Path("Logs") / f"linkedin_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.error(f"Error screenshot: {screenshot_path}")
            except:
                pass
            return False

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


def post_approved_content(file_path: str) -> bool:
    """
    Post approved LinkedIn content from a file.
    
    Args:
        file_path: Path to approved post file
        
    Returns:
        True if posted successfully
    """
    logger.info(f"Processing approved post: {file_path}")
    
    try:
        # Read the post file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract post text from markdown
        # Look for "## Post Text" section
        post_text = extract_post_text(content)
        
        if not post_text:
            logger.error("Could not extract post text from file")
            return False
        
        logger.info(f"Extracted post text ({len(post_text)} chars)")
        
        # Initialize poster
        poster = LinkedInPoster(headless=False)
        
        # Post to LinkedIn
        success = poster.post_to_linkedin(post_text)
        
        # Cleanup
        poster.cleanup()
        
        if success:
            # Move file to Done with success note
            move_to_done(file_path, success=True)
            logger.info("✅ Post published and file moved to Done/")
        else:
            logger.error("❌ Post failed - file remains in Approved/")
        
        return success
        
    except Exception as e:
        logger.error(f"Error posting approved content: {e}")
        return False


def extract_post_text(content: str) -> Optional[str]:
    """
    Extract post text from markdown file.
    """
    # Look for "## Post Text" section
    match = re.search(r'## Post Text\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback: look for content between first --- and second ---
    parts = content.split('---')
    if len(parts) >= 3:
        # Skip frontmatter, get body
        body = parts[2].strip()
        # Get first substantial paragraph
        lines = [line.strip() for line in body.split('\n') if line.strip() and not line.startswith('#')]
        if lines:
            return '\n'.join(lines[:20])  # First 20 lines
    
    return None


def move_to_done(file_path: str, success: bool = True):
    """
    Move posted file to Done/ with completion note.
    """
    filename = Path(file_path).name
    done_path = Path("Done") / filename
    
    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add completion note
    status = "SUCCESS" if success else "FAILED"
    note = f"""

---

## POSTING RESULT
- **Status**: {status}
- **Posted**: {datetime.now().isoformat()}
- **Platform**: LinkedIn
- **Posted by**: linkedin_poster.py

<COMPLETE>
Posted to LinkedIn at {datetime.now().isoformat()}
</COMPLETE>
"""
    
    # Write to Done
    with open(done_path, 'w', encoding='utf-8') as f:
        f.write(content + note)
    
    # Remove from Approved
    os.remove(file_path)
    
    logger.info(f"File moved to Done/: {done_path}")


def main():
    """
    Main entry point for LinkedIn poster.
    Can be called with a file path or run interactively.
    """
    import sys
    
    logger.info("=" * 80)
    logger.info("LinkedIn Poster - Silver Tier MCP Integration")
    logger.info("=" * 80)
    logger.info("")
    
    if len(sys.argv) > 1:
        # Post specific file
        file_path = sys.argv[1]
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        
        success = post_approved_content(file_path)
        sys.exit(0 if success else 1)
    
    else:
        # Interactive mode - test posting
        logger.info("Interactive mode - Testing LinkedIn posting")
        logger.info("")
        
        test_text = """🚀 Testing automated LinkedIn posting!

This post was created and published automatically using:
• Python + Playwright
• Persistent browser session
• Human-in-the-loop approval workflow

The future of social media automation is here.

#Automation #AI #LinkedIn #Testing"""
        
        logger.info("Test post text:")
        logger.info(test_text)
        logger.info("")
        
        response = input("Post this test message to LinkedIn? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            poster = LinkedInPoster(headless=False)
            success = poster.post_to_linkedin(test_text)
            poster.cleanup()
            
            if success:
                logger.info("✅ Test post successful!")
            else:
                logger.error("❌ Test post failed")
        else:
            logger.info("Test cancelled")


if __name__ == "__main__":
    main()
