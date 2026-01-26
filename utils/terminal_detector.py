"""
Terminal detection utilities for Code Launcher

This module provides functionality to detect available terminal applications
on the system and verify their accessibility.
"""

import shutil
import os
import logging

logger = logging.getLogger(__name__)


class TerminalDetector:
    """
    Detects and manages available terminal applications on the system.

    This class scans the system for known terminal applications using shutil.which()
    and maintains a registry of available terminals with their display names and
    executable paths.
    """

    # Known terminal applications with their display names and executable names
    KNOWN_TERMINALS = {
        'warp': {
            'name': 'Warp',
            'executable': 'warp-terminal'
        },
        'gnome-terminal': {
            'name': 'GNOME Terminal',
            'executable': 'gnome-terminal'
        },
        'konsole': {
            'name': 'Konsole',
            'executable': 'konsole'
        },
        'xterm': {
            'name': 'XTerm',
            'executable': 'xterm'
        },
        'alacritty': {
            'name': 'Alacritty',
            'executable': 'alacritty'
        },
        'terminator': {
            'name': 'Terminator',
            'executable': 'terminator'
        },
        'tilix': {
            'name': 'Tilix',
            'executable': 'tilix'
        },
        'kitty': {
            'name': 'Kitty',
            'executable': 'kitty'
        }
    }

    def __init__(self):
        """Initialize the terminal detector."""
        self.available_terminals = {}

    def detect_terminals(self):
        """
        Scan the system for available terminal applications.

        Returns:
            dict: Dictionary mapping terminal keys to their metadata
                 Format: {terminal_key: {'name': str, 'executable': str, 'path': str}}
        """
        logger.info("Starting terminal detection scan")
        detected = {}

        for terminal_key, terminal_info in self.KNOWN_TERMINALS.items():
            executable_name = terminal_info['executable']
            executable_path = shutil.which(executable_name)

            if executable_path and self.verify_terminal(executable_path):
                detected[terminal_key] = {
                    'name': terminal_info['name'],
                    'executable': executable_name,
                    'path': executable_path
                }
                logger.debug(f"Detected terminal: {terminal_info['name']} at {executable_path}")
            else:
                logger.debug(f"Terminal not found or not accessible: {executable_name}")

        self.available_terminals = detected
        logger.info(f"Terminal detection complete. Found {len(detected)} terminals")
        return detected

    def verify_terminal(self, executable_path):
        """
        Verify that a terminal executable is accessible and executable.

        Args:
            executable_path (str): Full path to the terminal executable

        Returns:
            bool: True if the terminal is accessible and executable, False otherwise
        """
        if not executable_path:
            return False

        try:
            # Check if file exists
            if not os.path.exists(executable_path):
                logger.debug(f"Terminal executable does not exist: {executable_path}")
                return False

            # Check if file is executable
            if not os.access(executable_path, os.X_OK):
                logger.debug(f"Terminal executable is not executable: {executable_path}")
                return False

            logger.debug(f"Terminal verified successfully: {executable_path}")
            return True

        except (OSError, PermissionError) as e:
            logger.debug(f"Error verifying terminal {executable_path}: {e}")
            return False

    def get_available_terminals(self):
        """
        Get the dictionary of available terminals.

        Returns:
            dict: Dictionary of available terminals with their metadata
        """
        return self.available_terminals.copy()

    def get_terminal_path(self, terminal_key):
        """
        Get the executable path for a specific terminal.

        Args:
            terminal_key (str): The key identifying the terminal

        Returns:
            str or None: The executable path if terminal is available, None otherwise
        """
        terminal_info = self.available_terminals.get(terminal_key)
        return terminal_info['path'] if terminal_info else None

    def get_terminal_name(self, terminal_key):
        """
        Get the display name for a specific terminal.

        Args:
            terminal_key (str): The key identifying the terminal

        Returns:
            str or None: The display name if terminal is available, None otherwise
        """
        terminal_info = self.available_terminals.get(terminal_key)
        return terminal_info['name'] if terminal_info else None

    def is_terminal_available(self, terminal_key):
        """
        Check if a specific terminal is available on the system.

        Args:
            terminal_key (str): The key identifying the terminal

        Returns:
            bool: True if the terminal is available, False otherwise
        """
        return terminal_key in self.available_terminals

    def get_fallback_terminal(self):
        """
        Get a fallback terminal when the preferred terminal is not available.

        Returns:
            str or None: The key of the first available terminal, or None if no terminals available
        """
        if not self.available_terminals:
            logger.warning("No terminals available for fallback")
            return None

        # Return the first available terminal as fallback
        fallback_key = next(iter(self.available_terminals))
        logger.info(f"Using fallback terminal: {self.available_terminals[fallback_key]['name']}")
        return fallback_key