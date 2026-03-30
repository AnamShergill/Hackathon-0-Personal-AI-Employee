"""
Debug script to inspect WhatsApp chat items and understand unread detection.
This will open WhatsApp Web and analyze the first 10 chat items.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def debug_unread_detection():
    """Inspect chat items to understand unread indicators"""
    
    session_dir = Path("Watchers/whatsapp_session")
    session_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("WhatsApp Unread Message Detection Debugger")
    print("=" * 80)
    print("\nThis will analyze your WhatsApp chats to find unread indicators.")
    print("Make sure you have at least one unread message!\n")
    
    with sync_playwright() as p:
        # Launch with persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720},
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
        
        print("Waiting for page to load...")
        time.sleep(10)
        
        print("\n" + "=" * 80)
        print("ANALYZING CHAT ITEMS")
        print("=" * 80)
        
        # Find chat items
        chat_items = page.query_selector_all('div[role="row"]')
        
        if not chat_items:
            chat_items = page.query_selector_all('div[role="listitem"]')
        
        print(f"\nFound {len(chat_items)} chat items")
        print("\nAnalyzing first 10 chats...\n")
        
        for idx, chat_item in enumerate(chat_items[:10]):
            print(f"\n{'='*60}")
            print(f"CHAT #{idx + 1}")
            print(f"{'='*60}")
            
            try:
                # Get chat name/title
                title_elem = chat_item.query_selector('span[title]')
                chat_name = title_elem.get_attribute('title') if title_elem else "Unknown"
                print(f"Chat Name: {chat_name}")
                
                # Check various unread indicators
                indicators = []
                
                # 1. Unread count badge
                unread_badge = chat_item.query_selector('span[data-testid="icon-unread-count"]')
                if unread_badge:
                    count = unread_badge.inner_text()
                    indicators.append(f"✅ Unread badge: {count}")
                else:
                    indicators.append("❌ No unread badge")
                
                # 2. Aria-label with "unread"
                unread_aria = chat_item.query_selector('div[aria-label*="unread" i]')
                if unread_aria:
                    aria_text = unread_aria.get_attribute('aria-label')
                    indicators.append(f"✅ Unread aria-label: {aria_text[:50]}")
                else:
                    indicators.append("❌ No unread aria-label")
                
                # 3. Unread icon markers
                unread_icons = chat_item.query_selector_all('span[data-icon*="unread"]')
                if unread_icons and len(unread_icons) > 0:
                    indicators.append(f"✅ Unread icon markers: {len(unread_icons)}")
                else:
                    indicators.append("❌ No unread icon markers")
                
                # 4. Bold text (strong tags)
                bold_elements = chat_item.query_selector_all('strong')
                if bold_elements and len(bold_elements) > 0:
                    bold_texts = [elem.inner_text()[:30] for elem in bold_elements[:2]]
                    indicators.append(f"✅ Bold elements: {len(bold_elements)} - {bold_texts}")
                else:
                    indicators.append("❌ No bold elements")
                
                # 5. Check for green dot or status indicators
                status_icons = chat_item.query_selector_all('span[data-icon="status-unread"], span[data-icon="unread-count"]')
                if status_icons and len(status_icons) > 0:
                    indicators.append(f"✅ Status icons: {len(status_icons)}")
                else:
                    indicators.append("❌ No status icons")
                
                # 6. Check all data-testid attributes
                all_testids = chat_item.query_selector_all('[data-testid]')
                testid_list = []
                for elem in all_testids[:5]:
                    testid = elem.get_attribute('data-testid')
                    if testid:
                        testid_list.append(testid)
                if testid_list:
                    indicators.append(f"📋 data-testid found: {', '.join(testid_list)}")
                
                # Print all indicators
                for indicator in indicators:
                    print(f"  {indicator}")
                
                # Get the HTML structure (first 500 chars)
                html = chat_item.inner_html()[:500]
                print(f"\n  HTML Preview: {html}...")
                
            except Exception as e:
                print(f"  ❌ Error analyzing chat: {e}")
        
        print("\n" + "=" * 80)
        print("MANUAL INSPECTION")
        print("=" * 80)
        print("\nThe browser will stay open for 60 seconds.")
        print("Please:")
        print("1. Look at your unread chats")
        print("2. Right-click on an unread chat → Inspect")
        print("3. Look for unique attributes (green dot, badge, bold text)")
        print("4. Note any data-testid or aria-label values")
        print("\nPress Ctrl+C to close early...")
        print("=" * 80)
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nClosing browser...")
        
        context.close()
        
    print("\n✅ Debug session complete!")
    print("\nBased on findings, update the unread detection logic in whatsapp_watcher.py")

if __name__ == "__main__":
    debug_unread_detection()
