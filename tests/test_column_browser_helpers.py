#!/usr/bin/env python3
"""
Unit tests for ColumnBrowser helper methods
Tests get_item_at_position, is_root_column, and get_hierarchy_info
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.column_browser import ColumnBrowser


class TestColumnBrowserGetItemAtPosition(unittest.TestCase):
    """Test cases for get_item_at_position method"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.browser = ColumnBrowser(self.callback)

    def test_get_item_at_position_returns_none_when_no_item(self):
        """Test that get_item_at_position returns (None, None) when clicking empty area"""
        # Mock get_path_at_pos to return None (no item at position)
        self.browser.treeview.get_path_at_pos = Mock(return_value=None)

        # Call method
        tree_path, column = self.browser.get_item_at_position(100, 100)

        # Verify returns (None, None)
        self.assertIsNone(tree_path)
        self.assertIsNone(column)
        self.browser.treeview.get_path_at_pos.assert_called_once_with(100, 100)

    def test_get_item_at_position_returns_path_and_column_when_item_exists(self):
        """Test that get_item_at_position returns correct path and column when clicking on item"""
        # Create mock return values
        mock_tree_path = Mock()
        mock_column = Mock()
        mock_cell_x = 10
        mock_cell_y = 5

        # Mock get_path_at_pos to return item info
        self.browser.treeview.get_path_at_pos = Mock(
            return_value=(mock_tree_path, mock_column, mock_cell_x, mock_cell_y)
        )

        # Call method
        tree_path, column = self.browser.get_item_at_position(150, 200)

        # Verify returns correct values
        self.assertEqual(tree_path, mock_tree_path)
        self.assertEqual(column, mock_column)
        self.browser.treeview.get_path_at_pos.assert_called_once_with(150, 200)

    def test_get_item_at_position_converts_coordinates_to_int(self):
        """Test that get_item_at_position converts float coordinates to int"""
        # Mock get_path_at_pos
        self.browser.treeview.get_path_at_pos = Mock(return_value=None)

        # Call with float coordinates
        self.browser.get_item_at_position(100.7, 200.3)

        # Verify coordinates were converted to int
        self.browser.treeview.get_path_at_pos.assert_called_once_with(100, 200)

    def test_get_item_at_position_handles_zero_coordinates(self):
        """Test that get_item_at_position handles (0, 0) coordinates"""
        # Mock get_path_at_pos
        self.browser.treeview.get_path_at_pos = Mock(return_value=None)

        # Call with zero coordinates
        tree_path, column = self.browser.get_item_at_position(0, 0)

        # Verify method was called and returns None
        self.assertIsNone(tree_path)
        self.assertIsNone(column)
        self.browser.treeview.get_path_at_pos.assert_called_once_with(0, 0)


class TestColumnBrowserIsRootColumn(unittest.TestCase):
    """Test cases for is_root_column method"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.browser = ColumnBrowser(self.callback)

    def test_is_root_column_returns_true_when_current_path_is_none(self):
        """Test that is_root_column returns True when current_path is None"""
        # Set current_path to None
        self.browser.current_path = None

        # Call method
        result = self.browser.is_root_column()

        # Verify returns True
        self.assertTrue(result)

    def test_is_root_column_returns_true_when_current_path_is_categories(self):
        """Test that is_root_column returns True when current_path is 'categories'"""
        # Set current_path to "categories"
        self.browser.current_path = "categories"

        # Call method
        result = self.browser.is_root_column()

        # Verify returns True
        self.assertTrue(result)

    def test_is_root_column_returns_false_when_current_path_is_category(self):
        """Test that is_root_column returns False when current_path is a category"""
        # Set current_path to a category path
        self.browser.current_path = "cat:Web"

        # Call method
        result = self.browser.is_root_column()

        # Verify returns False
        self.assertFalse(result)

    def test_is_root_column_returns_false_when_current_path_is_nested_category(self):
        """Test that is_root_column returns False when current_path is a nested category"""
        # Set current_path to a nested category path
        self.browser.current_path = "cat:Web:Frontend"

        # Call method
        result = self.browser.is_root_column()

        # Verify returns False
        self.assertFalse(result)

    def test_is_root_column_returns_false_when_current_path_is_projects(self):
        """Test that is_root_column returns False when current_path is projects view"""
        # Set current_path to projects view
        self.browser.current_path = "projects:cat:Web"

        # Call method
        result = self.browser.is_root_column()

        # Verify returns False
        self.assertFalse(result)


class TestColumnBrowserGetHierarchyInfo(unittest.TestCase):
    """Test cases for get_hierarchy_info method"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.browser = ColumnBrowser(self.callback)

    def test_get_hierarchy_info_returns_level_0_for_none_path(self):
        """Test that get_hierarchy_info returns level 0 when current_path is None"""
        # Set current_path to None
        self.browser.current_path = None

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 0 with no category
        self.assertEqual(info['level'], 0)
        self.assertIsNone(info['category'])
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "")

    def test_get_hierarchy_info_returns_level_0_for_categories_path(self):
        """Test that get_hierarchy_info returns level 0 when current_path is 'categories'"""
        # Set current_path to "categories"
        self.browser.current_path = "categories"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 0 with no category
        self.assertEqual(info['level'], 0)
        self.assertIsNone(info['category'])
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "categories")

    def test_get_hierarchy_info_returns_level_1_for_single_category(self):
        """Test that get_hierarchy_info returns level 1 for single category path"""
        # Set current_path to single category
        self.browser.current_path = "cat:Web"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 1 with category
        self.assertEqual(info['level'], 1)
        self.assertEqual(info['category'], "Web")
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "cat:Web")

    def test_get_hierarchy_info_returns_level_2_for_nested_category(self):
        """Test that get_hierarchy_info returns level 2 for nested category path"""
        # Set current_path to nested category
        self.browser.current_path = "cat:Web:Frontend"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 2 with category and subcategory
        self.assertEqual(info['level'], 2)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend")
        self.assertEqual(info['full_path'], "cat:Web:Frontend")

    def test_get_hierarchy_info_returns_level_3_for_deeply_nested_category(self):
        """Test that get_hierarchy_info returns level 3 for deeply nested category path"""
        # Set current_path to deeply nested category
        self.browser.current_path = "cat:Web:Frontend:React"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 3 with category and subcategory path
        self.assertEqual(info['level'], 3)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend:React")
        self.assertEqual(info['full_path'], "cat:Web:Frontend:React")

    def test_get_hierarchy_info_handles_projects_view_with_category(self):
        """Test that get_hierarchy_info handles projects view with category"""
        # Set current_path to projects view with category
        self.browser.current_path = "projects:cat:Web"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify extracts category from projects view
        self.assertEqual(info['level'], 1)
        self.assertEqual(info['category'], "Web")
        self.assertIsNone(info['subcategory_path'])

    def test_get_hierarchy_info_handles_projects_view_with_nested_category(self):
        """Test that get_hierarchy_info handles projects view with nested category"""
        # Set current_path to projects view with nested category
        self.browser.current_path = "projects:cat:Web:Frontend"

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify extracts category and subcategory from projects view
        self.assertEqual(info['level'], 2)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend")

    def test_get_hierarchy_info_handles_empty_string_path(self):
        """Test that get_hierarchy_info handles empty string path"""
        # Set current_path to empty string
        self.browser.current_path = ""

        # Call method
        info = self.browser.get_hierarchy_info()

        # Verify returns level 0
        self.assertEqual(info['level'], 0)
        self.assertIsNone(info['category'])
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "")


class TestColumnBrowserHelperMethodsIntegration(unittest.TestCase):
    """Integration tests for helper methods working together"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.browser = ColumnBrowser(self.callback)

    def test_is_root_column_and_get_hierarchy_info_consistency(self):
        """Test that is_root_column and get_hierarchy_info are consistent"""
        # Test root column scenarios
        root_paths = [None, "categories"]
        for path in root_paths:
            self.browser.current_path = path
            self.assertTrue(self.browser.is_root_column())
            info = self.browser.get_hierarchy_info()
            self.assertEqual(info['level'], 0)

        # Test non-root column scenarios
        non_root_paths = ["cat:Web", "cat:Web:Frontend", "projects:cat:Web"]
        for path in non_root_paths:
            self.browser.current_path = path
            self.assertFalse(self.browser.is_root_column())
            info = self.browser.get_hierarchy_info()
            self.assertGreater(info['level'], 0)

    def test_helper_methods_with_real_category_paths(self):
        """Test helper methods with realistic category paths"""
        # Test various realistic paths
        test_cases = [
            {
                'path': "cat:Development",
                'is_root': False,
                'level': 1,
                'category': "Development",
                'subcategory': None
            },
            {
                'path': "cat:Development:Python",
                'is_root': False,
                'level': 2,
                'category': "Development",
                'subcategory': "Python"
            },
            {
                'path': "cat:Development:Python:Django",
                'is_root': False,
                'level': 3,
                'category': "Development",
                'subcategory': "Python:Django"
            }
        ]

        for test_case in test_cases:
            self.browser.current_path = test_case['path']

            # Test is_root_column
            self.assertEqual(self.browser.is_root_column(), test_case['is_root'])

            # Test get_hierarchy_info
            info = self.browser.get_hierarchy_info()
            self.assertEqual(info['level'], test_case['level'])
            self.assertEqual(info['category'], test_case['category'])
            self.assertEqual(info['subcategory_path'], test_case['subcategory'])


if __name__ == '__main__':
    unittest.main()
