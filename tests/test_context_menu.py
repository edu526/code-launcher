#!/usr/bin/env python3
"""
Unit tests for ContextMenuHandler
Tests context detection and hierarchy path parsing
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from context_menu.handler import ContextMenuHandler
from context_menu.context_detector import (
    detect_context, get_hierarchy_info,
    ROOT_COLUMN, CHILD_COLUMN, CATEGORY_ITEM, PROJECT_ITEM
)
from context_menu.actions import (
    create_category_action, add_project_action, open_vscode_action,
    open_kiro_action, delete_category_action, rename_category_action,
    delete_project_action
)


class TestContextMenuHandler(unittest.TestCase):
    """Test cases for ContextMenuHandler class"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_init(self):
        """Test ContextMenuHandler initialization"""
        self.assertEqual(self.handler.column_browser, self.column_browser)
        self.assertEqual(self.handler.parent_window, self.parent_window)

    def test_detect_context_root_column_empty_area(self):
        """Test context detection for right-click on empty area of root column"""
        # Setup
        self.column_browser.current_path = "categories"
        self.column_browser.get_item_at_position = Mock(return_value=(None, None))
        self.column_browser.is_root_column = Mock(return_value=True)

        event = Mock()
        event.x = 100
        event.y = 100

        # Execute
        context = detect_context(self.column_browser, event)

        # Verify
        self.assertEqual(context['type'], ROOT_COLUMN)
        self.assertEqual(context['hierarchy_path'], "categories")
        self.assertIsNone(context['item_path'])
        self.assertFalse(context['is_project'])

    def test_detect_context_child_column_empty_area(self):
        """Test context detection for right-click on empty area of child column"""
        # Setup
        self.column_browser.current_path = "cat:Web"
        self.column_browser.get_item_at_position = Mock(return_value=(None, None))
        self.column_browser.is_root_column = Mock(return_value=False)

        event = Mock()
        event.x = 100
        event.y = 100

        # Execute
        context = detect_context(self.column_browser, event)

        # Verify
        self.assertEqual(context['type'], CHILD_COLUMN)
        self.assertEqual(context['hierarchy_path'], "cat:Web")
        self.assertIsNone(context['item_path'])
        self.assertFalse(context['is_project'])

    def test_detect_context_category_item(self):
        """Test context detection for right-click on category item"""
        # Setup
        self.column_browser.current_path = "categories"

        # Mock the tree model
        model = Mock()
        iter_mock = Mock()
        tree_path_mock = Mock()
        model.get_iter.return_value = iter_mock
        model.get_value.return_value = "cat:Web"

        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_model.return_value = model
        self.column_browser.get_item_at_position = Mock(return_value=(tree_path_mock, Mock()))

        event = Mock()
        event.x = 100
        event.y = 100

        # Execute
        context = detect_context(self.column_browser, event)

        # Verify
        self.assertEqual(context['type'], CATEGORY_ITEM)
        self.assertEqual(context['item_path'], "cat:Web")
        self.assertFalse(context['is_project'])

    def test_detect_context_project_item(self):
        """Test context detection for right-click on project item"""
        # Setup
        self.column_browser.current_path = "cat:Web"

        # Mock the tree model
        model = Mock()
        iter_mock = Mock()
        tree_path_mock = Mock()
        model.get_iter.return_value = iter_mock
        model.get_value.return_value = "/home/user/projects/my-project"

        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_model.return_value = model
        self.column_browser.get_item_at_position = Mock(return_value=(tree_path_mock, Mock()))

        event = Mock()
        event.x = 100
        event.y = 100

        # Execute
        context = detect_context(self.column_browser, event)

        # Verify
        self.assertEqual(context['type'], PROJECT_ITEM)
        self.assertEqual(context['item_path'], "/home/user/projects/my-project")
        self.assertTrue(context['is_project'])

    def test_get_hierarchy_info_root_level(self):
        """Test hierarchy info extraction for root level"""
        # Test with "categories"
        info = get_hierarchy_info("categories")
        self.assertEqual(info['level'], 0)
        self.assertIsNone(info['category'])
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "categories")

        # Test with None
        info = get_hierarchy_info(None)
        self.assertEqual(info['level'], 0)
        self.assertIsNone(info['category'])
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "")

    def test_get_hierarchy_info_first_level(self):
        """Test hierarchy info extraction for first level (category)"""
        info = get_hierarchy_info("cat:Web")
        self.assertEqual(info['level'], 1)
        self.assertEqual(info['category'], "Web")
        self.assertIsNone(info['subcategory_path'])
        self.assertEqual(info['full_path'], "cat:Web")

    def test_get_hierarchy_info_second_level(self):
        """Test hierarchy info extraction for second level (subcategory)"""
        info = get_hierarchy_info("cat:Web:Frontend")
        self.assertEqual(info['level'], 2)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend")
        self.assertEqual(info['full_path'], "cat:Web:Frontend")

    def test_get_hierarchy_info_deep_nesting(self):
        """Test hierarchy info extraction for deeply nested subcategories"""
        info = get_hierarchy_info("cat:Web:Frontend:React:Components")
        self.assertEqual(info['level'], 4)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend:React:Components")
        self.assertEqual(info['full_path'], "cat:Web:Frontend:React:Components")

    def test_get_hierarchy_info_projects_view(self):
        """Test hierarchy info extraction for projects view"""
        info = get_hierarchy_info("projects:cat:Web:Frontend")
        self.assertEqual(info['level'], 2)
        self.assertEqual(info['category'], "Web")
        self.assertEqual(info['subcategory_path'], "Frontend")


class TestContextTypeConstants(unittest.TestCase):
    """Test that context type constants are defined correctly"""

    def test_constants_defined(self):
        """Test that all context type constants are defined"""
        self.assertEqual(ROOT_COLUMN, "root_column")
        self.assertEqual(CHILD_COLUMN, "child_column")
        self.assertEqual(CATEGORY_ITEM, "category_item")
        self.assertEqual(PROJECT_ITEM, "project_item")


class TestCreateContextMenu(unittest.TestCase):
    """Test cases for create_context_menu method"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def _get_menu_item_labels(self, menu):
        """
        Helper to extract menu item labels from a Gtk.Menu

        Args:
            menu: Gtk.Menu instance

        Returns:
            List of menu item label strings
        """
        labels = []
        for item in menu.get_children():
            if isinstance(item, Gtk.MenuItem):
                labels.append(item.get_label())
        return labels

    def test_create_context_menu_root_column(self):
        """Test menu creation for root column context"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        menu = self.handler.create_context_menu(context)

        # Verify menu is created
        self.assertIsInstance(menu, Gtk.Menu)

        # Verify menu items
        labels = self._get_menu_item_labels(menu)
        self.assertEqual(len(labels), 2)
        self.assertIn("Create category", labels)
        self.assertIn("Add project", labels)

    def test_create_context_menu_child_column(self):
        """Test menu creation for child column context"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web',
            'item_path': None,
            'is_project': False
        }

        menu = self.handler.create_context_menu(context)

        # Verify menu is created
        self.assertIsInstance(menu, Gtk.Menu)

        # Verify menu items
        labels = self._get_menu_item_labels(menu)
        self.assertEqual(len(labels), 2)
        self.assertIn("Add subcategory", labels)
        self.assertIn("Add project", labels)

    def test_create_context_menu_category_item(self):
        """Test menu creation for category item context"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        menu = self.handler.create_context_menu(context)

        # Verify menu is created
        self.assertIsInstance(menu, Gtk.Menu)

        # Verify menu items
        labels = self._get_menu_item_labels(menu)
        self.assertEqual(len(labels), 2)
        self.assertIn("Add subcategory", labels)
        self.assertIn("Add project", labels)

    def test_create_context_menu_project_item(self):
        """Test menu creation for project item context"""
        context = {
            'type': PROJECT_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': '/home/user/projects/my-project',
            'is_project': True
        }

        menu = self.handler.create_context_menu(context)

        # Verify menu is created
        self.assertIsInstance(menu, Gtk.Menu)

        # Verify menu items
        labels = self._get_menu_item_labels(menu)
        self.assertEqual(len(labels), 1)
        self.assertIn("Open in VSCode", labels)

    def test_menu_item_callbacks_connected(self):
        """Test that menu items have callbacks connected"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Mock the action functions
        with patch('context_menu.actions.create_category_action') as mock_create, \
             patch('context_menu.actions.add_project_action') as mock_add:

            menu = self.handler.create_context_menu(context)

            # Get menu items
            items = menu.get_children()
            self.assertEqual(len(items), 2)

            # Activate first item (Create category)
            items[0].activate()
            mock_create.assert_called_once()

            # Activate second item (Add project)
            items[1].activate()
            mock_add.assert_called_once()

    def test_add_menu_item_helper(self):
        """Test the _add_menu_item helper method"""
        menu = Gtk.Menu()
        callback = Mock()

        self.handler._add_menu_item(menu, "Test Item", callback)

        # Verify item was added
        items = menu.get_children()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].get_label(), "Test Item")

        # Verify callback is connected
        items[0].activate()
        callback.assert_called_once()


class TestShowMenu(unittest.TestCase):
    """Test cases for show_menu method"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_show_menu_with_popup_at_pointer(self):
        """Test show_menu uses popup_at_pointer when available (GTK 3.22+)"""
        menu = Mock(spec=Gtk.Menu)
        menu.popup_at_pointer = Mock()

        event = Mock()
        event.button = 3
        event.time = 12345
        event.x = 100
        event.y = 200

        # Execute
        self.handler.show_menu(menu, event)

        # Verify popup_at_pointer was called with the event
        menu.popup_at_pointer.assert_called_once_with(event)

    def test_show_menu_with_legacy_popup(self):
        """Test show_menu falls back to legacy popup for older GTK versions"""
        menu = Mock(spec=Gtk.Menu)
        # Remove popup_at_pointer to simulate older GTK
        delattr(menu, 'popup_at_pointer')
        menu.popup = Mock()

        event = Mock()
        event.button = 3
        event.time = 12345
        event.x = 100
        event.y = 200

        # Execute
        self.handler.show_menu(menu, event)

        # Verify legacy popup was called with correct parameters
        menu.popup.assert_called_once_with(None, None, None, None, 3, 12345)

    def test_show_menu_handles_exception_gracefully(self):
        """Test show_menu handles exceptions without crashing"""
        menu = Mock(spec=Gtk.Menu)
        menu.popup_at_pointer = Mock(side_effect=Exception("Test error"))

        event = Mock()
        event.button = 3
        event.time = 12345
        event.x = 100
        event.y = 200

        # Execute - should not raise exception
        try:
            self.handler.show_menu(menu, event)
        except Exception as e:
            self.fail(f"show_menu raised exception: {e}")

    def test_show_menu_with_different_event_coordinates(self):
        """Test show_menu works with various event coordinates"""
        menu = Mock(spec=Gtk.Menu)
        menu.popup_at_pointer = Mock()

        # Test with different coordinates
        test_cases = [
            (0, 0),      # Top-left corner
            (1920, 1080), # Bottom-right (typical screen)
            (500, 300),   # Middle area
            (10, 10),     # Near edge
        ]

        for x, y in test_cases:
            event = Mock()
            event.button = 3
            event.time = 12345
            event.x = x
            event.y = y

            # Execute
            self.handler.show_menu(menu, event)

            # Verify popup_at_pointer was called
            self.assertTrue(menu.popup_at_pointer.called)
            menu.popup_at_pointer.reset_mock()

    def test_show_menu_with_different_button_values(self):
        """Test show_menu handles different mouse button values"""
        menu = Mock(spec=Gtk.Menu)
        # Remove popup_at_pointer to test legacy path
        delattr(menu, 'popup_at_pointer')
        menu.popup = Mock()

        # Test with button 3 (right-click)
        event = Mock()
        event.button = 3
        event.time = 12345
        event.x = 100
        event.y = 200

        self.handler.show_menu(menu, event)
        menu.popup.assert_called_with(None, None, None, None, 3, 12345)


class TestOnButtonPress(unittest.TestCase):
    """Test cases for on_button_press event handler"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_on_button_press_right_click(self):
        """Test on_button_press handles right-click (button 3)"""
        # Setup
        self.column_browser.current_path = "categories"
        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_path_at_pos.return_value = None

        # Mock the methods that will be called
        self.handler.detect_context = Mock(return_value={
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        })
        self.handler.create_context_menu = Mock(return_value=Mock(spec=Gtk.Menu))
        self.handler.show_menu = Mock()

        # Create event
        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100

        widget = Mock()

        # Execute
        result = self.handler.on_button_press(widget, event)

        # Verify
        self.assertTrue(result)  # Should return True to prevent default menu
        self.handler.detect_context.assert_called_once_with(event)
        self.handler.create_context_menu.assert_called_once()
        self.handler.show_menu.assert_called_once()

    def test_on_button_press_left_click(self):
        """Test on_button_press ignores left-click (button 1)"""
        # Create event
        event = Mock()
        event.button = 1  # Left-click

        widget = Mock()

        # Execute
        result = self.handler.on_button_press(widget, event)

        # Verify
        self.assertFalse(result)  # Should return False to allow other handlers

    def test_on_button_press_middle_click(self):
        """Test on_button_press ignores middle-click (button 2)"""
        # Create event
        event = Mock()
        event.button = 2  # Middle-click

        widget = Mock()

        # Execute
        result = self.handler.on_button_press(widget, event)

        # Verify
        self.assertFalse(result)  # Should return False to allow other handlers

    def test_on_button_press_error_handling(self):
        """Test on_button_press handles errors gracefully"""
        # Setup - make detect_context raise an exception
        self.handler.detect_context = Mock(side_effect=Exception("Test error"))

        # Create event
        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100

        widget = Mock()

        # Execute - should not raise exception
        try:
            result = self.handler.on_button_press(widget, event)
            # Should still return True to prevent default menu
            self.assertTrue(result)
        except Exception as e:
            self.fail(f"on_button_press raised exception: {e}")

    def test_on_button_press_prevents_default_menu(self):
        """Test on_button_press returns True to prevent default GTK menu"""
        # Setup
        self.column_browser.current_path = "categories"
        self.column_browser.treeview = Mock()
        self.column_browser.treeview.get_path_at_pos.return_value = None

        # Mock the methods
        self.handler.detect_context = Mock(return_value={
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        })
        self.handler.create_context_menu = Mock(return_value=Mock(spec=Gtk.Menu))
        self.handler.show_menu = Mock()

        # Create event
        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100

        widget = Mock()

        # Execute
        result = self.handler.on_button_press(widget, event)

        # Verify - returning True prevents default GTK context menu
        self.assertTrue(result)

    def test_on_button_press_calls_methods_in_order(self):
        """Test on_button_press calls methods in correct order"""
        # Setup
        call_order = []

        def mock_detect_context(event):
            call_order.append('detect_context')
            return {
                'type': ROOT_COLUMN,
                'hierarchy_path': 'categories',
                'item_path': None,
                'is_project': False
            }

        def mock_create_context_menu(context):
            call_order.append('create_context_menu')
            return Mock(spec=Gtk.Menu)

        def mock_show_menu(menu, event):
            call_order.append('show_menu')

        self.handler.detect_context = mock_detect_context
        self.handler.create_context_menu = mock_create_context_menu
        self.handler.show_menu = mock_show_menu

        # Create event
        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100

        widget = Mock()

        # Execute
        self.handler.on_button_press(widget, event)

        # Verify correct order
        self.assertEqual(call_order, ['detect_context', 'create_context_menu', 'show_menu'])

    def test_on_button_press_with_different_contexts(self):
        """Test on_button_press works with different context types"""
        # Test with different context types
        test_contexts = [
            {
                'type': ROOT_COLUMN,
                'hierarchy_path': 'categories',
                'item_path': None,
                'is_project': False
            },
            {
                'type': CHILD_COLUMN,
                'hierarchy_path': 'cat:Web',
                'item_path': None,
                'is_project': False
            },
            {
                'type': CATEGORY_ITEM,
                'hierarchy_path': 'categories',
                'item_path': 'cat:Web',
                'is_project': False
            },
            {
                'type': PROJECT_ITEM,
                'hierarchy_path': 'cat:Web',
                'item_path': '/home/user/project',
                'is_project': True
            }
        ]

        for context in test_contexts:
            # Setup
            self.handler.detect_context = Mock(return_value=context)
            self.handler.create_context_menu = Mock(return_value=Mock(spec=Gtk.Menu))
            self.handler.show_menu = Mock()

            # Create event
            event = Mock()
            event.button = 3  # Right-click
            event.x = 100
            event.y = 100

            widget = Mock()

            # Execute
            result = self.handler.on_button_press(widget, event)

            # Verify
            self.assertTrue(result)
            self.handler.detect_context.assert_called_once_with(event)
            self.handler.create_context_menu.assert_called_once_with(context)
            self.handler.show_menu.assert_called_once()


class TestCreateCategoryAction(unittest.TestCase):
    """Test cases for create_category_action method"""

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
                        "description": "Frontend projects",
                        "subcategories": {}
                    }
                }
            },
            "Mobile": {
                "icon": "folder",
                "description": "Mobile projects",
                "subcategories": {}
            }
        }
        self.parent_window.config = Mock()
        self.parent_window.reload_interface = Mock()

        # Mock column_browser methods
        self.column_browser.load_mixed_content = Mock()
        self.column_browser.current_path = "categories"

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_root_column(self, mock_dialog):
        """Test create_category_action for root column context"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify show_create_category_dialog was called
        mock_dialog.assert_called_once()

        # Verify the arguments
        call_args = mock_dialog.call_args
        self.assertEqual(call_args[0][0], self.parent_window)  # parent
        self.assertEqual(call_args[0][1], self.parent_window.categories)  # categories
        self.assertIsNotNone(call_args[0][2])  # callback

        # Verify pre_config
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['parent_category'])
        self.assertFalse(pre_config['force_subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'categories')

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_child_column_first_level(self, mock_dialog):
        """Test create_category_action for child column at first level"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify show_create_category_dialog was called
        mock_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['parent_category'], 'Web')
        self.assertTrue(pre_config['force_subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web')

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_child_column_nested(self, mock_dialog):
        """Test create_category_action for child column at nested level"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web:Frontend',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify Dialogs.show_create_category_dialog was called
        mock_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['parent_category'], 'Web:Frontend')
        self.assertTrue(pre_config['force_subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend')

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_category_item(self, mock_dialog):
        """Test create_category_action for category item context"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify Dialogs.show_create_category_dialog was called
        mock_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['parent_category'], 'Web')
        self.assertTrue(pre_config['force_subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web')

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_category_item_nested(self, mock_dialog):
        """Test create_category_action for nested category item"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': 'cat:Web:Frontend',
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify Dialogs.show_create_category_dialog was called
        mock_dialog.assert_called_once()

        # Verify pre_config
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertEqual(pre_config['parent_category'], 'Web:Frontend')
        self.assertTrue(pre_config['force_subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend')

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_callback_creates_main_category(self, mock_dialog):
        """Test that the callback creates a main category correctly"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Get the callback that was passed to the dialog
        call_args = mock_dialog.call_args
        callback = call_args[0][2]

        # Call the callback to create a new category
        callback("NewCategory", "New category description", "folder", None)

        # Verify the category was added
        self.assertIn("NewCategory", self.parent_window.categories)
        self.assertEqual(self.parent_window.categories["NewCategory"]["description"], "New category description")
        self.assertEqual(self.parent_window.categories["NewCategory"]["icon"], "folder")
        self.assertIn("subcategories", self.parent_window.categories["NewCategory"])

        # Verify save and column refresh were called
        self.parent_window.config.save_categories.assert_called_once_with(self.parent_window.categories)
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_callback_creates_subcategory(self, mock_dialog):
        """Test that the callback creates a subcategory correctly"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Get the callback that was passed to the dialog
        call_args = mock_dialog.call_args
        callback = call_args[0][2]

        # Call the callback to create a new subcategory
        callback("Backend", "Backend projects", "folder", "Web")

        # Verify the subcategory was added
        self.assertIn("Backend", self.parent_window.categories["Web"]["subcategories"])
        self.assertEqual(self.parent_window.categories["Web"]["subcategories"]["Backend"]["description"], "Backend projects")
        self.assertEqual(self.parent_window.categories["Web"]["subcategories"]["Backend"]["icon"], "folder")

        # Verify save and column refresh were called
        self.parent_window.config.save_categories.assert_called_once_with(self.parent_window.categories)
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_callback_creates_nested_subcategory(self, mock_dialog):
        """Test that the callback creates a nested subcategory correctly"""
        context = {
            'type': CHILD_COLUMN,
            'hierarchy_path': 'cat:Web:Frontend',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Get the callback that was passed to the dialog
        call_args = mock_dialog.call_args
        callback = call_args[0][2]

        # Call the callback to create a nested subcategory
        callback("React", "React projects", "folder", "Web:Frontend")

        # Verify the nested subcategory was added
        self.assertIn("React", self.parent_window.categories["Web"]["subcategories"]["Frontend"]["subcategories"])
        self.assertEqual(
            self.parent_window.categories["Web"]["subcategories"]["Frontend"]["subcategories"]["React"]["description"],
            "React projects"
        )

        # Verify save and column refresh were called
        self.parent_window.config.save_categories.assert_called_once_with(self.parent_window.categories)
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_callback_handles_existing_category(self, mock_dialog):
        """Test that the callback handles existing category gracefully"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Get the callback
        call_args = mock_dialog.call_args
        callback = call_args[0][2]

        # Try to create a category that already exists
        original_description = self.parent_window.categories["Web"]["description"]
        callback("Web", "Updated description", "folder", None)

        # Verify the category still exists and has subcategories dict
        self.assertIn("Web", self.parent_window.categories)
        self.assertIn("subcategories", self.parent_window.categories["Web"])

        # Verify save and column refresh were called
        self.parent_window.config.save_categories.assert_called_once()
        self.column_browser.load_mixed_content.assert_called_once()

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_with_invalid_context_type(self, mock_dialog):
        """Test create_category_action with invalid context type falls back gracefully"""
        context = {
            'type': 'invalid_type',
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify Dialogs.show_create_category_dialog was called with fallback config
        mock_dialog.assert_called_once()

        # Verify pre_config has fallback values
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['parent_category'])
        self.assertFalse(pre_config['force_subcategory'])

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_with_none_hierarchy_path(self, mock_dialog):
        """Test create_category_action handles None hierarchy_path"""
        context = {
            'type': ROOT_COLUMN,
            'hierarchy_path': None,
            'item_path': None,
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify it doesn't crash and calls the dialog
        mock_dialog.assert_called_once()

    @patch('src.dialogs.show_create_category_dialog')
    def test_create_category_action_with_empty_item_path(self, mock_dialog):
        """Test create_category_action handles empty item_path for category item"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': '',
            'is_project': False
        }

        # Execute
        create_category_action(context, self.column_browser, self.parent_window)

        # Verify it doesn't crash and calls the dialog
        mock_dialog.assert_called_once()

        # Verify pre_config handles empty item_path
        call_args = mock_dialog.call_args
        pre_config = call_args[1]['pre_config']
        self.assertIsNone(pre_config['parent_category'])


class TestOpenVSCodeAction(unittest.TestCase):
    """Test cases for open_vscode_action method"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_open_vscode_action_success(self):
        """Test open_vscode_action successfully opens project in VSCode"""
        # Setup
        context = {
            'type': PROJECT_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': '/home/user/projects/my-project',
            'is_project': True
        }

        # Mock parent_window.open_vscode_project to return True (success)
        self.parent_window.open_vscode_project = Mock(return_value=True)

        # Execute
        open_vscode_action(context, self.parent_window)

        # Verify open_vscode_project was called with correct path
        self.parent_window.open_vscode_project.assert_called_once_with('/home/user/projects/my-project')

    def test_open_vscode_action_failure(self):
        """Test open_vscode_action handles failure gracefully"""
        # Setup
        context = {
            'type': PROJECT_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': '/home/user/projects/my-project',
            'is_project': True
        }

        # Mock parent_window.open_vscode_project to return False (failure)
        self.parent_window.open_vscode_project = Mock(return_value=False)

        # Execute - should not raise exception
        try:
            open_vscode_action(context, self.parent_window)
        except Exception as e:
            self.fail(f"open_vscode_action raised exception: {e}")

        # Verify open_vscode_project was called
        self.parent_window.open_vscode_project.assert_called_once_with('/home/user/projects/my-project')

    def test_open_vscode_action_no_project_path(self):
        """Test open_vscode_action handles missing project path"""
        # Setup
        context = {
            'type': PROJECT_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': None,  # No project path
            'is_project': True
        }

        # Mock show_error_dialog
        self.handler.show_error_dialog = Mock()

        # Execute
        open_vscode_action(context, self.parent_window)

        # Verify error dialog was shown
        self.handler.show_error_dialog.assert_called_once()
        error_message = self.handler.show_error_dialog.call_args[0][0]
        self.assertIn("Project path not found", error_message)

    def test_open_vscode_action_exception_handling(self):
        """Test open_vscode_action handles exceptions gracefully"""
        # Setup
        context = {
            'type': PROJECT_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': '/home/user/projects/my-project',
            'is_project': True
        }

        # Mock parent_window.open_vscode_project to raise exception
        self.parent_window.open_vscode_project = Mock(side_effect=Exception("Test error"))

        # Mock show_error_dialog
        self.handler.show_error_dialog = Mock()

        # Execute - should not raise exception
        try:
            open_vscode_action(context, self.parent_window)
        except Exception as e:
            self.fail(f"open_vscode_action raised exception: {e}")

        # Verify error dialog was shown
        self.handler.show_error_dialog.assert_called_once()
        error_message = self.handler.show_error_dialog.call_args[0][0]
        self.assertIn("Error opening project in VSCode", error_message)

    def test_open_vscode_action_with_different_project_paths(self):
        """Test open_vscode_action works with various project path formats"""
        # Test with different project path formats
        test_paths = [
            '/home/user/projects/my-project',
            '/var/www/html/website',
            '~/projects/test-project',
            '/opt/apps/production-app',
        ]

        for project_path in test_paths:
            # Setup
            context = {
                'type': PROJECT_ITEM,
                'hierarchy_path': 'cat:Web',
                'item_path': project_path,
                'is_project': True
            }

            # Mock parent_window.open_vscode_project
            self.parent_window.open_vscode_project = Mock(return_value=True)

            # Execute
            open_vscode_action(context, self.parent_window)

            # Verify open_vscode_project was called with correct path
            self.parent_window.open_vscode_project.assert_called_with(project_path)


class TestShowErrorDialog(unittest.TestCase):
    """Test cases for show_error_dialog method"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.parent_window = Mock()
        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    @patch('context_menu.Gtk.MessageDialog')
    def test_show_error_dialog_displays_message(self, mock_dialog_class):
        """Test show_error_dialog creates and displays error dialog"""
        # Setup
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        # Execute
        self.handler.show_error_dialog("Test error message")

        # Verify dialog was created with correct parameters
        mock_dialog_class.assert_called_once()
        call_kwargs = mock_dialog_class.call_args[1]
        self.assertEqual(call_kwargs['transient_for'], self.parent_window)
        self.assertEqual(call_kwargs['message_type'], Gtk.MessageType.ERROR)
        self.assertEqual(call_kwargs['buttons'], Gtk.ButtonsType.OK)
        self.assertEqual(call_kwargs['text'], "Test error message")

        # Verify dialog was shown and destroyed
        mock_dialog.set_position.assert_called_once_with(Gtk.WindowPosition.CENTER_ON_PARENT)
        mock_dialog.run.assert_called_once()
        mock_dialog.destroy.assert_called_once()

    @patch('context_menu.Gtk.MessageDialog')
    def test_show_error_dialog_handles_exception(self, mock_dialog_class):
        """Test show_error_dialog handles exceptions gracefully"""
        # Setup - make dialog creation raise exception
        mock_dialog_class.side_effect = Exception("Test error")

        # Execute - should not raise exception
        try:
            self.handler.show_error_dialog("Test error message")
        except Exception as e:
            self.fail(f"show_error_dialog raised exception: {e}")

    @patch('context_menu.Gtk.MessageDialog')
    def test_show_error_dialog_with_different_messages(self, mock_dialog_class):
        """Test show_error_dialog works with various error messages"""
        # Setup
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        # Test with different error messages
        test_messages = [
            "Error: No se encontró la ruta del proyecto",
            "Error al abrir proyecto en VSCode: File not found",
            "Error: Permiso denegado",
            "Error: VSCode no está instalado",
        ]

        for message in test_messages:
            # Execute
            self.handler.show_error_dialog(message)

            # Verify dialog was created with correct message
            call_kwargs = mock_dialog_class.call_args[1]
            self.assertEqual(call_kwargs['text'], message)

            # Reset mock for next iteration
            mock_dialog_class.reset_mock()
            mock_dialog.reset_mock()


if __name__ == '__main__':
    unittest.main()

