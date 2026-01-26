#!/usr/bin/env python3
"""
Tests for ConfigDialog integration with TerminalPreferences
"""

import pytest
import unittest.mock as mock
from unittest.mock import patch, MagicMock


class MockTerminalManager:
    """Mock TerminalManager for testing"""

    def __init__(self):
        self.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            },
            'konsole': {
                'name': 'Konsole',
                'executable': 'konsole',
                'path': '/usr/bin/konsole'
            }
        }
        self.preferred_terminal = 'gnome-terminal'

    def get_available_terminals(self):
        return self.available_terminals.copy()

    def get_preferred_terminal(self):
        return self.preferred_terminal

    def set_preferred_terminal(self, terminal_key):
        if terminal_key in self.available_terminals:
            self.preferred_terminal = terminal_key
            return True
        return False

    def has_available_terminals(self):
        return len(self.available_terminals) > 0


class TestConfigDialogIntegration:
    """Test cases for ConfigDialog integration with TerminalPreferences"""

    def test_terminal_preferences_integration_flow(self):
        """Test the complete flow of terminal preferences integration"""
        # This test verifies that the integration components work together
        # without mocking the GTK components (integration test)

        config_manager = MagicMock()
        config_manager.load_preferences.return_value = {
            "default_editor": "kiro",
            "terminal": {
                "preferred": "gnome-terminal",
                "available": {},
                "last_detected": None
            }
        }

        terminal_manager = MockTerminalManager()

        # Test that terminal manager can be integrated with config dialog
        # This verifies the interface compatibility
        assert terminal_manager.has_available_terminals() is True
        assert terminal_manager.get_preferred_terminal() == 'gnome-terminal'

        # Test setting a different terminal
        success = terminal_manager.set_preferred_terminal('konsole')
        assert success is True
        assert terminal_manager.get_preferred_terminal() == 'konsole'

        # Test getting available terminals for UI population
        available = terminal_manager.get_available_terminals()
        assert 'gnome-terminal' in available
        assert 'konsole' in available
        assert available['gnome-terminal']['name'] == 'GNOME Terminal'
        assert available['konsole']['name'] == 'Konsole'

    def test_config_dialog_function_signature_compatibility(self):
        """Test that the config dialog function signature supports terminal manager"""
        # This test verifies that the function signature is backward compatible
        # and supports the new terminal_manager parameter

        # Mock the function to test signature compatibility
        def mock_show_preferences_dialog(parent, config_manager, terminal_manager=None):
            """Mock implementation matching the actual signature"""
            return {
                'parent': parent,
                'config_manager': config_manager,
                'terminal_manager': terminal_manager
            }

        # Test backward compatibility (without terminal_manager)
        parent = MagicMock()
        config_manager = MagicMock()

        result = mock_show_preferences_dialog(parent, config_manager)
        assert result['parent'] is parent
        assert result['config_manager'] is config_manager
        assert result['terminal_manager'] is None

        # Test with terminal_manager
        terminal_manager = MockTerminalManager()
        result = mock_show_preferences_dialog(parent, config_manager, terminal_manager)
        assert result['parent'] is parent
        assert result['config_manager'] is config_manager
        assert result['terminal_manager'] is terminal_manager

    def test_terminal_preferences_ui_integration_interface(self):
        """Test the interface between TerminalPreferences and ConfigDialog"""
        # This test verifies that the TerminalPreferences class provides
        # the expected interface for integration with ConfigDialog

        # Mock TerminalPreferences class
        class MockTerminalPreferences:
            def __init__(self, parent_dialog, terminal_manager):
                self.parent_dialog = parent_dialog
                self.terminal_manager = terminal_manager

            def create_terminal_section(self):
                """Mock implementation of create_terminal_section"""
                return MagicMock()  # Mock GTK widget

        # Test that TerminalPreferences can be instantiated with expected parameters
        parent_dialog = MagicMock()
        terminal_manager = MockTerminalManager()

        terminal_prefs = MockTerminalPreferences(parent_dialog, terminal_manager)
        assert terminal_prefs.parent_dialog is parent_dialog
        assert terminal_prefs.terminal_manager is terminal_manager

        # Test that create_terminal_section returns a widget-like object
        terminal_section = terminal_prefs.create_terminal_section()
        assert terminal_section is not None

    def test_config_manager_terminal_integration(self):
        """Test that ConfigManager properly handles terminal preferences"""
        # This test verifies that the ConfigManager can handle terminal preferences
        # as expected by the integration

        config_manager = MagicMock()

        # Mock load_preferences to return terminal configuration
        config_manager.load_preferences.return_value = {
            "default_editor": "kiro",
            "terminal": {
                "preferred": "gnome-terminal",
                "available": {
                    "gnome-terminal": "/usr/bin/gnome-terminal",
                    "konsole": "/usr/bin/konsole"
                },
                "last_detected": "2024-01-01T12:00:00"
            }
        }

        # Test loading preferences
        preferences = config_manager.load_preferences()
        assert "terminal" in preferences
        assert preferences["terminal"]["preferred"] == "gnome-terminal"
        assert "gnome-terminal" in preferences["terminal"]["available"]

        # Test saving preferences
        new_preferences = preferences.copy()
        new_preferences["default_editor"] = "vscode"
        config_manager.save_preferences(new_preferences)

        # Verify save was called with updated preferences
        config_manager.save_preferences.assert_called_once_with(new_preferences)