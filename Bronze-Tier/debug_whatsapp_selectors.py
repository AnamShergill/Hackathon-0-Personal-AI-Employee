"""
Debug script to inspect WhatsApp Web DOM and find working selectors.
Run this to see what elements are available on the page.
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def debug_whatsapp_selectors():
    """Open WhatsApp Web and inspect available selectors"""
    
    session_dir = Path("Watchers/whatsapp_session")
    session_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("WhatsApp Web Selector Debugger")
    print("=" * 80)
    print("\nThis will open WhatsApp Web and inspect the DOM structure.")
    print("The browser will stay open for 60 seconds for manual inspection.")
    print("\n")
    
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
        print("PAGE INFORMATION")
        print("=" * 80)
        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")
        print()
        
        # Test various selectors
        selectors_to_test = [
            ("QR Code Canvas", 'canvas[aria-label*="Scan"]'),
            ("Search Box (contenteditable)", 'div[contenteditable="true"]'),
            ("Side Pane (ID)", '#pane-side'),
            ("Chat List (data-testid)", '[data-testid="chat-list"]'),
            ("Chat Items (role=row)", 'div[role="row"]'),
            ("Chat Items (role=listitem)", 'div[role="listitem"]'),
            ("Chat Items (role=gridcell)", 'div[role="gridcell"]'),
            ("Grid Container", 'div[role="grid"]'),
            ("List Container", 'div[role="list"]'),
            ("Main Element", 'main'),
            ("Conversation Panel", '[data-testid="conversation-panel-body"]'),
            ("Cell Frame Container", '[data-testid^="cell-frame-container"]'),
        ]
        
        print("=" * 80)
        print("SELECTOR TEST RESULTS")
        print("=" * 80)
        
        for name, selector in selectors_to_test:
            try:
                elements = page.query_selector_all(selector)
                count = len(elements)
                status = "✅" if count > 0 else "❌"
                print(f"{status} {name:40} | Selector: {selector:50} | Found: {count}")
                
                # If found, show first element details
                if count > 0 and elements[0]:
                    elem = elements[0]
                    try:
                        # Get attributes
                        attrs = []
                        for attr in ['id', 'class', 'role', 'aria-label', 'data-testid']:
                            val = elem.get_attribute(attr)
                            if val:
                                attrs.append(f"{attr}='{val[:50]}'")
                        if attrs:
                            print(f"   └─ Attributes: {', '.join(attrs)}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ {name:40} | Error: {str(e)[:50]}")
        
        print("\n" + "=" * 80)
        print("MANUAL INSPECTION")
        print("=" * 80)
        print("The browser will stay open for 60 seconds.")
        print("You can:")
        print("1. Right-click on the chat list → Inspect")
        print("2. Look for stable attributes (data-testid, role, id)")
        print("3. Note the structure of chat items")
        print("4. Check console for any errors")
        print("\nPress Ctrl+C to close early, or wait 60 seconds...")
        print("=" * 80)
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nClosing browser...")
        
        context.close()
        
    print("\n✅ Debug session complete!")
    print("Update the SELECTORS dictionary in whatsapp_watcher.py based on findings.")

if __name__ == "__main__":
    debug_whatsapp_selectors()
