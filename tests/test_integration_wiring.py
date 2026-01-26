#!/usr/bin/env python3
"""
Integration tests for terminal component wiring
Tests that all components are properly connected and can communicate
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestTerminalIntegrationWiring(unittest.TestCase):
    """Test that all terminal integration components are properly wired together"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('gi.repository.Gtk')
    @patch('gi.repository.Gdk')
    def test_terminal_manager_config_manager_integration(self, mock_gdk, mock_gtk):
        """Test that TerminalManager properly integrates with ConfigManager"""
        from src.core.config import ConfigManager
        from utils.terminal_manager import TerminalManager

        # Create config manager
        config_manager = ConfigManager()

        # Create terminal manager with config manager
        terminal_manager = TerminalManager(config_manager)

        # Verify integration
        self.assertEqual(terminal_manager.config_manager, config_manager)
        self.assertIsNotNone(terminal_manager.detector)

        # Test that terminal manager can save preferences through config manager
        with patch.object(config_manager, 'load_preferences') as mock_load, \
             patch.object(config_manager, 'save_preferences') as mock_save:

            mock_load.return_value = {
                "default_editor": "kiro",
                "terminal": {
                    "preferred": None,
                    "available": {},
                    "last_detected": None
                }
            }

            # Initialize terminal manager
            terminal_manager.initialize()

            # Set a preferred terminal (this should trigger config save)
            with patch.object(terminal_manager, 'available_terminals', {'gnome-terminal': {'name': 'GNOME Terminal', 'path': '/usr/bin/gnome-terminal'}}):
                result = terminal_manager.set_preferred_terminal('gnome-terminal')

                # Verify the operation succeeded
                self.assertTrue(result)

                # Verify config manager was called to save preferences
                mock_save.assert_called()

    @patch('gi.repository.Gtk')
    @patch('gi.repository.Gdk')
    def test_context_menu_terminal_manager_integration(self, mock_gdk, mock_gtk):
        """Test that context menu can access TerminalManager through parent window"""
        from src.context_menu.handler import ContextMenuHandler
        from utils.terminal_manager import TerminalManager

        # Create mock parent window with terminal manager
        mock_parent_window = Mock()
        mock_terminal_manager = Mock(spec=TerminalManager)
        mock_terminal_manager.has_available_terminals.return_value = True
        mock_parent_window.terminal_manager = mock_terminal_manager

        # Create mock column browser
        mock_column_browser = Mock()

        # Create context menu handler
        context_handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

        # Test that context menu can check terminal availability
        has_terminals = context_handler._has_available_terminals()

        # Verify the check succeeded
        self.assertTrue(has_terminals)
        mock_terminal_manager.has_available_terminals.assert_called_once()

    @patch('gi.repository.Gtk')
    @patch('gi.repository.Gdk')
    def test_preferences_dialog_terminal_manager_integration(self, mock_gdk, mock_gtk):
        """Test that preferences dialog can access and modify terminal settings"""
        from src.dialogs.terminal_preferences import TerminalPreferences
        from utils.terminal_manager import TerminalManager

        # Create mock terminal manager
        mock_terminal_manager = Mock(spec=TerminalManager)
        mock_terminal_manager.get_available_terminals.return_value = {
            'gnome-terminal': {'name': 'GNOME Terminal', 'path': '/usr/bin/gnome-terminal'},
            'konsole': {'name': 'Konsole', 'path': '/usr/bin/konsole'}
        }
        mock_terminal_manager.get_preferred_terminal.return_value = 'gnome-terminal'

        # Create mock parent dialog
        mock_parent_dialog = Mock()

        # Create terminal preferences
        terminal_prefs = TerminalPreferences(mock_parent_dialog, mock_terminal_manager)

        # Verify integration
        self.assertEqual(terminal_prefs.terminal_manager, mock_terminal_manager)
        self.assertEqual(terminal_prefs.parent_dialog, mock_parent_dialog)

        # Test that preferences can get available terminals
        available = terminal_prefs.is_terminals_available()
        self.assertTrue(available)
        mock_terminal_manager.has_available_terminals.assert_called()

    @patch('gi.repository.Gtk')
    @patch('gi.repository.Gdk')
    def test_main_window_terminal_manager_initialization(self, mock_gdk, mock_gtk):
        """Test that main window properly initializes TerminalManager"""
        # Mock GTK components
        mock_gtk.Window = Mock()
        mock_gtk.Box = Mock()
        mock_gtk.HeaderBar = Mock()
        mock_gtk.Button = Mock()
        mock_gtk.Image = Mock()
        mock_gtk.SearchEntry = Mock()
        mock_gtk.ScrolledWindow = Mock()
        mock_gdk.WindowTypeHint = Mock()
        mock_gdk.WindowTypeHint.DIALOG = 'dialog'

        # Mock other dependencies
        with patch('src.ui.search_manager.SearchManager'), \
             patch('src.ui.keyboard_handler.KeyboardHandler'), \
             patch('src.ui.navigation_manager.NavigationManager'), \
             patch('utils.terminal_manager.TerminalManager') as mock_terminal_manager_class:

            # Create mock terminal manager instance
            mock_terminal_manager = Mock()
            mock_terminal_manager.has_available_terminals.return_value = True
            mock_terminal_manager_class.return_value = mock_terminal_manager

            # Import and create window
            from src.ui.window import FinderStyleWindow
            window = FinderStyleWindow()

            # Verify terminal manager was created and initialized
            mock_terminal_manager_class.assert_called_once_with(window.config)
            mock_terminal_manager.initialize.assert_called_once()

            # Verify window has terminal manager
            self.assertEqual(window.terminal_manager, mock_terminal_manager)

            # Test terminal support check
            has_support = window.has_terminal_support()
            self.assertTrue(has_support)

    @patch('gi.repository.Gtk')
    @patch('gi.repository.Gdk')
    def test_context_menu_action_terminal_integration(self, mock_gdk, mock_gtk):
        """Test that context menu actions can successfully call terminal operations"""
        from context_menu.actions import open_in_terminal
        from utils.terminal_manager import TerminalManager

        # Create mock parent window with terminal manager
        mock_parent_window = Mock()
        mock_terminal_manager = Mock(spec=TerminalManager)
        mock_terminal_manager.has_available_terminals.return_value = True
        mock_terminal_manager.open_terminal.return_value = (True, "")
        mock_parent_window.terminal_manager = mock_terminal_manager

        # Create context with project path
        context = {'item_path': self.temp_dir}

        # Mock error dialog to avoid GTK calls
        with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Execute terminal action
            open_in_terminal(context, mock_parent_window)

            # Verify terminal manager was called
            mock_terminal_manager.has_available_terminals.assert_called_once()
            mock_terminal_manager.open_terminal.assert_called_once_with(self.temp_dir)

            # Verify no error dialog was shown (success case)
            mock_error_dialog.assert_not_called()

    def test_graceful_degradation_no_terminal_manager(self):
        """Test that components handle missing terminal manager gracefully"""
        from src.context_menu.handler import ContextMenuHandler

        # Create mock parent window without terminal manager
        mock_parent_window = Mock()
        mock_parent_window.terminal_manager = None

        # Create mock column browser
        mock_column_browser = Mock()

        # Create context menu handler
        context_handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

        # Test that context menu handles missing terminal manager gracefully
        has_terminals = context_handler._has_available_terminals()

        # Should return False without crashing
        self.assertFalse(has_terminals)

    def test_graceful_degradation_terminal_manager_exception(self):
        """Test that components handle terminal manager exceptions gracefully"""
        from src.context_menu.handler import ContextMenuHandler
        from utils.terminal_manager import TerminalManager

        # Create mock parent window with terminal manager that throws exception
        mock_parent_window = Mock()
        mock_terminal_manager = Mock(spec=TerminalManager)
        mock_terminal_manager.has_available_terminals.side_effect = Exception("Test exception")
        mock_parent_window.terminal_manager = mock_terminal_manager

        # Create mock column browser
        mock_column_browser = Mock()

        # Create context menu handler
        context_handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

        # Test that context menu handles terminal manager exceptions gracefully
        has_terminals = context_handler._has_available_terminals()

        # Should return False without crashing
        self.assertFalse(has_terminals)


if __name__ == '__main__':
    unittest.main()