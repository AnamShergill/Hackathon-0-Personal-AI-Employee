"""
Run both Gmail and WhatsApp watchers simultaneously.
This script starts both watchers in separate threads.
"""

import threading
import logging
import sys
from pathlib import Path

# Ensure Logs directory exists
Path("Logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/both_watchers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_gmail_watcher():
    """Run Gmail watcher in a thread"""
    try:
        from Watchers.gmail_watcher import GmailWatcher
        logger.info("Starting Gmail Watcher thread...")
        watcher = GmailWatcher(interval=300)  # 5 minutes
        watcher.run_forever()
    except KeyboardInterrupt:
        logger.info("Gmail Watcher stopped by user")
    except Exception as e:
        logger.error(f"Gmail Watcher error: {e}")


def run_whatsapp_watcher():
    """Run WhatsApp watcher in a thread"""
    try:
        from Watchers.whatsapp_watcher import WhatsAppWatcher
        logger.info("Starting WhatsApp Watcher thread...")
        watcher = WhatsAppWatcher(interval=60, headless=False)  # 1 minute
        watcher.run_forever()
    except KeyboardInterrupt:
        logger.info("WhatsApp Watcher stopped by user")
    except Exception as e:
        logger.error(f"WhatsApp Watcher error: {e}")


def main():
    """Main entry point - run both watchers"""
    print("=" * 80)
    print("SILVER TIER - DUAL WATCHER SYSTEM")
    print("=" * 80)
    print()
    print("Starting both Gmail and WhatsApp watchers...")
    print()
    print("Gmail Watcher: Checks every 5 minutes for starred/important emails")
    print("WhatsApp Watcher: Checks every 60 seconds for unread messages")
    print()
    print("Both watchers will create .md files in Needs_Action/ folder")
    print()
    print("Press Ctrl+C to stop both watchers")
    print("=" * 80)
    print()
    
    # Create threads for both watchers
    gmail_thread = threading.Thread(target=run_gmail_watcher, name="GmailWatcher", daemon=True)
    whatsapp_thread = threading.Thread(target=run_whatsapp_watcher, name="WhatsAppWatcher", daemon=True)
    
    try:
        # Start both threads
        gmail_thread.start()
        logger.info("✅ Gmail Watcher thread started")
        
        whatsapp_thread.start()
        logger.info("✅ WhatsApp Watcher thread started")
        
        # Keep main thread alive
        gmail_thread.join()
        whatsapp_thread.join()
        
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("Stopping both watchers...")
        print("=" * 80)
        logger.info("Both watchers stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
