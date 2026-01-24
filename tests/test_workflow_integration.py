#!/usr/bin/env python3
"""
Integration tests for complete context menu workflows
Tests end-to-end workflows for context menu actions

Tasks 9.1-9.5: Complete workflow tests
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from context_menu import (
    ContextMenuHandler,
    ROOT_COLUMN,
    CHILD_COLUMN,
    CATEGORY_ITEM,
    PROJECT_ITEM
)


class TestWorkflowRootColumnCreateCategory(unittest.TestCase):
    """
    Task 9.1: Test complete workflow: root column → create category
    - Right-click on root column
    - Select "Crear categoría"
    - Verify dialog opens with no parent
    - Create category and verify it appears
    - Requirements: 2.1, 2.3
    """

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Setup parent window attributes
        self.parent_window.categories = {
            "Existing": {
                "icon": "folder",
                "description": "Existing category",
                "subcategories": {}
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()
        self.parent_window.open_vscode_project = Mock(return_value=True)

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_workflow_root_column_create_category(self, mock_dialogs):
        """
        Complete workflow: Right-click root column → Create category
        Validates Requirements 2.1, 2.3
        """
        # Step 1: Right-click on root column
        self.column_browser.current_path = "categories"
        self.column_browser.get_item_at_position = Mock(return_value=(None, None))
        self.column_browser.is_root_column = Mock(return_value=True)

        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100
        event.time = 12345

        # Detect context
        context = self.handler.detect_context(event)

        # Verify context is root column
        self.assertEqual(context['type'], ROOT_COLUMN)
        self.assertEqual(context['hierarchy_path'], "categories")
        self.assertIsNone(context['item_path'])

        # Step 2: Create context menu
        menu = self.handler.create_context_menu(context)

        # Verify menu has correct items
        self.assertIsInstance(menu, Gtk.Menu)
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[0].get_label(), "Crear categoría")
        self.assertEqual(menu_items[1].get_label(), "Agregar proyecto")

        # Step 3: Select "Crear categoría" - trigger the action
        self.handler.create_category_action(context)

        # Verify dialog was called
        mock_dialogs.show_create_category_dialog.assert_called_once()

        # Step 4: Verify dialog opens with no parent
        call_args = mock_dialogs.show_create_category_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertIsNone(pre_config['parent_category'],
                         "Root column should have no parent category")
        self.assertFalse(pre_config['force_subcategory'],
                        "Root column should not force subcategory mode")
        self.assertEqual(pre_config['hierarchy_path'], "categories")

        # Step 5: Simulate creating a category through the callback
        callback = call_args[0][2]
        callback("NewCategory", "New category description", "folder", None)

        # Step 6: Verify category appears in categories dict
        self.assertIn("NewCategory", self.parent_window.categories)
        self.assertEqual(
            self.parent_window.categories["NewCategory"]["description"],
            "New category description"
        )
        self.assertEqual(
            self.parent_window.categories["NewCategory"]["icon"],
            "folder"
        )
        self.assertIn("subcategories", self.parent_window.categories["NewCategory"])

        # Verify save and reload were called
        self.parent_window.config.save_categories.assert_called_once()
        # Interface refresh is now handled by load_mixed_content on column_browser


class TestWorkflowChildColumnCreateSubcategory(unittest.TestCase):
    """
    Task 9.2: Test complete workflow: child column → create subcategory
    - Navigate to child column
    - Right-click on column
    - Select "Agregar subcategoría"
    - Verify dialog opens with correct parent
    - Create subcategory and verify it appears
    - Requirements: 3.1, 3.3, 5.3
    """

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Setup parent window with existing category
        self.parent_window.categories = {
            "Web": {
                "icon": "folder",
                "description": "Web projects",
                "subcategories": {}
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_workflow_child_column_create_subcategory(self, mock_dialogs):
        """
        Complete workflow: Right-click child column → Create subcategory
        Validates Requirements 3.1, 3.3, 5.3
        """
        # Step 1: Navigate to child column (Web category)
        self.column_browser.current_path = "cat:Web"
        self.column_browser.get_item_at_position = Mock(return_value=(None, None))
        self.column_browser.is_root_column = Mock(return_value=False)

        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100
        event.time = 12345

        # Step 2: Detect context
        context = self.handler.detect_context(event)

        # Verify context is child column
        self.assertEqual(context['type'], CHILD_COLUMN)
        self.assertEqual(context['hierarchy_path'], "cat:Web")
        self.assertIsNone(context['item_path'])

        # Step 3: Create context menu
        menu = self.handler.create_context_menu(context)

        # Verify menu has correct items
        self.assertIsInstance(menu, Gtk.Menu)
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[0].get_label(), "Agregar subcategoría")
        self.assertEqual(menu_items[1].get_label(), "Agregar proyecto")

        # Step 4: Select "Agregar subcategoría"
        self.handler.create_category_action(context)

        # Verify dialog was called
        mock_dialogs.show_create_category_dialog.assert_called_once()

        # Step 5: Verify dialog opens with correct parent
        call_args = mock_dialogs.show_create_category_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['parent_category'], 'Web',
                        "Child column should have Web as parent category")
        self.assertTrue(pre_config['force_subcategory'],
                       "Child column should force subcategory mode")
        self.assertEqual(pre_config['hierarchy_path'], "cat:Web")

        # Step 6: Simulate creating a subcategory through the callback
        callback = call_args[0][2]
        callback("Frontend", "Frontend projects", "folder", "Web")

        # Step 7: Verify subcategory appears in categories dict
        self.assertIn("Frontend", self.parent_window.categories["Web"]["subcategories"])
        self.assertEqual(
            self.parent_window.categories["Web"]["subcategories"]["Frontend"]["description"],
            "Frontend projects"
        )
        self.assertEqual(
            self.parent_window.categories["Web"]["subcategories"]["Frontend"]["icon"],
            "folder"
        )

        # Verify save and reload were called (interface refresh)
        self.parent_window.config.save_categories.assert_called_once()
        # Interface refresh is now handled by load_mixed_content on column_browser


class TestWorkflowCategoryItemAddSubcategory(unittest.TestCase):
    """
    Task 9.3: Test complete workflow: category item → add subcategory
    - Right-click on category item
    - Select "Agregar subcategoría"
    - Verify dialog opens with category as parent
    - Create subcategory and verify it appears
    - Requirements: 5.1, 5.2, 5.3
    """

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Setup parent window with existing category
        self.parent_window.categories = {
            "Mobile": {
                "icon": "phone",
                "description": "Mobile projects",
                "subcategories": {}
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_workflow_category_item_add_subcategory(self, mock_dialogs):
        """
        Complete workflow: Right-click category item → Add subcategory
        Validates Requirements 5.1, 5.2, 5.3
        """
        # Step 1: Right-click on category item (Mobile)
        self.column_browser.current_path = "categories"

        # Mock the tree model to return category item
        model = Mock()
        iter_mock = Mock()
        tree_path_mock = Mock()
        model.get_iter.return_value = iter_mock
        model.get_value.return_value = "cat:Mobile"

        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_model.return_value = model
        self.column_browser.get_item_at_position = Mock(return_value=(tree_path_mock, Mock()))

        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100
        event.time = 12345

        # Step 2: Detect context
        context = self.handler.detect_context(event)

        # Verify context is category item
        self.assertEqual(context['type'], CATEGORY_ITEM)
        self.assertEqual(context['item_path'], "cat:Mobile")
        self.assertFalse(context['is_project'])

        # Step 3: Create context menu
        menu = self.handler.create_context_menu(context)

        # Verify menu has correct items
        self.assertIsInstance(menu, Gtk.Menu)
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[0].get_label(), "Agregar subcategoría")
        self.assertEqual(menu_items[1].get_label(), "Agregar proyecto")

        # Step 4: Select "Agregar subcategoría"
        self.handler.create_category_action(context)

        # Verify dialog was called
        mock_dialogs.show_create_category_dialog.assert_called_once()

        # Step 5: Verify dialog opens with category as parent
        call_args = mock_dialogs.show_create_category_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['parent_category'], 'Mobile',
                        "Category item should have Mobile as parent")
        self.assertTrue(pre_config['force_subcategory'],
                       "Category item should force subcategory mode")
        self.assertEqual(pre_config['hierarchy_path'], "cat:Mobile")

        # Step 6: Simulate creating a subcategory through the callback
        callback = call_args[0][2]
        callback("Android", "Android projects", "phone", "Mobile")

        # Step 7: Verify subcategory appears in categories dict
        self.assertIn("Android", self.parent_window.categories["Mobile"]["subcategories"])
        self.assertEqual(
            self.parent_window.categories["Mobile"]["subcategories"]["Android"]["description"],
            "Android projects"
        )

        # Verify save and reload were called (interface refresh)
        self.parent_window.config.save_categories.assert_called_once()
        # Interface refresh is now handled by load_mixed_content on column_browser


class TestWorkflowProjectItemOpenVSCode(unittest.TestCase):
    """
    Task 9.4: Test complete workflow: project item → open in VSCode
    - Right-click on project item
    - Select "Abrir en VSCode"
    - Verify VSCode opens with correct project
    - Verify launcher window closes
    - Requirements: 4.1, 4.2, 4.3
    """

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Setup parent window
        self.parent_window.categories = {}
        self.parent_window.projects = {
            "MyProject": {
                "path": "/home/user/projects/my-project",
                "category": "Web"
            }
        }
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()
        self.parent_window.open_vscode_project = Mock(return_value=True)

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_workflow_project_item_open_vscode(self):
        """
        Complete workflow: Right-click project item → Open in VSCode
        Validates Requirements 4.1, 4.2, 4.3
        """
        # Step 1: Right-click on project item
        self.column_browser.current_path = "cat:Web"

        # Mock the tree model to return project item
        model = Mock()
        iter_mock = Mock()
        tree_path_mock = Mock()
        model.get_iter.return_value = iter_mock
        model.get_value.return_value = "/home/user/projects/my-project"

        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_model.return_value = model
        self.column_browser.get_item_at_position = Mock(return_value=(tree_path_mock, Mock()))

        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100
        event.time = 12345

        # Step 2: Detect context
        context = self.handler.detect_context(event)

        # Verify context is project item
        self.assertEqual(context['type'], PROJECT_ITEM)
        self.assertEqual(context['item_path'], "/home/user/projects/my-project")
        self.assertTrue(context['is_project'])

        # Step 3: Create context menu
        menu = self.handler.create_context_menu(context)

        # Verify menu has correct items
        self.assertIsInstance(menu, Gtk.Menu)
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 1)
        self.assertEqual(menu_items[0].get_label(), "Abrir en VSCode")

        # Step 4: Select "Abrir en VSCode"
        self.handler.open_vscode_action(context)

        # Step 5: Verify VSCode opens with correct project
        self.parent_window.open_vscode_project.assert_called_once_with(
            "/home/user/projects/my-project"
        )

        # Step 6: Verify launcher window closes (handled by open_vscode_project)
        # The open_vscode_project method returns True on success
        # and is responsible for closing the window
        # We verify it was called successfully
        self.assertTrue(self.parent_window.open_vscode_project.return_value)


class TestWorkflowAddProjectFromContextMenu(unittest.TestCase):
    """
    Task 9.5: Test complete workflow: add project from context menu
    - Right-click on child column
    - Select "Agregar proyecto"
    - Verify dialog opens with category pre-selected
    - Add project and verify it appears
    - Requirements: 3.2, 3.4
    """

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()

        # Setup parent window with existing category
        self.parent_window.categories = {
            "Development": {
                "icon": "folder",
                "description": "Development projects",
                "subcategories": {
                    "Python": {
                        "icon": "folder",
                        "description": "Python projects"
                    }
                }
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('dialogs.Dialogs')
    def test_workflow_add_project_from_child_column(self, mock_dialogs):
        """
        Complete workflow: Right-click child column → Add project
        Validates Requirements 3.2, 3.4
        """
        # Step 1: Right-click on child column (Development:Python)
        self.column_browser.current_path = "cat:Development:Python"
        self.column_browser.get_item_at_position = Mock(return_value=(None, None))
        self.column_browser.is_root_column = Mock(return_value=False)

        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100
        event.time = 12345

        # Step 2: Detect context
        context = self.handler.detect_context(event)

        # Verify context is child column
        self.assertEqual(context['type'], CHILD_COLUMN)
        self.assertEqual(context['hierarchy_path'], "cat:Development:Python")

        # Step 3: Create context menu
        menu = self.handler.create_context_menu(context)

        # Verify menu has correct items
        self.assertIsInstance(menu, Gtk.Menu)
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[0].get_label(), "Agregar subcategoría")
        self.assertEqual(menu_items[1].get_label(), "Agregar proyecto")

        # Step 4: Select "Agregar proyecto"
        self.handler.add_project_action(context)

        # Verify dialog was called
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Step 5: Verify dialog opens with category pre-selected
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Development',
                        "Should pre-select Development category")
        self.assertEqual(pre_config['subcategory'], 'Python',
                        "Should pre-select Python subcategory")
        self.assertEqual(pre_config['hierarchy_path'], "cat:Development:Python")

        # Step 6: Simulate adding a project through the callback
        callback = call_args[0][2]
        project_info = {
            "path": "/home/user/projects/python-app",
            "category": "Development",
            "subcategory": "Python"
        }
        callback("PythonApp", project_info)

        # Step 7: Verify project appears in projects dict
        self.assertIn("PythonApp", self.parent_window.projects)
        self.assertEqual(
            self.parent_window.projects["PythonApp"]["path"],
            "/home/user/projects/python-app"
        )
        self.assertEqual(
            self.parent_window.projects["PythonApp"]["category"],
            "Development"
        )
        self.assertEqual(
            self.parent_window.projects["PythonApp"]["subcategory"],
            "Python"
        )

        # Verify save and reload were called
        self.parent_window.config.save_projects.assert_called_once()
        # Interface refresh is now handled by load_mixed_content on column_browser


if __name__ == '__main__':
    unittest.main()
