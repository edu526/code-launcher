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
            "categories": lambda: column.load_hierarchy_level(self.window.categories, None),
            "hierarchy": lambda: column.load_hierarchy_level(self.window.categories, path),
            "mixed": lambda: column.load_mixed_content(self.window.categories, path, self.window.projects),
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

    def on_column_selection(self, path, is_dir):
        """
        Handle column selection events

        Args:
            path: Selected path
            is_dir: Whether the selection is a directory
        """
        self.window.selected_path = path

        # Determine what to do based on selection type
        if path and path.startswith("cat:"):
            self._handle_category_selection(path)
        elif path and path.startswith("categories"):
            # In categories view
            pass
        else:
            # It's a normal project or directory - don't expand further
            pass

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

        # Remove columns to the right of the selected level
        target_columns_count = depth_level + 1

        while len(self.window.columns) > target_columns_count:
            old_column = self.window.columns.pop()
            self.window.columns_box.remove(old_column)

        # Create or reload column for content
        if len(self.window.columns) == target_columns_count - 1:
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
                    self.window.projects
                )
                existing_column.current_path = hierarchy_path

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
                    self.on_column_selection(path, True)

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
                    self.on_column_selection(path, True)

        return False
