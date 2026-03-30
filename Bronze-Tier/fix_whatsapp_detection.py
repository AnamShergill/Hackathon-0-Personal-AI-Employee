"""
Quick fix script for WhatsApp detection issues.
This will help diagnose why the watcher shows 0 unread chats.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
from datetime import datetime

def fix_whatsapp_detection():
    """Interactive script to fix WhatsApp detection"""
    
    print("=" * 80)
    print("WhatsApp Detection Fix Script")
    print("=" * 80)
    print()
    print("This script will help you fix the '0 unread chats' issue.")
    print()
    print("BEFORE RUNNING:")
    print("1. Make sure you have at least ONE unread message in WhatsApp")
    print("2. Don't open that message on your phone (keep it unread)")
    print("3. Close any other WhatsApp Web tabs")
    print()
    
    input("Press Enter when ready...")
    
    session_dir = Path("Watchers/whatsapp_session")
    session_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        print("\n📱 Opening WhatsApp Web...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720},
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
        
        print("⏳ Waiting 15 seconds for WhatsApp to load...")
        time.sleep(15)
        
        print("\n" + "=" * 80)
        print("STEP 1: Checking if WhatsApp is loaded")
        print("=" * 80)
        
        # Check if logged in
        qr_code = page.query_selector('canvas[aria-label*="Scan"]')
        if qr_code:
            print("❌ NOT LOGGED IN - QR code detected")
            print("\nPlease:")
            print("1. Scan the QR code with your phone")
            print("2. Wait for it to load")
            print("3. Press Enter when you see your chats")
            input()
            time.sleep(5)
        else:
            print("✅ Already logged in")
        
        print("\n" + "=" * 80)
        print("STEP 2: Finding chat list container")
        print("=" * 80)
        
        # Try multiple selectors for chat list
        chat_list_selectors = [
            ('[data-testid="chat-list"]', 'data-testid'),
            ('div[role="grid"]', 'role=grid'),
            ('#pane-side', 'id=pane-side'),
            ('div[aria-label*="Chat list" i]', 'aria-label'),
        ]
        
        chat_list = None
        working_selector = None
        
        for selector, name in chat_list_selectors:
            elem = page.query_selector(selector)
            if elem:
                print(f"✅ Found chat list using: {name}")
                print(f"   Selector: {selector}")
                chat_list = elem
                working_selector = selector
                break
            else:
                print(f"❌ Not found: {name}")
        
        if not chat_list:
            print("\n⚠️  Could not find chat list with any selector!")
            print("\nManual check:")
            print("1. Do you see your chats in the browser window?")
            print("2. If YES, the selectors need updating")
            print("3. If NO, WhatsApp hasn't loaded properly")
            
            # Take screenshot
            screenshot_path = Path("Logs") / f"whatsapp_no_chatlist_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            print("\nPlease inspect the page manually and update selectors.")
            context.close()
            return
        
        print("\n" + "=" * 80)
        print("STEP 3: Finding chat items")
        print("=" * 80)
        
        # Try multiple selectors for chat items
        chat_item_selectors = [
            ('div[role="row"]', 'role=row'),
            ('div[role="listitem"]', 'role=listitem'),
            ('div[role="gridcell"]', 'role=gridcell'),
            ('[data-testid^="cell-frame-container"]', 'data-testid'),
        ]
        
        chat_items = []
        working_item_selector = None
        
        for selector, name in chat_item_selectors:
            items = page.query_selector_all(selector)
            if items and len(items) > 0:
                print(f"✅ Found {len(items)} chat items using: {name}")
                print(f"   Selector: {selector}")
                chat_items = items
                working_item_selector = selector
                break
            else:
                print(f"❌ Not found: {name}")
        
        if not chat_items:
            print("\n⚠️  Could not find any chat items!")
            print("\nThis means the chat list is empty or selectors are wrong.")
            screenshot_path = Path("Logs") / f"whatsapp_no_items_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            context.close()
            return
        
        print(f"\n✅ Found {len(chat_items)} total chats")
        
        print("\n" + "=" * 80)
        print("STEP 4: Detecting unread messages")
        print("=" * 80)
        
        unread_chats = []
        
        print("\nAnalyzing first 10 chats for unread indicators...")
        for i, chat_item in enumerate(chat_items[:10]):
            # Get chat name
            title_elem = chat_item.query_selector('span[title]')
            chat_name = title_elem.get_attribute('title') if title_elem else f"Chat #{i+1}"
            
            # Check multiple unread indicators
            indicators = {
                'badge_count': chat_item.query_selector('span[data-testid="icon-unread-count"]') is not None,
                'unread_aria': chat_item.query_selector('[aria-label*="unread" i]') is not None,
                'unread_icon': chat_item.query_selector('span[data-icon*="unread"]') is not None,
                'bold_text': len(chat_item.query_selector_all('strong')) > 0,
                'green_badge': chat_item.query_selector('span[style*="background-color: rgb(37, 211, 102)"]') is not None,
            }
            
            is_unread = any(indicators.values())
            
            if is_unread:
                unread_chats.append((chat_name, indicators))
                print(f"\n✅ UNREAD: {chat_name[:40]}")
                for indicator, found in indicators.items():
                    if found:
                        print(f"   - {indicator}: ✅")
            else:
                print(f"   {chat_name[:40]}: No unread indicators")
        
        print(f"\n" + "=" * 80)
        print(f"RESULTS: Found {len(unread_chats)} unread chats")
        print("=" * 80)
        
        if len(unread_chats) == 0:
            print("\n⚠️  NO UNREAD CHATS DETECTED")
            print("\nPossible reasons:")
            print("1. You don't have any unread messages")
            print("2. The unread indicators have changed (WhatsApp update)")
            print("3. Messages are marked as read automatically")
            print("\nManual check:")
            print("- Look at the browser window")
            print("- Do you see any chats with green badges or bold text?")
            print("- If YES, the detection logic needs updating")
            print("- If NO, send yourself a test message")
            
            # Take screenshot
            screenshot_path = Path("Logs") / f"whatsapp_no_unread_{int(time.time())}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            
        else:
            print(f"\n✅ SUCCESS! Detected {len(unread_chats)} unread chats:")
            for chat_name, indicators in unread_chats:
                print(f"   - {chat_name}")
            
            print("\n" + "=" * 80)
            print("STEP 5: Testing message extraction")
            print("=" * 80)
            
            # Try to extract from first unread chat
            print(f"\nOpening first unread chat: {unread_chats[0][0]}")
            
            # Find and click the first unread chat
            for chat_item in chat_items[:10]:
                title_elem = chat_item.query_selector('span[title]')
                if title_elem and title_elem.get_attribute('title') == unread_chats[0][0]:
                    chat_item.click()
                    time.sleep(2)
                    break
            
            # Try to find message container
            container_selectors = [
                'div[data-testid="conversation-panel-body"]',
                'div[data-testid="conversation-panel-messages"]',
                'div[role="application"]',
                'div.copyable-area',
            ]
            
            message_container = None
            for selector in container_selectors:
                container = page.query_selector(selector)
                if container:
                    print(f"✅ Found message container: {selector}")
                    message_container = container
                    break
            
            if message_container:
                # Try to find message bubbles
                bubbles = message_container.query_selector_all('div[data-testid="msg-container"]')
                if not bubbles:
                    bubbles = message_container.query_selector_all('span.selectable-text')
                
                print(f"✅ Found {len(bubbles)} message elements")
                
                if bubbles:
                    # Extract last message
                    last_bubble = bubbles[-1]
                    text_elements = last_bubble.query_selector_all('span.selectable-text, span[dir="ltr"]')
                    text = ' '.join([el.inner_text() for el in text_elements if el.inner_text()])
                    
                    if text:
                        print(f"\n✅ Extracted message text:")
                        print(f"   {text[:100]}...")
                    else:
                        print("\n⚠️  Could not extract message text")
            else:
                print("❌ Could not find message container")
        
        # Save working selectors
        print("\n" + "=" * 80)
        print("RECOMMENDED SELECTORS")
        print("=" * 80)
        
        if working_selector and working_item_selector:
            print("\nUpdate these in Watchers/whatsapp_watcher.py:")
            print(f"\n'chat_list_primary': '{working_selector}',")
            print(f"'chat_item': '{working_item_selector}',")
            
            # Save to file
            config_file = Path("whatsapp_selectors_working.txt")
            with open(config_file, 'w') as f:
                f.write(f"# Working selectors found on {datetime.now()}\n")
                f.write(f"chat_list_primary = '{working_selector}'\n")
                f.write(f"chat_item = '{working_item_selector}'\n")
                f.write(f"\n# Unread detection:\n")
                if unread_chats:
                    for indicator, found in unread_chats[0][1].items():
                        if found:
                            f.write(f"# - {indicator} works\n")
            
            print(f"\n✅ Saved to: {config_file}")
        
        print("\n" + "=" * 80)
        print("Browser will stay open for 30 seconds for manual inspection")
        print("Press Ctrl+C to close early...")
        print("=" * 80)
        
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        
        context.close()
    
    print("\n✅ Diagnostic complete!")
    print("\nNext steps:")
    print("1. Review the output above")
    print("2. Update selectors in Watchers/whatsapp_watcher.py if needed")
    print("3. Test with: python Watchers/whatsapp_watcher.py")

if __name__ == "__main__":
    fix_whatsapp_detection()
