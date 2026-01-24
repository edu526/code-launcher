#!/usr/bin/env python3
"""
Keyboard shortcuts handler for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk


class KeyboardHandler:
    """Manages keyboard shortcuts"""

    def __init__(self, window):
        """
        Initialize keyboard handler

        Args:
            window: FinderStyleWindow instance
        """
        self.window = window

    def on_key_press(self, widget, event):
        """
        Handle keyboard shortcuts

        Args:
            widget: GTK widget
            event: Gdk.EventKey

        Returns:
            True if event was handled, False otherwise
        """
        # ESC to close
        if event.keyval == Gdk.KEY_Escape:
            self.window.destroy()
            return True

        # Enter to open
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self.window.selected_path:
                self.window.on_open_clicked(None)
            return True

        # Ctrl+O also opens
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_o:
            if self.window.selected_path:
                self.window.on_open_clicked(None)
            return True

        return False
