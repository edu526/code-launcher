#!/usr/bin/env python3
"""
Unit tests for add_project_action in ContextMenuHandler
Tests the add project functionality from context menus
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from context_menu import (
    ContextMenuHandler,
    ROOT_COLUMN,
    CHILD_COLUMN,
    CATEGORY_ITEM,
    PROJECT_ITEM
)


class TestAddProjectAction(unittest.TestCase):
    """Test cases for add_project_action method"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Mock parent window attributes
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
            },
            "Mobile": {
                "icon": "folder",
                "description": "Mobile projects",
                "subcategories": {}
            }
        }
        self.parent_window.projects = {
            "ExistingProject": {
                "path": "/home/user/existing",
                "category": "Web"
            }
        }
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        # Mock column_browser methods
        self.column_browser.load_mixed_content = Mock()
        self.column_browser.current_path = "categories"

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_add_project_action_root_column(self, mock_dialogs):
        """Test add_project_action for root column context"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify Dialogs.show_add_project_dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify the arguments
        call_args = mock_dialogs.show_add_project_dialog.call_args
        self.assertEqual(call_args[0][0], self.parent_window)  # parent
        self.assertEqual(call_args[0][1], self.parent_window.categories)  # categories
        self.assertIsNotNone(call_args[0][2])  # callback

        # Verify pre_config
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['category'])
        self.assertIsNone(pre_config['subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'categories')

    @patch('dialogs.Dialogs')
    def test_add_project_action_child_column_first_level(self, mock_dialogs):
        """Test add_project_action for child column at first level"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify Dialogs.show_add_project_dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['category'], 'Web')
        self.assertIsNone(pre_config['subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web')

    @patch('dialogs.Dialogs')
    def test_add_project_action_child_column_with_subcategory(self, mock_dialogs):
        """Test add_project_action for child column with subcategory"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web:Frontend',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify Dialogs.show_add_project_dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['category'], 'Web')
        self.assertEqual(pre_config['subcategory'], 'Frontend')
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend')

    @patch('dialogs.Dialogs')
    def test_add_project_action_child_column_deeply_nested(self, mock_dialogs):
        """Test add_project_action for deeply nested subcategory"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web:Frontend:React:Components',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify Dialogs.show_add_project_dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['category'], 'Web')
        self.assertEqual(pre_config['subcategory'], 'Frontend:React:Components')
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend:React:Components')

    @patch('dialogs.Dialogs')
    def test_add_project_callback_adds_project(self, mock_dialogs):
        """Test that the callback adds a project correctly"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Get the callback that was passed to the dialog
        call_args = mock_dialogs.show_add_project_dialog.call_args
        callback = call_args[0][2]

        # Call the callback to add a new project
        project_info = {
            "path": "/home/user/new-project",
            "category": "Web"
        }
        callback("NewProject", project_info)

        # Verify the project was added
        self.assertIn("NewProject", self.parent_window.projects)
        self.assertEqual(self.parent_window.projects["NewProject"]["path"], "/home/user/new-project")
        self.assertEqual(self.parent_window.projects["NewProject"]["category"], "Web")

        # Verify save and column refresh were called
        self.parent_window.config.save_projects.assert_called_once_with(self.parent_window.projects)
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('dialogs.Dialogs')
    def test_add_project_callback_adds_project_with_subcategory(self, mock_dialogs):
        """Test that the callback adds a project with subcategory correctly"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web:Frontend',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Get the callback that was passed to the dialog
        call_args = mock_dialogs.show_add_project_dialog.call_args
        callback = call_args[0][2]

        # Call the callback to add a new project with subcategory
        project_info = {
            "path": "/home/user/frontend-project",
            "category": "Web",
            "subcategory": "Frontend"
        }
        callback("FrontendProject", project_info)

        # Verify the project was added with subcategory
        self.assertIn("FrontendProject", self.parent_window.projects)
        self.assertEqual(self.parent_window.projects["FrontendProject"]["path"], "/home/user/frontend-project")
        self.assertEqual(self.parent_window.projects["FrontendProject"]["category"], "Web")
        self.assertEqual(self.parent_window.projects["FrontendProject"]["subcategory"], "Frontend")

        # Verify save and column refresh were called
        self.parent_window.config.save_projects.assert_called_once_with(self.parent_window.projects)
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('dialogs.Dialogs')
    def test_add_project_callback_updates_existing_project(self, mock_dialogs):
        """Test that the callback can update an existing project"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Mobile',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Get the callback
        call_args = mock_dialogs.show_add_project_dialog.call_args
        callback = call_args[0][2]

        # Update an existing project
        project_info = {
            "path": "/home/user/updated-path",
            "category": "Mobile"
        }
        callback("ExistingProject", project_info)

        # Verify the project was updated
        self.assertEqual(self.parent_window.projects["ExistingProject"]["path"], "/home/user/updated-path")
        self.assertEqual(self.parent_window.projects["ExistingProject"]["category"], "Mobile")

        # Verify save and column refresh were called
        self.parent_window.config.save_projects.assert_called_once()
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('dialogs.Dialogs')
    def test_add_project_action_with_invalid_context_type(self, mock_dialogs):
        """Test add_project_action with invalid context type falls back gracefully"""
        context = {
            'type': 'invalid_type',
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify Dialogs.show_add_project_dialog was called with fallback config
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config has fallback values
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['category'])
        self.assertIsNone(pre_config['subcategory'])

    @patch('dialogs.Dialogs')
    def test_add_project_action_with_none_hierarchy_path(self, mock_dialogs):
        """Test add_project_action handles None hierarchy_path"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': None,
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify it doesn't crash and calls the dialog
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verify pre_config handles None hierarchy_path
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['category'])
        self.assertIsNone(pre_config['subcategory'])
        self.assertIsNone(pre_config['hierarchy_path'])

    @patch('dialogs.Dialogs')
    def test_add_project_action_from_root_column_no_preselection(self, mock_dialogs):
        """Test that root column context doesn't pre-select any category"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify pre_config has no category pre-selected
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['category'])
        self.assertIsNone(pre_config['subcategory'])

    @patch('dialogs.Dialogs')
    def test_add_project_action_preserves_hierarchy_path(self, mock_dialogs):
        """Test that hierarchy_path is preserved in pre_config"""
        test_cases = [
            ('categories', ROOT_COLUMN),
            ('cat:Web', CHILD_COLUMN),
            ('cat:Web:Frontend', CHILD_COLUMN),
            ('cat:Mobile:Android:Kotlin', CHILD_COLUMN),
        ]

        for hierarchy_path, context_type in test_cases:
            # Reset mock
            mock_dialogs.reset_mock()

            context = {
                'type': context_type,
                'hierarchy_path': hierarchy_path,
                'item_path': None,
                'is_project': False
            }

            # Execute
            self.handler.add_project_action(context)

            # Verify hierarchy_path is preserved
            call_args = mock_dialogs.show_add_project_dialog.call_args
            pre_config = call_args[1]['pre_config']
            self.assertEqual(pre_config['hierarchy_path'], hierarchy_path,
                           f"Failed for hierarchy_path: {hierarchy_path}")


class TestAddProjectActionIntegration(unittest.TestCase):
    """Integration tests for add_project_action with real hierarchy parsing"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        self.parent_window.categories = {
            "Development": {
                "icon": "folder",
                "description": "Development projects",
                "subcategories": {
                    "Python": {
                        "icon": "folder",
                        "description": "Python projects"
                    },
                    "JavaScript": {
                        "icon": "folder",
                        "description": "JavaScript projects"
                    }
                }
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_hierarchy_info_extraction_for_add_project(self, mock_dialogs):
        """Test that hierarchy info is correctly extracted for add_project_action"""
        # Test case: nested subcategory
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Development:Python',
            'item_path': None,
            'is_project': False
        }

        # Execute
        self.handler.add_project_action(context)

        # Verify the pre_config has correct hierarchy info
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Development')
        self.assertEqual(pre_config['subcategory'], 'Python')

    @patch('dialogs.Dialogs')
    def test_add_project_from_different_hierarchy_levels(self, mock_dialogs):
        """Test add_project_action from different hierarchy levels"""
        test_cases = [
            # (hierarchy_path, expected_category, expected_subcategory)
            ('categories', None, None),
            ('cat:Development', 'Development', None),
            ('cat:Development:Python', 'Development', 'Python'),
        ]

        for hierarchy_path, expected_category, expected_subcategory in test_cases:
            # Reset mock
            mock_dialogs.reset_mock()

            context_type = ROOT_COLUMN if hierarchy_path == 'categories' else CHILD_COLUMN
            context = {
                'type': context_type,
                'hierarchy_path': hierarchy_path,
                'item_path': None,
                'is_project': False
            }

            # Execute
            self.handler.add_project_action(context)

            # Verify pre_config
            call_args = mock_dialogs.show_add_project_dialog.call_args
            pre_config = call_args[1]['pre_config']

            self.assertEqual(pre_config['category'], expected_category,
                           f"Failed for hierarchy_path: {hierarchy_path}")
            self.assertEqual(pre_config['subcategory'], expected_subcategory,
                           f"Failed for hierarchy_path: {hierarchy_path}")


if __name__ == '__main__':
    unittest.main()
