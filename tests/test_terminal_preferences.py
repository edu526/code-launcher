#!/usr/bin/env python3
"""
Tests for TerminalPreferences dialog component
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()

# Import after mocking GTK
from dialogs.terminal_preferences import TerminalPreferences


class TestTerminalPreferences(unittest.TestCase):
    """Test cases for TerminalPreferences class"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock GTK components
        self.mock_gtk = sys.modules['gi.repository.Gtk']
        self.mock_gtk.Box = Mock()
        self.mock_gtk.Label = Mock()
        self.mock_gtk.ComboBoxText = Mock()
        self.mock_gtk.Orientation = Mock()
        self.mock_gtk.Orientation.VERTICAL = 'vertical'
        self.mock_gtk.Orientation.HORIZONTAL = 'horizontal'
        self.mock_gtk.Align = Mock()
        self.mock_gtk.Align.START = 'start'

        # Mock parent dialog and terminal manager
        self.mock_parent_dialog = Mock()
        self.mock_terminal_manager = Mock()

        # Create TerminalPreferences instance
        self.terminal_prefs = TerminalPreferences(
            self.mock_parent_dialog,
            self.mock_terminal_manager
        )

    def test_init(self):
        """Test TerminalPreferences initialization"""
        self.assertEqual(self.terminal_prefs.parent_dialog, self.mock_parent_dialog)
        self.assertEqual(self.terminal_prefs.terminal_manager, self.mock_terminal_manager)
        self.assertIsNone(self.terminal_prefs.terminal_combo)
        self.assertIsNone(self.terminal_prefs.terminal_section)
        self.assertEqual(self.terminal_prefs._terminal_keys, [])

    def test_create_terminal_section(self):
        """Test creating terminal section widgets"""
        # Mock terminal manager
        self.mock_terminal_manager.get_available_terminals.return_value = {
            'gnome-terminal': {'name': 'GNOME Terminal', 'path': '/usr/bin/gnome-terminal'}
        }
        self.mock_terminal_manager.get_preferred_terminal.return_value = 'gnome-terminal'

        # Create terminal section
        result = self.terminal_prefs.create_terminal_section()

        # Verify widgets were created
        self.assertIsNotNone(result)
        self.assertIsNotNone(self.terminal_prefs.terminal_section)
        self.assertIsNotNone(self.terminal_prefs.terminal_combo)

        # Verify combo box was configured
        self.terminal_prefs.terminal_combo.connect.assert_called_with("changed", self.terminal_prefs.on_terminal_changed)

    def test_populate_terminal_options_with_terminals(self):
        """Test populating terminal options when terminals are available"""
        # Mock combo box
        mock_combo = Mock()
        self.terminal_prefs.terminal_combo = mock_combo

        # Mock available terminals
        available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal', 'path': '/usr/bin/gnome-terminal'},
            'konsole': {'name': 'Konsole', 'path': '/usr/bin/konsole'}
        }
        self.mock_terminal_manager.get_available_terminals.return_value = available_terminals
        self.mock_terminal_manager.get_preferred_terminal.return_value = 'gnome-terminal'

        # Populate options
        self.terminal_prefs.populate_terminal_options()

        # Verify combo box was populated
        mock_combo.remove_all.assert_called_once()
        mock_combo.set_sensitive.assert_called_with(True)

        # Verify terminals were added
        expected_calls = [
            unittest.mock.call('GNOME Terminal'),
            unittest.mock.call('Konsole')
        ]
        mock_combo.append_text.assert_has_calls(expected_calls)

        # Verify terminal keys were stored
        self.assertEqual(self.terminal_prefs._terminal_keys, ['gnome-terminal', 'konsole'])

    def test_populate_terminal_options_no_terminals(self):
        """Test populating terminal options when no terminals are available"""
        # Mock combo box
        mock_combo = Mock()
        self.terminal_prefs.terminal_combo = mock_combo

        # Mock no available terminals
        self.mock_terminal_manager.get_available_terminals.return_value = {}

        # Populate options
        self.terminal_prefs.populate_terminal_options()

        # Verify combo box was disabled
        mock_combo.remove_all.assert_called_once()
        mock_combo.append_text.assert_called_with("No terminals detected")
        mock_combo.set_sensitive.assert_called_with(False)

    def test_on_terminal_changed_valid_selection(self):
        """Test handling valid terminal selection change"""
        # Set up terminal keys
        self.terminal_prefs._terminal_keys = ['gnome-terminal', 'konsole']

        # Mock combo box
        mock_combo = Mock()
        mock_combo.get_active.return_value = 1
        mock_combo.get_active_text.return_value = 'Konsole'

        # Mock successful terminal setting
        self.mock_terminal_manager.set_preferred_terminal.return_value = True

        # Handle selection change
        self.terminal_prefs.on_terminal_changed(mock_combo)

        # Verify terminal manager was called
        self.mock_terminal_manager.set_preferred_terminal.assert_called_with('konsole')

    def test_on_terminal_changed_invalid_selection(self):
        """Test handling invalid terminal selection change"""
        # Set up terminal keys
        self.terminal_prefs._terminal_keys = ['gnome-terminal']

        # Mock combo box with invalid selection
        mock_combo = Mock()
        mock_combo.get_active.return_value = 5  # Invalid index

        # Handle selection change
        self.terminal_prefs.on_terminal_changed(mock_combo)

        # Verify terminal manager was not called
        self.mock_terminal_manager.set_preferred_terminal.assert_not_called()

    def test_get_selected_terminal(self):
        """Test getting selected terminal"""
        # Set up terminal keys and combo box
        self.terminal_prefs._terminal_keys = ['gnome-terminal', 'konsole']
        mock_combo = Mock()
        mock_combo.get_active.return_value = 1
        self.terminal_prefs.terminal_combo = mock_combo

        # Get selected terminal
        result = self.terminal_prefs.get_selected_terminal()

        # Verify correct terminal key returned
        self.assertEqual(result, 'konsole')

    def test_set_selected_terminal_valid(self):
        """Test setting selected terminal with valid key"""
        # Set up terminal keys and combo box
        self.terminal_prefs._terminal_keys = ['gnome-terminal', 'konsole']
        mock_combo = Mock()
        self.terminal_prefs.terminal_combo = mock_combo

        # Set selected terminal
        result = self.terminal_prefs.set_selected_terminal('konsole')

        # Verify selection was set
        self.assertTrue(result)
        mock_combo.set_active.assert_called_with(1)

    def test_set_selected_terminal_invalid(self):
        """Test setting selected terminal with invalid key"""
        # Set up terminal keys and combo box
        self.terminal_prefs._terminal_keys = ['gnome-terminal']
        mock_combo = Mock()
        self.terminal_prefs.terminal_combo = mock_combo

        # Try to set invalid terminal
        result = self.terminal_prefs.set_selected_terminal('invalid-terminal')

        # Verify selection was not set
        self.assertFalse(result)
        mock_combo.set_active.assert_not_called()

    def test_is_terminals_available(self):
        """Test checking if terminals are available"""
        # Mock terminal manager
        self.mock_terminal_manager.has_available_terminals.return_value = True

        # Check availability
        result = self.terminal_prefs.is_terminals_available()

        # Verify result
        self.assertTrue(result)
        self.mock_terminal_manager.has_available_terminals.assert_called_once()

    def test_refresh_terminal_options(self):
        """Test refreshing terminal options"""
        # Mock combo box
        mock_combo = Mock()
        self.terminal_prefs.terminal_combo = mock_combo

        # Mock terminal manager
        self.mock_terminal_manager.get_available_terminals.return_value = {
            'xterm': {'name': 'XTerm', 'path': '/usr/bin/xterm'}
        }
        self.mock_terminal_manager.get_preferred_terminal.return_value = 'xterm'

        # Refresh options
        self.terminal_prefs.refresh_terminal_options()

        # Verify terminal manager was re-initialized
        self.mock_terminal_manager.initialize.assert_called_once()

        # Verify combo box was repopulated
        mock_combo.remove_all.assert_called_once()


if __name__ == '__main__':
    unittest.main()