"""
LinkedIn Setup Script - First-Time Configuration
This script guides you through setting up LinkedIn posting automation.
"""

import sys
import time
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_step(number, text):
    """Print step number"""
    print(f"\n{'='*80}")
    print(f"STEP {number}: {text}")
    print('='*80 + "\n")


def check_dependencies():
    """Check if all dependencies are installed"""
    print_step(1, "Checking Dependencies")
    
    deps = {
        'schedule': 'import schedule',
        'playwright': 'from playwright.sync_api import sync_playwright',
        'yaml': 'import yaml',
    }
    
    missing = []
    for name, import_stmt in deps.items():
        try:
            exec(import_stmt)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nRun these commands:")
        if 'schedule' in missing:
            print("  uv pip install schedule --system")
        if 'playwright' in missing:
            print("  uv pip install playwright --system")
            print("  playwright install chromium")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_folders():
    """Check if required folders exist"""
    print_step(2, "Checking Folders")
    
    folders = [
        "Watchers/linkedin_session",
        "Pending_Approval",
        "Approved",
        "Logs"
    ]
    
    for folder in folders:
        path = Path(folder)
        if path.exists():
            print(f"✅ {folder} exists")
        else:
            print(f"⚠️  Creating {folder}...")
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {folder} created")
    
    print("\n✅ All folders ready!")
    return True


def setup_linkedin_session():
    """Guide user through LinkedIn login"""
    print_step(3, "LinkedIn First-Time Login")
    
    print("This will open LinkedIn in a browser for you to login.")
    print()
    print("What will happen:")
    print("  1. Browser opens to LinkedIn")
    print("  2. You login with your email/password")
    print("  3. Complete any 2FA if required")
    print("  4. Session is saved automatically")
    print("  5. Future runs will reuse this session")
    print()
    print("⚠️  IMPORTANT:")
    print("  - Use your real LinkedIn credentials")
    print("  - Session is stored locally (never shared)")
    print("  - You only need to do this ONCE")
    print()
    
    response = input("Ready to proceed? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Setup cancelled. Run this script again when ready.")
        return False
    
    print("\n🚀 Launching LinkedIn poster...")
    print("   (Browser will open in a moment...)")
    print()
    
    # Import and run linkedin poster
    try:
        sys.path.insert(0, '.')
        from Watchers.linkedin_poster import LinkedInPoster
        
        print("Opening browser...")
        poster = LinkedInPoster(headless=False)
        
        print("\n" + "=" * 80)
        print("BROWSER OPENED - Please complete login")
        print("=" * 80)
        print()
        print("In the browser window:")
        print("  1. Enter your LinkedIn email")
        print("  2. Enter your password")
        print("  3. Complete 2FA if prompted")
        print("  4. Wait for feed to load")
        print()
        print("This script will wait for you...")
        print("=" * 80)
        
        # Wait for user to login
        time.sleep(10)
        
        # Check if logged in
        current_url = poster.page.url
        if 'feed' in current_url or 'mynetwork' in current_url:
            print("\n✅ Login successful! Session saved.")
            print(f"   Current URL: {current_url}")
            
            # Take screenshot
            screenshot_path = Path("Logs") / "linkedin_setup_success.png"
            poster.page.screenshot(path=str(screenshot_path))
            print(f"   Screenshot: {screenshot_path}")
            
            poster.cleanup()
            return True
        else:
            print(f"\n⚠️  Current URL: {current_url}")
            print("   Please complete login in the browser...")
            print("   Press Enter when you see your LinkedIn feed...")
            input()
            
            # Check again
            current_url = poster.page.url
            if 'feed' in current_url or 'mynetwork' in current_url or 'linkedin.com' in current_url:
                print("\n✅ Login successful! Session saved.")
                screenshot_path = Path("Logs") / "linkedin_setup_success.png"
                poster.page.screenshot(path=str(screenshot_path))
                print(f"   Screenshot: {screenshot_path}")
                poster.cleanup()
                return True
            else:
                print("\n❌ Login may have failed. Please try again.")
                poster.cleanup()
                return False
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        return False


def test_posting():
    """Test posting functionality"""
    print_step(4, "Test Posting (Optional)")
    
    print("Would you like to test posting a message to LinkedIn?")
    print()
    print("This will post a test message to your LinkedIn feed.")
    print("⚠️  This will be PUBLICLY VISIBLE on your profile!")
    print()
    
    response = input("Post a test message? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n⏭️  Skipping test post. You can test later with:")
        print("   python Watchers/linkedin_poster.py")
        return True
    
    test_text = """🚀 Testing automated LinkedIn posting!

This post was created and published automatically using:
• Python + Playwright
• Persistent browser session
• Human-in-the-loop approval workflow

The future of social media automation is here.

#Automation #AI #LinkedIn #Testing"""
    
    print("\n📝 Test post text:")
    print("-" * 80)
    print(test_text)
    print("-" * 80)
    print()
    
    response = input("Confirm posting this to LinkedIn? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n⏭️  Test post cancelled.")
        return True
    
    try:
        sys.path.insert(0, '.')
        from Watchers.linkedin_poster import LinkedInPoster
        
        print("\n🚀 Posting to LinkedIn...")
        poster = LinkedInPoster(headless=False)
        success = poster.post_to_linkedin(test_text)
        poster.cleanup()
        
        if success:
            print("\n✅ Test post successful!")
            print("   Check your LinkedIn feed to see the post")
            return True
        else:
            print("\n❌ Test post failed. Check logs for details.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test post: {e}")
        return False


def print_summary():
    """Print setup summary"""
    print_header("SETUP COMPLETE!")
    
    print("✅ LinkedIn automation is now configured!")
    print()
    print("What you can do now:")
    print()
    print("1. Generate LinkedIn posts:")
    print("   python -c \"exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])\"")
    print()
    print("2. Review posts in Pending_Approval/:")
    print("   ls Pending_Approval/")
    print("   cat Pending_Approval/linkedin_post_*.md")
    print()
    print("3. Approve posts (move to Approved/):")
    print("   mv Pending_Approval/linkedin_post_*.md Approved/")
    print()
    print("4. Start approved watcher (auto-posts approved content):")
    print("   python Watchers/approved_watcher.py")
    print()
    print("5. Or post manually:")
    print("   python Watchers/linkedin_poster.py Approved/linkedin_post_*.md")
    print()
    print("6. Start all watchers:")
    print("   python run_all_watchers.py")
    print()
    print("📚 Documentation:")
    print("   - START_HERE.md - Quick start guide")
    print("   - QUICK_REFERENCE.md - Command reference")
    print("   - INSTALL_AND_TEST.md - Detailed testing")
    print()
    print("🎉 Silver Tier is now 100% complete!")
    print()


def main():
    """Main setup flow"""
    print_header("LinkedIn Automation Setup")
    print("This script will guide you through setting up LinkedIn posting.")
    print()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return False
    
    # Step 2: Check folders
    if not check_folders():
        print("\n❌ Folder setup failed.")
        return False
    
    # Step 3: LinkedIn login
    if not setup_linkedin_session():
        print("\n❌ LinkedIn setup failed. Please try again.")
        return False
    
    # Step 4: Test posting (optional)
    test_posting()
    
    # Summary
    print_summary()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
