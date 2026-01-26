#!/usr/bin/env python3
"""
Terminal preferences dialog component for Code Launcher

This module provides the TerminalPreferences class that creates GTK widgets
for terminal selection and integrates with the TerminalManager for terminal
preference management.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging

logger = logging.getLogger(__name__)


class TerminalPreferences:
    """
    Terminal preferences UI component for the preferences dialog.

    This class creates and manages GTK widgets for terminal selection,
    populates terminal options from detected terminals, and handles
    terminal selection changes.
    """

    def __init__(self, parent_dialog, terminal_manager):
        """
        Initialize the terminal preferences component.

        Args:
            parent_dialog: Parent dialog window for modal behavior
            terminal_manager: TerminalManager instance for terminal operations
        """
        self.parent_dialog = parent_dialog
        self.terminal_manager = terminal_manager
        self.terminal_combo = None
        self.terminal_section = None
        self._terminal_keys = []  # Track terminal keys for combo box indices
        self._pending_terminal_selection = None  # Store pending selection until OK is pressed

    def create_terminal_section(self):
        """
        Create GTK widgets for terminal selection.

        Returns:
            Gtk.Box: Container with terminal preference widgets
        """
        logger.debug("Creating terminal preferences section")

        # Main container
        self.terminal_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Section label
        label = Gtk.Label(label="Terminal Preferences:")
        label.set_halign(Gtk.Align.START)
        label.set_markup("<b>Terminal Preferences:</b>")
        self.terminal_section.pack_start(label, False, False, 0)

        # Terminal selection container
        selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Terminal selection label
        terminal_label = Gtk.Label(label="Default terminal:")
        terminal_label.set_halign(Gtk.Align.START)
        selection_box.pack_start(terminal_label, False, False, 0)

        # Terminal dropdown
        self.terminal_combo = Gtk.ComboBoxText()
        self.terminal_combo.set_hexpand(True)
        self.terminal_combo.connect("changed", self.on_terminal_changed)
        selection_box.pack_start(self.terminal_combo, True, True, 0)

        self.terminal_section.pack_start(selection_box, False, False, 0)

        # Info label
        info_label = Gtk.Label()
        info_label.set_markup("<small><i>Select the terminal application to use when opening projects in terminal.</i></small>")
        info_label.set_halign(Gtk.Align.START)
        info_label.set_line_wrap(True)
        self.terminal_section.pack_start(info_label, False, False, 5)

        # Populate terminal options
        self.populate_terminal_options()

        return self.terminal_section

    def populate_terminal_options(self):
        """
        Fill dropdown with detected terminals.

        This method clears the current options and repopulates the dropdown
        with all available terminals from the TerminalManager. Implements
        graceful degradation when no terminals are available.
        """
        if not self.terminal_combo:
            logger.warning("Terminal combo box not initialized")
            return

        logger.debug("Populating terminal options")

        # Clear existing options
        self.terminal_combo.remove_all()
        self._terminal_keys.clear()

        # Get available terminals with graceful degradation
        try:
            available_terminals = self.terminal_manager.get_available_terminals()
        except Exception as e:
            logger.error(f"Error getting available terminals: {e}")
            available_terminals = {}

        if not available_terminals:
            logger.warning("No terminals available for selection")
            # Add placeholder option when no terminals are available
            self.terminal_combo.append_text("No terminals detected")
            self.terminal_combo.set_sensitive(False)

            # Update info label to explain the situation
            if hasattr(self, 'terminal_section') and self.terminal_section:
                # Find and update the info label
                for child in self.terminal_section.get_children():
                    if isinstance(child, Gtk.Label) and child.get_text().startswith("<small><i>"):
                        child.set_markup("<small><i>No terminal applications were detected on your system. "
                                       "Please install a terminal application such as gnome-terminal, konsole, or xterm "
                                       "to enable terminal functionality.</i></small>")
                        break
            return

        # Enable combo box if terminals are available
        self.terminal_combo.set_sensitive(True)

        # Add terminal options
        for terminal_key, terminal_info in available_terminals.items():
            display_name = terminal_info.get('name', terminal_key)
            self.terminal_combo.append_text(display_name)
            self._terminal_keys.append(terminal_key)
            logger.debug(f"Added terminal option: {display_name} ({terminal_key})")

        # Set current selection
        self._set_current_selection()

    def on_terminal_changed(self, combo_box):
        """
        Handle terminal selection changes.

        Args:
            combo_box (Gtk.ComboBoxText): The combo box that triggered the event
        """
        active_index = combo_box.get_active()

        if active_index < 0 or active_index >= len(self._terminal_keys):
            logger.warning(f"Invalid terminal selection index: {active_index}")
            return

        selected_terminal_key = self._terminal_keys[active_index]
        selected_display_name = combo_box.get_active_text()

        logger.info(f"Terminal selection changed to: {selected_display_name} ({selected_terminal_key})")

        # Store the selection temporarily, but don't save to config yet
        # The parent dialog will handle saving when user clicks OK
        self._pending_terminal_selection = selected_terminal_key
        logger.debug(f"Pending terminal selection: {selected_terminal_key}")

    def refresh_terminal_options(self):
        """
        Refresh the terminal options by re-detecting terminals.

        This method can be called to update the dropdown when terminals
        may have been installed or removed from the system. Implements
        graceful degradation for detection failures.
        """
        logger.info("Refreshing terminal options")

        try:
            # Re-initialize terminal manager to detect new terminals
            self.terminal_manager.initialize()
        except Exception as e:
            logger.error(f"Error re-initializing terminal manager: {e}")
            # Continue with existing state rather than failing completely

        # Repopulate options (this method already handles graceful degradation)
        self.populate_terminal_options()

    def get_selected_terminal(self):
        """
        Get the currently selected terminal key.

        Returns:
            str or None: Terminal key of selected terminal, None if no selection
        """
        if not self.terminal_combo:
            return None

        active_index = self.terminal_combo.get_active()
        if active_index < 0 or active_index >= len(self._terminal_keys):
            return None

        return self._terminal_keys[active_index]

    def set_selected_terminal(self, terminal_key):
        """
        Set the selected terminal by key.

        Args:
            terminal_key (str): Terminal key to select

        Returns:
            bool: True if terminal was selected successfully, False otherwise
        """
        if not self.terminal_combo or terminal_key not in self._terminal_keys:
            logger.warning(f"Cannot select terminal: {terminal_key}")
            return False

        try:
            index = self._terminal_keys.index(terminal_key)
            self.terminal_combo.set_active(index)
            logger.debug(f"Set terminal selection to: {terminal_key}")
            return True
        except ValueError:
            logger.error(f"Terminal key not found in options: {terminal_key}")
            return False

    def is_terminals_available(self):
        """
        Check if any terminals are available for selection.

        Returns:
            bool: True if terminals are available, False otherwise
        """
        try:
            return self.terminal_manager.has_available_terminals()
        except Exception as e:
            logger.error(f"Error checking terminal availability: {e}")
            return False

    def _set_current_selection(self):
        """
        Set the combo box selection to match the current preferred terminal.

        This method is called internally to sync the UI with the terminal
        manager's preferred terminal setting. Implements graceful degradation
        for cases where preferred terminal is not available.
        """
        if not self.terminal_combo:
            return

        try:
            preferred_terminal = self.terminal_manager.get_preferred_terminal()
        except Exception as e:
            logger.error(f"Error getting preferred terminal: {e}")
            preferred_terminal = None

        if not preferred_terminal or preferred_terminal not in self._terminal_keys:
            # No preferred terminal or preferred terminal not available
            if self._terminal_keys:
                # Select first available terminal
                self.terminal_combo.set_active(0)
                # Initialize pending selection with first available terminal
                self._pending_terminal_selection = self._terminal_keys[0]
                logger.debug("Set selection to first available terminal")
            else:
                # No terminals available
                self.terminal_combo.set_active(-1)
                self._pending_terminal_selection = None
                logger.debug("No terminals available for selection")
            return

        try:
            index = self._terminal_keys.index(preferred_terminal)
            # Temporarily disconnect signal to avoid triggering change event
            self.terminal_combo.handler_block_by_func(self.on_terminal_changed)
            self.terminal_combo.set_active(index)
            self.terminal_combo.handler_unblock_by_func(self.on_terminal_changed)

            # Initialize pending selection with current preferred terminal
            self._pending_terminal_selection = preferred_terminal

            logger.debug(f"Set selection to preferred terminal: {preferred_terminal}")
        except ValueError:
            logger.error(f"Preferred terminal not found in options: {preferred_terminal}")
            # Fall back to first available terminal
            if self._terminal_keys:
                self.terminal_combo.set_active(0)
                # Initialize pending selection with first available terminal
                self._pending_terminal_selection = self._terminal_keys[0]
        except Exception as e:
            logger.error(f"Error setting terminal selection: {e}")
            # Fall back to first available terminal if possible
            if self._terminal_keys:
                try:
                    self.terminal_combo.set_active(0)
                    self._pending_terminal_selection = self._terminal_keys[0]
                except Exception:
                    pass  # Give up gracefully

    def get_pending_terminal_selection(self):
        """
        Get the pending terminal selection (not yet saved).

        Returns:
            str or None: Terminal key of pending selection, None if no pending selection
        """
        return getattr(self, '_pending_terminal_selection', None)

    def apply_terminal_selection(self):
        """
        Apply the pending terminal selection to the terminal manager.

        Returns:
            bool: True if selection was applied successfully, False otherwise
        """
        pending_selection = self.get_pending_terminal_selection()
        if pending_selection is None:
            logger.debug("No pending terminal selection to apply")
            return True

        success = self.terminal_manager.set_preferred_terminal(pending_selection)
        if success:
            logger.info(f"Applied terminal selection: {pending_selection}")
            self._pending_terminal_selection = None  # Clear pending selection
        else:
            logger.error(f"Failed to apply terminal selection: {pending_selection}")

        return success

    def cancel_terminal_selection(self):
        """
        Cancel any pending terminal selection and revert to current preference.
        """
        logger.debug("Cancelling pending terminal selection")
        self._pending_terminal_selection = None
        self._set_current_selection()  # Revert UI to current preference