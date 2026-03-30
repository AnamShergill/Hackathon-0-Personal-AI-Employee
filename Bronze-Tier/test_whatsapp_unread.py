"""
Test WhatsApp watcher with enhanced debugging to detect unread messages.
This will run ONE cycle and show detailed analysis of the first 5 chats.
"""

import logging
from Watchers.whatsapp_watcher import WhatsAppWatcher

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_unread_detection():
    """Test unread message detection with debug output"""
    
    print("=" * 80)
    print("WhatsApp Unread Detection Test")
    print("=" * 80)
    print()
    print("This will:")
    print("1. Open WhatsApp Web (reuse existing session)")
    print("2. Analyze the first 5 chats with detailed logging")
    print("3. Try to detect unread messages")
    print("4. Run ONE check cycle then exit")
    print()
    print("Make sure you have sent yourself a test message!")
    print("=" * 80)
    print()
    
    try:
        # Create watcher with scan_all mode for debugging
        watcher = WhatsAppWatcher(interval=60, headless=False, scan_all=True)
        
        # Run one cycle
        logger.info("Running ONE check cycle...")
        result = watcher.run_once()
        
        logger.info(f"Check complete! Processed {result} messages")
        
        # Keep browser open for manual inspection
        print("\n" + "=" * 80)
        print("Browser will stay open for 30 seconds for manual inspection")
        print("Check the console output above to see what was detected")
        print("=" * 80)
        
        import time
        time.sleep(30)
        
        # Cleanup
        watcher.cleanup()
        
        print("\n✅ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unread_detection()
