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
    """Generate a weekly briefing summary"""
    logger.info("📊 Generating weekly briefing...")
    
    try:
        # Count files in various folders
        needs_action = len(list(Path("Needs_Action").glob("*.md")))
        plans = len(list(Path("Plans").glob("*.md")))
        done = len(list(Path("Done").glob("*.md")))
        pending_approval = len(list(Path("Pending_Approval").glob("*.md")))
        approved = len(list(Path("Approved").glob("*.md")))
        
        # Create briefing
        briefing = f"""# Weekly Briefing - {datetime.now().strftime('%Y-%m-%d')}

## System Status
- **Needs Action**: {needs_action} items
- **Plans Created**: {plans} items
- **Completed**: {done} items
- **Pending Approval**: {pending_approval} items
- **Approved**: {approved} items

## Activity Summary
- Total items processed this week: {done}
- Items awaiting human review: {pending_approval}
- Active plans in progress: {plans}

## Recommendations
{'- Review pending approval items' if pending_approval > 0 else '- No pending approvals'}
{'- Process items in Needs_Action/' if needs_action > 0 else '- Inbox clear'}
{'- Execute approved items' if approved > 0 else '- No approved items waiting'}

---
*Generated automatically by Daily Runner at {datetime.now().isoformat()}*
"""
        
        # Save briefing
        briefing_path = Path("Briefings") / f"briefing_{datetime.now().strftime('%Y%m%d')}.md"
        briefing_path.parent.mkdir(exist_ok=True)
        
        with open(briefing_path, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        logger.info(f"✅ Weekly briefing saved: {briefing_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate briefing: {e}")
        return False


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


def weekly_routine():
    """Weekly routine - run on Monday at 8 AM"""
    logger.info("📅 WEEKLY ROUTINE STARTING")
    logger.info("=" * 80)
    
    # 1. Generate comprehensive weekly briefing
    generate_weekly_briefing()
    
    # 2. Clean up old logs
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
