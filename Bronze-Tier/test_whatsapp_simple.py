"""
Simple WhatsApp test - just check if we can detect ANY unread messages
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def test_whatsapp_simple():
    """Simple test to see if WhatsApp is working at all"""
    
    session_dir = Path("Watchers/whatsapp_session")
    session_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("WhatsApp Simple Test")
    print("=" * 80)
    print("\nThis will:")
    print("1. Open WhatsApp Web")
    print("2. Wait for it to load")
    print("3. Try to find ANY indication of unread messages")
    print("4. Show you what it finds")
    print("\n")
    
    input("Press Enter to start (make sure you have unread messages in WhatsApp)...")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720},
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print("\n📱 Opening WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
        
        print("⏳ Waiting 20 seconds for page to load...")
        time.sleep(20)
        
        print("\n" + "=" * 80)
        print("🔍 SEARCHING FOR UNREAD INDICATORS")
        print("=" * 80)
        
        # Strategy 1: Look for green badges/dots
        print("\n1️⃣  Looking for green unread badges...")
        green_elements = page.query_selector_all('[style*="background"]')
        print(f"   Found {len(green_elements)} elements with background styles")
        
        # Strategy 2: Look for bold text (unread chats have bold names)
        print("\n2️⃣  Looking for bold text (unread chat names)...")
        bold_elements = page.query_selector_all('strong, b, [style*="font-weight"]')
        print(f"   Found {len(bold_elements)} bold elements")
        if bold_elements:
            for i, elem in enumerate(bold_elements[:5]):
                try:
                    text = elem.inner_text()
                    if text and len(text) < 50:
                        print(f"      - {text}")
                except:
                    pass
        
        # Strategy 3: Look for aria-label with "unread"
        print("\n3️⃣  Looking for aria-labels containing 'unread'...")
        unread_aria = page.query_selector_all('[aria-label*="unread" i]')
        print(f"   Found {len(unread_aria)} elements with 'unread' in aria-label")
        if unread_aria:
            for i, elem in enumerate(unread_aria[:3]):
                aria = elem.get_attribute('aria-label')
                print(f"      - {aria}")
        
        # Strategy 4: Look for spans with numbers (message counts)
        print("\n4️⃣  Looking for message count badges...")
        spans = page.query_selector_all('span')
        number_spans = []
        for span in spans[:200]:  # Check first 200 spans
            try:
                text = span.inner_text()
                if text and text.isdigit() and int(text) > 0 and int(text) < 100:
                    number_spans.append(text)
            except:
                pass
        print(f"   Found {len(number_spans)} spans with numbers: {number_spans[:10]}")
        
        # Strategy 5: Look for data-testid with "unread"
        print("\n5️⃣  Looking for data-testid containing 'unread'...")
        unread_testid = page.query_selector_all('[data-testid*="unread" i]')
        print(f"   Found {len(unread_testid)} elements")
        if unread_testid:
            for i, elem in enumerate(unread_testid[:3]):
                testid = elem.get_attribute('data-testid')
                print(f"      - data-testid='{testid}'")
        
        # Strategy 6: Look for any chat-like containers
        print("\n6️⃣  Looking for chat containers...")
        chat_containers = page.query_selector_all('div[role="row"], div[role="listitem"], div[role="gridcell"]')
        print(f"   Found {len(chat_containers)} potential chat containers")
        
        if chat_containers:
            print("\n   Analyzing first 3 chat containers:")
            for i, container in enumerate(chat_containers[:3]):
                print(f"\n   📦 Container {i+1}:")
                
                # Look for name
                title_elem = container.query_selector('span[title]')
                if title_elem:
                    name = title_elem.get_attribute('title')
                    print(f"      Name: {name}")
                
                # Look for unread indicators within this container
                has_bold = len(container.query_selector_all('strong')) > 0
                has_badge = container.query_selector('span[data-testid*="unread"]') is not None
                has_aria = container.query_selector('[aria-label*="unread" i]') is not None
                
                print(f"      Has bold text: {has_bold}")
                print(f"      Has unread badge: {has_badge}")
                print(f"      Has unread aria: {has_aria}")
                print(f"      Likely unread: {has_bold or has_badge or has_aria}")
        
        # Take screenshot
        screenshot_path = Path("Logs") / f"whatsapp_test_{int(time.time())}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE")
        print("=" * 80)
        print("\nThe browser will stay open for 30 seconds.")
        print("Please manually verify:")
        print("1. Do you see unread messages in the WhatsApp window?")
        print("2. Do they have green badges or bold text?")
        print("3. Right-click on an unread chat → Inspect → note the structure")
        print("\nPress Ctrl+C to close early...")
        print("=" * 80)
        
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n⏹️  Closing...")
        
        context.close()
        
    print("\n✅ Done!")

if __name__ == "__main__":
    test_whatsapp_simple()
