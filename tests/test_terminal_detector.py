"""
Tests for terminal detection functionality
"""

import pytest
import unittest.mock as mock
import os
from hypothesis import given, strategies as st, settings
from utils.terminal_detector import TerminalDetector


class TestTerminalDetector:
    """Test cases for TerminalDetector class"""

    def test_init(self):
        """Test TerminalDetector initialization"""
        detector = TerminalDetector()
        assert detector.available_terminals == {}
        assert isinstance(detector.KNOWN_TERMINALS, dict)
        assert len(detector.KNOWN_TERMINALS) > 0

    def test_known_terminals_structure(self):
        """Test that KNOWN_TERMINALS has the expected structure"""
        detector = TerminalDetector()

        for terminal_key, terminal_info in detector.KNOWN_TERMINALS.items():
            assert isinstance(terminal_key, str)
            assert isinstance(terminal_info, dict)
            assert 'name' in terminal_info
            assert 'executable' in terminal_info
            assert isinstance(terminal_info['name'], str)
            assert isinstance(terminal_info['executable'], str)

    @mock.patch('shutil.which')
    @mock.patch.object(TerminalDetector, 'verify_terminal')
    def test_detect_terminals_success(self, mock_verify, mock_which):
        """Test successful terminal detection"""
        detector = TerminalDetector()

        # Mock shutil.which to return paths for some terminals
        def mock_which_side_effect(executable):
            if executable in ['gnome-terminal', 'xterm']:
                return f'/usr/bin/{executable}'
            return None

        mock_which.side_effect = mock_which_side_effect
        mock_verify.return_value = True

        result = detector.detect_terminals()

        # Should detect gnome-terminal and xterm
        assert len(result) == 2
        assert 'gnome-terminal' in result
        assert 'xterm' in result

        # Check structure of detected terminals
        for terminal_key, terminal_info in result.items():
            assert 'name' in terminal_info
            assert 'executable' in terminal_info
            assert 'path' in terminal_info
            assert terminal_info['path'].startswith('/usr/bin/')

    @mock.patch('shutil.which')
    def test_detect_terminals_none_found(self, mock_which):
        """Test terminal detection when no terminals are found"""
        detector = TerminalDetector()
        mock_which.return_value = None

        result = detector.detect_terminals()

        assert result == {}
        assert detector.available_terminals == {}

    @mock.patch('os.path.exists')
    @mock.patch('os.access')
    def test_verify_terminal_success(self, mock_access, mock_exists):
        """Test successful terminal verification"""
        detector = TerminalDetector()
        mock_exists.return_value = True
        mock_access.return_value = True

        result = detector.verify_terminal('/usr/bin/gnome-terminal')

        assert result is True
        mock_exists.assert_called_once_with('/usr/bin/gnome-terminal')
        mock_access.assert_called_once_with('/usr/bin/gnome-terminal', os.X_OK)

    @mock.patch('os.path.exists')
    def test_verify_terminal_not_exists(self, mock_exists):
        """Test terminal verification when file doesn't exist"""
        detector = TerminalDetector()
        mock_exists.return_value = False

        result = detector.verify_terminal('/usr/bin/nonexistent')

        assert result is False

    @mock.patch('os.path.exists')
    @mock.patch('os.access')
    def test_verify_terminal_not_executable(self, mock_access, mock_exists):
        """Test terminal verification when file is not executable"""
        detector = TerminalDetector()
        mock_exists.return_value = True
        mock_access.return_value = False

        result = detector.verify_terminal('/usr/bin/not-executable')

        assert result is False

    def test_verify_terminal_empty_path(self):
        """Test terminal verification with empty path"""
        detector = TerminalDetector()

        result = detector.verify_terminal('')
        assert result is False

        result = detector.verify_terminal(None)
        assert result is False

    def test_get_available_terminals(self):
        """Test getting available terminals"""
        detector = TerminalDetector()
        detector.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        result = detector.get_available_terminals()

        assert result == detector.available_terminals
        # Ensure it returns a copy, not the original
        assert result is not detector.available_terminals

    def test_get_terminal_path(self):
        """Test getting terminal path"""
        detector = TerminalDetector()
        detector.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        result = detector.get_terminal_path('gnome-terminal')
        assert result == '/usr/bin/gnome-terminal'

        result = detector.get_terminal_path('nonexistent')
        assert result is None

    def test_get_terminal_name(self):
        """Test getting terminal display name"""
        detector = TerminalDetector()
        detector.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        result = detector.get_terminal_name('gnome-terminal')
        assert result == 'GNOME Terminal'

        result = detector.get_terminal_name('nonexistent')
        assert result is None

    def test_is_terminal_available(self):
        """Test checking terminal availability"""
        detector = TerminalDetector()
        detector.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            }
        }

        assert detector.is_terminal_available('gnome-terminal') is True
        assert detector.is_terminal_available('nonexistent') is False

    def test_get_fallback_terminal(self):
        """Test getting fallback terminal"""
        detector = TerminalDetector()

        # Test with no terminals available
        result = detector.get_fallback_terminal()
        assert result is None

        # Test with terminals available
        detector.available_terminals = {
            'gnome-terminal': {
                'name': 'GNOME Terminal',
                'executable': 'gnome-terminal',
                'path': '/usr/bin/gnome-terminal'
            },
            'xterm': {
                'name': 'XTerm',
                'executable': 'xterm',
                'path': '/usr/bin/xterm'
            }
        }

        result = detector.get_fallback_terminal()
        assert result in ['gnome-terminal', 'xterm']  # Should return one of the available terminals


class TestTerminalDetectorProperties:
    """Property-based tests for TerminalDetector class"""

    @given(st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_terminal_detection_completeness(self, available_terminals):
        """
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

        Property 1: Terminal Detection Completeness
        For any system with available terminal executables in PATH, the Terminal_Detector
        should find all known terminals that are executable and maintain accurate metadata
        (display names and paths) for each detected terminal.
        """
        detector = TerminalDetector()

        # Create mock paths for available terminals
        mock_paths = {}
        for terminal_key in available_terminals:
            executable = detector.KNOWN_TERMINALS[terminal_key]['executable']
            mock_paths[executable] = f'/usr/bin/{executable}'

        with mock.patch('shutil.which') as mock_which, \
             mock.patch.object(detector, 'verify_terminal') as mock_verify:

            # Configure mocks
            def which_side_effect(executable):
                return mock_paths.get(executable)

            mock_which.side_effect = which_side_effect
            mock_verify.return_value = True

            # Run detection
            result = detector.detect_terminals()

            # Property 1: Completeness - All available terminals should be detected
            assert len(result) == len(available_terminals), \
                f"Expected {len(available_terminals)} terminals, found {len(result)}"

            # Property 2: Correctness - Only available terminals should be detected
            detected_keys = set(result.keys())
            expected_keys = set(available_terminals)
            assert detected_keys == expected_keys, \
                f"Detected terminals {detected_keys} don't match expected {expected_keys}"

            # Property 3: Metadata completeness - Each detected terminal has complete metadata
            for terminal_key, terminal_info in result.items():
                assert 'name' in terminal_info, f"Missing 'name' for {terminal_key}"
                assert 'executable' in terminal_info, f"Missing 'executable' for {terminal_key}"
                assert 'path' in terminal_info, f"Missing 'path' for {terminal_key}"

                # Verify metadata accuracy
                expected_name = detector.KNOWN_TERMINALS[terminal_key]['name']
                expected_executable = detector.KNOWN_TERMINALS[terminal_key]['executable']
                expected_path = mock_paths[expected_executable]

                assert terminal_info['name'] == expected_name, \
                    f"Wrong name for {terminal_key}: got {terminal_info['name']}, expected {expected_name}"
                assert terminal_info['executable'] == expected_executable, \
                    f"Wrong executable for {terminal_key}: got {terminal_info['executable']}, expected {expected_executable}"
                assert terminal_info['path'] == expected_path, \
                    f"Wrong path for {terminal_key}: got {terminal_info['path']}, expected {expected_path}"

            # Property 4: Verification calls - verify_terminal should be called for each found executable
            expected_calls = [mock.call(mock_paths[detector.KNOWN_TERMINALS[key]['executable']])
                            for key in available_terminals]
            mock_verify.assert_has_calls(expected_calls, any_order=True)

            # Property 5: State consistency - available_terminals should match detection result
            assert detector.available_terminals == result, \
                "Internal state doesn't match detection result"

    @given(st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_terminal_detection_with_verification_failures(self, terminals_in_path):
        """
        **Validates: Requirements 1.3, 1.4**

        Property: Terminal Detection with Verification Failures
        When terminals are found in PATH but fail verification (not executable, permission issues),
        they should not be included in the final results.
        """
        detector = TerminalDetector()

        # Split terminals into those that pass/fail verification
        passing_terminals = set(list(terminals_in_path)[:len(terminals_in_path)//2])
        failing_terminals = terminals_in_path - passing_terminals

        # Create mock paths for all terminals in PATH
        mock_paths = {}
        for terminal_key in terminals_in_path:
            executable = detector.KNOWN_TERMINALS[terminal_key]['executable']
            mock_paths[executable] = f'/usr/bin/{executable}'

        with mock.patch('shutil.which') as mock_which, \
             mock.patch.object(detector, 'verify_terminal') as mock_verify:

            # Configure mocks
            def which_side_effect(executable):
                return mock_paths.get(executable)

            def verify_side_effect(path):
                # Only terminals in passing_terminals should pass verification
                for terminal_key in passing_terminals:
                    expected_path = f'/usr/bin/{detector.KNOWN_TERMINALS[terminal_key]["executable"]}'
                    if path == expected_path:
                        return True
                return False

            mock_which.side_effect = which_side_effect
            mock_verify.side_effect = verify_side_effect

            # Run detection
            result = detector.detect_terminals()

            # Property: Only verified terminals should be in results
            assert len(result) == len(passing_terminals), \
                f"Expected {len(passing_terminals)} verified terminals, found {len(result)}"

            detected_keys = set(result.keys())
            expected_keys = set(passing_terminals)
            assert detected_keys == expected_keys, \
                f"Detected terminals {detected_keys} don't match expected verified terminals {expected_keys}"

            # Property: All terminals in PATH should have been checked for verification
            if terminals_in_path:
                expected_verify_calls = [mock.call(mock_paths[detector.KNOWN_TERMINALS[key]['executable']])
                                       for key in terminals_in_path]
                mock_verify.assert_has_calls(expected_verify_calls, any_order=True)

    @given(st.lists(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=0, max_size=8))
    @settings(max_examples=100)
    def test_terminal_detection_idempotency(self, available_terminals):
        """
        **Validates: Requirements 1.1, 1.4**

        Property: Terminal Detection Idempotency
        Running detect_terminals() multiple times with the same system state
        should produce identical results.
        """
        detector = TerminalDetector()
        available_set = set(available_terminals)  # Remove duplicates

        # Create mock paths for available terminals
        mock_paths = {}
        for terminal_key in available_set:
            executable = detector.KNOWN_TERMINALS[terminal_key]['executable']
            mock_paths[executable] = f'/usr/bin/{executable}'

        with mock.patch('shutil.which') as mock_which, \
             mock.patch.object(detector, 'verify_terminal') as mock_verify:

            # Configure mocks
            def which_side_effect(executable):
                return mock_paths.get(executable)

            mock_which.side_effect = which_side_effect
            mock_verify.return_value = True

            # Run detection multiple times
            result1 = detector.detect_terminals()
            result2 = detector.detect_terminals()
            result3 = detector.detect_terminals()

            # Property: All results should be identical
            assert result1 == result2 == result3, \
                "Multiple detection runs produced different results"

            # Property: Internal state should be consistent
            assert detector.available_terminals == result1, \
                "Internal state inconsistent after first detection"
            assert detector.available_terminals == result2, \
                "Internal state inconsistent after second detection"
            assert detector.available_terminals == result3, \
                "Internal state inconsistent after third detection"

    @given(st.sets(st.sampled_from(list(TerminalDetector.KNOWN_TERMINALS.keys())), min_size=1, max_size=8))
    @settings(max_examples=100)
    def test_fallback_terminal_property(self, available_terminals):
        """
        **Validates: Requirements 1.5**

        Property: Fallback Terminal Selection
        When terminals are available, get_fallback_terminal() should return one of them.
        The returned terminal should be a valid key from available terminals.
        """
        detector = TerminalDetector()

        # Set up available terminals
        detector.available_terminals = {
            terminal_key: {
                'name': detector.KNOWN_TERMINALS[terminal_key]['name'],
                'executable': detector.KNOWN_TERMINALS[terminal_key]['executable'],
                'path': f'/usr/bin/{detector.KNOWN_TERMINALS[terminal_key]["executable"]}'
            }
            for terminal_key in available_terminals
        }

        # Get fallback terminal
        fallback = detector.get_fallback_terminal()

        # Property: Fallback should be one of the available terminals
        assert fallback in available_terminals, \
            f"Fallback terminal {fallback} not in available terminals {available_terminals}"

        # Property: Fallback should be consistent (same terminal each time)
        fallback2 = detector.get_fallback_terminal()
        assert fallback == fallback2, \
            "Fallback terminal selection should be consistent"

    def test_no_terminals_fallback_property(self):
        """
        **Validates: Requirements 1.5**

        Property: No Terminals Fallback
        When no terminals are available, get_fallback_terminal() should return None.
        """
        detector = TerminalDetector()

        # Ensure no terminals are available
        detector.available_terminals = {}

        # Get fallback terminal
        fallback = detector.get_fallback_terminal()

        # Property: Should return None when no terminals available
        assert fallback is None, \
            f"Expected None when no terminals available, got {fallback}"