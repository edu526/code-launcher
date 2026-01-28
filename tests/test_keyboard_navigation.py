#!/usr/bin/env python3
"""
Test keyboard navigation improvements
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.keyboard_handler import KeyboardHandler


class TestKeyboardNavigation(unittest.TestCase):
    """Test keyboard navigation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.window = Mock()
        self.window.columns = []
        self.window.search_entry = Mock()
        self.handler = KeyboardHandler(self.window)

    def test_navigate_up_from_top_goes_to_search(self):
        """Test that up arrow from top of column goes to search"""
        # Setup: column has focus with first item selected
        mock_column = Mock()
        mock_treeview = Mock()
        mock_selection = Mock()
        mock_store = Mock()
        mock_iter = Mock()
        mock_path = Mock()

        mock_column.treeview = mock_treeview
        mock_treeview.has_focus.return_value = True
        mock_treeview.get_selection.return_value = mock_selection
        mock_selection.get_selected.return_value = (mock_store, mock_iter)
        mock_store.get_path.return_value = mock_path
        mock_path.get_indices.return_value = [0]  # First item (index 0)

        self.window.columns = [mock_column]
        self.window.search_entry.has_focus.return_value = False

        # Execute
        self.handler._navigate_up()

        # Verify: focus moved to search
        self.window.search_entry.grab_focus.assert_called_once()
        self.window.search_entry.set_position.assert_called_once_with(-1)

    def test_navigate_down_from_search_to_column(self):
        """Test that down arrow moves from search to first column"""
        # Setup: search has focus
        self.window.search_entry.has_focus.return_value = True

        # Create mock column
        mock_column = Mock()
        mock_treeview = Mock()
        mock_selection = Mock()
        mock_store = Mock()
        mock_iter = Mock()

        mock_column.treeview = mock_treeview
        mock_treeview.get_selection.return_value = mock_selection
        mock_selection.get_selected.return_value = (mock_store, None)  # No selection
        mock_column.store = mock_store
        mock_store.get_iter_first.return_value = mock_iter
        mock_store.get_path.return_value = Mock()

        self.window.columns = [mock_column]

        # Execute
        self.handler._navigate_down()

        # Verify: focus moved to first column
        mock_treeview.grab_focus.assert_called_once()
        mock_selection.select_iter.assert_called_once_with(mock_iter)

    def test_navigate_up_selects_first_if_no_selection(self):
        """Test that up arrow selects first item if nothing selected"""
        # Setup: column has focus but no selection
        mock_column = Mock()
        mock_treeview = Mock()
        mock_selection = Mock()
        mock_store = Mock()
        mock_iter = Mock()

        mock_column.treeview = mock_treeview
        mock_treeview.has_focus.return_value = True
        mock_treeview.get_selection.return_value = mock_selection
        mock_selection.get_selected.return_value = (mock_store, None)  # No selection
        mock_store.get_iter_first.return_value = mock_iter
        mock_store.get_path.return_value = Mock()

        self.window.columns = [mock_column]
        self.window.search_entry.has_focus.return_value = False

        # Execute
        self.handler._navigate_up()

        # Verify: first item selected
        mock_selection.select_iter.assert_called_once_with(mock_iter)

    def test_navigate_down_selects_first_if_no_selection(self):
        """Test that down arrow selects first item if nothing selected"""
        # Setup: column has focus but no selection
        mock_column = Mock()
        mock_treeview = Mock()
        mock_selection = Mock()
        mock_store = Mock()
        mock_iter = Mock()

        mock_column.treeview = mock_treeview
        mock_treeview.has_focus.return_value = True
        mock_treeview.get_selection.return_value = mock_selection
        mock_selection.get_selected.return_value = (mock_store, None)  # No selection
        mock_store.get_iter_first.return_value = mock_iter
        mock_store.get_path.return_value = Mock()

        self.window.columns = [mock_column]
        self.window.search_entry.has_focus.return_value = False

        # Execute
        self.handler._navigate_down()

        # Verify: first item selected
        mock_selection.select_iter.assert_called_once_with(mock_iter)

    def test_navigate_right_selects_first_if_no_selection(self):
        """Test that right arrow selects first item in next column if nothing selected"""
        # Setup: two columns, first has focus
        mock_column1 = Mock()
        mock_column2 = Mock()

        mock_treeview1 = Mock()
        mock_treeview2 = Mock()
        mock_selection2 = Mock()
        mock_store2 = Mock()
        mock_iter2 = Mock()

        mock_column1.treeview = mock_treeview1
        mock_column2.treeview = mock_treeview2

        mock_treeview1.has_focus.return_value = True
        mock_treeview2.has_focus.return_value = False
        mock_treeview2.get_selection.return_value = mock_selection2
        mock_selection2.get_selected.return_value = (mock_store2, None)  # No selection
        mock_column2.store = mock_store2
        mock_store2.get_iter_first.return_value = mock_iter2

        self.window.columns = [mock_column1, mock_column2]

        # Execute
        self.handler._navigate_right()

        # Verify: focus moved and first item selected
        mock_treeview2.grab_focus.assert_called_once()
        mock_selection2.select_iter.assert_called_once_with(mock_iter2)


if __name__ == '__main__':
    unittest.main()
