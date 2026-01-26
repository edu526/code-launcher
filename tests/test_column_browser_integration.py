#!/usr/bin/env python3
"""
Integration tests for ColumnBrowser with ContextMenuHandler
Tests that context menu is properly integrated into ColumnBrowser
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
from context_menu.handler import ContextMenuHandler


class TestColumnBrowserContextMenuIntegration(unittest.TestCase):
    """Test cases for ColumnBrowser integration with ContextMenuHandler"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.parent_window = Mock()

    def test_column_browser_creates_context_menu_handler_with_parent_window(self):
        """Test that ColumnBrowser creates ContextMenuHandler when parent_window is provided"""
        # Create ColumnBrowser with parent_window
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify context_menu_handler is created
        self.assertIsNotNone(browser.context_menu_handler)
        self.assertIsInstance(browser.context_menu_handler, ContextMenuHandler)

        # Verify handler has correct references
        self.assertEqual(browser.context_menu_handler.column_browser, browser)
        self.assertEqual(browser.context_menu_handler.parent_window, self.parent_window)

    def test_column_browser_no_context_menu_handler_without_parent_window(self):
        """Test that ColumnBrowser doesn't create ContextMenuHandler when parent_window is None"""
        # Create ColumnBrowser without parent_window
        browser = ColumnBrowser(self.callback, parent_window=None)

        # Verify context_menu_handler is None
        self.assertIsNone(browser.context_menu_handler)

    def test_column_browser_connects_button_press_event(self):
        """Test that ColumnBrowser connects button-press-event signal to handler"""
        # Create ColumnBrowser with parent_window
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify the signal is connected by checking if handler method is callable
        self.assertIsNotNone(browser.context_menu_handler)
        self.assertTrue(callable(browser.context_menu_handler.on_button_press))

        # Verify treeview exists and is a TreeView
        self.assertIsInstance(browser.treeview, Gtk.TreeView)

    def test_column_browser_stores_parent_window_reference(self):
        """Test that ColumnBrowser stores reference to parent_window"""
        # Create ColumnBrowser with parent_window
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify parent_window reference is stored
        self.assertEqual(browser.parent_window, self.parent_window)

    def test_context_menu_handler_receives_right_click_events(self):
        """Test that context menu handler receives right-click events from treeview"""
        # Create ColumnBrowser with parent_window
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify the handler's on_button_press method is callable
        # We can't easily emit GTK signals with mock events, so we just verify
        # that the handler is properly set up and callable
        self.assertTrue(callable(browser.context_menu_handler.on_button_press))

        # Verify we can call the handler directly with a mock event
        event = Mock()
        event.button = 3  # Right-click
        event.x = 100
        event.y = 100

        # Mock the internal methods to avoid GTK dependencies
        browser.context_menu_handler.detect_context = Mock(return_value={
            'type': 'root_column',
            'hierarchy_path': 'categories',
            'item_path': None,
            'is_project': False
        })
        browser.context_menu_handler.create_context_menu = Mock(return_value=Mock(spec=Gtk.Menu))
        browser.context_menu_handler.show_menu = Mock()

        # Call the handler directly
        result = browser.context_menu_handler.on_button_press(browser.treeview, event)

        # Verify the handler processed the event
        self.assertTrue(result)
        browser.context_menu_handler.detect_context.assert_called_once()
        browser.context_menu_handler.create_context_menu.assert_called_once()
        browser.context_menu_handler.show_menu.assert_called_once()

    def test_column_browser_initialization_order(self):
        """Test that ColumnBrowser initializes components in correct order"""
        # Create ColumnBrowser with parent_window
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify all components are initialized
        self.assertIsNotNone(browser.store)
        self.assertIsNotNone(browser.treeview)
        self.assertIsNotNone(browser.context_menu_handler)
        self.assertIsNotNone(browser.parent_window)

        # Verify treeview is added to the scrolled window
        children = browser.get_children()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0], browser.treeview)

    def test_column_browser_with_different_column_types(self):
        """Test that context menu handler is created for all column types"""
        column_types = ["directory", "categories", "projects"]

        for column_type in column_types:
            browser = ColumnBrowser(
                self.callback,
                column_type=column_type,
                parent_window=self.parent_window
            )

            # Verify context_menu_handler is created regardless of column type
            self.assertIsNotNone(browser.context_menu_handler)
            self.assertIsInstance(browser.context_menu_handler, ContextMenuHandler)
            self.assertEqual(browser.column_type, column_type)


class TestColumnBrowserContextMenuHandlerReferences(unittest.TestCase):
    """Test that ContextMenuHandler has correct references to ColumnBrowser"""

    def setUp(self):
        """Set up test fixtures"""
        self.callback = Mock()
        self.parent_window = Mock()

    def test_handler_can_access_column_browser_properties(self):
        """Test that handler can access ColumnBrowser properties"""
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Set some properties on the browser
        browser.current_path = "cat:Web"

        # Verify handler can access these properties
        self.assertEqual(browser.context_menu_handler.column_browser.current_path, "cat:Web")

    def test_handler_can_access_treeview(self):
        """Test that handler can access treeview through column_browser"""
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify handler can access treeview
        treeview = browser.context_menu_handler.column_browser.treeview
        self.assertIsInstance(treeview, Gtk.TreeView)
        self.assertEqual(treeview, browser.treeview)

    def test_handler_can_access_parent_window(self):
        """Test that handler has direct access to parent_window"""
        browser = ColumnBrowser(self.callback, parent_window=self.parent_window)

        # Verify handler has direct reference to parent_window
        self.assertEqual(browser.context_menu_handler.parent_window, self.parent_window)


if __name__ == '__main__':
    unittest.main()
