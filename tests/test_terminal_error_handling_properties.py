#!/usr/bin/env python3
"""
Property-based tests for terminal error handling and fallback mechanisms

This test module validates Property 5: Error Handling and Fallback
which ensures the terminal system handles failures gracefully and provides
appropriate fallback behavior and error messages.
"""

import pytest
import unittest.mock as mock
import subprocess
import os
import tempfile
import logging
from hypothesis import given, strategies as st, settings, assume
from utils.terminal_manager import TerminalManager
from utils.terminal_detector import TerminalDetector


class MockConfigManager:
    """Mock ConfigManager for testing"""

    def __init__(self):
        self.preferences = {}

    def load_preferences(self):
        return self.preferences.copy()

    def save_preferences(self, preferences):
        self.preferences = preferences.copy()


class TestTerminalErrorHandlingProperties:
    """Property-based tests for terminal error handling and fallback mechanisms"""

    @given(st.sets(
        st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())),
        min_size=1,
        max_size=8
    ))
    @settings(max_examples=100)
    def test_error_handling_and_fallback_property(self, available_terminals):
        """
        **Validates: Requirements 5.1, 5.3, 5.4**

        Property 5: Error Handling and Fallback
        For any terminal launch failure (missing terminal, inaccessible directory, or launch error),
        the system should either successfully fall back to an alternative terminal or provide a
        specific, user-friendly error message while logging the failure.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Set up available terminals
        available_list = list(available_terminals)
        manager.available_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_list
        }

        # Set preferred terminal to first available
        manager.preferred_terminal = available_list[0]

        # Create a valid test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_directory = os.path.join(temp_dir, 'test-project')
            os.makedirs(test_directory, exist_ok=True)

            # Test Case 1: Preferred terminal fails, fallback succeeds
            # Property 5.1: When preferred terminal cannot be launched, system should attempt fallback
            if len(available_list) > 1:
                call_count = 0
                def mock_popen_preferred_fails(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:  # Preferred terminal fails
                        raise FileNotFoundError("Preferred terminal not found")
                    else:  # Fallback succeeds
                        return mock.Mock(pid=12345)

                with mock.patch('subprocess.Popen', side_effect=mock_popen_preferred_fails), \
                     mock.patch('utils.terminal_manager.logger') as mock_logger:

                    success, error_msg = manager.open_terminal(test_directory)

                    # Property: Should succeed with fallback
                    assert success is True, "Should succeed when fallback terminal works"
                    assert error_msg == "", "No error message when fallback succeeds"

                    # Property 5.4: Should log the failure and fallback attempt
                    mock_logger.warning.assert_called()
                    mock_logger.info.assert_called()

                    # Verify at least 2 attempts were made (preferred + fallback)
                    assert call_count >= 2, "Should attempt preferred terminal and at least one fallback"

            # Test Case 2: All terminals fail - comprehensive error message
            # Property 5.1 & 5.3: When all terminals fail, provide specific error details
            with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("All terminals fail")), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property: Should fail with comprehensive error message
                assert success is False, "Should fail when all terminals fail"
                assert len(error_msg) > 0, "Should provide error message when all terminals fail"

                # Property 5.3: Error message should contain specific details
                assert "Failed to open terminal" in error_msg, "Error message should mention terminal failure"
                assert manager.preferred_terminal in error_msg, "Error message should mention preferred terminal"

                if len(available_list) > 1:
                    assert "fallback" in error_msg.lower(), "Error message should mention fallback attempts"
                    assert str(len(available_list) - 1) in error_msg, "Error message should mention number of fallbacks tried"

                # Property 5.4: Should log all failure attempts
                mock_logger.error.assert_called()

            # Test Case 3: Directory validation errors
            # Property 5.3: Inaccessible directory should provide specific error details
            test_cases = [
                (None, "No directory path provided"),
                ("", "No directory path provided"),
                ("/nonexistent/path/xyz", "Directory does not exist"),
            ]

            for invalid_path, expected_error_fragment in test_cases:
                with mock.patch('utils.terminal_manager.logger') as mock_logger:
                    success, error_msg = manager.open_terminal(invalid_path)

                    # Property: Should fail with specific error message
                    assert success is False, f"Should fail for invalid path: {invalid_path}"
                    assert expected_error_fragment in error_msg, \
                        f"Error message should contain '{expected_error_fragment}' for path: {invalid_path}"

                    # Property 5.4: Should log directory validation failure
                    mock_logger.error.assert_called()

            # Test Case 4: File instead of directory
            file_path = os.path.join(temp_dir, 'test-file.txt')
            with open(file_path, 'w') as f:
                f.write('test')

            with mock.patch('utils.terminal_manager.logger') as mock_logger:
                success, error_msg = manager.open_terminal(file_path)

                # Property 5.3: Should provide specific error for file vs directory
                assert success is False, "Should fail when path is a file, not directory"
                assert "not a directory" in error_msg, "Error message should specify path is not a directory"
                assert file_path in error_msg, "Error message should include the problematic path"

                # Property 5.4: Should log the validation error
                mock_logger.error.assert_called()

    @given(st.sampled_from([
        FileNotFoundError("Terminal executable not found"),
        PermissionError("Permission denied"),
        subprocess.SubprocessError("Process failed to start"),
        OSError("System error occurred"),
        RuntimeError("Unexpected runtime error")
    ]))
    @settings(max_examples=100)
    def test_specific_launch_error_handling_property(self, launch_exception):
        """
        **Validates: Requirements 5.1, 5.3, 5.4**

        Property 5: Error Handling and Fallback (Specific Launch Errors)
        For any specific type of terminal launch error, the system should handle it
        gracefully, attempt fallbacks, and provide appropriate error messages with logging.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Set up multiple terminals for fallback testing
        manager.available_terminals = {
            'primary-terminal': {
                'name': 'Primary Terminal',
                'executable': 'primary-terminal',
                'path': '/usr/bin/primary-terminal'
            },
            'fallback-terminal': {
                'name': 'Fallback Terminal',
                'executable': 'fallback-terminal',
                'path': '/usr/bin/fallback-terminal'
            }
        }
        manager.preferred_terminal = 'primary-terminal'

        # Create valid test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_directory = os.path.join(temp_dir, 'test-project')
            os.makedirs(test_directory, exist_ok=True)

            # Test Case 1: Primary fails with specific error, fallback succeeds
            call_count = 0
            def mock_popen_with_specific_error(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:  # Primary terminal fails with specific error
                    raise launch_exception
                else:  # Fallback succeeds
                    return mock.Mock(pid=12345)

            with mock.patch('subprocess.Popen', side_effect=mock_popen_with_specific_error), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property 5.1: Should succeed with fallback despite specific error
                assert success is True, f"Should succeed with fallback despite {type(launch_exception).__name__}"
                assert error_msg == "", "No error message when fallback succeeds"

                # Property 5.4: Should log the specific error type
                mock_logger.warning.assert_called()
                warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
                assert any("Primary terminal 'primary-terminal' failed" in call for call in warning_calls), \
                    "Should log primary terminal failure"

                # Verify fallback was attempted
                assert call_count == 2, "Should attempt primary and fallback terminal"

            # Test Case 2: All terminals fail with the same specific error
            with mock.patch('subprocess.Popen', side_effect=launch_exception), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property: Should fail with comprehensive error when all attempts fail
                assert success is False, f"Should fail when all terminals fail with {type(launch_exception).__name__}"
                assert len(error_msg) > 0, "Should provide error message when all terminals fail"

                # Property 5.3: Error message should be user-friendly and informative
                assert "Failed to open terminal" in error_msg, "Error message should mention terminal failure"
                assert "Primary terminal 'primary-terminal' failed" in error_msg, \
                    "Error message should mention primary terminal failure"
                assert "Tried 1 fallback terminal(s)" in error_msg, \
                    "Error message should mention fallback attempts"

                # Property 5.4: Should log all failure attempts
                mock_logger.error.assert_called()
                error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
                assert any("All terminal launch attempts failed" in call for call in error_calls), \
                    "Should log comprehensive failure"

    @given(st.sets(
        st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())),
        min_size=2,
        max_size=6
    ))
    @settings(max_examples=100)
    def test_fallback_priority_and_logging_property(self, available_terminals):
        """
        **Validates: Requirements 5.1, 5.4**

        Property 5: Error Handling and Fallback (Priority and Logging)
        For any set of available terminals, when the preferred terminal fails,
        the system should try fallback terminals in priority order and log
        each attempt appropriately.
        """
        manager = TerminalManager()
        manager._initialized = True

        available_list = list(available_terminals)
        assume(len(available_list) >= 2)  # Need at least 2 terminals for meaningful fallback testing

        # Set up available terminals
        manager.available_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_list
        }

        # Set preferred terminal to first one
        preferred_terminal = available_list[0]
        manager.preferred_terminal = preferred_terminal

        # Create valid test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_directory = os.path.join(temp_dir, 'test-project')
            os.makedirs(test_directory, exist_ok=True)

            # Test fallback behavior - preferred fails, first fallback succeeds
            call_count = 0
            successful_fallback = None

            def mock_popen_fallback_test(*args, **kwargs):
                nonlocal call_count, successful_fallback
                call_count += 1
                if call_count == 1:  # Preferred terminal fails
                    raise FileNotFoundError("Preferred terminal failed")
                elif call_count == 2:  # First fallback succeeds
                    # Determine which fallback terminal this should be
                    fallback_terminals = manager._get_fallback_terminals(exclude=preferred_terminal)
                    if fallback_terminals:
                        successful_fallback = fallback_terminals[0]
                    return mock.Mock(pid=12345)
                else:
                    raise RuntimeError("Unexpected call")

            with mock.patch('subprocess.Popen', side_effect=mock_popen_fallback_test), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property 5.1: Should succeed with first available fallback
                assert success is True, "Should succeed with fallback terminal"
                assert error_msg == "", "No error message when fallback succeeds"

                # Property 5.4: Should log preferred terminal failure
                mock_logger.warning.assert_called()
                warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
                assert any(f"Primary terminal '{preferred_terminal}' failed" in call for call in warning_calls), \
                    "Should log preferred terminal failure"

                # Property 5.4: Should log fallback attempt and success
                info_calls = [call.args[0] for call in mock_logger.info.call_args_list]
                assert any("Attempting fallback terminal" in call for call in info_calls), \
                    "Should log fallback attempt"

                # Property: Should only try preferred + first fallback (not all fallbacks)
                assert call_count == 2, "Should stop after first successful fallback"

            # Test comprehensive fallback failure - all terminals fail
            with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("All terminals fail")), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property: Should fail after trying all available terminals
                assert success is False, "Should fail when all terminals fail"

                # Property 5.4: Should log all attempts
                expected_attempts = len(available_list)  # All available terminals should be tried

                # Count actual attempts by checking info log calls for launch attempts
                info_calls = [call.args[0] for call in mock_logger.info.call_args_list]
                launch_attempts = [call for call in info_calls if "Attempting to launch terminal" in call or "Attempting fallback terminal" in call]

                # Should have at least attempted the preferred terminal
                assert len(launch_attempts) >= 1, "Should log at least the preferred terminal attempt"

                # Property 5.3: Error message should reflect the number of fallback attempts
                fallback_count = len(available_list) - 1  # All except preferred
                if fallback_count > 0:
                    assert f"Tried {fallback_count} fallback terminal(s)" in error_msg, \
                        f"Error message should mention {fallback_count} fallback attempts"

    @given(st.one_of(
        st.just({}),  # No terminals available
        st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=1, max_size=3)
    ))
    @settings(max_examples=100)
    def test_no_terminals_error_handling_property(self, available_terminals_input):
        """
        **Validates: Requirements 5.2, 5.3, 5.4**

        Property 5: Error Handling and Fallback (No Terminals Available)
        When no terminals are available on the system, the system should provide
        a clear, helpful error message and log the situation appropriately.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Convert set to dict or use empty dict
        if isinstance(available_terminals_input, set):
            available_terminals = {
                terminal_key: {
                    'name': f'Test {terminal_key}',
                    'executable': terminal_key,
                    'path': f'/usr/bin/{terminal_key}'
                }
                for terminal_key in available_terminals_input
            }
        else:
            available_terminals = {}

        manager.available_terminals = available_terminals

        # Create valid test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_directory = os.path.join(temp_dir, 'test-project')
            os.makedirs(test_directory, exist_ok=True)

            if not available_terminals:
                # Test Case: No terminals available
                with mock.patch('utils.terminal_manager.logger') as mock_logger:
                    success, error_msg = manager.open_terminal(test_directory)

                    # Property 5.2: Should fail with helpful error message when no terminals available
                    assert success is False, "Should fail when no terminals are available"
                    assert len(error_msg) > 0, "Should provide error message when no terminals available"

                    # Property 5.3: Error message should be specific and helpful
                    assert "No terminal applications are available" in error_msg, \
                        "Error message should mention no terminals available"
                    assert "install a terminal application" in error_msg, \
                        "Error message should suggest installing terminals"
                    assert any(term in error_msg for term in ["gnome-terminal", "konsole", "xterm"]), \
                        "Error message should suggest specific terminal applications"

                    # Property 5.4: Should log the no-terminals situation
                    mock_logger.error.assert_called()
                    error_calls = [call.args[0] for call in mock_logger.error.call_args_list]
                    assert any("No terminals available" in call for call in error_calls), \
                        "Should log no terminals available situation"

            else:
                # Test Case: Terminals available but all fail
                # This tests the fallback to system default when known terminals fail
                with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("All known terminals fail")), \
                     mock.patch('utils.terminal_manager.logger') as mock_logger:

                    # Set preferred terminal
                    manager.preferred_terminal = next(iter(available_terminals))

                    success, error_msg = manager.open_terminal(test_directory)

                    # Property: Should fail with comprehensive error when all known terminals fail
                    assert success is False, "Should fail when all available terminals fail"

                    # Property 5.3: Error message should mention the available terminals that failed
                    assert "Failed to open terminal" in error_msg, "Should mention terminal failure"
                    assert manager.preferred_terminal in error_msg, "Should mention preferred terminal"

                    # Property 5.4: Should log all failure attempts
                    mock_logger.error.assert_called()

    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd'), min_codepoint=32, max_codepoint=126)))
    @settings(max_examples=50)
    def test_system_default_fallback_property(self, directory_name):
        """
        **Validates: Requirements 5.1, 5.4**

        Property 5: Error Handling and Fallback (System Default Terminal)
        When all known terminals fail, the system should attempt to use the system
        default terminal as a last resort and log the attempt appropriately.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Set up one available terminal that will fail
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }
        manager.preferred_terminal = 'gnome-terminal'

        # Create valid test directory with generated name
        clean_dir_name = ''.join(c for c in directory_name if c.isalnum() or c in '-_')
        if not clean_dir_name:
            clean_dir_name = 'test-project'

        with tempfile.TemporaryDirectory() as temp_dir:
            test_directory = os.path.join(temp_dir, clean_dir_name)
            os.makedirs(test_directory, exist_ok=True)

            # Test Case 1: Known terminals fail, system default succeeds
            call_count = 0
            def mock_popen_system_default_succeeds(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:  # Known terminal fails
                    raise FileNotFoundError("Known terminal failed")
                else:  # System default succeeds (since no fallback terminals available)
                    return mock.Mock(pid=12345)

            with mock.patch('subprocess.Popen', side_effect=mock_popen_system_default_succeeds), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property 5.1: Should succeed with system default terminal
                assert success is True, "Should succeed when system default terminal works"
                assert error_msg == "", "No error message when system default succeeds"

                # Property 5.4: Should log the fallback to system default
                info_calls = [call.args[0] for call in mock_logger.info.call_args_list]
                assert any("system default terminal" in call.lower() or "attempting system default" in call.lower() for call in info_calls), \
                    "Should log system default terminal attempt"

                # Should have tried known terminal + system default
                assert call_count >= 2, "Should attempt known terminal and system default"

            # Test Case 2: All terminals including system default fail
            with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("All terminals fail")), \
                 mock.patch('utils.terminal_manager.logger') as mock_logger:

                success, error_msg = manager.open_terminal(test_directory)

                # Property: Should fail with comprehensive error when everything fails
                assert success is False, "Should fail when all terminals including system default fail"
                assert len(error_msg) > 0, "Should provide error message when all attempts fail"

                # Property 5.3: Error message should be comprehensive
                assert "Failed to open terminal" in error_msg, "Should mention terminal failure"

                # Property 5.4: Should log comprehensive failure
                mock_logger.error.assert_called()

            # Test Case 3: System default with $TERMINAL environment variable
            custom_terminal = 'custom-terminal-app'
            with mock.patch.dict(os.environ, {'TERMINAL': custom_terminal}):
                call_count = 0
                def mock_popen_custom_terminal(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:  # Known terminal fails
                        raise FileNotFoundError("Known terminal failed")
                    elif call_count == 2:  # Custom terminal from $TERMINAL succeeds
                        # Verify the command uses the custom terminal
                        command = args[0]
                        assert command[0] == custom_terminal, f"Should use $TERMINAL value: {custom_terminal}"
                        return mock.Mock(pid=12345)
                    else:
                        raise RuntimeError("Unexpected call")

                with mock.patch('subprocess.Popen', side_effect=mock_popen_custom_terminal), \
                     mock.patch('utils.terminal_manager.logger') as mock_logger:

                    success, error_msg = manager.open_terminal(test_directory)

                    # Property 5.1: Should succeed with $TERMINAL environment variable
                    assert success is True, "Should succeed when $TERMINAL environment variable works"
                    assert error_msg == "", "No error message when $TERMINAL succeeds"

                    # Property 5.4: Should log the custom terminal attempt
                    info_calls = [call.args[0] for call in mock_logger.info.call_args_list]
                    # Should log either system default attempt or successful launch
                    assert len(info_calls) > 0, "Should log terminal launch attempts"

                    assert call_count == 2, "Should try known terminal then $TERMINAL"


if __name__ == '__main__':
    pytest.main([__file__])