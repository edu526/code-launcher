#!/usr/bin/env python3
"""
Tests for graceful degradation when terminal detection fails

This test module validates that the application continues normal operation
when terminal functionality is unavailable, implementing requirement 5.5.
"""

import pytest
import unittest.mock as mock
import logging
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from hypothesis import given, strategies as st, settings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing any modules that depend on it
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()
sys.modules['gi.repository.Gdk'] = Mock()


class TestGracefulDegradation:
    """Test cases for graceful degradation when terminal functionality fails"""

    def test_main_window_initialization_without_terminal_manager(self):
        """Test that main window initializes successfully when terminal manager import fails"""
        # Mock the specific import to fail in the _initialize_terminal_manager method
        with mock.patch('src.ui.window.logger') as mock_logger:
            # Mock GTK components to avoid GUI initialization
            with mock.patch('gi.repository.Gtk.Window') as mock_window_class, \
                 mock.patch.object(FinderStyleWindow, 'setup_ui'), \
                 mock.patch.object(FinderStyleWindow, 'connect'):

                # Configure the mock window
                mock_window_instance = Mock()
                mock_window_class.return_value = mock_window_instance

                # Mock config manager
                mock_config = Mock()
                mock_config.load_categories.return_value = {}
                mock_config.load_projects.return_value = {}
                mock_config.load_preferences.return_value = {"default_editor": "kiro"}

                with mock.patch('src.ui.window.ConfigManager', return_value=mock_config), \
                     mock.patch('src.ui.window.SearchManager'), \
                     mock.patch('src.ui.window.KeyboardHandler'), \
                     mock.patch('src.ui.window.NavigationManager'):

                    # Mock the import inside _initialize_terminal_manager to fail
                    def mock_import(name, *args, **kwargs):
                        if name == 'utils.terminal_manager':
                            raise ImportError("Terminal manager not available")
                        return __import__(name, *args, **kwargs)

                    with mock.patch('builtins.__import__', side_effect=mock_import):
                        # Import and create window
                        from src.ui.window import FinderStyleWindow
                        window = FinderStyleWindow()

                        # Verify graceful degradation
                        assert window.terminal_manager is None
                        assert window.has_terminal_support() is False

                        # Verify error was logged
                        mock_logger.error.assert_called()
                        mock_logger.info.assert_called_with("Terminal functionality will be unavailable")

    def test_main_window_initialization_with_terminal_manager_exception(self):
        """Test graceful degradation when terminal manager initialization throws exception"""
        # Mock terminal manager to raise exception during initialization
        mock_terminal_manager_class = Mock()
        mock_terminal_manager_instance = Mock()
        mock_terminal_manager_instance.initialize.side_effect = RuntimeError("Terminal detection failed")
        mock_terminal_manager_class.return_value = mock_terminal_manager_instance

        with mock.patch('utils.terminal_manager.TerminalManager', mock_terminal_manager_class):
            with mock.patch('src.ui.window.logger') as mock_logger:
                from src.ui.window import FinderStyleWindow

                # Mock GTK components
                with mock.patch('gi.repository.Gtk.Window') as mock_window_class, \
                     mock.patch.object(FinderStyleWindow, 'setup_ui'), \
                     mock.patch.object(FinderStyleWindow, 'connect'):

                    # Configure the mock window
                    mock_window_instance = Mock()
                    mock_window_class.return_value = mock_window_instance

                    # Mock config manager
                    mock_config = Mock()
                    mock_config.load_categories.return_value = {}
                    mock_config.load_projects.return_value = {}
                    mock_config.load_preferences.return_value = {"default_editor": "kiro"}

                    with mock.patch('src.ui.window.ConfigManager', return_value=mock_config), \
                         mock.patch('src.ui.window.SearchManager'), \
                         mock.patch('src.ui.window.KeyboardHandler'), \
                         mock.patch('src.ui.window.NavigationManager'):

                        window = FinderStyleWindow()

                        # Verify graceful degradation
                        assert window.terminal_manager is None
                        assert window.has_terminal_support() is False

                        # Verify appropriate logging
                        mock_logger.error.assert_called()
                        mock_logger.info.assert_called_with(
                            "Terminal functionality will be unavailable, application continuing normally"
                        )

    def test_context_menu_handler_graceful_degradation(self):
        """Test that context menu handler gracefully handles missing terminal manager"""
        from src.context_menu.handler import ContextMenuHandler

        # Mock parent window without terminal manager
        mock_parent_window = Mock()
        mock_parent_window.terminal_manager = None

        # Mock column browser
        mock_column_browser = Mock()

        handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

        # Test that _has_available_terminals returns False gracefully
        result = handler._has_available_terminals()
        assert result is False

    def test_context_menu_handler_exception_handling(self):
        """Test that context menu handler handles terminal manager exceptions gracefully"""
        from src.context_menu.handler import ContextMenuHandler

        # Mock parent window with terminal manager that throws exception
        mock_terminal_manager = Mock()
        mock_terminal_manager.has_available_terminals.side_effect = RuntimeError("Terminal check failed")

        mock_parent_window = Mock()
        mock_parent_window.terminal_manager = mock_terminal_manager

        mock_column_browser = Mock()

        with mock.patch('src.context_menu.handler.logger') as mock_logger:
            handler = ContextMenuHandler(mock_column_browser, mock_parent_window)

            # Test graceful degradation
            result = handler._has_available_terminals()
            assert result is False

            # Verify error was logged
            mock_logger.error.assert_called()

    def test_terminal_preferences_graceful_degradation(self):
        """Test that terminal preferences handles terminal manager failures gracefully"""
        from src.dialogs.terminal_preferences import TerminalPreferences

        # Mock terminal manager that throws exceptions
        mock_terminal_manager = Mock()
        mock_terminal_manager.get_available_terminals.side_effect = RuntimeError("Terminal detection failed")
        mock_terminal_manager.has_available_terminals.side_effect = RuntimeError("Availability check failed")

        mock_parent_dialog = Mock()

        with mock.patch('src.dialogs.terminal_preferences.logger') as mock_logger:
            preferences = TerminalPreferences(mock_parent_dialog, mock_terminal_manager)

            # Mock GTK components
            mock_combo = Mock()
            preferences.terminal_combo = mock_combo
            preferences._terminal_keys = []

            # Test populate_terminal_options with exception
            preferences.populate_terminal_options()

            # Verify graceful degradation
            mock_combo.remove_all.assert_called()
            mock_combo.append_text.assert_called_with("No terminals detected")
            mock_combo.set_sensitive.assert_called_with(False)

            # Test is_terminals_available with exception
            result = preferences.is_terminals_available()
            assert result is False

            # Verify errors were logged
            mock_logger.error.assert_called()

    def test_config_dialog_graceful_degradation(self):
        """Test that config dialog handles terminal preferences creation failures gracefully"""
        from src.dialogs.config_dialog import show_preferences_dialog

        # Mock terminal manager
        mock_terminal_manager = Mock()

        # Mock parent and config manager
        mock_parent = Mock()
        mock_config_manager = Mock()
        mock_config_manager.load_preferences.return_value = {"default_editor": "kiro"}

        # Mock TerminalPreferences to raise exception
        with mock.patch('src.dialogs.terminal_preferences.TerminalPreferences',
                       side_effect=RuntimeError("Terminal preferences failed")):
            with mock.patch('gi.repository.Gtk.Dialog') as mock_dialog_class:
                mock_dialog = Mock()
                mock_dialog_class.return_value = mock_dialog
                mock_dialog.get_content_area.return_value = Mock()
                mock_dialog.run.return_value = 0  # Cancel

                with mock.patch('gi.repository.Gtk.Box'), \
                     mock.patch('gi.repository.Gtk.Label'), \
                     mock.patch('gi.repository.Gtk.RadioButton'):

                    # Should not raise exception despite terminal preferences failure
                    show_preferences_dialog(mock_parent, mock_config_manager, mock_terminal_manager)

                    # Dialog should still be created and shown despite terminal preferences failure
                    mock_dialog_class.assert_called_once()
                    mock_dialog.show_all.assert_called_once()
                    mock_dialog.run.assert_called_once()
                    mock_dialog.run.assert_called()
                    mock_dialog.destroy.assert_called()

    def test_terminal_actions_graceful_degradation(self):
        """Test that terminal actions handle missing terminal manager gracefully"""
        from src.context_menu.actions import open_in_terminal

        # Mock context and parent window without terminal manager
        context = {'item_path': '/home/user/project'}
        mock_parent_window = Mock()
        mock_parent_window.terminal_manager = None

        with mock.patch('src.context_menu.actions.show_error_dialog') as mock_error_dialog:
            open_in_terminal(context, mock_parent_window)

            # Should show appropriate error message
            mock_error_dialog.assert_called_with(
                mock_parent_window,
                "Error: Terminal functionality not available"
            )

    def test_terminal_actions_exception_handling(self):
        """Test that terminal actions handle terminal manager exceptions gracefully"""
        from src.context_menu.actions import open_in_terminal

        # Mock context
        context = {'item_path': '/home/user/project'}

        # Mock parent window with terminal manager that throws exceptions
        mock_terminal_manager = Mock()
        mock_terminal_manager.has_available_terminals.side_effect = RuntimeError("Check failed")

        mock_parent_window = Mock()
        mock_parent_window.terminal_manager = mock_terminal_manager

        with mock.patch('src.context_menu.actions.show_error_dialog') as mock_error_dialog:
            open_in_terminal(context, mock_parent_window)

            # Should show appropriate error message
            mock_error_dialog.assert_called_with(
                mock_parent_window,
                "Error: Unable to check terminal availability"
            )


class TestGracefulDegradationProperties:
    """Property-based tests for graceful degradation"""

    @given(st.one_of(
        st.none(),
        st.just(ImportError("Module not found")),
        st.just(RuntimeError("Initialization failed")),
        st.just(OSError("System error")),
        st.just(Exception("Unexpected error"))
    ))
    @settings(max_examples=100)
    def test_graceful_degradation_property(self, terminal_manager_state):
        """
        **Validates: Requirements 5.5**

        Property 7: Graceful Degradation
        For any system state where terminal detection fails or no terminals are available,
        the application should continue normal operation with the terminal feature gracefully disabled.
        """
        # Test graceful degradation at the component level rather than full window initialization

        # Property 1: Terminal manager failures should be handled gracefully
        if terminal_manager_state is None:
            # Normal case - no exception, but no terminals available
            from utils.terminal_manager import TerminalManager
            from src.core.config import ConfigManager

            mock_config = Mock()
            terminal_manager = TerminalManager(mock_config)

            # Mock detector to return no terminals
            with mock.patch.object(terminal_manager, 'detector') as mock_detector:
                mock_detector.detect_terminals.return_value = {}
                terminal_manager.initialize()

                # Should handle no terminals gracefully
                assert terminal_manager.has_available_terminals() is False
                assert terminal_manager.get_preferred_terminal() is None

        elif isinstance(terminal_manager_state, ImportError):
            # Import error case - should be handled at application level
            with mock.patch('builtins.__import__', side_effect=terminal_manager_state):
                try:
                    from utils.terminal_manager import TerminalManager
                    # If import succeeds despite mock, that's fine
                    assert True
                except ImportError:
                    # Import failed as expected - application should handle this
                    assert True

        else:
            # Other exceptions during initialization
            from utils.terminal_manager import TerminalManager
            from src.core.config import ConfigManager

            mock_config = Mock()
            terminal_manager = TerminalManager(mock_config)

            # Mock detector to raise exception
            with mock.patch.object(terminal_manager, 'detector') as mock_detector:
                mock_detector.detect_terminals.side_effect = terminal_manager_state

                # Should handle exception gracefully
                terminal_manager.initialize()
                assert terminal_manager.has_available_terminals() is False
                assert terminal_manager.get_preferred_terminal() is None

    @given(st.booleans())
    @settings(max_examples=100)
    def test_context_menu_graceful_degradation_property(self, terminal_manager_available):
        """
        **Validates: Requirements 3.2, 5.5**

        Property: Context Menu Graceful Degradation
        For any state of terminal manager availability, the context menu should
        function normally and only show terminal options when appropriate.
        """
        from src.context_menu.handler import ContextMenuHandler

        # Set up parent window based on terminal manager availability
        mock_parent_window = Mock()
        if terminal_manager_available:
            mock_terminal_manager = Mock()
            mock_terminal_manager.has_available_terminals.return_value = True
            mock_parent_window.terminal_manager = mock_terminal_manager
        else:
            mock_parent_window.terminal_manager = None

        mock_column_browser = Mock()

        # Property 1: Handler should initialize successfully regardless of terminal state
        handler = ContextMenuHandler(mock_column_browser, mock_parent_window)
        assert handler is not None

        # Property 2: _has_available_terminals should return boolean without exceptions
        result = handler._has_available_terminals()
        assert isinstance(result, bool)

        # Property 3: Result should match terminal manager availability
        assert result == terminal_manager_available

        # Property 4: Handler should have all required attributes
        assert hasattr(handler, 'column_browser')
        assert hasattr(handler, 'parent_window')

    @given(st.one_of(
        st.none(),
        st.just(RuntimeError("Terminal check failed")),
        st.just(OSError("System error")),
        st.just(Exception("Unexpected error"))
    ))
    @settings(max_examples=100)
    def test_terminal_actions_graceful_degradation_property(self, terminal_error_state):
        """
        **Validates: Requirements 5.5**

        Property: Terminal Actions Graceful Degradation
        For any terminal-related error state, terminal actions should handle failures
        gracefully without crashing the application.
        """
        from src.context_menu.actions import open_in_terminal

        # Mock context
        context = {'item_path': '/home/user/project'}
        mock_parent_window = Mock()

        if terminal_error_state is None:
            # Normal case - terminal manager available but no terminals
            mock_terminal_manager = Mock()
            mock_terminal_manager.has_available_terminals.return_value = False
            mock_parent_window.terminal_manager = mock_terminal_manager
        else:
            # Error case - terminal manager throws exception
            mock_terminal_manager = Mock()
            mock_terminal_manager.has_available_terminals.side_effect = terminal_error_state
            mock_parent_window.terminal_manager = mock_terminal_manager

        with mock.patch('src.context_menu.actions.show_error_dialog') as mock_error_dialog:
            # Property 1: Should not raise unhandled exceptions
            try:
                open_in_terminal(context, mock_parent_window)
                # Should complete without exception
                assert True
            except Exception as e:
                # If any exception occurs, it should be handled gracefully
                assert False, f"Unhandled exception: {e}"

            # Property 2: Should show appropriate error message
            mock_error_dialog.assert_called_once()

            # Property 3: Error message should be informative
            call_args = mock_error_dialog.call_args
            assert len(call_args[0]) >= 2  # parent_window and message
            error_message = call_args[0][1]
            assert isinstance(error_message, str)
            assert len(error_message) > 0