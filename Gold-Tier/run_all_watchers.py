"""
Master Runner - Start All Watchers and Scheduler
Starts all watchers in separate threads for easy management.
"""

import threading
import logging
import sys
import time
from pathlib import Path

# Ensure Logs directory exists
Path("Logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/master_runner.log'),
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


def run_approved_watcher():
    """Run Approved watcher in a thread"""
    try:
        from Watchers.approved_watcher import ApprovedWatcher
        logger.info("Starting Approved Watcher thread...")
        watcher = ApprovedWatcher(interval=30)  # 30 seconds
        watcher.run_forever()
    except KeyboardInterrupt:
        logger.info("Approved Watcher stopped by user")
    except Exception as e:
        logger.error(f"Approved Watcher error: {e}")


def run_scheduler():
    """Run scheduler in a thread"""
    try:
        import sys
        sys.path.insert(0, '.')
        from schedulers.daily_runner import setup_schedule
        import schedule
        
        logger.info("Starting Scheduler thread...")
        setup_schedule()
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")


def main():
    """Main entry point - run all watchers and scheduler"""
    print("=" * 80)
    print("SILVER TIER - MASTER RUNNER")
    print("=" * 80)
    print()
    print("Starting all watchers and scheduler...")
    print()
    print("Components:")
    print("  1. Gmail Watcher (300s interval)")
    print("  2. WhatsApp Watcher (60s interval)")
    print("  3. Approved Watcher (30s interval)")
    print("  4. Scheduler (daily tasks)")
    print()
    print("Press Ctrl+C to stop all components")
    print("=" * 80)
    print()
    
    # Create threads for all components
    threads = []
    
    # Gmail watcher
    gmail_thread = threading.Thread(target=run_gmail_watcher, name="GmailWatcher", daemon=True)
    threads.append(("Gmail Watcher", gmail_thread))
    
    # WhatsApp watcher
    whatsapp_thread = threading.Thread(target=run_whatsapp_watcher, name="WhatsAppWatcher", daemon=True)
    threads.append(("WhatsApp Watcher", whatsapp_thread))
    
    # Approved watcher
    approved_thread = threading.Thread(target=run_approved_watcher, name="ApprovedWatcher", daemon=True)
    threads.append(("Approved Watcher", approved_thread))
    
    # Scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, name="Scheduler", daemon=True)
    threads.append(("Scheduler", scheduler_thread))
    
    try:
        # Start all threads
        for name, thread in threads:
            thread.start()
            logger.info(f"✅ {name} thread started")
            time.sleep(2)  # Stagger starts
        
        print()
        print("=" * 80)
        print("All components running!")
        print("Check Logs/ folder for detailed logs")
        print("=" * 80)
        print()
        
        # Keep main thread alive
        while True:
            time.sleep(10)
            # Check if any thread died
            for name, thread in threads:
                if not thread.is_alive():
                    logger.warning(f"⚠️  {name} thread died - system may need restart")
        
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("Stopping all components...")
        print("=" * 80)
        logger.info("All components stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
