"""
Enhanced WhatsApp Web debugger - waits for page to fully load and provides detailed DOM inspection.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def debug_whatsapp_live():
    """Open WhatsApp Web and wait for it to fully load, then inspect"""
    
    session_dir = Path("Watchers/whatsapp_session")
    session_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("WhatsApp Web Live Debugger")
    print("=" * 80)
    print("\nThis will:")
    print("1. Open WhatsApp Web")
    print("2. Wait for it to FULLY load (30 seconds)")
    print("3. Inspect the actual DOM structure")
    print("4. Show you what selectors work")
    print("\n")
    
    with sync_playwright() as p:
        # Launch with persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720},
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print("📱 Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
        
        print("⏳ Waiting 30 seconds for WhatsApp to fully load...")
        print("   (This gives time for all dynamic content to render)")
        
        for i in range(30, 0, -5):
            print(f"   {i} seconds remaining...")
            time.sleep(5)
        
        print("\n" + "=" * 80)
        print("📊 PAGE STATE")
        print("=" * 80)
        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")
        
        # Check if logged in by looking for common elements
        print("\n🔍 Checking login status...")
        
        # Check for QR code (not logged in)
        qr_elements = page.query_selector_all('canvas')
        if qr_elements:
            print(f"⚠️  Found {len(qr_elements)} canvas elements (might be QR code)")
            print("   If you see a QR code, please scan it with your phone!")
        
        # Get ALL divs and check their attributes
        print("\n" + "=" * 80)
        print("🔎 ANALYZING PAGE STRUCTURE")
        print("=" * 80)
        
        all_divs = page.query_selector_all('div')
        print(f"Total <div> elements on page: {len(all_divs)}")
        
        # Count divs by role
        roles = {}
        testids = {}
        ids = {}
        
        for div in all_divs[:500]:  # Check first 500 divs
            role = div.get_attribute('role')
            if role:
                roles[role] = roles.get(role, 0) + 1
            
            testid = div.get_attribute('data-testid')
            if testid:
                testids[testid] = testids.get(testid, 0) + 1
            
            id_attr = div.get_attribute('id')
            if id_attr:
                ids[id_attr] = ids.get(id_attr, 0) + 1
        
        print("\n📋 Divs by ROLE attribute:")
        if roles:
            for role, count in sorted(roles.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   role='{role}': {count} elements")
        else:
            print("   ❌ No role attributes found")
        
        print("\n📋 Divs by DATA-TESTID attribute:")
        if testids:
            for testid, count in sorted(testids.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   data-testid='{testid}': {count} elements")
        else:
            print("   ❌ No data-testid attributes found")
        
        print("\n📋 Divs by ID attribute:")
        if ids:
            for id_attr, count in sorted(ids.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   id='{id_attr}': {count} elements")
        else:
            print("   ❌ No id attributes found")
        
        # Look for chat-like structures
        print("\n" + "=" * 80)
        print("💬 LOOKING FOR CHAT STRUCTURES")
        print("=" * 80)
        
        # Try to find anything that looks like a chat list
        potential_selectors = [
            ('Spans with title', 'span[title]'),
            ('Divs with aria-label', 'div[aria-label]'),
            ('Any role=button', '[role="button"]'),
            ('Any role=textbox', '[role="textbox"]'),
            ('Any contenteditable', '[contenteditable="true"]'),
            ('Images (avatars?)', 'img'),
            ('SVG icons', 'svg'),
        ]
        
        for name, selector in potential_selectors:
            elements = page.query_selector_all(selector)
            print(f"{name:30} | {selector:40} | Found: {len(elements)}")
            
            # Show first 3 examples
            if elements and len(elements) > 0:
                for i, elem in enumerate(elements[:3]):
                    try:
                        text = elem.inner_text()[:50] if elem.inner_text() else ""
                        aria = elem.get_attribute('aria-label')
                        aria_str = f" | aria-label: {aria[:30]}" if aria else ""
                        if text or aria:
                            print(f"   Example {i+1}: {text}{aria_str}")
                    except:
                        pass
        
        # Take a screenshot
        screenshot_path = Path("Logs") / f"whatsapp_debug_{int(time.time())}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
        print("\n" + "=" * 80)
        print("🔧 MANUAL INSPECTION TIME")
        print("=" * 80)
        print("The browser will stay open for 60 seconds.")
        print("\nPlease:")
        print("1. Look at the browser window")
        print("2. Right-click on a chat in the list → Inspect")
        print("3. Look for stable attributes (data-testid, role, id, class)")
        print("4. Note the parent container structure")
        print("\nPress Ctrl+C to close early...")
        print("=" * 80)
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n⏹️  Closing browser...")
        
        context.close()
        
    print("\n✅ Debug session complete!")
    print("\nNext steps:")
    print("1. Review the output above")
    print("2. Update SELECTORS in whatsapp_watcher.py")
    print("3. Test again with: python Watchers/whatsapp_watcher.py")

if __name__ == "__main__":
    debug_whatsapp_live()
