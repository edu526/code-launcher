"""
Tests for terminal management functionality
"""

import pytest
import unittest.mock as mock
import subprocess
import os
import tempfile
from hypothesis import given, strategies as st, settings
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


class TestTerminalManager:
    """Test cases for TerminalManager class"""

    def test_init(self):
        """Test TerminalManager initialization"""
        manager = TerminalManager()
        assert manager.config_manager is None
        assert isinstance(manager.detector, TerminalDetector)
        assert manager.available_terminals == {}
        assert manager.preferred_terminal is None
        assert manager._initialized is False

    def test_init_with_config_manager(self):
        """Test TerminalManager initialization with config manager"""
        config_manager = MockConfigManager()
        manager = TerminalManager(config_manager)
        assert manager.config_manager is config_manager

    @mock.patch.object(TerminalDetector, 'detect_terminals')
    def test_initialize_no_config(self, mock_detect):
        """Test initialization without config manager"""
        mock_detect.return_value = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        manager = TerminalManager()
        manager.initialize()

        assert manager._initialized is True
        assert len(manager.available_terminals) == 1
        assert manager.preferred_terminal == 'gnome-terminal'
        mock_detect.assert_called_once()

    @mock.patch.object(TerminalDetector, 'detect_terminals')
    def test_initialize_with_config(self, mock_detect):
        """Test initialization with config manager and saved preferences"""
        mock_detect.return_value = {
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

        config_manager = MockConfigManager()
        config_manager.preferences = {
            'terminal': {
                'preferred': 'konsole'
            }
        }

        manager = TerminalManager(config_manager)

        with mock.patch.object(manager.detector, 'is_terminal_available', return_value=True):
            manager.initialize()

        assert manager._initialized is True
        assert manager.preferred_terminal == 'konsole'

    @mock.patch.object(TerminalDetector, 'detect_terminals')
    def test_initialize_preferred_not_available(self, mock_detect):
        """Test initialization when preferred terminal from config is not available"""
        mock_detect.return_value = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        config_manager = MockConfigManager()
        config_manager.preferences = {
            'terminal': {
                'preferred': 'konsole'  # Not available
            }
        }

        manager = TerminalManager(config_manager)
        manager.initialize()

        # Should fall back to available terminal
        assert manager.preferred_terminal == 'gnome-terminal'

    def test_get_available_terminals_auto_initialize(self):
        """Test that get_available_terminals auto-initializes"""
        manager = TerminalManager()

        with mock.patch.object(manager, 'initialize') as mock_init:
            manager.get_available_terminals()
            mock_init.assert_called_once()

    def test_get_available_terminals_returns_copy(self):
        """Test that get_available_terminals returns a copy"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {'test': 'data'}

        result = manager.get_available_terminals()
        assert result == manager.available_terminals
        assert result is not manager.available_terminals

    def test_set_preferred_terminal_success(self):
        """Test successful setting of preferred terminal"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'}
        }

        result = manager.set_preferred_terminal('gnome-terminal')

        assert result is True
        assert manager.preferred_terminal == 'gnome-terminal'

    def test_set_preferred_terminal_not_available(self):
        """Test setting preferred terminal that's not available"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {}

        result = manager.set_preferred_terminal('nonexistent')

        assert result is False
        assert manager.preferred_terminal != 'nonexistent'

    def test_set_preferred_terminal_with_config(self):
        """Test setting preferred terminal with config manager"""
        config_manager = MockConfigManager()
        manager = TerminalManager(config_manager)
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        result = manager.set_preferred_terminal('gnome-terminal')

        assert result is True
        assert config_manager.preferences['terminal']['preferred'] == 'gnome-terminal'

    def test_is_terminal_available(self):
        """Test terminal availability checking"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'}
        }

        assert manager.is_terminal_available('gnome-terminal') is True
        assert manager.is_terminal_available('nonexistent') is False

    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    @mock.patch('os.access')
    @mock.patch('subprocess.Popen')
    def test_open_terminal_success(self, mock_popen, mock_access, mock_isdir, mock_exists):
        """Test successful terminal opening"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_access.return_value = True
        mock_process = mock.Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }
        manager.preferred_terminal = 'gnome-terminal'

        success, error_msg = manager.open_terminal('/home/user/project')

        assert success is True
        assert error_msg == ""
        mock_popen.assert_called_once()

        # Check command arguments
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == 'gnome-terminal'
        assert '--working-directory=/home/user/project' in call_args

    @mock.patch('os.path.exists')
    def test_open_terminal_directory_not_exists(self, mock_exists):
        """Test opening terminal with non-existent directory"""
        mock_exists.return_value = False

        manager = TerminalManager()
        manager._initialized = True

        success, error_msg = manager.open_terminal('/nonexistent/path')

        assert success is False
        assert "does not exist" in error_msg

    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    def test_open_terminal_not_directory(self, mock_isdir, mock_exists):
        """Test opening terminal with path that's not a directory"""
        mock_exists.return_value = True
        mock_isdir.return_value = False

        manager = TerminalManager()
        manager._initialized = True

        success, error_msg = manager.open_terminal('/path/to/file.txt')

        assert success is False
        assert "not a directory" in error_msg

    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    @mock.patch('os.access')
    def test_open_terminal_no_terminals_available(self, mock_access, mock_isdir, mock_exists):
        """Test opening terminal when no terminals are available"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_access.return_value = True

        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {}

        success, error_msg = manager.open_terminal('/home/user')

        assert success is False
        assert "No terminal applications are available" in error_msg

    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    @mock.patch('os.access')
    @mock.patch('subprocess.Popen')
    def test_open_terminal_with_fallback(self, mock_popen, mock_access, mock_isdir, mock_exists):
        """Test terminal opening with fallback when preferred fails"""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_access.return_value = True

        # First call fails, second succeeds
        mock_popen.side_effect = [subprocess.SubprocessError("Failed"), mock.Mock(pid=12345)]

        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'},
            'xterm': {'name': 'XTerm'}
        }
        manager.preferred_terminal = 'gnome-terminal'

        with mock.patch.object(manager, '_get_fallback_terminal', return_value='xterm'):
            success, error_msg = manager.open_terminal('/home/user/project')

        assert success is True
        assert error_msg == ""
        assert mock_popen.call_count == 2

    def test_get_terminal_display_name(self):
        """Test getting terminal display name"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        result = manager.get_terminal_display_name('gnome-terminal')
        assert result == 'GNOME Terminal'

        result = manager.get_terminal_display_name('nonexistent')
        assert result is None

    def test_has_available_terminals(self):
        """Test checking if any terminals are available"""
        manager = TerminalManager()
        manager._initialized = True

        manager.available_terminals = {}
        assert manager.has_available_terminals() is False

        manager.available_terminals = {'gnome-terminal': {'name': 'GNOME Terminal'}}
        assert manager.has_available_terminals() is True

    def test_generate_terminal_command(self):
        """Test terminal command generation"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {'name': 'GNOME Terminal'},
            'konsole': {'name': 'Konsole'},
            'xterm': {'name': 'XTerm'}
        }

        # Test gnome-terminal command
        result = manager._generate_terminal_command('gnome-terminal', '/home/user/project')
        expected = ['gnome-terminal', '--working-directory=/home/user/project']
        assert result == expected

        # Test konsole command
        result = manager._generate_terminal_command('konsole', '/home/user/project')
        expected = ['konsole', '--workdir', '/home/user/project']
        assert result == expected

        # Test xterm command (more complex with shell)
        result = manager._generate_terminal_command('xterm', '/home/user/project')
        expected = ['xterm', '-e', 'cd /home/user/project && bash']
        assert result == expected

    def test_generate_terminal_command_unsupported(self):
        """Test command generation for unsupported terminal"""
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {}

        result = manager._generate_terminal_command('unsupported', '/home/user')
        assert result is None

    def test_load_preferred_terminal_no_config(self):
        """Test loading preferred terminal without config manager"""
        manager = TerminalManager()

        result = manager._load_preferred_terminal()
        assert result is None

    def test_save_preferred_terminal_no_config(self):
        """Test saving preferred terminal without config manager"""
        manager = TerminalManager()

        # Should not raise exception
        manager._save_preferred_terminal('gnome-terminal')

    @mock.patch('utils.terminal_manager.datetime')
    def test_save_preferred_terminal_with_config(self, mock_datetime):
        """Test saving preferred terminal with config manager"""
        mock_now = mock.Mock()
        mock_now.isoformat.return_value = '2024-01-01T12:00:00'
        mock_datetime.now.return_value = mock_now

        config_manager = MockConfigManager()
        manager = TerminalManager(config_manager)
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        manager._save_preferred_terminal('gnome-terminal')

        expected_prefs = {
            'terminal': {
                'preferred': 'gnome-terminal',
                'available': {
                    'gnome-terminal': '/usr/bin/gnome-terminal'
                },
                'last_detected': '2024-01-01T12:00:00'
            }
        }
        assert config_manager.preferences == expected_prefs


class TestTerminalManagerProperties:
    """Property-based tests for TerminalManager class"""

    @given(st.sets(st.sampled_from(list(TerminalManager.TERMINAL_COMMANDS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_terminal_launch_command_generation(self, available_terminals):
        """
        **Validates: Requirements 4.1, 4.2**

        Property 4: Terminal Launch Command Generation
        For any valid project directory path and detected terminal, the system should
        generate the correct command-line arguments for that terminal type to open
        in the specified directory.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Set up available terminals
        manager.available_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_terminals
        }

        # Test command generation for each available terminal
        test_directory = '/home/user/test-project'

        for terminal_key in available_terminals:
            command = manager._generate_terminal_command(terminal_key, test_directory)

            # Property 1: Command should be generated for supported terminals
            if terminal_key in manager.TERMINAL_COMMANDS:
                assert command is not None, f"Command should be generated for {terminal_key}"
                assert isinstance(command, list), f"Command should be a list for {terminal_key}"
                assert len(command) > 0, f"Command should not be empty for {terminal_key}"

                # Property 2: Directory path should be included in command
                command_str = ' '.join(command)
                assert test_directory in command_str, \
                    f"Directory path should be in command for {terminal_key}: {command_str}"

                # Property 3: Command should match expected template structure
                expected_template = manager.TERMINAL_COMMANDS[terminal_key]
                assert len(command) == len(expected_template), \
                    f"Command length should match template for {terminal_key}"

                # Property 4: First argument should be the terminal executable name
                assert command[0] == expected_template[0], \
                    f"First argument should be terminal name for {terminal_key}"

    @given(st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_preference_persistence_round_trip(self, available_terminals):
        """
        **Validates: Requirements 2.3, 2.4, 6.1**

        Property 2: Preference Persistence Round Trip
        For any valid terminal selection, storing the preference and then loading it
        should result in the same terminal being selected, with immediate persistence
        to preferences.json.
        """
        if not available_terminals:
            # Skip test if no terminals available
            return

        config_manager = MockConfigManager()
        manager = TerminalManager(config_manager)
        manager._initialized = True

        # Set up available terminals
        manager.available_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_terminals
        }

        # Also set up detector's available terminals for the _load_preferred_terminal method
        manager.detector.available_terminals = manager.available_terminals.copy()

        # Test round trip for each available terminal
        for terminal_key in available_terminals:
            # Clear previous state
            config_manager.preferences = {}

            # Set preferred terminal
            success = manager.set_preferred_terminal(terminal_key)
            assert success is True, f"Should be able to set available terminal {terminal_key}"

            # Property 1: Preference should be immediately persisted
            assert 'terminal' in config_manager.preferences, \
                "Terminal section should exist in preferences"
            assert config_manager.preferences['terminal']['preferred'] == terminal_key, \
                f"Preferred terminal should be persisted as {terminal_key}"

            # Property 2: Loading preference should return the same terminal
            loaded_terminal = manager._load_preferred_terminal()
            assert loaded_terminal == terminal_key, \
                f"Loaded terminal should match saved terminal {terminal_key}"

            # Property 3: Manager state should reflect the preference
            assert manager.get_preferred_terminal() == terminal_key, \
                f"Manager should return preferred terminal {terminal_key}"

    @given(st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=1, max_size=8))
    @settings(max_examples=100)
    def test_terminal_availability_consistency(self, available_terminals):
        """
        **Validates: Requirements 1.4, 4.1**

        Property: Terminal Availability Consistency
        For any set of available terminals, the manager should consistently report
        availability and provide access to terminal metadata.
        """
        manager = TerminalManager()
        manager._initialized = True

        # Set up available terminals
        manager.available_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_terminals
        }

        # Property 1: All available terminals should be reported as available
        for terminal_key in available_terminals:
            assert manager.is_terminal_available(terminal_key) is True, \
                f"Available terminal {terminal_key} should be reported as available"

        # Property 2: Non-available terminals should be reported as not available
        all_known_terminals = set(TerminalDetector.KNOWN_TERMINALS.keys())
        unavailable_terminals = all_known_terminals - available_terminals

        for terminal_key in unavailable_terminals:
            assert manager.is_terminal_available(terminal_key) is False, \
                f"Unavailable terminal {terminal_key} should be reported as not available"

        # Property 3: get_available_terminals should return exactly the available terminals
        returned_terminals = manager.get_available_terminals()
        assert set(returned_terminals.keys()) == available_terminals, \
            "get_available_terminals should return exactly the available terminals"

        # Property 4: Display names should be available for all available terminals
        for terminal_key in available_terminals:
            display_name = manager.get_terminal_display_name(terminal_key)
            assert display_name is not None, \
                f"Display name should be available for {terminal_key}"
            assert isinstance(display_name, str), \
                f"Display name should be string for {terminal_key}"
            assert len(display_name) > 0, \
                f"Display name should not be empty for {terminal_key}"

    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126)))
    @settings(max_examples=50)
    def test_directory_validation_property(self, path_component):
        """
        **Validates: Requirements 4.3, 5.3**

        Property: Directory Validation
        For any directory path, the terminal manager should properly validate
        the path before attempting to launch a terminal.
        """
        manager = TerminalManager()
        manager._initialized = True
        manager.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }
        manager.preferred_terminal = 'gnome-terminal'

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_path = os.path.join(temp_dir, 'test-project')
            os.makedirs(valid_path, exist_ok=True)

            # Property 1: Valid existing directory should be accepted
            with mock.patch('subprocess.Popen') as mock_popen:
                mock_popen.return_value = mock.Mock(pid=12345)
                success, error_msg = manager.open_terminal(valid_path)
                assert success is True, "Valid directory should be accepted"
                assert error_msg == "", "No error message should be returned for valid directory"
                mock_popen.assert_called_once()

            # Property 2: Non-existent directory should be rejected
            nonexistent_path = os.path.join(temp_dir, 'nonexistent', path_component)
            success, error_msg = manager.open_terminal(nonexistent_path)
            assert success is False, "Non-existent directory should be rejected"
            assert "does not exist" in error_msg, "Error message should mention directory doesn't exist"

            # Property 3: File path (not directory) should be rejected
            file_path = os.path.join(temp_dir, 'test-file.txt')
            with open(file_path, 'w') as f:
                f.write('test')

            success, error_msg = manager.open_terminal(file_path)
            assert success is False, "File path should be rejected"
            assert "not a directory" in error_msg, "Error message should mention path is not a directory"

            # Property 4: Empty or None path should be rejected
            success, error_msg = manager.open_terminal('')
            assert success is False, "Empty path should be rejected"
            assert "No directory path provided" in error_msg, "Error message should mention no path provided"

            success, error_msg = manager.open_terminal(None)
            assert success is False, "None path should be rejected"
            assert "No directory path provided" in error_msg, "Error message should mention no path provided"

    @given(st.lists(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_initialization_idempotency(self, available_terminals):
        """
        **Validates: Requirements 1.1, 6.2**

        Property: Initialization Idempotency
        Multiple calls to initialize() should produce consistent results and
        not cause side effects or state corruption.
        """
        available_set = set(available_terminals)  # Remove duplicates

        config_manager = MockConfigManager()
        manager = TerminalManager(config_manager)

        # Mock terminal detection to return consistent results
        mock_terminals = {
            terminal_key: {
                'name': f'Test {terminal_key}',
                'executable': terminal_key,
                'path': f'/usr/bin/{terminal_key}'
            }
            for terminal_key in available_set
        }

        with mock.patch.object(manager.detector, 'detect_terminals', return_value=mock_terminals):
            # Initialize multiple times
            manager.initialize()
            state_after_first = {
                'available_terminals': manager.available_terminals.copy(),
                'preferred_terminal': manager.preferred_terminal,
                'initialized': manager._initialized
            }

            manager.initialize()
            state_after_second = {
                'available_terminals': manager.available_terminals.copy(),
                'preferred_terminal': manager.preferred_terminal,
                'initialized': manager._initialized
            }

            manager.initialize()
            state_after_third = {
                'available_terminals': manager.available_terminals.copy(),
                'preferred_terminal': manager.preferred_terminal,
                'initialized': manager._initialized
            }

            # Property: All states should be identical
            assert state_after_first == state_after_second == state_after_third, \
                "Multiple initialization calls should produce identical state"

            # Property: Should be marked as initialized
            assert manager._initialized is True, \
                "Manager should be marked as initialized"

            # Property: Available terminals should match detection results
            assert manager.available_terminals == mock_terminals, \
                "Available terminals should match detection results"