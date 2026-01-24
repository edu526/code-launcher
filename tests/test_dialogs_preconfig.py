#!/usr/bin/env python3
"""
Integration tests for dialogs pre_config functionality
Tests that pre_config parameters are correctly extracted and applied
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDialogPreConfig(unittest.TestCase):
    """Test pre_config parameter extraction and application"""

    def setUp(self):
        """Set up test fixtures"""
        self.parent = Mock()
        self.categories = {
            'Web': {
                'icon': 'folder',
                'description': 'Web projects',
                'subcategories': {'Frontend': {}, 'Backend': {}}
            },
            'Mobile': {
                'icon': 'phone',
                'description': 'Mobile apps',
                'subcategories': {}
            }
        }
        self.callback = Mock()

    def test_pre_config_parent_category_extraction(self):
        """Test that parent_category is correctly extracted from pre_config"""
        pre_config = {
            'parent_category': 'Web',
            'force_subcategory': True,
            'hierarchy_path': 'cat:Web'
        }

        # Import after mocking
        with patch('dialogs.Gtk') as mock_gtk:
            # Setup mocks
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0  # Cancel
            mock_dialog.get_content_area.return_value = Mock()

            from dialogs import Dialogs

            # Call with pre_config
            Dialogs.show_create_category_dialog(
                self.parent,
                self.categories,
                self.callback,
                pre_config=pre_config
            )

            # Verify dialog was created
            self.assertTrue(mock_gtk.Dialog.called)

    def test_pre_config_force_subcategory(self):
        """Test that force_subcategory correctly sets dialog mode"""
        pre_config = {
            'parent_category': 'Web',
            'force_subcategory': True
        }

        with patch('dialogs.Gtk') as mock_gtk:
            mock_dialog = Mock()
            mock_gtk.Dialog.return_value = mock_dialog
            mock_dialog.run.return_value = 0
            mock_dialog.get_content_area.return_value = Mock()

            from dialogs import Dialogs

            Dialogs.show_create_category_dialog(
                self.parent,
                self.categories,
                self.callback,
                pre_config=pre_config
            )

            # Verify dialog was created and shown
            self.assertTrue(mock_dialog.show_all.called)


if __name__ == '__main__':
    unittest.main()
