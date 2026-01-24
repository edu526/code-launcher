#!/usr/bin/env python3
"""
Test to verify that "Add project" works from a CATEGORY_ITEM
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from context_menu import ContextMenuHandler, CATEGORY_ITEM


class TestCategoryItemAddProject(unittest.TestCase):
    """Test that verifies adding project from category item"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.column_browser.load_mixed_content = Mock()
        self.column_browser.current_path = "categories"

        self.parent_window = Mock()
        self.parent_window.categories = {
            "Web": {
                "icon": "folder",
                "description": "Web projects",
                "subcategories": {
                    "Frontend": {
                        "icon": "folder",
                        "description": "Frontend projects"
                    }
                }
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_menu_has_add_project_option(self):
        """Test that category item menu has 'Add project' option"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        menu = self.handler.create_context_menu(context)

        # Verify that menu has 2 options
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)

        # Verify labels
        labels = [item.get_label() for item in menu_items]
        self.assertIn("Add subcategory", labels)
        self.assertIn("Add project", labels)

        print("✅ Category item menu has 'Add project'")

    @patch('dialogs.Dialogs')
    def test_add_project_from_category_item(self, mock_dialogs):
        """Test adding project from category item (Web)"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        # Execute action
        self.handler.add_project_action(context)

        # Verify that dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Web')
        self.assertIsNone(pre_config['subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web')

        print("✅ Correct pre-config for category item 'Web'")

    @patch('dialogs.Dialogs')
    def test_add_project_from_nested_category_item(self, mock_dialogs):
        """Test adding project from nested category item (Web:Frontend)"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': 'cat:Web:Frontend',
            'is_project': False
        }

        # Execute action
        self.handler.add_project_action(context)

        # Verify that dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Web')
        self.assertEqual(pre_config['subcategory'], 'Frontend')
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend')

        print("✅ Correct pre-config for nested category item 'Web:Frontend'")

    @patch('dialogs.Dialogs')
    def test_add_project_callback_from_category_item(self, mock_dialogs):
        """Test that callback adds project correctly"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        # Execute action
        self.handler.add_project_action(context)

        # Get callback
        call_args = mock_dialogs.show_add_project_dialog.call_args
        callback = call_args[0][2]

        # Simulate adding project
        project_info = {
            "path": "/home/user/my-web-project",
            "category": "Web"
        }
        callback("MyWebProject", project_info)

        # Verify that project was added
        self.assertIn("MyWebProject", self.parent_window.projects)
        self.assertEqual(self.parent_window.projects["MyWebProject"]["path"], "/home/user/my-web-project")
        self.assertEqual(self.parent_window.projects["MyWebProject"]["category"], "Web")

        # Verify that it was saved and refreshed
        self.parent_window.config.save_projects.assert_called_once()
        self.column_browser.load_mixed_content.assert_called_once()

        print("✅ Project added correctly from category item")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TEST: Add Project from Category Item")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
