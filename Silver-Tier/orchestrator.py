"""
Orchestrator for the AI Employee System
This script coordinates the execution of various agent skills and watchers.
For Bronze Tier, this is a stub ready for future Silver/Gold Tier functionality.
"""
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Orchestrates the AI Employee system by coordinating watchers, skills, and workflows.
    """

    def __init__(self):
        self.is_running = False
        self.active_watchers = []
        self.skill_registry = {}
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment or config files.
        """
        return {
            "dashboard_update_interval": int(os.getenv("DASHBOARD_UPDATE_INTERVAL", 30)),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
        }

    def register_skill(self, skill_name: str, skill_function):
        """
        Register a skill function with the orchestrator.
        """
        self.skill_registry[skill_name] = skill_function
        logger.info(f"Registered skill: {skill_name}")

    def discover_skills(self):
        """
        Discover and register available skills from the Skills/ directory.
        """
        skills_dir = Path("Skills")
        if not skills_dir.exists():
            logger.warning("Skills directory not found")
            return

        # Look for .py files in Skills directory (though skills are in .md for now)
        # This is prepared for when skills might be implemented as Python modules
        for skill_file in skills_dir.glob("*.py"):
            if skill_file.name.startswith('__'):
                continue

            try:
                spec = importlib.util.spec_from_file_location(skill_file.stem, skill_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for functions that might be skills
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        self.register_skill(f"{skill_file.stem}.{attr_name}", attr)
            except Exception as e:
                logger.error(f"Error loading skill from {skill_file}: {e}")

        # Also register any skills that might be available as runnable scripts
        self.register_skill("email_processor", self.run_email_processor)

    def run_email_processor(self):
        """
        Run the email processor skill - a core Bronze Tier capability.
        """
        logger.info("Running email processor skill...")

        # Import and run the email processor from the markdown skill
        # This is a simplified version - in a real system this would be more sophisticated
        import sys
        import subprocess

        try:
            # For Bronze Tier, we'll execute the skill as a script
            result = subprocess.run([sys.executable, "Skills/01_EMAIL_PROCESSOR.py"],
                                    capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("Email processor completed successfully")
            else:
                logger.error(f"Email processor failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("Email processor timed out")
        except Exception as e:
            logger.error(f"Error running email processor: {e}")

    def update_dashboard(self):
        """
        Update the dashboard with current system status.
        """
        import re
        from datetime import datetime

        # Read current dashboard
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            logger.warning("Dashboard.md not found")
            return

        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'\{\{timestamp\}\}', timestamp, content)

        # Count items in various directories
        def count_files(directory):
            path = Path(directory)
            if path.exists():
                return len(list(path.glob('*')))
            return 0

        # Update counts
        content = re.sub(r'\{\{inbox_count\}\}', str(count_files('Inbox')), content)
        content = re.sub(r'\{\{needs_action_count\}\}', str(count_files('Needs_Action')), content)
        content = re.sub(r'\{\{done_count\}\}', str(count_files('Done')), content)
        content = re.sub(r'\{\{pending_approval_count\}\}', str(count_files('Pending_Approval')), content)
        content = re.sub(r'\{\{approved_count\}\}', str(count_files('Approved')), content)

        # Update status of watchers
        active_watchers = "Active" if self.active_watchers else "Inactive"
        content = re.sub(r'\{\{gmail_watcher_status\}\}', active_watchers, content)

        # Write back the updated dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info("Dashboard updated")

    def ralph_wiggum_loop(self):
        """
        Execute the Ralph Wiggum pattern: Act, Inform, Wait.
        This is the core autonomy loop of the AI Employee.
        """
        logger.info("Starting Ralph Wiggum loop...")

        # Act: Process any new emails
        if Path("Needs_Action").exists():
            needs_action_files = list(Path("Needs_Action").glob("*.md"))
            if needs_action_files:
                logger.info(f"Found {len(needs_action_files)} items needing action")
                self.run_email_processor()

        # Inform: Update dashboard with current status
        self.update_dashboard()

        # Wait: Log the waiting state
        logger.info("Ralph Wiggum loop: Waiting for next cycle (status updated)")

    def run(self, interval: int = 60):
        """
        Run the orchestrator continuously.
        """
        logger.info("Starting AI Employee Orchestrator...")
        self.is_running = True
        self.discover_skills()

        while self.is_running:
            try:
                self.ralph_wiggum_loop()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")
                time.sleep(10)  # Wait before retrying

        logger.info("AI Employee Orchestrator stopped")


def main():
    """
    Main entry point for the orchestrator.
    """
    orchestrator = AIOrchestrator()

    # For Bronze Tier, we can run specific tasks or start the full orchestrator
    import sys

    if len(sys.argv) > 1:
        # Run specific task
        task = sys.argv[1]
        if task == "email_processor":
            orchestrator.run_email_processor()
        elif task == "update_dashboard":
            orchestrator.update_dashboard()
        else:
            print(f"Unknown task: {task}")
            print("Available tasks: email_processor, update_dashboard")
    else:
        # Run full orchestrator loop
        orchestrator.run()


if __name__ == "__main__":
    main()