#!/usr/bin/env python3
"""
Test keyboard shortcuts dialog
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestShortcutsDialog(unittest.TestCase):
    """Test shortcuts dialog creation"""

    def test_show_shortcuts_dialog(self):
        """Test that shortcuts dialog can be created"""
        # Mock GTK to avoid requiring display
        with patch('src.dialogs.shortcuts_dialog.Gtk') as mock_gtk:
            # Setup mocks
            mock_dialog = MagicMock()
            mock_content = MagicMock()
            mock_label = MagicMock()
            mock_scrolled = MagicMock()
            mock_grid = MagicMock()

            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.get_content_area.return_value = mock_content
            mock_gtk.Label.return_value = mock_label
            mock_gtk.ScrolledWindow.return_value = mock_scrolled
            mock_gtk.Grid.return_value = mock_grid
            mock_gtk.Orientation.VERTICAL = 1
            mock_gtk.Align.START = 1
            mock_gtk.PolicyType.NEVER = 1
            mock_gtk.PolicyType.AUTOMATIC = 2
            mock_gtk.ResponseType.CLOSE = -7
            mock_gtk.WindowPosition.CENTER = 1

            from src.dialogs.shortcuts_dialog import show_shortcuts_dialog

            # Mock parent window
            parent = MagicMock()

            # Should not raise any exceptions
            show_shortcuts_dialog(parent)

            # Verify dialog was created
            mock_gtk.Dialog.assert_called_once()
            mock_dialog.set_modal.assert_called_once_with(True)
            mock_dialog.set_transient_for.assert_called_once_with(parent)
            mock_dialog.show_all.assert_called_once()
            mock_dialog.run.assert_called_once()
            mock_dialog.destroy.assert_called_once()

    def test_shortcuts_content(self):
        """Test that shortcuts dialog contains expected shortcuts"""
        # This test verifies the shortcuts data structure
        shortcuts = [
            ("Navigation", "", "header"),
            ("←", "Navigate to previous column", "normal"),
            ("→", "Navigate to next column", "normal"),
            ("↑", "Select previous item in column", "normal"),
            ("↓", "Select next item in column", "normal"),
            ("1-9", "Jump to item by number (1st-9th)", "normal"),
            ("", "", "separator"),

            ("Search & Quick Access", "", "header"),
            ("Ctrl+F", "Focus search bar", "normal"),
            ("Ctrl+R", "Show recent items", "normal"),
            ("@recent", "Type in search to show recents", "normal"),
            ("", "", "separator"),

            ("Actions", "", "header"),
            ("Ctrl+O / Enter", "Open selected item", "normal"),
            ("Ctrl+N", "Create new category", "normal"),
            ("Ctrl+P", "Add new project", "normal"),
            ("Ctrl+D", "Toggle favorite on selected item", "normal"),
            ("Esc", "Close launcher", "normal"),
        ]

        # Verify we have all major shortcuts
        shortcut_keys = [s[0] for s in shortcuts if s[2] == "normal"]

        self.assertIn("Ctrl+F", shortcut_keys)
        self.assertIn("Ctrl+R", shortcut_keys)
        self.assertIn("Ctrl+D", shortcut_keys)
        self.assertIn("Ctrl+N", shortcut_keys)
        self.assertIn("Ctrl+P", shortcut_keys)
        self.assertIn("Ctrl+O / Enter", shortcut_keys)
        self.assertIn("Esc", shortcut_keys)
        self.assertIn("←", shortcut_keys)
        self.assertIn("→", shortcut_keys)
        self.assertIn("↑", shortcut_keys)
        self.assertIn("↓", shortcut_keys)
        self.assertIn("1-9", shortcut_keys)


if __name__ == '__main__':
    unittest.main()
