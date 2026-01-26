#!/usr/bin/env python3
"""
Tests for comprehensive error handling in TerminalManager

This test module specifically validates the error handling and fallback
mechanisms implemented in task 6.1.
"""

import pytest
import unittest.mock as mock
import subprocess
import os
import tempfile
from utils.terminal_manager import TerminalManager


class MockConfigManager:
    """Mock ConfigManager for testing"""

    def __init__(self):
        self.preferences = {}

    def load_preferences(self):
        return self.preferences.copy()

    def save_preferences(self, preferences):
        self.preferences = preferences.copy()


class TestTerminalErrorHandling:
    """Test cases for comprehensive error handling in TerminalManager"""

    def test_directory_validation_comprehensive(self):
        """Test comprehensive directory validation with specific error messages"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }
        manager.preferred_terminal = 'gnome-terminal'

        # Test None path
        success, error_msg = manager.open_terminal(None)
        assert success is False
        assert "No directory path provided" in error_msg

        # Test empty path
        success, error_msg = manager.open_terminal("")
        assert success is False
        assert "No directory path provided" in error_msg

        # Test non-existent directory
        with mock.patch('os.path.exists', return_value=False):
            success, error_msg = manager.open_terminal('/nonexistent/path')
            assert success is False
            assert "Directory does not exist" in error_msg
            assert "/nonexistent/path" in error_msg

        # Test file instead of directory
        with mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.isdir', return_value=False):
            success, error_msg = manager.open_terminal('/path/to/file.txt')
            assert success is False
            assert "Path is not a directory" in error_msg
            assert "/path/to/file.txt" in error_msg

        # Test inaccessible directory
        with mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.access', return_value=False):
            success, error_msg = manager.open_terminal('/restricted/path')
            assert success is False
            assert "Directory is not accessible" in error_msg
            assert "/restricted/path" in error_msg

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_terminal_launch_specific_errors(self, mock_access, mock_isdir, mock_exists):
        """Test specific error handling for different terminal launch failures"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }
        manager.preferred_terminal = 'gnome-terminal'

        # Test FileNotFoundError - all attempts fail
        with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("No such file")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "Failed to open terminal" in error_msg

        # Test PermissionError - all attempts fail
        with mock.patch('subprocess.Popen', side_effect=PermissionError("Permission denied")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "Failed to open terminal" in error_msg

        # Test SubprocessError - all attempts fail
        with mock.patch('subprocess.Popen', side_effect=subprocess.SubprocessError("Process failed")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "Failed to open terminal" in error_msg

        # Test OSError - all attempts fail
        with mock.patch('subprocess.Popen', side_effect=OSError("System error")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "Failed to open terminal" in error_msg

        # Test unexpected exception - all attempts fail
        with mock.patch('subprocess.Popen', side_effect=RuntimeError("Unexpected error")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "Failed to open terminal" in error_msg

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_fallback_terminal_priority(self, mock_access, mock_isdir, mock_exists):
        """Test that fallback terminals are tried in priority order"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'warp': {'name': 'Warp'},
            'gnome-terminal': {'name': 'GNOME Terminal'},
            'konsole': {'name': 'Konsole'},
            'xterm': {'name': 'XTerm'},
            'alacritty': {'name': 'Alacritty'}
        }
        manager.preferred_terminal = 'warp'

        # Mock subprocess to fail for first few attempts, succeed on gnome-terminal
        call_count = 0
        def mock_popen_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # warp fails
                raise FileNotFoundError("warp-terminal not found")
            elif call_count == 2:  # gnome-terminal succeeds
                return mock.Mock(pid=12345)
            else:
                raise RuntimeError("Unexpected call")

        with mock.patch('subprocess.Popen', side_effect=mock_popen_side_effect):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is True
            assert error_msg == ""
            assert call_count == 2

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_system_default_terminal_fallback(self, mock_access, mock_isdir, mock_exists):
        """Test fallback to system default terminal when all known terminals fail"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'}
        }
        manager.preferred_terminal = 'gnome-terminal'

        call_count = 0
        def mock_popen_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # gnome-terminal fails
                raise FileNotFoundError("gnome-terminal not found")
            elif call_count == 2:  # system default succeeds
                return mock.Mock(pid=12345)
            else:
                raise RuntimeError("Unexpected call")

        with mock.patch('subprocess.Popen', side_effect=mock_popen_side_effect):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is True
            assert error_msg == ""
            assert call_count == 2

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_comprehensive_error_message_generation(self, mock_access, mock_isdir, mock_exists):
        """Test generation of comprehensive error messages when all attempts fail"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'},
            'konsole': {'name': 'Konsole'},
            'xterm': {'name': 'XTerm'}
        }
        manager.preferred_terminal = 'gnome-terminal'

        # Mock all terminals to fail
        with mock.patch('subprocess.Popen', side_effect=FileNotFoundError("All terminals fail")):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False

            # Check that error message contains comprehensive information
            assert "Failed to open terminal" in error_msg
            assert "Primary terminal 'gnome-terminal' failed" in error_msg
            assert "Tried 2 fallback terminal(s)" in error_msg
            assert "konsole" in error_msg
            assert "xterm" in error_msg
            assert "Please check that your terminal applications are properly installed" in error_msg
            assert "You can configure your preferred terminal in the application preferences" in error_msg

    def test_no_terminals_available_error_message(self):
        """Test error message when no terminals are available"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {}

        with mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.access', return_value=True):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is False
            assert "No terminal applications are available on this system" in error_msg
            assert "Please install a terminal application such as gnome-terminal, konsole, or xterm" in error_msg

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_system_default_terminal_environment_variable(self, mock_access, mock_isdir, mock_exists):
        """Test that system default terminal respects $TERMINAL environment variable"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'}
        }
        manager.preferred_terminal = 'gnome-terminal'

        call_count = 0
        def mock_popen_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # gnome-terminal fails
                raise FileNotFoundError("gnome-terminal not found")
            elif call_count == 2:  # $TERMINAL succeeds
                # Verify that the command uses the TERMINAL env var
                command = args[0]
                assert command[0] == 'custom-terminal'
                return mock.Mock(pid=12345)
            else:
                raise RuntimeError("Unexpected call")

        with mock.patch.dict(os.environ, {'TERMINAL': 'custom-terminal'}), \
             mock.patch('subprocess.Popen', side_effect=mock_popen_side_effect):
            success, error_msg = manager.open_terminal('/home/user/project')
            assert success is True
            assert error_msg == ""
            assert call_count == 2

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.access', return_value=True)
    def test_fallback_terminals_exclude_preferred(self, mock_access, mock_isdir, mock_exists):
        """Test that fallback terminals exclude the preferred terminal"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'},
            'konsole': {'name': 'Konsole'},
            'xterm': {'name': 'XTerm'}
        }
        manager.preferred_terminal = 'konsole'

        # Get fallback terminals
        fallback_terminals = manager._get_fallback_terminals(exclude='konsole')

        # Verify konsole is not in fallback list
        assert 'konsole' not in fallback_terminals
        assert 'gnome-terminal' in fallback_terminals
        assert 'xterm' in fallback_terminals

    def test_logging_for_terminal_operations(self):
        """Test that terminal operations are properly logged"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'}
        }
        manager.preferred_terminal = 'gnome-terminal'

        with mock.patch('os.path.exists', return_value=False), \
             mock.patch('utils.terminal_manager.logger') as mock_logger:

            success, error_msg = manager.open_terminal('/nonexistent/path')

            # Verify error logging
            mock_logger.error.assert_called_with(
                "Directory validation failed: Directory does not exist: /nonexistent/path"
            )

        # Test successful launch logging
        with mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.access', return_value=True), \
             mock.patch('subprocess.Popen', return_value=mock.Mock(pid=12345)), \
             mock.patch('utils.terminal_manager.logger') as mock_logger:

            success, error_msg = manager.open_terminal('/home/user/project')

            # Verify info logging for successful launch
            mock_logger.info.assert_any_call(
                "Attempting to launch terminal 'gnome-terminal' in directory: /home/user/project"
            )
            mock_logger.info.assert_any_call(
                "Terminal 'gnome-terminal' launched successfully with PID: 12345"
            )

        # Test fallback logging
        with mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.access', return_value=True), \
             mock.patch('subprocess.Popen', side_effect=[
                 FileNotFoundError("Primary fails"),
                 mock.Mock(pid=12345)
             ]), \
             mock.patch('utils.terminal_manager.logger') as mock_logger:

            manager.available_terminals['xterm'] = {'name': 'XTerm'}
            success, error_msg = manager.open_terminal('/home/user/project')

            # Verify warning logging for primary failure and info for fallback success
            mock_logger.warning.assert_any_call(
                "Primary terminal 'gnome-terminal' failed: Terminal executable not found: gnome-terminal"
            )
            mock_logger.info.assert_any_call(
                "Attempting fallback terminal 'xterm'"
            )