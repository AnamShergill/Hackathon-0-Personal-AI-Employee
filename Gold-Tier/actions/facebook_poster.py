#!/usr/bin/env python3
"""
Facebook Poster - Gold Tier Phase 3
Automates posting to Facebook using Playwright with persistent session.
Posts approved content from Approved/ folder to Facebook.

Features:
- Persistent browser session (login once)
- Text + image posting
- Visibility control (public/friends/only_me)
- Error handling and retries
- Screenshot capture for verification
- Rate limiting (max 3 posts/day)
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
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
        logging.FileHandler(log_dir / 'facebook_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacebookPoster:
    """
    Facebook poster that automates posting using Playwright with persistent session.
    
    Features:
    - Persistent browser session (login once)
    - Automated post creation with text and images
    - Visibility control
    - Error handling and retries
    - Screenshot capture for verification
    - Rate limiting
    """
    
    # Facebook selectors (2026 - multiple fallbacks for robustness)
    SELECTORS = {
        # Login page
        'login_email': 'input[name="email"]',
        'login_password': 'input[name="pass"]',
        'login_button': 'button[name="login"]',
        
        # Feed/Home
        'feed': 'div[role="feed"]',
        'main_feed': 'div[role="main"]',
        
        # Create post - multiple fallbacks
        'create_post_primary': 'div[role="button"][aria-label*="What\'s on your mind" i]',
        'create_post_alt1': 'div[role="button"]:has-text("What\'s on your mind")',
        'create_post_alt2': 'span:has-text("What\'s on your mind")',
        'create_post_clickable': 'div[data-pagelet*="FeedComposer"]',
        
        # Post textarea - multiple fallbacks
        'post_textarea_primary': 'div[role="textbox"][contenteditable="true"]',
        'post_textarea_alt1': 'div[aria-label*="What\'s on your mind" i][contenteditable="true"]',
        'post_textarea_alt2': 'div[data-contents="true"][contenteditable="true"]',
        
        # Photo/video button
        'photo_button_primary': 'div[aria-label*="Photo/video" i]',
        'photo_button_alt1': 'div[aria-label*="Add photos" i]',
        'photo_input': 'input[type="file"][accept*="image"]',
        
        # Visibility/audience selector
        'audience_button': 'div[aria-label*="Select audience" i]',
        'audience_public': 'div[role="menuitem"]:has-text("Public")',
        'audience_friends': 'div[role="menuitem"]:has-text("Friends")',
        'audience_only_me': 'div[role="menuitem"]:has-text("Only me")',
        
        # Post button - multiple fallbacks
        'post_button_primary': 'div[aria-label="Post" i][role="button"]',
        'post_button_alt1': 'div[role="button"]:has-text("Post")',
        'post_button_alt2': 'button:has-text("Post")',
    }
    
    # Rate limiting
    RATE_LIMIT_FILE = Path("Logs") / "facebook_rate_limit.json"
    MAX_POSTS_PER_DAY = 3
    MIN_INTERVAL_HOURS = 4

    def __init__(self, headless: bool = False):
        """
        Initialize Facebook poster.
        
        Args:
            headless: Run browser in headless mode (default: False for first login)
        """
        self.headless = headless
        self.session_dir = Path("actions/facebook_session")
        self.session_dir.mkdir(exist_ok=True, parents=True)
        
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info(f"Initializing Facebook Poster")
        self._check_rate_limit()
        self._initialize_browser()

    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        try:
            if self.RATE_LIMIT_FILE.exists():
                with open(self.RATE_LIMIT_FILE, 'r') as f:
                    data = json.load(f)
                
                # Get posts from last 24 hours
                cutoff = datetime.now() - timedelta(days=1)
                recent_posts = [
                    datetime.fromisoformat(ts) 
                    for ts in data.get('posts', [])
                    if datetime.fromisoformat(ts) > cutoff
                ]
                
                if len(recent_posts) >= self.MAX_POSTS_PER_DAY:
                    logger.error(f"❌ Rate limit exceeded: {len(recent_posts)} posts in last 24 hours")
                    logger.error(f"   Maximum: {self.MAX_POSTS_PER_DAY} posts per day")
                    logger.error(f"   Please wait before posting again")
                    raise Exception("Rate limit exceeded")
                
                # Check minimum interval
                if recent_posts:
                    last_post = max(recent_posts)
                    time_since_last = datetime.now() - last_post
                    min_interval = timedelta(hours=self.MIN_INTERVAL_HOURS)
                    
                    if time_since_last < min_interval:
                        remaining = min_interval - time_since_last
                        logger.error(f"❌ Minimum interval not met")
                        logger.error(f"   Last post: {time_since_last.total_seconds() / 3600:.1f} hours ago")
                        logger.error(f"   Minimum: {self.MIN_INTERVAL_HOURS} hours")
                        logger.error(f"   Wait: {remaining.total_seconds() / 3600:.1f} more hours")
                        raise Exception("Minimum interval not met")
                
                logger.info(f"✅ Rate limit check passed ({len(recent_posts)}/{self.MAX_POSTS_PER_DAY} posts today)")
        
        except FileNotFoundError:
            logger.info("No rate limit history found - creating new")
        except json.JSONDecodeError:
            logger.warning("Rate limit file corrupted - resetting")

    def _record_post(self):
        """Record a post for rate limiting"""
        try:
            data = {'posts': []}
            if self.RATE_LIMIT_FILE.exists():
                with open(self.RATE_LIMIT_FILE, 'r') as f:
                    data = json.load(f)
            
            data['posts'].append(datetime.now().isoformat())
            
            # Keep only last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            data['posts'] = [
                ts for ts in data['posts']
                if datetime.fromisoformat(ts) > cutoff
            ]
            
            with open(self.RATE_LIMIT_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Post recorded for rate limiting")
        
        except Exception as e:
            logger.warning(f"Could not record post: {e}")

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
            self._navigate_to_facebook()
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def _navigate_to_facebook(self):
        """Navigate to Facebook and handle login if needed"""
        try:
            logger.info("Navigating to Facebook...")
            self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=60000)
            
            # Wait for network to settle
            time.sleep(3)
            
            # Check if we need to login
            current_url = self.page.url
            
            if 'login' in current_url or self.page.query_selector(self.SELECTORS['login_email']):
                logger.warning("=" * 80)
                logger.warning("LOGIN REQUIRED - FIRST TIME SETUP")
                logger.warning("=" * 80)
                logger.warning("Please log in to Facebook in the browser window")
                logger.warning("1. Enter your email and password")
                logger.warning("2. Complete any 2FA if required")
                logger.warning("3. Wait for feed to load")
                logger.warning("=" * 80)
                
                # Wait for user to login (check for feed)
                logger.info("Waiting for login... (timeout: 180 seconds)")
                try:
                    # Wait for feed to appear
                    self.page.wait_for_selector(self.SELECTORS['feed'], timeout=180000)
                    logger.info("✅ Login successful! Session saved.")
                except PlaywrightTimeout:
                    logger.error("Login timeout - please try again")
                    raise Exception("Facebook login timeout")
                
                time.sleep(3)
            else:
                logger.info("✅ Already logged in (session restored)")
            
            # Verify we're logged in
            logger.info("Verifying Facebook feed loaded...")
            
            logged_in = False
            
            # Strategy 1: Look for "What's on your mind" composer
            try:
                for selector in [self.SELECTORS['create_post_primary'],
                               self.SELECTORS['create_post_alt1'],
                               self.SELECTORS['create_post_clickable']]:
                    if self.page.query_selector(selector):
                        logger.info(f"✅ Found create post button with: {selector}")
                        logged_in = True
                        break
            except:
                pass
            
            # Strategy 2: Look for feed
            if not logged_in:
                try:
                    if self.page.query_selector(self.SELECTORS['feed']) or self.page.query_selector(self.SELECTORS['main_feed']):
                        logger.info("✅ Found feed - logged in")
                        logged_in = True
                except:
                    pass
            
            if logged_in:
                # Take success screenshot
                screenshot_path = Path("Logs") / f"facebook_login_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"✅ Login verified! Screenshot: {screenshot_path}")
            else:
                logger.warning("⚠️  Could not verify login - may need manual check")
                screenshot_path = Path("Logs") / f"facebook_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.page.screenshot(path=str(screenshot_path))
                logger.warning(f"Debug screenshot: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Facebook: {e}")
            raise

    def post_to_facebook(self, text: str, image_path: Optional[str] = None, visibility: str = 'public') -> bool:
        """
        Post content to Facebook.
        
        Args:
            text: Post text content
            image_path: Optional path to image to attach
            visibility: Post visibility (public, friends, only_me)
            
        Returns:
            True if post was successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info("POSTING TO FACEBOOK")
            logger.info("=" * 80)
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Image: {image_path if image_path else 'None'}")
            logger.info(f"Visibility: {visibility}")
            
            # Ensure we're on the feed
            if 'facebook.com' not in self.page.url or 'login' in self.page.url:
                logger.info("Navigating to Facebook feed...")
                self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
            
            # Click "What's on your mind" to open composer
            logger.info("Opening post composer...")
            composer_opened = False
            
            for selector in [self.SELECTORS['create_post_primary'],
                           self.SELECTORS['create_post_alt1'],
                           self.SELECTORS['create_post_alt2'],
                           self.SELECTORS['create_post_clickable']]:
                try:
                    create_button = self.page.wait_for_selector(selector, timeout=5000)
                    if create_button:
                        logger.info(f"Found create post button with: {selector}")
                        create_button.click()
                        time.sleep(2)
                        composer_opened = True
                        break
                except PlaywrightTimeout:
                    continue
            
            if not composer_opened:
                logger.error("Could not find 'What's on your mind' button")
                raise Exception("Could not open post composer")
            
            # Wait for post modal/textarea to appear
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
                    # Look for photo/video button
                    photo_button = None
                    for selector in [self.SELECTORS['photo_button_primary'],
                                   self.SELECTORS['photo_button_alt1']]:
                        try:
                            photo_button = self.page.query_selector(selector)
                            if photo_button:
                                logger.info(f"Found photo button with: {selector}")
                                photo_button.click()
                                time.sleep(1)
                                break
                        except:
                            continue
                    
                    # Find file input and upload
                    file_input = self.page.query_selector(self.SELECTORS['photo_input'])
                    if file_input:
                        file_input.set_input_files(image_path)
                        time.sleep(3)
                        logger.info("✅ Image uploaded")
                    else:
                        logger.warning("Could not find image upload input")
                except Exception as e:
                    logger.warning(f"Image upload failed: {e}")
            
            # Set visibility if not public
            if visibility.lower() != 'public':
                logger.info(f"Setting visibility to: {visibility}")
                try:
                    audience_button = self.page.query_selector(self.SELECTORS['audience_button'])
                    if audience_button:
                        audience_button.click()
                        time.sleep(1)
                        
                        # Select appropriate visibility
                        if visibility.lower() == 'friends':
                            selector = self.SELECTORS['audience_friends']
                        elif visibility.lower() == 'only_me':
                            selector = self.SELECTORS['audience_only_me']
                        else:
                            selector = self.SELECTORS['audience_public']
                        
                        visibility_option = self.page.query_selector(selector)
                        if visibility_option:
                            visibility_option.click()
                            time.sleep(1)
                            logger.info(f"✅ Visibility set to: {visibility}")
                    else:
                        logger.warning("Could not find audience selector")
                except Exception as e:
                    logger.warning(f"Could not set visibility: {e}")
            
            # Take screenshot before posting
            screenshot_path = Path("Logs") / f"facebook_pre_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Click Post button
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
            
            # Wait for post to complete
            time.sleep(5)
            
            # Verify post was successful
            logger.info("✅ Post published successfully!")
            
            # Take screenshot after posting
            screenshot_path = Path("Logs") / f"facebook_post_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Success screenshot: {screenshot_path}")
            
            # Record post for rate limiting
            self._record_post()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            # Take error screenshot
            try:
                screenshot_path = Path("Logs") / f"facebook_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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
    Post approved Facebook content from a file.
    
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
        
        # Extract post text
        post_text = extract_post_text(content)
        if not post_text:
            logger.error("Could not extract post text from file")
            return False
        
        # Extract image path if present
        image_path = extract_image_path(content)
        
        # Extract visibility
        visibility = extract_visibility(content)
        
        logger.info(f"Extracted post text ({len(post_text)} chars)")
        if image_path:
            logger.info(f"Image: {image_path}")
        logger.info(f"Visibility: {visibility}")
        
        # Initialize poster
        poster = FacebookPoster(headless=False)
        
        # Post to Facebook
        success = poster.post_to_facebook(post_text, image_path, visibility)
        
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
    """Extract post text from markdown file"""
    # Look for "## Post Text" section
    match = re.search(r'## Post Text\s*\n(.*?)\n##', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback: look for content after frontmatter
    parts = content.split('---')
    if len(parts) >= 3:
        body = parts[2].strip()
        lines = [line.strip() for line in body.split('\n') if line.strip() and not line.startswith('#')]
        if lines:
            return '\n'.join(lines[:20])
    
    return None


def extract_image_path(content: str) -> Optional[str]:
    """Extract image path from markdown file"""
    match = re.search(r'path:\s*(.+)', content)
    if match:
        path = match.group(1).strip()
        if Path(path).exists():
            return path
    return None


def extract_visibility(content: str) -> str:
    """Extract visibility setting from markdown file"""
    # Check frontmatter
    match = re.search(r'visibility:\s*(\w+)', content)
    if match:
        return match.group(1).strip().lower()
    
    # Check metadata section
    match = re.search(r'Visibility:\s*(\w+)', content, re.IGNORECASE)
    if match:
        return match.group(1).strip().lower()
    
    return 'public'  # Default


def move_to_done(file_path: str, success: bool = True):
    """Move posted file to Done/ with completion note"""
    filename = Path(file_path).name
    done_dir = Path("Approved") / "Done"
    done_dir.mkdir(exist_ok=True, parents=True)
    done_path = done_dir / filename
    
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
- **Platform**: Facebook
- **Posted by**: facebook_poster.py

<COMPLETE>
Posted to Facebook at {datetime.now().isoformat()}
</COMPLETE>
"""
    
    # Write to Done
    with open(done_path, 'w', encoding='utf-8') as f:
        f.write(content + note)
    
    # Remove from Approved
    os.remove(file_path)
    
    logger.info(f"File moved to Done/: {done_path}")


def main():
    """Main entry point for Facebook poster"""
    logger.info("=" * 80)
    logger.info("Facebook Poster - Gold Tier Phase 3")
    logger.info("=" * 80)
    logger.info("")
    
    if len(sys.argv) > 2 and sys.argv[1] == '--file':
        # Post specific file
        file_path = sys.argv[2]
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        
        success = post_approved_content(file_path)
        sys.exit(0 if success else 1)
    
    else:
        # Interactive mode - test posting
        logger.info("Interactive mode - Testing Facebook posting")
        logger.info("")
        
        test_text = """🚀 Testing automated Facebook posting!

This post was created and published automatically using:
• Python + Playwright
• Persistent browser session
• Human-in-the-loop approval workflow

The future of social media automation is here.

#Automation #AI #Facebook #Testing"""
        
        logger.info("Test post text:")
        logger.info(test_text)
        logger.info("")
        
        response = input("Post this test message to Facebook? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            poster = FacebookPoster(headless=False)
            success = poster.post_to_facebook(test_text)
            poster.cleanup()
            
            if success:
                logger.info("✅ Test post successful!")
            else:
                logger.error("❌ Test post failed")
        else:
            logger.info("Test cancelled")


if __name__ == "__main__":
    main()
