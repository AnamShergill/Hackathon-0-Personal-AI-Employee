import abc
import logging
import time
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseWatcher(abc.ABC):
    """
    Abstract base class for all watchers in the AI Employee system.
    All specific watchers should inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, name: str, interval: int = 60):
        """
        Initialize the watcher.

        Args:
            name: Name of the watcher for identification
            interval: Polling interval in seconds
        """
        self.name = name
        self.interval = interval
        self.is_running = False
        self.last_run = None

    @abc.abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new updates/events from the source.

        Returns:
            List of events/updates found since last check
        """
        pass

    @abc.abstractmethod
    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event/update.

        Args:
            event: The event to process

        Returns:
            True if processing was successful, False otherwise
        """
        pass

    def run_once(self) -> int:
        """
        Run one cycle of checking and processing.

        Returns:
            Number of events processed
        """
        logger.info(f"{self.name} running check...")
        try:
            events = self.check_for_updates()
            logger.info(f"{self.name} found {len(events)} events")

            processed_count = 0
            for event in events:
                if self.process_event(event):
                    processed_count += 1

            self.last_run = time.time()
            logger.info(f"{self.name} completed cycle, processed {processed_count} events")
            return processed_count
        except Exception as e:
            logger.error(f"Error in {self.name} run cycle: {e}")
            return 0

    def run_forever(self):
        """
        Run the watcher continuously with the specified interval.
        """
        logger.info(f"Starting {self.name} with {self.interval}s interval")
        self.is_running = True

        try:
            while self.is_running:
                self.run_once()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info(f"{self.name} stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in {self.name}: {e}")
        finally:
            self.is_running = False
            logger.info(f"{self.name} has stopped")

    def stop(self):
        """
        Stop the watcher gracefully.
        """
        logger.info(f"Stopping {self.name}...")
        self.is_running = False