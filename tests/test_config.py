#!/usr/bin/env python3
"""
Tests for ConfigManager terminal preference functionality
"""

import os
import json
import tempfile
import shutil
from unittest.mock import patch
import pytest
from hypothesis import given, strategies as st, settings

from src.core.config import ConfigManager


class TestConfigManagerTerminalPreferences:
    """Test terminal preference functionality in ConfigManager"""

    def setup_method(self):
        """Set up test environment with temporary config directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, ".config", "code-launcher")
        os.makedirs(self.config_dir, exist_ok=True)
        self.preferences_file = os.path.join(self.config_dir, "preferences.json")

        # Patch the config paths to use our temp directory
        self.config_patch = patch('src.core.config.CONFIG_DIR', self.config_dir)
        self.preferences_patch = patch('src.core.config.PREFERENCES_FILE', self.preferences_file)

        self.config_patch.start()
        self.preferences_patch.start()

        self.config_manager = ConfigManager()

    def teardown_method(self):
        """Clean up test environment"""
        self.config_patch.stop()
        self.preferences_patch.stop()
        shutil.rmtree(self.temp_dir)

    def test_load_preferences_with_defaults(self):
        """Test loading preferences creates default terminal configuration"""
        preferences = self.config_manager.load_preferences()

        assert "default_editor" in preferences
        assert "terminal" in preferences
        assert preferences["terminal"]["preferred"] is None
        assert preferences["terminal"]["available"] == {}
        assert preferences["terminal"]["last_detected"] is None

    def test_load_preferences_backward_compatibility(self):
        """Test loading old preferences.json without terminal config"""
        # Create old-style preferences file
        old_prefs = {"default_editor": "vscode"}
        with open(self.preferences_file, 'w') as f:
            json.dump(old_prefs, f)

        preferences = self.config_manager.load_preferences()

        # Should have old preference plus new terminal defaults
        assert preferences["default_editor"] == "vscode"
        assert "terminal" in preferences
        assert preferences["terminal"]["preferred"] is None
        assert preferences["terminal"]["available"] == {}
        assert preferences["terminal"]["last_detected"] is None

    def test_load_preferences_partial_terminal_config(self):
        """Test loading preferences with partial terminal configuration"""
        # Create preferences with partial terminal config
        partial_prefs = {
            "default_editor": "kiro",
            "terminal": {
                "preferred": "gnome-terminal"
                # Missing "available" and "last_detected"
            }
        }
        with open(self.preferences_file, 'w') as f:
            json.dump(partial_prefs, f)

        preferences = self.config_manager.load_preferences()

        # Should merge with defaults
        assert preferences["default_editor"] == "kiro"
        assert preferences["terminal"]["preferred"] == "gnome-terminal"
        assert preferences["terminal"]["available"] == {}
        assert preferences["terminal"]["last_detected"] is None

    def test_get_terminal_preferences(self):
        """Test getting terminal-specific preferences"""
        terminal_prefs = self.config_manager.get_terminal_preferences()

        assert terminal_prefs["preferred"] is None
        assert terminal_prefs["available"] == {}
        assert terminal_prefs["last_detected"] is None

    def test_set_terminal_preferences(self):
        """Test setting terminal-specific preferences"""
        new_terminal_prefs = {
            "preferred": "konsole",
            "available": {"konsole": "/usr/bin/konsole"},
            "last_detected": "2024-01-15T10:30:00Z"
        }

        self.config_manager.set_terminal_preferences(new_terminal_prefs)

        # Verify preferences were saved
        loaded_prefs = self.config_manager.load_preferences()
        assert loaded_prefs["terminal"] == new_terminal_prefs

    def test_get_set_preferred_terminal(self):
        """Test getting and setting preferred terminal"""
        # Initially should be None
        assert self.config_manager.get_preferred_terminal() is None

        # Set preferred terminal
        self.config_manager.set_preferred_terminal("gnome-terminal")

        # Should be persisted
        assert self.config_manager.get_preferred_terminal() == "gnome-terminal"

    def test_get_set_available_terminals(self):
        """Test getting and setting available terminals"""
        # Initially should be empty
        assert self.config_manager.get_available_terminals() == {}

        # Set available terminals
        terminals = {
            "gnome-terminal": "/usr/bin/gnome-terminal",
            "konsole": "/usr/bin/konsole"
        }
        self.config_manager.set_available_terminals(terminals)

        # Should be persisted
        assert self.config_manager.get_available_terminals() == terminals

    def test_get_set_last_detected_time(self):
        """Test getting and setting last detection timestamp"""
        # Initially should be None
        assert self.config_manager.get_last_detected_time() is None

        # Set timestamp
        timestamp = "2024-01-15T10:30:00Z"
        self.config_manager.set_last_detected_time(timestamp)

        # Should be persisted
        assert self.config_manager.get_last_detected_time() == timestamp

    def test_corrupted_preferences_file(self):
        """Test handling of corrupted preferences.json"""
        # Create corrupted JSON file
        with open(self.preferences_file, 'w') as f:
            f.write("{ invalid json")

        # Should fall back to defaults
        preferences = self.config_manager.load_preferences()

        assert preferences["default_editor"] == "kiro"
        assert "terminal" in preferences
        assert preferences["terminal"]["preferred"] is None

    def test_preferences_persistence_across_instances(self):
        """Test that preferences persist across ConfigManager instances"""
        # Set preferences with first instance
        self.config_manager.set_preferred_terminal("xterm")
        self.config_manager.set_available_terminals({"xterm": "/usr/bin/xterm"})

        # Create new instance
        new_config_manager = ConfigManager()

        # Should load same preferences
        assert new_config_manager.get_preferred_terminal() == "xterm"
        assert new_config_manager.get_available_terminals() == {"xterm": "/usr/bin/xterm"}

    def test_terminal_preferences_dont_affect_other_preferences(self):
        """Test that terminal preferences don't interfere with other settings"""
        # Set editor preference
        prefs = self.config_manager.load_preferences()
        prefs["default_editor"] = "vscode"
        self.config_manager.save_preferences(prefs)

        # Set terminal preference
        self.config_manager.set_preferred_terminal("konsole")

        # Editor preference should be unchanged
        loaded_prefs = self.config_manager.load_preferences()
        assert loaded_prefs["default_editor"] == "vscode"
        assert loaded_prefs["terminal"]["preferred"] == "konsole"


class TestConfigManagerProperties:
    """Property-based tests for ConfigManager terminal preferences"""

    def setup_method(self):
        """Set up test environment with temporary config directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, ".config", "code-launcher")
        os.makedirs(self.config_dir, exist_ok=True)
        self.preferences_file = os.path.join(self.config_dir, "preferences.json")

        # Patch the config paths to use our temp directory
        self.config_patch = patch('src.core.config.CONFIG_DIR', self.config_dir)
        self.preferences_patch = patch('src.core.config.PREFERENCES_FILE', self.preferences_file)

        self.config_patch.start()
        self.preferences_patch.start()

    def teardown_method(self):
        """Clean up test environment"""
        self.config_patch.stop()
        self.preferences_patch.stop()
        shutil.rmtree(self.temp_dir)

    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), min_codepoint=32, max_codepoint=126)))
    @settings(max_examples=100)
    def test_preference_persistence_round_trip(self, terminal_name):
        """
        **Validates: Requirements 2.3, 2.4, 6.1**

        Property 2: Preference Persistence Round Trip
        For any valid terminal selection, storing the preference and then loading it
        should result in the same terminal being selected, with immediate persistence
        to preferences.json.
        """
        # Clean terminal name to avoid filesystem issues
        clean_terminal_name = ''.join(c for c in terminal_name if c.isalnum() or c in '-_')
        if not clean_terminal_name:
            clean_terminal_name = "test-terminal"

        config_manager = ConfigManager()

        # Create mock available terminals that includes our test terminal
        available_terminals = {
            clean_terminal_name: f"/usr/bin/{clean_terminal_name}",
            "gnome-terminal": "/usr/bin/gnome-terminal",  # Always include a known terminal
            "xterm": "/usr/bin/xterm"
        }

        # Set available terminals first
        config_manager.set_available_terminals(available_terminals)

        # Property 1: Setting preferred terminal should immediately persist to file
        config_manager.set_preferred_terminal(clean_terminal_name)

        # Verify immediate persistence - file should exist and contain the preference
        assert os.path.exists(self.preferences_file), \
            "Preferences file should be created immediately after setting preference"

        with open(self.preferences_file, 'r') as f:
            file_contents = json.load(f)
            assert file_contents["terminal"]["preferred"] == clean_terminal_name, \
                f"Preference should be immediately saved to file: expected {clean_terminal_name}"

        # Property 2: Loading preference should return the same terminal
        loaded_terminal = config_manager.get_preferred_terminal()
        assert loaded_terminal == clean_terminal_name, \
            f"Loaded terminal should match saved terminal: expected {clean_terminal_name}, got {loaded_terminal}"

        # Property 3: Round trip across ConfigManager instances (simulating application restart)
        new_config_manager = ConfigManager()
        reloaded_terminal = new_config_manager.get_preferred_terminal()
        assert reloaded_terminal == clean_terminal_name, \
            f"Terminal preference should persist across instances: expected {clean_terminal_name}, got {reloaded_terminal}"

        # Property 4: Available terminals should also persist
        reloaded_available = new_config_manager.get_available_terminals()
        assert clean_terminal_name in reloaded_available, \
            f"Available terminals should include the preferred terminal {clean_terminal_name}"
        assert reloaded_available[clean_terminal_name] == available_terminals[clean_terminal_name], \
            f"Terminal path should persist correctly"

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), min_codepoint=32, max_codepoint=126)),
        values=st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Po'), min_codepoint=32, max_codepoint=126)),
        min_size=1,
        max_size=10
    ))
    @settings(max_examples=100)
    def test_available_terminals_persistence_round_trip(self, terminals_dict):
        """
        **Validates: Requirements 2.3, 2.4, 6.1**

        Property 2: Preference Persistence Round Trip (Available Terminals)
        For any valid set of available terminals, storing them and then loading
        should result in the same terminals being available, with immediate persistence
        to preferences.json.
        """
        # Clean terminal names and paths to avoid filesystem issues
        clean_terminals = {}
        for name, path in terminals_dict.items():
            clean_name = ''.join(c for c in name if c.isalnum() or c in '-_')
            clean_path = ''.join(c for c in path if c.isprintable() and c not in '"\'\\')
            if clean_name and clean_path:
                clean_terminals[clean_name] = clean_path

        if not clean_terminals:
            clean_terminals = {"test-terminal": "/usr/bin/test-terminal"}

        config_manager = ConfigManager()

        # Property 1: Setting available terminals should immediately persist to file
        config_manager.set_available_terminals(clean_terminals)

        # Verify immediate persistence
        assert os.path.exists(self.preferences_file), \
            "Preferences file should be created immediately after setting available terminals"

        with open(self.preferences_file, 'r') as f:
            file_contents = json.load(f)
            assert file_contents["terminal"]["available"] == clean_terminals, \
                f"Available terminals should be immediately saved to file"

        # Property 2: Loading available terminals should return the same set
        loaded_terminals = config_manager.get_available_terminals()
        assert loaded_terminals == clean_terminals, \
            f"Loaded terminals should match saved terminals"

        # Property 3: Round trip across ConfigManager instances (simulating application restart)
        new_config_manager = ConfigManager()
        reloaded_terminals = new_config_manager.get_available_terminals()
        assert reloaded_terminals == clean_terminals, \
            f"Available terminals should persist across instances"

        # Property 4: Individual terminal paths should be accessible
        for terminal_name, expected_path in clean_terminals.items():
            assert terminal_name in reloaded_terminals, \
                f"Terminal {terminal_name} should be in reloaded terminals"
            assert reloaded_terminals[terminal_name] == expected_path, \
                f"Path for {terminal_name} should match: expected {expected_path}, got {reloaded_terminals[terminal_name]}"

    @given(st.one_of(st.none(), st.text(min_size=1, max_size=50)))
    @settings(max_examples=100)
    def test_last_detected_time_persistence_round_trip(self, timestamp):
        """
        **Validates: Requirements 2.3, 2.4, 6.1**

        Property 2: Preference Persistence Round Trip (Last Detected Time)
        For any valid timestamp (including None), storing it and then loading
        should result in the same timestamp being returned, with immediate persistence
        to preferences.json.
        """
        config_manager = ConfigManager()

        # Property 1: Setting last detected time should immediately persist to file
        config_manager.set_last_detected_time(timestamp)

        # Verify immediate persistence
        assert os.path.exists(self.preferences_file), \
            "Preferences file should be created immediately after setting timestamp"

        with open(self.preferences_file, 'r') as f:
            file_contents = json.load(f)
            assert file_contents["terminal"]["last_detected"] == timestamp, \
                f"Last detected time should be immediately saved to file"

        # Property 2: Loading timestamp should return the same value
        loaded_timestamp = config_manager.get_last_detected_time()
        assert loaded_timestamp == timestamp, \
            f"Loaded timestamp should match saved timestamp: expected {timestamp}, got {loaded_timestamp}"

        # Property 3: Round trip across ConfigManager instances (simulating application restart)
        new_config_manager = ConfigManager()
        reloaded_timestamp = new_config_manager.get_last_detected_time()
        assert reloaded_timestamp == timestamp, \
            f"Timestamp should persist across instances: expected {timestamp}, got {reloaded_timestamp}"

    @given(st.dictionaries(
        keys=st.sampled_from(["preferred", "available", "last_detected"]),
        values=st.one_of(
            st.none(),
            st.text(min_size=1, max_size=30),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126)),
                values=st.text(min_size=1, max_size=50),
                min_size=0,
                max_size=5
            )
        ),
        min_size=1,
        max_size=3
    ))
    @settings(max_examples=100)
    def test_terminal_preferences_structure_persistence(self, terminal_config):
        """
        **Validates: Requirements 2.3, 2.4, 6.1**

        Property 2: Preference Persistence Round Trip (Complete Terminal Config)
        For any valid terminal configuration structure, storing it and then loading
        should result in the same configuration being returned, with immediate persistence
        to preferences.json.
        """
        config_manager = ConfigManager()

        # Clean the configuration to ensure valid data types
        clean_config = {}
        for key, value in terminal_config.items():
            if key == "preferred":
                if isinstance(value, str):
                    clean_value = ''.join(c for c in value if c.isalnum() or c in '-_') or None
                    clean_config[key] = clean_value
                elif value is None:
                    clean_config[key] = value
                # Skip invalid values - they will be replaced with defaults
            elif key == "available":
                if isinstance(value, dict):
                    clean_dict = {}
                    for k, v in value.items():
                        clean_k = ''.join(c for c in k if c.isalnum() or c in '-_')
                        clean_v = ''.join(c for c in str(v) if c.isprintable() and c not in '"\'\\')
                        if clean_k and clean_v:
                            clean_dict[clean_k] = clean_v
                    clean_config[key] = clean_dict
                # Skip invalid values - they will be replaced with defaults
            elif key == "last_detected":
                if isinstance(value, (str, type(None))):
                    clean_config[key] = value
                elif isinstance(value, str):
                    clean_config[key] = str(value)
                # Skip invalid values - they will be replaced with defaults

        # If no valid values were found, use at least one valid value for testing
        if not clean_config:
            clean_config = {"preferred": "test-terminal"}

        # Property 1: Setting terminal preferences should immediately persist to file
        config_manager.set_terminal_preferences(clean_config)

        # Verify immediate persistence
        assert os.path.exists(self.preferences_file), \
            "Preferences file should be created immediately after setting terminal preferences"

        with open(self.preferences_file, 'r') as f:
            file_contents = json.load(f)
            saved_terminal_config = file_contents["terminal"]

            # Check that all provided keys are saved correctly
            for key, expected_value in clean_config.items():
                assert key in saved_terminal_config, f"Key {key} should be in saved config"
                assert saved_terminal_config[key] == expected_value, \
                    f"Value for {key} should match: expected {expected_value}, got {saved_terminal_config[key]}"

        # Property 2: Loading terminal preferences should return the same configuration
        loaded_config = config_manager.get_terminal_preferences()
        for key, expected_value in clean_config.items():
            assert key in loaded_config, f"Key {key} should be in loaded config"
            assert loaded_config[key] == expected_value, \
                f"Loaded value for {key} should match saved value: expected {expected_value}, got {loaded_config[key]}"

        # Property 3: Round trip across ConfigManager instances (simulating application restart)
        new_config_manager = ConfigManager()
        reloaded_config = new_config_manager.get_terminal_preferences()
        for key, expected_value in clean_config.items():
            assert key in reloaded_config, f"Key {key} should be in reloaded config"
            assert reloaded_config[key] == expected_value, \
                f"Reloaded value for {key} should persist across instances: expected {expected_value}, got {reloaded_config[key]}"

        # Property 4: Default values should be preserved for missing keys
        default_keys = {"preferred": None, "available": {}, "last_detected": None}
        for key, default_value in default_keys.items():
            if key not in clean_config:
                assert reloaded_config[key] == default_value, \
                    f"Default value for {key} should be preserved: expected {default_value}, got {reloaded_config[key]}"

    @given(st.one_of(
        # Valid preference files with various structures
        st.dictionaries(
            keys=st.sampled_from(["default_editor", "terminal", "other_setting"]),
            values=st.one_of(
                st.text(min_size=1, max_size=20),
                st.dictionaries(
                    keys=st.sampled_from(["preferred", "available", "last_detected", "extra_key"]),
                    values=st.one_of(
                        st.none(),
                        st.text(min_size=1, max_size=30),
                        st.dictionaries(
                            keys=st.text(min_size=1, max_size=15),
                            values=st.text(min_size=1, max_size=50),
                            min_size=0,
                            max_size=3
                        )
                    ),
                    min_size=0,
                    max_size=5
                ),
                st.integers(),
                st.booleans()
            ),
            min_size=0,
            max_size=5
        ),
        # Missing file (None represents no file)
        st.none(),
        # Empty file content
        st.just({}),
        # Old format files (missing terminal section)
        st.dictionaries(
            keys=st.sampled_from(["default_editor", "window_size", "last_opened"]),
            values=st.one_of(st.text(min_size=1, max_size=20), st.integers(), st.lists(st.integers(), min_size=2, max_size=2)),
            min_size=1,
            max_size=3
        )
    ))
    @settings(max_examples=100)
    def test_configuration_validation_and_defaults(self, preferences_content):
        """
        **Validates: Requirements 6.2, 6.4, 6.5**

        Property 6: Configuration Validation and Defaults
        For any preferences.json file (including missing, corrupted, or incomplete files),
        the Preferences_Manager should provide valid default values for all terminal-related
        configuration keys and maintain backward compatibility.
        """
        config_manager = ConfigManager()

        # Simulate different file states
        if preferences_content is not None:
            try:
                with open(self.preferences_file, 'w') as f:
                    json.dump(preferences_content, f)
            except (TypeError, ValueError):
                # If the content can't be serialized to JSON, create a corrupted file
                with open(self.preferences_file, 'w') as f:
                    f.write("{ corrupted json content")
        else:
            # Simulate missing file by ensuring it doesn't exist
            if os.path.exists(self.preferences_file):
                os.remove(self.preferences_file)

        # Property 1: Loading preferences should always succeed and return valid structure
        try:
            loaded_preferences = config_manager.load_preferences()
        except Exception as e:
            pytest.fail(f"Loading preferences should never fail, but got exception: {e}")

        # Property 2: All required keys should be present with valid default values
        assert isinstance(loaded_preferences, dict), \
            "Loaded preferences should always be a dictionary"

        assert "default_editor" in loaded_preferences, \
            "default_editor key should always be present"
        assert loaded_preferences["default_editor"] in ["kiro", "vscode"] or isinstance(loaded_preferences["default_editor"], str), \
            f"default_editor should be a valid string, got: {loaded_preferences['default_editor']}"

        assert "terminal" in loaded_preferences, \
            "terminal key should always be present"
        assert isinstance(loaded_preferences["terminal"], dict), \
            "terminal value should always be a dictionary"

        # Property 3: Terminal section should have all required keys with correct defaults
        terminal_config = loaded_preferences["terminal"]

        assert "preferred" in terminal_config, \
            "terminal.preferred key should always be present"
        assert terminal_config["preferred"] is None or isinstance(terminal_config["preferred"], str), \
            f"terminal.preferred should be None or string, got: {terminal_config['preferred']}"

        assert "available" in terminal_config, \
            "terminal.available key should always be present"
        assert isinstance(terminal_config["available"], dict), \
            f"terminal.available should be a dictionary, got: {type(terminal_config['available'])}"

        assert "last_detected" in terminal_config, \
            "terminal.last_detected key should always be present"
        assert terminal_config["last_detected"] is None or isinstance(terminal_config["last_detected"], str), \
            f"terminal.last_detected should be None or string, got: {terminal_config['last_detected']}"

        # Property 4: Backward compatibility - old preferences should be preserved
        if preferences_content is not None and isinstance(preferences_content, dict):
            for key, value in preferences_content.items():
                if key != "terminal" and isinstance(value, (str, int, bool, list)):
                    # Non-terminal settings should be preserved only if they are valid
                    if key in loaded_preferences:
                        if key == "default_editor":
                            # default_editor should only preserve valid string values
                            if isinstance(value, str):
                                assert loaded_preferences[key] == value, \
                                    f"Valid default_editor should be preserved: expected {value}, got {loaded_preferences[key]}"
                            else:
                                # Invalid default_editor should be replaced with default
                                assert loaded_preferences[key] == "kiro", \
                                    f"Invalid default_editor should be replaced with 'kiro', got {loaded_preferences[key]}"
                        else:
                            # Other settings can be preserved as-is if they are basic types
                            assert loaded_preferences[key] == value or str(loaded_preferences[key]) == str(value), \
                                f"Backward compatibility: {key} should be preserved, expected {value}, got {loaded_preferences[key]}"

        # Property 5: Default values should be used when keys are missing
        if preferences_content is None or not isinstance(preferences_content, dict) or "terminal" not in preferences_content:
            # When terminal section is missing, defaults should be used
            assert terminal_config["preferred"] is None, \
                "Default preferred terminal should be None"
            assert terminal_config["available"] == {}, \
                "Default available terminals should be empty dict"
            assert terminal_config["last_detected"] is None, \
                "Default last_detected should be None"

        # Property 6: Partial terminal configuration should be merged with defaults
        if (preferences_content is not None and isinstance(preferences_content, dict) and
            "terminal" in preferences_content and isinstance(preferences_content["terminal"], dict)):

            original_terminal = preferences_content["terminal"]

            # Check that valid provided values are preserved, invalid ones get defaults
            for key in ["preferred", "available", "last_detected"]:
                if key in original_terminal:
                    original_value = original_terminal[key]

                    if key == "preferred":
                        # preferred should be None or string
                        if original_value is None or isinstance(original_value, str):
                            assert terminal_config[key] == original_value, \
                                f"Valid terminal.{key} should be preserved: expected {original_value}, got {terminal_config[key]}"
                        else:
                            # Invalid value should be replaced with default
                            assert terminal_config[key] is None, \
                                f"Invalid terminal.{key} should be replaced with default None, got {terminal_config[key]}"

                    elif key == "available":
                        # available should be a dict with string keys and values
                        if isinstance(original_value, dict):
                            # Check if all keys and values are strings
                            valid_dict = all(isinstance(k, str) and isinstance(v, str)
                                           for k, v in original_value.items())
                            if valid_dict:
                                assert terminal_config[key] == original_value, \
                                    f"Valid terminal.{key} should be preserved: expected {original_value}, got {terminal_config[key]}"
                            else:
                                # Partially valid dict should have only valid entries preserved
                                expected_dict = {k: v for k, v in original_value.items()
                                               if isinstance(k, str) and isinstance(v, str)}
                                assert terminal_config[key] == expected_dict, \
                                    f"Partially valid terminal.{key} should preserve valid entries: expected {expected_dict}, got {terminal_config[key]}"
                        else:
                            # Invalid value should be replaced with default
                            assert terminal_config[key] == {}, \
                                f"Invalid terminal.{key} should be replaced with default {{}}, got {terminal_config[key]}"

                    elif key == "last_detected":
                        # last_detected should be None or string
                        if original_value is None or isinstance(original_value, str):
                            assert terminal_config[key] == original_value, \
                                f"Valid terminal.{key} should be preserved: expected {original_value}, got {terminal_config[key]}"
                        else:
                            # Invalid value should be replaced with default
                            assert terminal_config[key] is None, \
                                f"Invalid terminal.{key} should be replaced with default None, got {terminal_config[key]}"

        # Property 7: Configuration should be immediately saveable and loadable
        try:
            config_manager.save_preferences(loaded_preferences)
            reloaded_preferences = config_manager.load_preferences()

            # Essential structure should be preserved
            assert reloaded_preferences["terminal"]["preferred"] == loaded_preferences["terminal"]["preferred"], \
                "Preferred terminal should survive save/load cycle"
            assert reloaded_preferences["terminal"]["available"] == loaded_preferences["terminal"]["available"], \
                "Available terminals should survive save/load cycle"
            assert reloaded_preferences["terminal"]["last_detected"] == loaded_preferences["terminal"]["last_detected"], \
                "Last detected time should survive save/load cycle"

        except Exception as e:
            pytest.fail(f"Validated preferences should be saveable and reloadable, but got exception: {e}")

        # Property 8: Terminal-specific methods should work with validated configuration
        try:
            terminal_prefs = config_manager.get_terminal_preferences()
            assert isinstance(terminal_prefs, dict), \
                "get_terminal_preferences should return a dictionary"
            assert "preferred" in terminal_prefs, \
                "Terminal preferences should have preferred key"
            assert "available" in terminal_prefs, \
                "Terminal preferences should have available key"
            assert "last_detected" in terminal_prefs, \
                "Terminal preferences should have last_detected key"

            # These methods should not raise exceptions
            preferred = config_manager.get_preferred_terminal()
            available = config_manager.get_available_terminals()
            last_detected = config_manager.get_last_detected_time()

            assert preferred is None or isinstance(preferred, str), \
                "get_preferred_terminal should return None or string"
            assert isinstance(available, dict), \
                "get_available_terminals should return a dictionary"
            assert last_detected is None or isinstance(last_detected, str), \
                "get_last_detected_time should return None or string"

        except Exception as e:
            pytest.fail(f"Terminal-specific methods should work with validated config, but got exception: {e}")

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=100)
    def test_corrupted_preferences_file_handling(self, corrupted_content):
        """
        **Validates: Requirements 6.2, 6.4, 6.5**

        Property 6: Configuration Validation and Defaults (Corrupted Files)
        For any corrupted or invalid JSON content in preferences.json,
        the ConfigManager should gracefully fall back to defaults and continue operation.
        """
        config_manager = ConfigManager()

        # Create a file with potentially corrupted content
        with open(self.preferences_file, 'w') as f:
            f.write(corrupted_content)

        # Property 1: Loading should never crash, even with corrupted content
        try:
            loaded_preferences = config_manager.load_preferences()
        except Exception as e:
            pytest.fail(f"Loading corrupted preferences should not crash, but got exception: {e}")

        # Property 2: Should fall back to valid defaults
        assert isinstance(loaded_preferences, dict), \
            "Should return valid dictionary even with corrupted input"

        assert "default_editor" in loaded_preferences, \
            "Should have default_editor even with corrupted input"
        assert "terminal" in loaded_preferences, \
            "Should have terminal section even with corrupted input"

        terminal_config = loaded_preferences["terminal"]
        assert isinstance(terminal_config, dict), \
            "Terminal config should be valid dict even with corrupted input"
        assert "preferred" in terminal_config, \
            "Should have terminal.preferred even with corrupted input"
        assert "available" in terminal_config, \
            "Should have terminal.available even with corrupted input"
        assert "last_detected" in terminal_config, \
            "Should have terminal.last_detected even with corrupted input"

        # Property 3: Defaults should be sensible values
        assert loaded_preferences["default_editor"] == "kiro", \
            "Default editor should be 'kiro' when falling back from corruption"
        assert terminal_config["preferred"] is None, \
            "Default preferred terminal should be None when falling back from corruption"
        assert terminal_config["available"] == {}, \
            "Default available terminals should be empty dict when falling back from corruption"
        assert terminal_config["last_detected"] is None, \
            "Default last_detected should be None when falling back from corruption"

        # Property 4: Should be able to save and reload the corrected preferences
        try:
            config_manager.save_preferences(loaded_preferences)
            reloaded_preferences = config_manager.load_preferences()

            assert reloaded_preferences == loaded_preferences, \
                "Corrected preferences should be stable across save/load cycles"

        except Exception as e:
            pytest.fail(f"Corrected preferences should be saveable, but got exception: {e}")

        # Property 5: File should now contain valid JSON
        try:
            with open(self.preferences_file, 'r') as f:
                file_content = json.load(f)
            assert isinstance(file_content, dict), \
                "Saved file should contain valid JSON dictionary"
        except json.JSONDecodeError:
            pytest.fail("After handling corruption, file should contain valid JSON")