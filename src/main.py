#!/usr/bin/env python3
"""
Code Launcher - Entry Point
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
import os
import fcntl
import subprocess
import logging

# Import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.core.config import LOCK_FILE, CONFIG_DIR

# Create configuration directory if it doesn't exist (before logging setup)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(CONFIG_DIR, "code-launcher.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application"""
    logger.info("Starting Code Launcher")

    # Try to acquire the lock
    try:
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Lock file acquired successfully")
    except BlockingIOError:
        logger.warning("Another instance is already running")
        # Another instance is already running, bring it to front
        try:
            subprocess.run(
                ['wmctrl', '-a', 'Code Launcher'],
                check=False,
                stderr=subprocess.DEVNULL
            )
            logger.info("Brought existing window to front")
        except FileNotFoundError:
            logger.error("wmctrl not installed")
            print("wmctrl is not installed. Install wmctrl with 'sudo apt install wmctrl' "
                  "to activate the existing window.")
        lock_file.close()
        return
    except Exception as e:
        logger.error(f"Error creating lock file: {e}")
        print(f"Error creating lock file: {e}")
        return

    # Create window
    from src.ui.window import FinderStyleWindow
    window = FinderStyleWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    logger.info("Main window created and shown")

    try:
        Gtk.main()
    finally:
        logger.info("Application shutting down")
        lock_file.close()
        try:
            os.unlink(LOCK_FILE)
            logger.info("Lock file removed")
        except:
            pass


if __name__ == "__main__":
    main()
