"""
Terminal management utilities for Code Launcher

This module provides functionality to manage terminal applications, handle
terminal preferences, and launch terminals with specific working directories.
"""

import subprocess
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .terminal_detector import TerminalDetector

logger = logging.getLogger(__name__)


class TerminalManager:
    """
    Manages terminal applications and provides launching functionality.

    This class orchestrates terminal operations by coordinating with TerminalDetector
    for discovery, ConfigManager for preferences, and provides methods for launching
    terminals with specific working directories.
    """

    # Terminal command templates for different terminal types
    # Format: [command, args...] where {} is replaced with directory path
    TERMINAL_COMMANDS = {
        'gnome-terminal': ['gnome-terminal', '--working-directory={}'],
        'konsole': ['konsole', '--workdir', '{}'],
        'xterm': ['xterm', '-e', 'cd {} && bash'],
        'alacritty': ['alacritty', '--working-directory', '{}'],
        'warp': ['bash', '-c', 'cd "{}" && warp-terminal'],
        'terminator': ['terminator', '--working-directory={}'],
        'tilix': ['tilix', '--working-directory={}'],
        'kitty': ['kitty', '--directory={}']
    }

    def __init__(self, config_manager=None):
        """
        Initialize the terminal manager.

        Args:
            config_manager: ConfigManager instance for preference persistence
        """
        self.config_manager = config_manager
        self.detector = TerminalDetector()
        self.available_terminals = {}
        self.preferred_terminal = None
        self._initialized = False

    def initialize(self):
        """
        Initialize terminal detection and load preferences.

        This method should be called once during application startup to detect
        available terminals and load user preferences.

        Implements graceful degradation - if terminal detection fails, the manager
        will continue to function with no available terminals.
        """
        logger.info("Initializing TerminalManager")

        try:
            # Detect available terminals
            self.available_terminals = self.detector.detect_terminals()
            logger.info(f"Detected {len(self.available_terminals)} terminals")
        except Exception as e:
            logger.error(f"Terminal detection failed: {e}")
            logger.info("Continuing with no available terminals")
            self.available_terminals = {}

        try:
            # Load preferred terminal from configuration
            if self.config_manager:
                self.preferred_terminal = self._load_preferred_terminal()
        except Exception as e:
            logger.error(f"Failed to load preferred terminal from config: {e}")
            self.preferred_terminal = None

        try:
            # Set default if no preference or preferred terminal not available
            if not self.preferred_terminal or self.preferred_terminal not in self.available_terminals:
                self.preferred_terminal = self._get_default_terminal()
        except Exception as e:
            logger.error(f"Failed to set default terminal: {e}")
            self.preferred_terminal = None

        try:
            # Update available terminals in preferences
            if self.config_manager and self.available_terminals:
                self._update_available_terminals_in_config()
        except Exception as e:
            logger.error(f"Failed to update available terminals in config: {e}")

        self._initialized = True
        logger.info(f"TerminalManager initialized with preferred terminal: {self.preferred_terminal}")

    def get_available_terminals(self) -> Dict[str, Dict[str, str]]:
        """
        Get dictionary of available terminals.

        Returns:
            dict: Dictionary mapping terminal keys to their metadata
                 Format: {terminal_key: {'name': str, 'executable': str, 'path': str}}
        """
        if not self._initialized:
            self.initialize()
        return self.available_terminals.copy()

    def get_preferred_terminal(self) -> Optional[str]:
        """
        Get the user's preferred terminal or default.

        Returns:
            str or None: Terminal key of preferred terminal, None if no terminals available
        """
        if not self._initialized:
            self.initialize()
        return self.preferred_terminal

    def set_preferred_terminal(self, terminal_key: str) -> bool:
        """
        Set and persist the user's preferred terminal.

        Args:
            terminal_key (str): Key of the terminal to set as preferred

        Returns:
            bool: True if terminal was set successfully, False if terminal not available
        """
        if not self._initialized:
            self.initialize()

        if not self.is_terminal_available(terminal_key):
            logger.warning(f"Cannot set preferred terminal to unavailable terminal: {terminal_key}")
            return False

        self.preferred_terminal = terminal_key

        # Persist preference if config manager is available
        if self.config_manager:
            self._save_preferred_terminal(terminal_key)

        logger.info(f"Preferred terminal set to: {terminal_key}")
        return True

    def is_terminal_available(self, terminal_key: str) -> bool:
        """
        Check if a specific terminal is available.

        Args:
            terminal_key (str): Key of the terminal to check

        Returns:
            bool: True if terminal is available, False otherwise
        """
        if not self._initialized:
            self.initialize()
        return terminal_key in self.available_terminals

    def open_terminal(self, directory_path: str) -> Tuple[bool, str]:
        """
        Launch preferred terminal in the specified directory.

        Args:
            directory_path (str): Path to the directory to open in terminal

        Returns:
            tuple: (success: bool, error_message: str) - success status and user-friendly error message
        """
        if not self._initialized:
            self.initialize()

        # Validate directory path
        validation_result = self._validate_directory_path(directory_path)
        if not validation_result[0]:
            logger.error(f"Directory validation failed: {validation_result[1]}")
            return False, validation_result[1]

        # Get terminal to use
        terminal_key = self.preferred_terminal
        if not terminal_key or not self.is_terminal_available(terminal_key):
            logger.warning(f"Preferred terminal '{terminal_key}' not available, using fallback")
            terminal_key = self._get_fallback_terminal()

        if not terminal_key:
            error_msg = "No terminal applications are available on this system. Please install a terminal application such as gnome-terminal, konsole, or xterm."
            logger.error("No terminals available for launching")
            return False, error_msg

        # Attempt to launch terminal with comprehensive error handling
        return self._launch_terminal_with_fallback(terminal_key, directory_path)

    def _validate_directory_path(self, directory_path: str) -> Tuple[bool, str]:
        """
        Validate directory path for terminal opening.

        Args:
            directory_path (str): Path to validate

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if not directory_path:
            return False, "No directory path provided."

        if not os.path.exists(directory_path):
            return False, f"Directory does not exist: {directory_path}"

        if not os.path.isdir(directory_path):
            return False, f"Path is not a directory: {directory_path}"

        if not os.access(directory_path, os.R_OK):
            return False, f"Directory is not accessible: {directory_path}"

        return True, ""

    def _launch_terminal_with_fallback(self, terminal_key: str, directory_path: str) -> Tuple[bool, str]:
        """
        Launch terminal with comprehensive fallback handling.

        Args:
            terminal_key (str): Primary terminal to launch
            directory_path (str): Directory to open in terminal

        Returns:
            tuple: (success: bool, error_message: str)
        """
        # Try primary terminal
        logger.info(f"Attempting to launch terminal '{terminal_key}' in directory: {directory_path}")
        success, error_msg = self._attempt_terminal_launch(terminal_key, directory_path)

        if success:
            return True, ""

        # Log primary failure
        logger.warning(f"Primary terminal '{terminal_key}' failed: {error_msg}")

        # Try fallback terminals
        fallback_terminals = self._get_fallback_terminals(exclude=terminal_key)

        for fallback_key in fallback_terminals:
            logger.info(f"Attempting fallback terminal '{fallback_key}'")
            success, fallback_error = self._attempt_terminal_launch(fallback_key, directory_path)

            if success:
                logger.info(f"Successfully launched fallback terminal '{fallback_key}'")
                return True, ""
            else:
                logger.warning(f"Fallback terminal '{fallback_key}' failed: {fallback_error}")

        # Try system default terminal as last resort
        logger.info("Attempting system default terminal as last resort")
        success, system_error = self._attempt_system_default_terminal(directory_path)

        if success:
            logger.info("Successfully launched system default terminal")
            return True, ""

        # All attempts failed - return comprehensive error message
        error_msg = self._generate_comprehensive_error_message(terminal_key, error_msg, fallback_terminals)
        logger.error(f"All terminal launch attempts failed: {error_msg}")
        return False, error_msg

    def _attempt_terminal_launch(self, terminal_key: str, directory_path: str) -> Tuple[bool, str]:
        """
        Attempt to launch a specific terminal.

        Args:
            terminal_key (str): Terminal to launch
            directory_path (str): Directory to open

        Returns:
            tuple: (success: bool, error_message: str)
        """
        # Generate command for terminal
        command = self._generate_terminal_command(terminal_key, directory_path)
        if not command:
            return False, f"Could not generate command for terminal '{terminal_key}'"

        try:
            logger.debug(f"Terminal command: {' '.join(command)}")

            # Use subprocess.Popen to launch terminal without blocking
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            logger.info(f"Terminal '{terminal_key}' launched successfully with PID: {process.pid}")
            return True, ""

        except FileNotFoundError as e:
            error_msg = f"Terminal executable not found: {terminal_key}"
            logger.error(f"FileNotFoundError launching {terminal_key}: {e}")
            return False, error_msg

        except PermissionError as e:
            error_msg = f"Permission denied launching terminal: {terminal_key}"
            logger.error(f"PermissionError launching {terminal_key}: {e}")
            return False, error_msg

        except subprocess.SubprocessError as e:
            error_msg = f"Failed to start terminal process: {terminal_key}"
            logger.error(f"SubprocessError launching {terminal_key}: {e}")
            return False, error_msg

        except OSError as e:
            error_msg = f"System error launching terminal: {terminal_key}"
            logger.error(f"OSError launching {terminal_key}: {e}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error launching terminal: {terminal_key}"
            logger.error(f"Unexpected error launching {terminal_key}: {e}")
            return False, error_msg

    def _get_fallback_terminals(self, exclude: str = None) -> List[str]:
        """
        Get list of fallback terminals in priority order.

        Args:
            exclude (str): Terminal key to exclude from fallbacks

        Returns:
            list: List of terminal keys in priority order
        """
        if not self.available_terminals:
            return []

        # Define priority order for fallback terminals
        priority_order = [
            'gnome-terminal',  # Most common on GNOME systems
            'konsole',         # Most common on KDE systems
            'xterm',           # Universal fallback
            'alacritty',       # Modern alternative
            'terminator',      # Popular choice
            'tilix',           # GNOME alternative
            'kitty',           # Modern alternative
            'warp'             # Newer terminal
        ]

        # Get available terminals in priority order
        fallback_terminals = []

        # First, add terminals in priority order
        for terminal_key in priority_order:
            if (terminal_key in self.available_terminals and
                terminal_key != exclude):
                fallback_terminals.append(terminal_key)

        # Then add any remaining available terminals
        for terminal_key in self.available_terminals:
            if (terminal_key not in fallback_terminals and
                terminal_key != exclude):
                fallback_terminals.append(terminal_key)

        return fallback_terminals

    def _attempt_system_default_terminal(self, directory_path: str) -> Tuple[bool, str]:
        """
        Attempt to launch system default terminal using x-terminal-emulator or $TERMINAL.

        Args:
            directory_path (str): Directory to open

        Returns:
            tuple: (success: bool, error_message: str)
        """
        # Try common system default terminal commands
        default_commands = [
            ['x-terminal-emulator', '--working-directory', directory_path],
            ['x-terminal-emulator', '-e', f'cd "{directory_path}" && bash'],
        ]

        # Also try $TERMINAL environment variable
        terminal_env = os.environ.get('TERMINAL')
        if terminal_env:
            default_commands.insert(0, [terminal_env, '-e', f'cd "{directory_path}" && bash'])

        for command in default_commands:
            try:
                logger.debug(f"Trying system default command: {' '.join(command)}")

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

                logger.info(f"System default terminal launched with PID: {process.pid}")
                return True, ""

            except (FileNotFoundError, PermissionError, subprocess.SubprocessError, OSError, Exception) as e:
                logger.debug(f"System default command failed: {' '.join(command)}: {e}")
                continue

        return False, "System default terminal not available"

    def _generate_comprehensive_error_message(self, primary_terminal: str, primary_error: str,
                                            fallback_terminals: List[str]) -> str:
        """
        Generate a comprehensive user-friendly error message.

        Args:
            primary_terminal (str): Primary terminal that failed
            primary_error (str): Error from primary terminal
            fallback_terminals (list): List of fallback terminals that were tried

        Returns:
            str: User-friendly error message
        """
        if not self.available_terminals:
            return ("No terminal applications are available on this system. "
                   "Please install a terminal application such as gnome-terminal, konsole, or xterm.")

        error_parts = [
            f"Failed to open terminal in the specified directory.",
            f"Primary terminal '{primary_terminal}' failed: {primary_error}"
        ]

        if fallback_terminals:
            error_parts.append(f"Tried {len(fallback_terminals)} fallback terminal(s): {', '.join(fallback_terminals)}")

        error_parts.extend([
            "Please check that your terminal applications are properly installed and accessible.",
            "You can configure your preferred terminal in the application preferences."
        ])

        return " ".join(error_parts)

    def get_terminal_display_name(self, terminal_key: str) -> Optional[str]:
        """
        Get the display name for a terminal.

        Args:
            terminal_key (str): Key of the terminal

        Returns:
            str or None: Display name of the terminal, None if not available
        """
        if not self._initialized:
            self.initialize()

        terminal_info = self.available_terminals.get(terminal_key)
        return terminal_info['name'] if terminal_info else None

    def has_available_terminals(self) -> bool:
        """
        Check if any terminals are available on the system.

        Returns:
            bool: True if at least one terminal is available, False otherwise
        """
        if not self._initialized:
            self.initialize()
        return len(self.available_terminals) > 0

    def _load_preferred_terminal(self) -> Optional[str]:
        """
        Load preferred terminal from configuration.

        Returns:
            str or None: Preferred terminal key, None if not set or not available
        """
        if not self.config_manager:
            return None

        try:
            # Get terminal preferences from config
            preferences = self.config_manager.load_preferences()
            terminal_config = preferences.get('terminal', {})
            preferred = terminal_config.get('preferred')

            if preferred and preferred in self.available_terminals:
                logger.debug(f"Loaded preferred terminal from config: {preferred}")
                return preferred
            elif preferred:
                logger.warning(f"Preferred terminal from config not available: {preferred}")

        except Exception as e:
            logger.error(f"Error loading preferred terminal from config: {e}")

        return None

    def _save_preferred_terminal(self, terminal_key: str):
        """
        Save preferred terminal to configuration.

        Args:
            terminal_key (str): Terminal key to save as preferred
        """
        if not self.config_manager:
            return

        try:
            # Get current preferences
            preferences = self.config_manager.load_preferences()

            # Ensure terminal section exists
            if 'terminal' not in preferences:
                preferences['terminal'] = {}

            # Update preferred terminal
            preferences['terminal']['preferred'] = terminal_key
            preferences['terminal']['available'] = {
                key: info['path'] for key, info in self.available_terminals.items()
            }
            preferences['terminal']['last_detected'] = self._get_current_timestamp()

            # Save preferences
            self.config_manager.save_preferences(preferences)
            logger.debug(f"Saved preferred terminal to config: {terminal_key}")

        except Exception as e:
            logger.error(f"Error saving preferred terminal to config: {e}")

    def _update_available_terminals_in_config(self):
        """
        Update the list of available terminals in configuration.

        This method ensures that the preferences file contains the current
        list of detected terminals.
        """
        if not self.config_manager:
            return

        try:
            # Get current preferences
            preferences = self.config_manager.load_preferences()

            # Ensure terminal section exists
            if 'terminal' not in preferences:
                preferences['terminal'] = {}

            # Update available terminals
            preferences['terminal']['available'] = {
                key: info['path'] for key, info in self.available_terminals.items()
            }
            preferences['terminal']['last_detected'] = self._get_current_timestamp()

            # Save preferences
            self.config_manager.save_preferences(preferences)
            logger.debug(f"Updated available terminals in config: {list(self.available_terminals.keys())}")

        except Exception as e:
            logger.error(f"Error updating available terminals in config: {e}")

    def _get_default_terminal(self) -> Optional[str]:
        """
        Get the default terminal when no preference is set.

        Returns:
            str or None: Default terminal key, None if no terminals available
        """
        if not self.available_terminals:
            return None

        # Return the first available terminal as default
        return next(iter(self.available_terminals))

    def _get_fallback_terminal(self) -> Optional[str]:
        """
        Get a fallback terminal when preferred terminal is not available.

        Returns:
            str or None: Fallback terminal key, None if no terminals available
        """
        fallback_terminals = self._get_fallback_terminals(exclude=self.preferred_terminal)
        return fallback_terminals[0] if fallback_terminals else None

    def _generate_terminal_command(self, terminal_key: str, directory_path: str) -> Optional[List[str]]:
        """
        Generate command line arguments for launching a terminal.

        Args:
            terminal_key (str): Key of the terminal to launch
            directory_path (str): Directory path to open in terminal

        Returns:
            list or None: Command arguments, None if terminal not supported
        """
        if terminal_key not in self.TERMINAL_COMMANDS:
            logger.error(f"No command template for terminal: {terminal_key}")
            return None

        if not self.is_terminal_available(terminal_key):
            logger.error(f"Terminal not available: {terminal_key}")
            return None

        # Special handling for Warp terminal
        if terminal_key == 'warp':
            return self._generate_warp_command(directory_path)

        # Get command template
        command_template = self.TERMINAL_COMMANDS[terminal_key].copy()

        # Replace directory placeholder with actual path
        command = []
        for arg in command_template:
            if '{}' in arg:
                command.append(arg.format(directory_path))
            else:
                command.append(arg)

        return command

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.

        Returns:
            str: Current timestamp
        """
        return datetime.now().isoformat()

    def _generate_warp_command(self, directory_path: str) -> List[str]:
        """
        Generate special command for Warp terminal with working directory.

        Uses Warp's URL protocol to open a new tab in the specified directory.

        Args:
            directory_path (str): Directory path to open in terminal

        Returns:
            list: Command arguments for launching Warp
        """
        # Use Warp's URL protocol to open in specific directory
        warp_url = f"warp://action/new_tab?path={directory_path}"
        return ['warp-terminal', warp_url]