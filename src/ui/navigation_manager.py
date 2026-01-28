#!/usr/bin/env python3
"""
Navigation and column management for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from src.ui.column_browser import ColumnBrowser


class NavigationManager:
    """Manages column navigation and hierarchy"""

    def __init__(self, window):
        """
        Initialize navigation manager

        Args:
            window: FinderStyleWindow instance
        """
        self.window = window

    def add_column(self, path=None, column_type="directory"):
        """
        Add a new column to the interface

        Args:
            path: Path for the column content
            column_type: Type of column (categories, hierarchy, mixed, projects, directory)

        Returns:
            ColumnBrowser instance
        """
        if column_type not in ["categories", "hierarchy", "mixed", "projects", "directory"]:
            raise ValueError(f"Invalid column_type: {column_type}")

        column = ColumnBrowser(self.on_column_selection, column_type, self.window)

        # Mapeo de tipos a métodos de carga
        loaders = {
            "categories": lambda: column.load_hierarchy_level(self.window.categories, None, self.window.projects, self.window.files),
            "hierarchy": lambda: column.load_hierarchy_level(self.window.categories, path, self.window.projects, self.window.files),
            "mixed": lambda: column.load_mixed_content(self.window.categories, path, self.window.projects, self.window.files),
            "projects": lambda: column.load_projects_at_level(path, self.window.projects),
            "directory": lambda: column.load_directory(path)
        }

        loaders[column_type]()
        self._pack_column(column)
        return column

    def _pack_column(self, column):
        """
        Pack and display a column

        Args:
            column: ColumnBrowser instance
        """
        self.window.columns.append(column)
        self.window.columns_box.pack_start(column, True, True, 1)
        column.show_all()

        # Ensure we always have 3 columns visible
        self._ensure_three_columns()

    def _ensure_three_columns(self):
        """Ensure there are always 3 columns visible (fill with empty ones if needed)"""
        # Don't add empty columns if we're in search or recent items mode
        if len(self.window.columns) > 0:
            first_column = self.window.columns[0]
            if hasattr(first_column, 'current_path'):
                # Skip if in search or recent items mode
                if first_column.current_path in ["search_results", "recent_items"]:
                    return

        while len(self.window.columns) < 3:
            # Create empty placeholder column
            empty_column = ColumnBrowser(self.on_column_selection, "empty", self.window)
            empty_column.store.clear()  # Keep it empty
            empty_column.current_path = "empty"
            self.window.columns.append(empty_column)
            self.window.columns_box.pack_start(empty_column, True, True, 1)
            empty_column.show_all()

    def on_column_selection(self, path, is_dir, source_column=None):
        """
        Handle column selection events

        Args:
            path: Selected path
            is_dir: Whether the selection is a directory
            source_column: The column that triggered this selection (optional)
        """
        self.window.selected_path = path

        # Determine what to do based on selection type
        if path and path.startswith("cat:"):
            self._handle_category_selection(path)
        elif path and path.startswith("categories"):
            # In categories view
            pass
        else:
            # It's a normal project or file - clear columns to the right
            self._clear_columns_after_selection(source_column)

    def _clear_columns_after_selection(self, source_column=None):
        """
        Clear content of columns to the right of the current selection

        Args:
            source_column: The column that triggered the selection (optional)
        """
        # Find which column has the selection
        selected_column_index = -1

        if source_column:
            # If we know the source column, find its index
            for i, column in enumerate(self.window.columns):
                if column == source_column:
                    selected_column_index = i
                    break
        else:
            # Otherwise, search for the column with selection
            for i, column in enumerate(self.window.columns):
                selection = column.treeview.get_selection()
                model, iter = selection.get_selected()
                if iter:
                    selected_column_index = i
                    break

        if selected_column_index >= 0:
            # Clear all columns after the selected one (but keep them visible)
            for i in range(selected_column_index + 1, len(self.window.columns)):
                if i < len(self.window.columns):  # Safety check
                    self.window.columns[i].store.clear()
                    if hasattr(self.window.columns[i], 'current_path'):
                        self.window.columns[i].current_path = "empty"

    def _handle_category_selection(self, hierarchy_path):
        """
        Handle category/subcategory selection

        Args:
            hierarchy_path: Hierarchy path (e.g., "cat:Web:Frontend")
        """
        # Parse the path to determine the level
        path_parts = hierarchy_path.split(":")
        if len(path_parts) < 2:
            return

        # Determine depth level
        depth_level = len(path_parts) - 1

        # Remove columns to the right of the selected level (but keep minimum 3)
        target_columns_count = max(depth_level + 1, 3)

        while len(self.window.columns) > target_columns_count:
            old_column = self.window.columns.pop()
            self.window.columns_box.remove(old_column)

        # Create or reload column for content
        if len(self.window.columns) == depth_level:
            # Create new mixed column
            mixed_column = self.add_column(hierarchy_path, "mixed")
            mixed_column.current_path = hierarchy_path
        else:
            # Reload existing column
            if len(self.window.columns) > 0 and len(self.window.columns) > depth_level:
                existing_column = self.window.columns[depth_level]
                existing_column.load_mixed_content(
                    self.window.categories,
                    hierarchy_path,
                    self.window.projects,
                    self.window.files
                )
                existing_column.current_path = hierarchy_path

        # Ensure we have 3 columns
        self._ensure_three_columns()

    def reload_interface(self):
        """Reload the entire interface"""
        # Clear columns
        for column in self.window.columns:
            self.window.columns_box.remove(column)
        self.window.columns.clear()

        # Reload configuration
        self.window.categories = self.window.config.load_categories()
        self.window.projects = self.window.config.load_projects()

        # Create first column with categories
        self.add_column(None, "categories")

        # _ensure_three_columns is called by add_column -> _pack_column

    def select_first_category(self):
        """Select the first category automatically and cascade to first subcategory if exists"""
        if self.window.columns and len(self.window.columns) > 0:
            first_column = self.window.columns[0]
            if first_column.current_path == "categories":
                # Select first item in first column
                first_iter = first_column.store.get_iter_first()
                if first_iter:
                    selection = first_column.treeview.get_selection()
                    selection.select_iter(first_iter)

                    # Get the path of first item
                    path = first_column.store.get_value(first_iter, 1)

                    # Trigger selection to create next column
                    self.on_column_selection(path, True, None)

                    # Schedule cascade selection for next column
                    GLib.timeout_add(50, self._cascade_select_first)
        return False

    def _cascade_select_first(self):
        """Cascade selection to first item in newly created column"""
        if len(self.window.columns) > 1:
            second_column = self.window.columns[1]

            # Check if this column has items
            first_iter = second_column.store.get_iter_first()
            if first_iter:
                # Check if first item is a category (not a project)
                path = second_column.store.get_value(first_iter, 1)

                # Only auto-select if it's a subcategory (starts with "cat:")
                if path and path.startswith("cat:"):
                    selection = second_column.treeview.get_selection()
                    selection.select_iter(first_iter)

                    # Trigger selection to potentially create next column
                    self.on_column_selection(path, True, None)

        return False
