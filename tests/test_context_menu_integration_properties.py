#!/usr/bin/env python3
"""
Property-based tests for context menu integration with terminal functionality
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import pytest
from hypothesis import given, strategies as st, settings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before any imports
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()
sys.modules['gi.repository.Gdk'] = Mock()

# Import after mocking GTK
from src.context_menu.handler import ContextMenuHandler
from src.context_menu.context_detector import (
    ROOT_COLUMN,
    CHILD_COLUMN,
    CATEGORY_ITEM,
    PROJECT_ITEM
)


class TestContextMenuIntegrationProperties:
    """Property-based tests for context menu integration with terminal functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock column browser and parent window
        self.mock_column_browser = Mock()
        self.mock_parent_window = Mock()

    @given(st.sets(
        st.sampled_from(['gnome-terminal', 'konsole', 'xterm', 'alacritty', 'warp', 'terminator', 'tilix', 'kitty']),
        min_size=0,
        max_size=8
    ))
    @settings(max_examples=100)
    def test_context_menu_conditional_display_terminal_availability_logic(self, available_terminals):
        """
        **Validates: Requirements 3.1, 3.2, 3.4**

        Property 3: Context Menu Conditional Display
        For any project item, the context menu should display "Open In Terminal" if and only if
        at least one terminal is detected, while maintaining all existing menu items and their ordering.

        This test focuses on the core logic of _has_available_terminals method which determines
        whether the terminal option should be shown in the context menu.
        """
        # Set up terminal manager mock
        mock_terminal_manager = Mock()
        mock_terminal_manager.has_available_terminals.return_value = len(available_terminals) > 0
        mock_terminal_manager.get_available_terminals.return_value = {
            terminal: {
                'name': f'Test {terminal}',
                'executable': terminal,
                'path': f'/usr/bin/{terminal}'
            }
            for terminal in available_terminals
        }

        # Set up parent window with terminal manager
        self.mock_parent_window.terminal_manager = mock_terminal_manager

        # Create handler instance
        handler = ContextMenuHandler(self.mock_column_browser, self.mock_parent_window)

        # Property 1: _has_available_terminals should return True if and only if terminals are available
        has_terminals_result = handler._has_available_terminals()
        expected_result = len(available_terminals) > 0

        assert has_terminals_result == expected_result, \
            f"_has_available_terminals() returned {has_terminals_result}, expected {expected_result} for terminals: {available_terminals}"

        # Property 2: Terminal manager should be called to check availability
        mock_terminal_manager.has_available_terminals.assert_called_once()

        # Property 3: Result should be consistent across multiple calls
        second_result = handler._has_available_terminals()
        assert second_result == has_terminals_result, \
            "Multiple calls to _has_available_terminals should return consistent results"


if __name__ == '__main__':
    pytest.main([__file__])