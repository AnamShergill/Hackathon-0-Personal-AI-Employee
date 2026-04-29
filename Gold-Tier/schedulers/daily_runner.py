"""
Daily Runner - Scheduled Task Automation
Runs watchers, processors, and generates content on a schedule.
Uses Python 'schedule' library for cron-like scheduling.
"""

import schedule
import time
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_command(command: list, description: str, timeout: int = 300):
    """
    Run a command and log the result.
    
    Args:
        command: Command to run as list
        description: Description for logging
        timeout: Timeout in seconds
    """
    logger.info(f"=" * 80)
    logger.info(f"Running: {description}")
    logger.info(f"=" * 80)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                logger.info(f"Output: {result.stdout[:500]}")
        else:
            logger.error(f"❌ {description} failed")
            if result.stderr:
                logger.error(f"Error: {result.stderr[:500]}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {description} timeout")
        return False
    except Exception as e:
        logger.error(f"❌ {description} error: {e}")
        return False


def generate_linkedin_post():
    """Generate a LinkedIn post"""
    logger.info("📝 Generating LinkedIn post...")
    
    # Run the LinkedIn post generator
    command = [
        sys.executable,
        '-c',
        """
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'```python\\n(.*?)\\n```', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"""
    ]
    
    return run_command(command, "LinkedIn Post Generation", timeout=60)


def run_ralph_loop():
    """Run the Ralph Wiggum processing loop"""
    logger.info("🤖 Running Ralph Wiggum processing loop...")
    
    # This would call your main orchestrator
    # For now, we'll run the orchestrator skill
    command = [
        sys.executable,
        '-c',
        """
import sys
sys.path.insert(0, '.')

# Run orchestrator
with open('Skills/00_MAIN_ORCHESTRATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'```python\\n(.*?)\\n```', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"""
    ]
    
    return run_command(command, "Ralph Wiggum Loop", timeout=300)


def generate_weekly_briefing():
    """Generate a comprehensive weekly CEO briefing"""
    logger.info("📊 Generating weekly CEO briefing...")
    
    command = [
        sys.executable,
        'actions/weekly_briefing_generator.py',
        '--run-now'
    ]
    
    return run_command(command, "Weekly CEO Briefing Generation", timeout=120)


def cleanup_old_logs():
    """Clean up old log files (keep last 30 days)"""
    logger.info("🧹 Cleaning up old logs...")
    
    try:
        log_dir = Path("Logs")
        if not log_dir.exists():
            return True
        
        # Get all log files
        log_files = list(log_dir.glob("*.log"))
        
        # Keep only recent files
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(days=30)
        
        deleted_count = 0
        for log_file in log_files:
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_time:
                log_file.unlink()
                deleted_count += 1
        
        logger.info(f"✅ Cleaned up {deleted_count} old log files")
        return True
        
    except Exception as e:
        logger.error(f"❌ Log cleanup failed: {e}")
        return False


def morning_routine():
    """Morning routine - run at 9 AM"""
    logger.info("☀️  MORNING ROUTINE STARTING")
    logger.info("=" * 80)
    
    # 1. Run Ralph loop to process overnight messages
    run_ralph_loop()
    
    # 2. Generate LinkedIn post
    generate_linkedin_post()
    
    logger.info("=" * 80)
    logger.info("☀️  MORNING ROUTINE COMPLETE")


def afternoon_routine():
    """Afternoon routine - run at 2 PM"""
    logger.info("🌤️  AFTERNOON ROUTINE STARTING")
    logger.info("=" * 80)
    
    # 1. Run Ralph loop again
    run_ralph_loop()
    
    logger.info("=" * 80)
    logger.info("🌤️  AFTERNOON ROUTINE COMPLETE")


def evening_routine():
    """Evening routine - run at 6 PM"""
    logger.info("🌙 EVENING ROUTINE STARTING")
    logger.info("=" * 80)
    
    # 1. Run Ralph loop
    run_ralph_loop()
    
    # 2. Generate daily briefing
    generate_weekly_briefing()
    
    logger.info("=" * 80)
    logger.info("🌙 EVENING ROUTINE COMPLETE")


def sunday_evening_routine():
    """Sunday evening routine - run at 8 PM for weekly briefing"""
    logger.info("📊 SUNDAY EVENING ROUTINE STARTING")
    logger.info("=" * 80)
    
    # Generate comprehensive weekly CEO briefing
    generate_weekly_briefing()
    
    logger.info("=" * 80)
    logger.info("📊 SUNDAY EVENING ROUTINE COMPLETE")


def weekly_routine():
    """Weekly routine - run on Monday at 8 AM"""
    logger.info("📅 WEEKLY ROUTINE STARTING")
    logger.info("=" * 80)
    
    # Clean up old logs
    cleanup_old_logs()
    
    logger.info("=" * 80)
    logger.info("📅 WEEKLY ROUTINE COMPLETE")


def setup_schedule():
    """Set up the schedule for all tasks"""
    logger.info("Setting up schedule...")
    
    # Morning routine - 9 AM
    schedule.every().day.at("09:00").do(morning_routine)
    logger.info("  ✅ Morning routine: 9:00 AM daily")
    
    # Afternoon routine - 2 PM
    schedule.every().day.at("14:00").do(afternoon_routine)
    logger.info("  ✅ Afternoon routine: 2:00 PM daily")
    
    # Evening routine - 6 PM
    schedule.every().day.at("18:00").do(evening_routine)
    logger.info("  ✅ Evening routine: 6:00 PM daily")
    
    # Sunday evening - 8 PM (Weekly CEO Briefing)
    schedule.every().sunday.at("20:00").do(sunday_evening_routine)
    logger.info("  ✅ Sunday evening routine: 8:00 PM (Weekly CEO Briefing)")
    
    # Weekly routine - Monday 8 AM
    schedule.every().monday.at("08:00").do(weekly_routine)
    logger.info("  ✅ Weekly routine: Monday 8:00 AM")
    
    # LinkedIn post generation - 10 AM daily
    schedule.every().day.at("10:00").do(generate_linkedin_post)
    logger.info("  ✅ LinkedIn post: 10:00 AM daily")
    
    # Ralph loop - every 2 hours during work hours
    schedule.every().day.at("08:00").do(run_ralph_loop)
    schedule.every().day.at("10:00").do(run_ralph_loop)
    schedule.every().day.at("12:00").do(run_ralph_loop)
    schedule.every().day.at("14:00").do(run_ralph_loop)
    schedule.every().day.at("16:00").do(run_ralph_loop)
    schedule.every().day.at("18:00").do(run_ralph_loop)
    logger.info("  ✅ Ralph loop: Every 2 hours (8 AM - 6 PM)")
    
    logger.info("")
    logger.info("Schedule configured successfully!")


def main():
    """Main entry point for scheduler"""
    logger.info("=" * 80)
    logger.info("DAILY RUNNER - Scheduled Task Automation")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Starting scheduler...")
    logger.info("")
    
    # Set up schedule
    setup_schedule()
    
    logger.info("")
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    logger.info("=" * 80)
    logger.info("")
    
    # Run scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("Scheduler stopped by user")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()
