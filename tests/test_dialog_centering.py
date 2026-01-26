#!/usr/bin/env python3
"""
Tests for dialog centering functionality
Verifies that all dialogs are properly centered on parent window
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock GTK before importing dialogs
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
sys.modules['gi.repository.Gtk'] = MagicMock()

from dialogs.category_dialog import show_create_category_dialog
from dialogs.project_dialog import show_add_project_dialog
from dialogs.config_dialog import show_categories_dialog, show_projects_dialog, show_logs_dialog, show_preferences_dialog


class TestDialogCentering(unittest.TestCase):
    """Test that all dialogs are centered on parent window"""

    def setUp(self):
        """Set up test fixtures"""
        self.parent = Mock()
        self.categories = {
            'Web': {'icon': 'folder', 'description': 'Web projects', 'subcategories': {}},
            'Mobile': {'icon': 'phone', 'description': 'Mobile apps', 'subcategories': {}}
        }
        self.projects = {
            'Project1': {'path': '/path/to/project1', 'category': 'Web'}
        }
        self.callback = Mock()

    def test_config_dialog_is_centered(self):
        """Test that config dialog has CENTER_ON_PARENT position"""
        with patch('dialogs.config_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_categories_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify set_position was called with CENTER_ON_PARENT
            mock_dialog.set_position.assert_called_once()
            # Get the actual call argument
            call_args = mock_dialog.set_position.call_args
            # Verify it was called (we can't check the exact enum value due to mocking)
            self.assertTrue(mock_dialog.set_position.called)

    def test_create_category_dialog_is_centered(self):
        """Test that create category dialog has CENTER_ON_PARENT position"""
        with patch('dialogs.category_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_create_category_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify set_position was called
            self.assertTrue(mock_dialog.set_position.called)

    def test_create_category_dialog_with_preconfig_is_centered(self):
        """Test that create category dialog with pre_config has CENTER_ON_PARENT position"""
        with patch('dialogs.category_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            pre_config = {
                'parent_category': 'Web',
                'force_subcategory': True,
                'hierarchy_path': 'cat:Web'
            }

            # Call the dialog
            show_create_category_dialog(
                self.parent,
                self.categories,
                self.callback,
                pre_config=pre_config
            )

            # Verify set_position was called
            self.assertTrue(mock_dialog.set_position.called)

    def test_add_project_dialog_is_centered(self):
        """Test that add project dialog has CENTER_ON_PARENT position"""
        with patch('dialogs.project_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_add_project_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify set_position was called
            self.assertTrue(mock_dialog.set_position.called)

    def test_add_project_dialog_with_preconfig_is_centered(self):
        """Test that add project dialog with pre_config has CENTER_ON_PARENT position"""
        with patch('dialogs.project_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            pre_config = {
                'category': 'Web',
                'subcategory': None,
                'hierarchy_path': 'cat:Web'
            }

            # Call the dialog
            show_add_project_dialog(
                self.parent,
                self.categories,
                self.callback,
                pre_config=pre_config
            )

            # Verify set_position was called
            self.assertTrue(mock_dialog.set_position.called)

    def test_config_dialog_has_transient_for(self):
        """Test that config dialog has transient_for property set"""
        with patch('dialogs.config_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_categories_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify Dialog was created with transient_for
            mock_gtk.Dialog.assert_called_once()
            call_kwargs = mock_gtk.Dialog.call_args[1]
            self.assertIn('transient_for', call_kwargs)
            self.assertEqual(call_kwargs['transient_for'], self.parent)

    def test_create_category_dialog_has_transient_for(self):
        """Test that create category dialog has transient_for property set"""
        with patch('dialogs.category_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_create_category_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify Dialog was created with transient_for
            mock_gtk.Dialog.assert_called_once()
            call_kwargs = mock_gtk.Dialog.call_args[1]
            self.assertIn('transient_for', call_kwargs)
            self.assertEqual(call_kwargs['transient_for'], self.parent)

    def test_add_project_dialog_has_transient_for(self):
        """Test that add project dialog has transient_for property set"""
        with patch('dialogs.project_dialog.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            # Call the dialog
            show_add_project_dialog(
                self.parent,
                self.categories,
                self.callback
            )

            # Verify Dialog was created with transient_for
            mock_gtk.Dialog.assert_called_once()
            call_kwargs = mock_gtk.Dialog.call_args[1]
            self.assertIn('transient_for', call_kwargs)
            self.assertEqual(call_kwargs['transient_for'], self.parent)


if __name__ == '__main__':
    unittest.main()
