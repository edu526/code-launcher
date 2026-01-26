#!/usr/bin/env python3
"""
Tests for terminal action in context menu
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()

from context_menu.actions import open_in_terminal


class TestTerminalAction(unittest.TestCase):
    """Test cases for open_in_terminal action"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_parent_window = Mock()
        self.mock_terminal_manager = Mock()
        self.mock_parent_window.terminal_manager = self.mock_terminal_manager

        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_open_in_terminal_success(self):
        """Test successful terminal opening"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_terminal_manager.has_available_terminals.return_value = True
        self.mock_terminal_manager.open_terminal.return_value = (True, "")

        # Execute
        open_in_terminal(context, self.mock_parent_window)

        # Verify
        self.mock_terminal_manager.has_available_terminals.assert_called_once()
        self.mock_terminal_manager.open_terminal.assert_called_once_with(self.temp_dir)

    def test_open_in_terminal_no_path(self):
        """Test handling of missing project path"""
        # Setup
        context = {}

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once_with(
                self.mock_parent_window,
                "Error: Project path not found"
            )
            self.mock_terminal_manager.open_terminal.assert_not_called()

    def test_open_in_terminal_no_terminal_manager(self):
        """Test handling when terminal manager is not available"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_parent_window.terminal_manager = None

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once_with(
                self.mock_parent_window,
                "Error: Terminal functionality not available"
            )

    def test_open_in_terminal_no_terminals_available(self):
        """Test handling when no terminals are available on system"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_terminal_manager.has_available_terminals.return_value = False

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once_with(
                self.mock_parent_window,
                "Error: No terminal applications found on system"
            )
            self.mock_terminal_manager.open_terminal.assert_not_called()

    def test_open_in_terminal_launch_failure(self):
        """Test handling when terminal launch fails"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_terminal_manager.has_available_terminals.return_value = True
        self.mock_terminal_manager.open_terminal.return_value = (False, "Terminal launch failed")
        self.mock_terminal_manager.get_preferred_terminal.return_value = 'gnome-terminal'
        self.mock_terminal_manager.get_terminal_display_name.return_value = 'GNOME Terminal'

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once()
            error_message = mock_error_dialog.call_args[0][1]
            self.assertIn("Terminal launch failed", error_message)

    def test_open_in_terminal_launch_failure_no_display_name(self):
        """Test handling when terminal launch fails and no display name available"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_terminal_manager.has_available_terminals.return_value = True
        self.mock_terminal_manager.open_terminal.return_value = (False, "Unknown terminal error")
        self.mock_terminal_manager.get_preferred_terminal.return_value = 'unknown-terminal'
        self.mock_terminal_manager.get_terminal_display_name.return_value = None

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once()
            error_message = mock_error_dialog.call_args[0][1]
            self.assertIn("Unknown terminal error", error_message)

    def test_open_in_terminal_exception_handling(self):
        """Test handling of unexpected exceptions"""
        # Setup
        context = {'item_path': self.temp_dir}
        self.mock_terminal_manager.has_available_terminals.side_effect = Exception("Test exception")

        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute
            open_in_terminal(context, self.mock_parent_window)

            # Verify
            mock_error_dialog.assert_called_once()
            error_message = mock_error_dialog.call_args[0][1]
            self.assertIn("Error: Unable to check terminal availability", error_message)


if __name__ == '__main__':
    unittest.main()