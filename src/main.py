#!/usr/bin/env python3
"""
Code Launcher - Entry Point
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import sys
import os
import fcntl
import logging
import signal

# Import local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.core.config import LOCK_FILE, PID_FILE, CONFIG_DIR

# Create configuration directory if it doesn't exist (before logging setup)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(CONFIG_DIR, "code-launcher.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def bring_window_to_front():
    """
    Bring existing window to front using signals
    This works without external dependencies
    """
    try:
        # Read PID from separate PID file (not the locked file)
        with open(PID_FILE, 'r') as f:
            content = f.read().strip()
            logger.debug(f"PID file content: '{content}'")
            if content:
                pid = int(content)
                logger.info(f"Found existing instance with PID: {pid}")

                # Verify process exists
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    logger.debug(f"Process {pid} exists")
                except ProcessLookupError:
                    logger.error(f"Process {pid} does not exist")
                    return False

                # Send SIGUSR1 signal to existing process to bring window to front
                os.kill(pid, signal.SIGUSR1)
                logger.info(f"Sent SIGUSR1 signal to process {pid}")
                return True
            else:
                logger.warning("PID file is empty")
    except (FileNotFoundError, ValueError, ProcessLookupError) as e:
        logger.warning(f"Could not signal existing instance: {e}")
    except Exception as e:
        logger.error(f"Error bringing window to front: {e}", exc_info=True)

    return False


def setup_signal_handler(window):
    """
    Setup signal handler to bring window to front when SIGUSR1 is received

    Args:
        window: GTK Window instance
    """
    def handle_sigusr1(signum, frame):
        """Handle SIGUSR1 signal by bringing window to front"""
        logger.info("Received signal to bring window to front")

        # Use GLib.idle_add to safely interact with GTK from signal handler
        from gi.repository import GLib
        GLib.idle_add(activate_window, window)

    signal.signal(signal.SIGUSR1, handle_sigusr1)
    logger.debug("Signal handler registered for SIGUSR1")


def activate_window(window):
    """
    Activate and bring window to front

    Args:
        window: GTK Window instance
    """
    try:
        logger.debug("Attempting to activate window...")

        # Get the GDK window
        gdk_window = window.get_window()

        if gdk_window:
            # Method 1: Raise the window to top of stack
            gdk_window.raise_()
            logger.debug("Window raised")

            # Method 2: Focus the window
            gdk_window.focus(Gdk.CURRENT_TIME)
            logger.debug("Window focused")

        # Method 3: Deiconify if minimized
        window.deiconify()
        logger.debug("Window deiconified")

        # Method 4: Present with timestamp (brings to front)
        window.present_with_time(Gdk.CURRENT_TIME)
        logger.debug("Window presented with time")

        # Method 5: Set urgency hint to grab attention
        window.set_urgency_hint(True)
        logger.debug("Urgency hint set")

        # Remove urgency hint after a short delay
        from gi.repository import GLib
        def remove_urgency():
            window.set_urgency_hint(False)
            logger.debug("Urgency hint removed")
            return False
        GLib.timeout_add(500, remove_urgency)

        # Method 6: Grab focus
        window.grab_focus()
        logger.debug("Focus grabbed")

        # Method 7: Show all (ensure visibility)
        window.show_all()
        logger.debug("Window shown")

        logger.info("Window brought to front successfully")
    except Exception as e:
        logger.error(f"Error activating window: {e}", exc_info=True)

    return False


def main():
    """Main entry point for the application"""
    logger.info("Starting Code Launcher")

    # Try to acquire the lock
    lock_file = None
    try:
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_NB | fcntl.LOCK_EX)

        # Write PID to separate PID file for inter-process communication
        with open(PID_FILE, 'w') as pid_file:
            pid_file.write(str(os.getpid()))

        logger.info(f"Lock file acquired successfully with PID {os.getpid()}")
    except BlockingIOError:
        logger.warning("Another instance is already running")

        # Close our lock file attempt
        if lock_file:
            try:
                lock_file.close()
            except:
                pass

        # Another instance is already running, bring it to front
        if bring_window_to_front():
            logger.info("Brought existing window to front")
        else:
            logger.warning("Could not bring existing window to front")
            print("Another instance is already running")

        return
    except Exception as e:
        logger.error(f"Error creating lock file: {e}")
        print(f"Error creating lock file: {e}")
        if lock_file:
            try:
                lock_file.close()
            except:
                pass
        return

    # Create window
    from src.ui.window import FinderStyleWindow
    window = FinderStyleWindow()
    window.connect("destroy", Gtk.main_quit)

    # Setup signal handler to bring window to front
    setup_signal_handler(window)

    window.show_all()
    logger.info("Main window created and shown")

    try:
        Gtk.main()
    finally:
        logger.info("Application shutting down")
        if lock_file:
            try:
                lock_file.close()
            except:
                pass
        try:
            os.unlink(LOCK_FILE)
            logger.info("Lock file removed")
        except:
            pass
        try:
            os.unlink(PID_FILE)
            logger.info("PID file removed")
        except:
            pass


if __name__ == "__main__":
    main()
