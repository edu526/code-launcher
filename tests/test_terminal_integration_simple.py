#!/usr/bin/env python3
"""
Simple integration test to verify terminal workflow functionality
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import os
import sys
import json
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock GTK before importing
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()
sys.modules['gi.repository.Gdk'] = Mock()


class TestTerminalIntegrationSimple(unittest.TestCase):
    """Simple integration tests for terminal workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, '.config', 'code-launcher')
        os.makedirs(self.config_dir, exist_ok=True)
        self.preferences_file = os.path.join(self.config_dir, 'preferences.json')

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_terminal_manager_initialization(self):
        """Test that terminal manager can be initialized"""
        with patch('utils.terminal_detector.shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'

            from src.core.config import ConfigManager
            from utils.terminal_manager import TerminalManager

            config_manager = ConfigManager()
            config_manager.config_dir = self.config_dir
            config_manager.preferences_file = self.preferences_file

            terminal_manager = TerminalManager(config_manager)
            terminal_manager.initialize()

            self.assertTrue(terminal_manager.has_available_terminals())
            self.assertEqual(terminal_manager.get_preferred_terminal(), 'gnome-terminal')

    def test_terminal_preferences_persistence(self):
        """Test that terminal preferences logic works correctly (without file system)"""
        with patch('utils.terminal_detector.shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'

            from src.core.config import ConfigManager
            from utils.terminal_manager import TerminalManager

            # Mock the config manager's save/load methods to avoid file system
            config_manager = ConfigManager()
            config_manager.config_dir = self.config_dir
            config_manager.preferences_file = self.preferences_file

            # Mock the save_preferences method
            with patch.object(config_manager, 'save_preferences') as mock_save, \
                 patch.object(config_manager, 'load_preferences') as mock_load:

                # Set up mock to return saved preferences
                saved_prefs = {}
                def save_side_effect(prefs):
                    saved_prefs.update(prefs)
                def load_side_effect():
                    return saved_prefs.copy()

                mock_save.side_effect = save_side_effect
                mock_load.side_effect = load_side_effect

                # First session - initialize and save preferences
                terminal_manager_1 = TerminalManager(config_manager)
                terminal_manager_1.initialize()

                # Set preferred terminal (should trigger save)
                if terminal_manager_1.has_available_terminals():
                    preferred = terminal_manager_1.get_preferred_terminal()
                    result = terminal_manager_1.set_preferred_terminal(preferred)
                    self.assertTrue(result)

                    # Verify save was called
                    mock_save.assert_called()

                    # Second session - load preferences
                    terminal_manager_2 = TerminalManager(config_manager)
                    terminal_manager_2.initialize()

                    # Verify preferences were loaded correctly
                    self.assertEqual(terminal_manager_2.get_preferred_terminal(), preferred)
                    mock_load.assert_called()

    def test_terminal_launch_workflow(self):
        """Test the complete terminal launch workflow"""
        with patch('utils.terminal_detector.shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'

            from src.core.config import ConfigManager
            from utils.terminal_manager import TerminalManager
            from context_menu.actions import open_in_terminal

            config_manager = ConfigManager()
            config_manager.config_dir = self.config_dir
            config_manager.preferences_file = self.preferences_file

            terminal_manager = TerminalManager(config_manager)
            terminal_manager.initialize()

            # Create test project directory
            test_project_dir = os.path.join(self.temp_dir, 'test-project')
            os.makedirs(test_project_dir, exist_ok=True)

            # Mock parent window
            mock_parent_window = Mock()
            mock_parent_window.terminal_manager = terminal_manager

            context = {'item_path': test_project_dir}

            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_popen.return_value = mock_process

                # Execute terminal action
                open_in_terminal(context, mock_parent_window)

                # Verify terminal was launched
                mock_popen.assert_called_once()
                call_args = mock_popen.call_args[0][0]
                self.assertEqual(call_args[0], 'gnome-terminal')

    def test_error_handling_no_terminals(self):
        """Test error handling when no terminals are available"""
        with patch('utils.terminal_detector.shutil.which', return_value=None):
            from src.core.config import ConfigManager
            from utils.terminal_manager import TerminalManager
            from context_menu.actions import open_in_terminal

            config_manager = ConfigManager()
            config_manager.config_dir = self.config_dir
            config_manager.preferences_file = self.preferences_file

            terminal_manager = TerminalManager(config_manager)
            terminal_manager.initialize()

            # Should handle no terminals gracefully
            self.assertFalse(terminal_manager.has_available_terminals())
            self.assertIsNone(terminal_manager.get_preferred_terminal())

            # Test terminal action with no terminals
            mock_parent_window = Mock()
            mock_parent_window.terminal_manager = terminal_manager

            test_project_dir = os.path.join(self.temp_dir, 'test-project')
            os.makedirs(test_project_dir, exist_ok=True)
            context = {'item_path': test_project_dir}

            with patch('context_menu.actions.show_error_dialog') as mock_error_dialog:
                open_in_terminal(context, mock_parent_window)

                # Should show error message
                mock_error_dialog.assert_called_once()
                error_message = mock_error_dialog.call_args[0][1]
                self.assertIn("No terminal applications found", error_message)

    def test_context_menu_integration(self):
        """Test context menu integration with terminal functionality"""
        with patch('utils.terminal_detector.shutil.which') as mock_which:
            mock_which.return_value = '/usr/bin/gnome-terminal'

            from src.core.config import ConfigManager
            from utils.terminal_manager import TerminalManager
            from src.context_menu.handler import ContextMenuHandler

            config_manager = ConfigManager()
            config_manager.config_dir = self.config_dir
            config_manager.preferences_file = self.preferences_file

            terminal_manager = TerminalManager(config_manager)
            terminal_manager.initialize()

            mock_parent_window = Mock()
            mock_parent_window.terminal_manager = terminal_manager
            mock_column_browser = Mock()

            context_handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

            # Should report terminals available
            self.assertTrue(context_handler._has_available_terminals())


if __name__ == '__main__':
    unittest.main()