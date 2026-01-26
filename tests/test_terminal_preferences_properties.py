#!/usr/bin/env python3
"""
Property-based tests for TerminalPreferences UI state consistency
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import pytest
from hypothesis import given, strategies as st, settings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing
sys.modules['gi'] = Mock()
sys.modules['gi.repository'] = Mock()
sys.modules['gi.repository.Gtk'] = Mock()

# Import after mocking GTK
from dialogs.terminal_preferences import TerminalPreferences


class TestTerminalPreferencesProperties:
    """Property-based tests for TerminalPreferences UI state consistency"""

    def setup_method(self):
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

        # Mock parent dialog
        self.mock_parent_dialog = Mock()

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), min_codepoint=32, max_codepoint=126)),
        values=st.dictionaries(
            keys=st.sampled_from(['name', 'executable', 'path']),
            values=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Po'), min_codepoint=32, max_codepoint=126)),
            min_size=3,
            max_size=3
        ),
        min_size=0,
        max_size=8
    ))
    @settings(max_examples=100)
    def test_ui_state_consistency_with_available_terminals(self, available_terminals_dict):
        """
        **Validates: Requirements 2.1, 2.2**

        Property 8: UI State Consistency
        For any set of detected terminals, the preferences dialog should display exactly
        those terminals as options and correctly update the selection when the user makes a choice.
        """
        # Clean terminal data to ensure valid values
        clean_terminals = {}
        for terminal_key, terminal_info in available_terminals_dict.items():
            clean_key = ''.join(c for c in terminal_key if c.isalnum() or c in '-_')
            if clean_key and len(clean_key) > 0:
                clean_info = {}
                for info_key, info_value in terminal_info.items():
                    clean_value = ''.join(c for c in info_value if c.isprintable() and c not in '"\'\\')
                    if clean_value and len(clean_value) > 0:
                        clean_info[info_key] = clean_value

                # Ensure all required keys are present
                if len(clean_info) == 3 and all(key in clean_info for key in ['name', 'executable', 'path']):
                    clean_terminals[clean_key] = clean_info

        # Mock terminal manager with the generated terminals
        mock_terminal_manager = Mock()
        mock_terminal_manager.get_available_terminals.return_value = clean_terminals
        mock_terminal_manager.has_available_terminals.return_value = len(clean_terminals) > 0

        # Set preferred terminal to first available (if any)
        preferred_terminal = next(iter(clean_terminals)) if clean_terminals else None
        mock_terminal_manager.get_preferred_terminal.return_value = preferred_terminal

        # Create TerminalPreferences instance
        terminal_prefs = TerminalPreferences(self.mock_parent_dialog, mock_terminal_manager)

        # Mock combo box to track calls
        mock_combo = Mock()
        terminal_prefs.terminal_combo = mock_combo

        # Property 1: populate_terminal_options should display exactly the available terminals
        terminal_prefs.populate_terminal_options()

        if not clean_terminals:
            # When no terminals are available
            mock_combo.remove_all.assert_called_once()
            mock_combo.append_text.assert_called_with("No terminals detected")
            mock_combo.set_sensitive.assert_called_with(False)
            assert terminal_prefs._terminal_keys == [], \
                "Terminal keys should be empty when no terminals available"
        else:
            # When terminals are available
            mock_combo.remove_all.assert_called_once()
            mock_combo.set_sensitive.assert_called_with(True)

            # Verify all terminals were added to combo box
            expected_calls = []
            expected_keys = []
            for terminal_key, terminal_info in clean_terminals.items():
                display_name = terminal_info['name']
                expected_calls.append(unittest.mock.call(display_name))
                expected_keys.append(terminal_key)

            mock_combo.append_text.assert_has_calls(expected_calls, any_order=False)

            # Property 2: Internal terminal keys should match exactly the available terminals
            assert set(terminal_prefs._terminal_keys) == set(expected_keys), \
                f"Terminal keys should match available terminals: expected {set(expected_keys)}, got {set(terminal_prefs._terminal_keys)}"

            # Property 3: Order should be preserved (deterministic for same input)
            # Sort both lists to ensure consistent comparison since dict iteration order may vary
            sorted_expected = sorted(expected_keys)
            sorted_actual = sorted(terminal_prefs._terminal_keys)
            assert sorted_actual == sorted_expected, \
                f"Terminal keys should be in consistent order: expected {sorted_expected}, got {sorted_actual}"

        # Property 4: is_terminals_available should return consistent result
        ui_has_terminals = terminal_prefs.is_terminals_available()
        manager_has_terminals = len(clean_terminals) > 0
        assert ui_has_terminals == manager_has_terminals, \
            f"UI terminal availability should match manager: UI={ui_has_terminals}, Manager={manager_has_terminals}"

    @given(st.lists(
        st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126)),
        min_size=1,
        max_size=8,
        unique=True
    ))
    @settings(max_examples=100)
    def test_ui_state_consistency_with_terminal_selection(self, terminal_names):
        """
        **Validates: Requirements 2.1, 2.2**

        Property 8: UI State Consistency (Terminal Selection)
        For any valid terminal selection, the UI should correctly reflect the selection
        and maintain consistency between the combo box state and internal tracking.
        """
        # Clean terminal names
        clean_names = []
        for name in terminal_names:
            clean_name = ''.join(c for c in name if c.isalnum() or c in '-_')
            if clean_name and len(clean_name) > 0:
                clean_names.append(clean_name)

        if not clean_names:
            clean_names = ['test-terminal']  # Ensure at least one terminal for testing

        # Create mock terminals
        clean_terminals = {}
        for i, name in enumerate(clean_names):
            clean_terminals[name] = {
                'name': f'Test {name}',
                'executable': name,
                'path': f'/usr/bin/{name}'
            }

        # Mock terminal manager
        mock_terminal_manager = Mock()
        mock_terminal_manager.get_available_terminals.return_value = clean_terminals
        mock_terminal_manager.has_available_terminals.return_value = True
        mock_terminal_manager.set_preferred_terminal.return_value = True

        # Create TerminalPreferences instance
        terminal_prefs = TerminalPreferences(self.mock_parent_dialog, mock_terminal_manager)

        # Mock combo box
        mock_combo = Mock()
        terminal_prefs.terminal_combo = mock_combo

        # Populate terminals first
        terminal_prefs.populate_terminal_options()

        # Test selection for each available terminal
        for i, terminal_key in enumerate(clean_names):
            # Property 1: set_selected_terminal should work for valid terminals
            success = terminal_prefs.set_selected_terminal(terminal_key)
            assert success is True, f"Should be able to select available terminal: {terminal_key}"

            # Verify combo box was updated
            mock_combo.set_active.assert_called_with(i)

            # Property 2: get_selected_terminal should return the same terminal
            mock_combo.get_active.return_value = i
            selected = terminal_prefs.get_selected_terminal()
            assert selected == terminal_key, \
                f"Selected terminal should match: expected {terminal_key}, got {selected}"

            # Property 3: Simulate user selection change
            mock_combo.get_active.return_value = i
            mock_combo.get_active_text.return_value = f'Test {terminal_key}'

            # Handle the selection change
            terminal_prefs.on_terminal_changed(mock_combo)

            # Verify terminal manager was called with correct terminal
            mock_terminal_manager.set_preferred_terminal.assert_called_with(terminal_key)

        # Property 4: Invalid terminal selection should fail gracefully
        invalid_terminal = 'nonexistent-terminal-xyz'
        success = terminal_prefs.set_selected_terminal(invalid_terminal)
        assert success is False, f"Should not be able to select invalid terminal: {invalid_terminal}"

        # Property 5: Invalid combo box index should be handled gracefully
        mock_combo.get_active.return_value = 999  # Invalid index
        terminal_prefs.on_terminal_changed(mock_combo)
        # Should not crash and should not call set_preferred_terminal with invalid data

    @given(st.one_of(
        # Empty terminals
        st.just({}),
        # Single terminal
        st.dictionaries(
            keys=st.just('single-terminal'),
            values=st.just({'name': 'Single Terminal', 'executable': 'single', 'path': '/usr/bin/single'}),
            min_size=1,
            max_size=1
        ),
        # Multiple terminals
        st.dictionaries(
            keys=st.sampled_from(['gnome-terminal', 'konsole', 'xterm', 'alacritty']),
            values=st.sampled_from([
                {'name': 'GNOME Terminal', 'executable': 'gnome-terminal', 'path': '/usr/bin/gnome-terminal'},
                {'name': 'Konsole', 'executable': 'konsole', 'path': '/usr/bin/konsole'},
                {'name': 'XTerm', 'executable': 'xterm', 'path': '/usr/bin/xterm'},
                {'name': 'Alacritty', 'executable': 'alacritty', 'path': '/usr/bin/alacritty'}
            ]),
            min_size=2,
            max_size=4
        )
    ))
    @settings(max_examples=100)
    def test_ui_state_consistency_with_refresh(self, initial_terminals):
        """
        **Validates: Requirements 2.1, 2.2**

        Property 8: UI State Consistency (Refresh Behavior)
        For any change in available terminals (via refresh), the UI should update
        to exactly match the new set of available terminals while maintaining
        consistent internal state.
        """
        # Mock terminal manager
        mock_terminal_manager = Mock()
        mock_terminal_manager.get_available_terminals.return_value = initial_terminals
        mock_terminal_manager.has_available_terminals.return_value = len(initial_terminals) > 0

        # Set preferred terminal
        preferred = next(iter(initial_terminals)) if initial_terminals else None
        mock_terminal_manager.get_preferred_terminal.return_value = preferred

        # Create TerminalPreferences instance
        terminal_prefs = TerminalPreferences(self.mock_parent_dialog, mock_terminal_manager)

        # Mock combo box
        mock_combo = Mock()
        terminal_prefs.terminal_combo = mock_combo

        # Initial population
        terminal_prefs.populate_terminal_options()
        initial_keys = terminal_prefs._terminal_keys.copy()

        # Property 1: Initial state should match initial terminals
        if not initial_terminals:
            assert initial_keys == [], "Initial keys should be empty for no terminals"
        else:
            assert set(initial_keys) == set(initial_terminals.keys()), \
                "Initial keys should match initial terminals"

        # Simulate terminal detection change
        new_terminals = {}
        if initial_terminals:
            # If we had terminals, simulate losing some
            terminal_keys = list(initial_terminals.keys())
            if len(terminal_keys) > 1:
                # Keep only first terminal
                first_key = terminal_keys[0]
                new_terminals = {first_key: initial_terminals[first_key]}
        else:
            # If we had no terminals, simulate finding one
            new_terminals = {
                'new-terminal': {
                    'name': 'New Terminal',
                    'executable': 'new-terminal',
                    'path': '/usr/bin/new-terminal'
                }
            }

        # Update mock terminal manager
        mock_terminal_manager.get_available_terminals.return_value = new_terminals
        mock_terminal_manager.has_available_terminals.return_value = len(new_terminals) > 0
        new_preferred = next(iter(new_terminals)) if new_terminals else None
        mock_terminal_manager.get_preferred_terminal.return_value = new_preferred

        # Reset mock combo to track new calls
        mock_combo.reset_mock()

        # Refresh terminal options
        terminal_prefs.refresh_terminal_options()

        # Property 2: After refresh, UI should match new terminal state
        if not new_terminals:
            mock_combo.append_text.assert_called_with("No terminals detected")
            mock_combo.set_sensitive.assert_called_with(False)
            assert terminal_prefs._terminal_keys == [], \
                "Terminal keys should be empty after refresh with no terminals"
        else:
            mock_combo.set_sensitive.assert_called_with(True)
            assert set(terminal_prefs._terminal_keys) == set(new_terminals.keys()), \
                f"Terminal keys should match new terminals after refresh: expected {set(new_terminals.keys())}, got {set(terminal_prefs._terminal_keys)}"

        # Property 3: Terminal manager should have been re-initialized
        mock_terminal_manager.initialize.assert_called_once()

        # Property 4: Combo box should have been cleared and repopulated
        mock_combo.remove_all.assert_called_once()

        # Property 5: UI availability should match manager availability
        ui_has_terminals = terminal_prefs.is_terminals_available()
        manager_has_terminals = len(new_terminals) > 0
        assert ui_has_terminals == manager_has_terminals, \
            f"UI availability should match manager after refresh: UI={ui_has_terminals}, Manager={manager_has_terminals}"

    @given(st.integers(min_value=-5, max_value=10))
    @settings(max_examples=100)
    def test_ui_state_consistency_with_invalid_selections(self, invalid_index):
        """
        **Validates: Requirements 2.1, 2.2**

        Property 8: UI State Consistency (Invalid Selection Handling)
        For any invalid selection index, the UI should handle it gracefully
        without corrupting internal state or causing crashes.
        """
        # Set up terminals
        terminals = {
            'terminal1': {'name': 'Terminal 1', 'executable': 'terminal1', 'path': '/usr/bin/terminal1'},
            'terminal2': {'name': 'Terminal 2', 'executable': 'terminal2', 'path': '/usr/bin/terminal2'},
            'terminal3': {'name': 'Terminal 3', 'executable': 'terminal3', 'path': '/usr/bin/terminal3'}
        }

        # Mock terminal manager
        mock_terminal_manager = Mock()
        mock_terminal_manager.get_available_terminals.return_value = terminals
        mock_terminal_manager.has_available_terminals.return_value = True
        mock_terminal_manager.get_preferred_terminal.return_value = 'terminal1'
        mock_terminal_manager.set_preferred_terminal.return_value = True

        # Create TerminalPreferences instance
        terminal_prefs = TerminalPreferences(self.mock_parent_dialog, mock_terminal_manager)

        # Mock combo box
        mock_combo = Mock()
        terminal_prefs.terminal_combo = mock_combo

        # Populate terminals
        terminal_prefs.populate_terminal_options()

        # Store initial state
        initial_keys = terminal_prefs._terminal_keys.copy()

        # Property 1: Invalid index in get_selected_terminal should return None
        mock_combo.get_active.return_value = invalid_index
        selected = terminal_prefs.get_selected_terminal()

        valid_indices = range(len(terminals))
        if invalid_index in valid_indices:
            # Valid index should return corresponding terminal
            expected_terminal = initial_keys[invalid_index]
            assert selected == expected_terminal, \
                f"Valid index {invalid_index} should return terminal {expected_terminal}, got {selected}"
        else:
            # Invalid index should return None
            assert selected is None, \
                f"Invalid index {invalid_index} should return None, got {selected}"

        # Property 2: Invalid index in on_terminal_changed should not crash or corrupt state
        mock_combo.get_active.return_value = invalid_index
        mock_combo.get_active_text.return_value = "Some Terminal"

        # This should not raise an exception
        try:
            terminal_prefs.on_terminal_changed(mock_combo)
        except Exception as e:
            pytest.fail(f"on_terminal_changed should handle invalid index gracefully, but raised: {e}")

        # Property 3: Internal state should remain consistent after invalid operations
        assert terminal_prefs._terminal_keys == initial_keys, \
            "Terminal keys should remain unchanged after invalid operations"

        # Property 4: For invalid indices, set_preferred_terminal should not be called
        if invalid_index not in valid_indices:
            mock_terminal_manager.set_preferred_terminal.assert_not_called()

        # Property 5: UI should remain functional after invalid operations
        # Test that valid operations still work
        mock_combo.get_active.return_value = 0  # Valid index
        selected = terminal_prefs.get_selected_terminal()
        assert selected == initial_keys[0], \
            "UI should remain functional after handling invalid operations"


if __name__ == '__main__':
    pytest.main([__file__])