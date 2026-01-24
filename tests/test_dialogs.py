#!/usr/bin/env python3
"""
Tests for dialogs module - specifically testing pre_config functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing dialogs
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
sys.modules['gi.repository.Gtk'] = MagicMock()

from dialogs import Dialogs


class TestShowCreateCategoryDialog(unittest.TestCase):
    """Test show_create_category_dialog with pre_config parameter"""

    def setUp(self):
        """Set up test fixtures"""
        self.parent = Mock()
        self.categories = {
            'Web': {'icon': 'folder', 'description': 'Web projects', 'subcategories': {}},
            'Mobile': {'icon': 'phone', 'description': 'Mobile apps', 'subcategories': {}}
        }
        self.callback = Mock()

    def test_signature_accepts_pre_config(self):
        """Test that the function accepts pre_config parameter"""
        # This test verifies the signature change
        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel

            # Should not raise an error
            try:
                Dialogs.show_create_category_dialog(
                    self.parent,
                    self.categories,
                    self.callback,
                    pre_config={'parent_category': 'Web'}
                )
            except TypeError as e:
                self.fail(f"Function should accept pre_config parameter: {e}")

    def test_backward_compatibility_without_pre_config(self):
        """Test that the function still works without pre_config (backward compatibility)"""
        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel

            # Should work without pre_config
            try:
                Dialogs.show_create_category_dialog(
                    self.parent,
                    self.categories,
                    self.callback
                )
            except TypeError as e:
                self.fail(f"Function should work without pre_config: {e}")


class TestShowAddProjectDialog(unittest.TestCase):
    """Test show_add_project_dialog with pre_config parameter"""

    def setUp(self):
        """Set up test fixtures"""
        self.parent = Mock()
        self.categories = {
            'Web': {
                'icon': 'folder',
                'description': 'Web projects',
                'subcategories': {
                    'Frontend': {'icon': 'folder', 'description': 'Frontend projects'},
                    'Backend': {'icon': 'folder', 'description': 'Backend projects'}
                }
            },
            'Mobile': {
                'icon': 'phone',
                'description': 'Mobile apps',
                'subcategories': {}
            }
        }
        self.callback = Mock()

    def test_signature_accepts_pre_config(self):
        """Test that the function accepts pre_config parameter"""
        # This test verifies the signature change
        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Should not raise an error
            try:
                Dialogs.show_add_project_dialog(
                    self.parent,
                    self.categories,
                    self.callback,
                    pre_config={'category': 'Web', 'subcategory': 'Frontend'}
                )
            except TypeError as e:
                self.fail(f"Function should accept pre_config parameter: {e}")

    def test_backward_compatibility_without_pre_config(self):
        """Test that the function still works without pre_config (backward compatibility)"""
        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Should work without pre_config
            try:
                Dialogs.show_add_project_dialog(
                    self.parent,
                    self.categories,
                    self.callback
                )
            except TypeError as e:
                self.fail(f"Function should work without pre_config: {e}")

    def test_pre_config_with_category_only(self):
        """Test pre_config with only category specified"""
        pre_config = {
            'category': 'Web',
            'subcategory': None,
            'hierarchy_path': 'cat:Web'
        }

        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Should not raise an error
            try:
                Dialogs.show_add_project_dialog(
                    self.parent,
                    self.categories,
                    self.callback,
                    pre_config=pre_config
                )
            except Exception as e:
                self.fail(f"Function should handle category-only pre_config: {e}")

    def test_pre_config_with_category_and_subcategory(self):
        """Test pre_config with both category and subcategory specified"""
        pre_config = {
            'category': 'Web',
            'subcategory': 'Frontend',
            'hierarchy_path': 'cat:Web:Frontend'
        }

        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Should not raise an error
            try:
                Dialogs.show_add_project_dialog(
                    self.parent,
                    self.categories,
                    self.callback,
                    pre_config=pre_config
                )
            except Exception as e:
                self.fail(f"Function should handle full pre_config: {e}")

    def test_pre_config_with_invalid_category(self):
        """Test pre_config with invalid category (should handle gracefully)"""
        pre_config = {
            'category': 'NonExistent',
            'subcategory': None,
            'hierarchy_path': 'cat:NonExistent'
        }

        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Should not raise an error, just fall back to default
            try:
                Dialogs.show_add_project_dialog(
                    self.parent,
                    self.categories,
                    self.callback,
                    pre_config=pre_config
                )
            except Exception as e:
                self.fail(f"Function should handle invalid category gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
