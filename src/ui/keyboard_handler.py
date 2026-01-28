#!/usr/bin/env python3
"""
Keyboard shortcuts handler for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk
import logging

logger = logging.getLogger(__name__)


class KeyboardHandler:
    """Manages keyboard shortcuts"""

    def __init__(self, window):
        """
        Initialize keyboard handler

        Args:
            window: FinderStyleWindow instance
        """
        self.window = window
        self.last_focused_column_index = None  # Remember which column we came from when going to search
        self.column_selections = {}  # Store last selection for each column index

    def _update_breadcrumb_trail(self):
        """Update the visual breadcrumb trail across all columns"""
        # Clear all breadcrumb markings first
        for column in self.window.columns:
            column.clear_breadcrumb_trail()

        # Find which column currently has focus
        focused_column_index = None
        for i, column in enumerate(self.window.columns):
            if column.treeview.has_focus():
                focused_column_index = i
                break

        # Only mark breadcrumb trail in columns BEFORE the focused one
        if focused_column_index is not None:
            for i in range(focused_column_index):
                if i in self.column_selections:
                    try:
                        path = self.column_selections[i]
                        column = self.window.columns[i]
                        iter = column.store.get_iter(path)
                        if iter:
                            item_path = column.store.get_value(iter, 1)
                            column.mark_breadcrumb_item(item_path)
                    except:
                        pass

    def on_key_press(self, widget, event):
        """
        Handle keyboard shortcuts

        Args:
            widget: GTK widget
            event: Gdk.EventKey

        Returns:
            True if event was handled, False otherwise
        """
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK

        # ESC to close
        if event.keyval == Gdk.KEY_Escape:
            self.window.destroy()
            return True

        # Enter to open selected item
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._open_selected_item()
            return True

        # Ctrl+O to open selected item
        if ctrl and event.keyval == Gdk.KEY_o:
            self._open_selected_item()
            return True

        # Ctrl+F to focus search
        if ctrl and event.keyval == Gdk.KEY_f:
            if hasattr(self.window, 'search_entry'):
                self.window.search_entry.grab_focus()
            return True

        # Ctrl+N to create new category
        if ctrl and event.keyval == Gdk.KEY_n:
            self._create_new_category()
            return True

        # Ctrl+P to add project
        if ctrl and event.keyval == Gdk.KEY_p:
            self._add_project()
            return True

        # Ctrl+D to toggle favorite
        if ctrl and event.keyval == Gdk.KEY_d:
            self._toggle_favorite()
            return True

        # Ctrl+R to show recents
        if ctrl and event.keyval == Gdk.KEY_r:
            self._show_recents()
            return True

        # Arrow keys for navigation
        if event.keyval == Gdk.KEY_Left:
            self._navigate_left()
            return True

        if event.keyval == Gdk.KEY_Right:
            self._navigate_right()
            return True

        if event.keyval == Gdk.KEY_Up:
            self._navigate_up()
            return True

        if event.keyval == Gdk.KEY_Down:
            self._navigate_down()
            return True

        # Number keys 1-9 to jump to items
        if event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_9:
            index = event.keyval - Gdk.KEY_1
            self._select_item_by_index(index)
            return True

        return False

    def _open_selected_item(self):
        """Open the currently selected item"""
        if not self.window.columns:
            return

        # Find the last column with a selection
        for column in reversed(self.window.columns):
            selected_path = column.get_selected_path()
            if selected_path:
                # Get the icon to determine type
                selection = column.treeview.get_selection()
                model, iter = selection.get_selected()
                if iter:
                    icon = model.get_value(iter, 3)

                    if selected_path.startswith("cat:"):
                        # It's a category
                        # If in search/recent mode, navigate to it
                        if column.current_path in ["search_results", "recent_items"]:
                            # Clear search
                            if hasattr(self.window, 'search_entry'):
                                self.window.search_entry.set_text("")

                            # Reload normal interface
                            self.window.reload_interface()

                            # Navigate to selected category
                            from gi.repository import GLib
                            GLib.idle_add(column._navigate_to_category, selected_path)
                        # Otherwise just return (normal navigation handles it)
                        return
                    elif icon == "text-x-generic":
                        # It's a file
                        from utils.text_editor_utils import open_file_in_editor
                        text_editor = getattr(self.window, 'default_text_editor', 'gnome-text-editor')
                        success = open_file_in_editor(selected_path, text_editor)

                        if success:
                            # Add to recents
                            file_name = self.window._get_file_name(selected_path)
                            if file_name:
                                self.window.config.add_recent(selected_path, file_name, "file")

                        if self.window.close_on_open:
                            self.window.destroy()
                    else:
                        # It's a project
                        default_editor = getattr(self.window, 'default_editor', 'kiro')
                        if default_editor == "vscode":
                            self.window.open_vscode_project(selected_path)
                        else:
                            self.window.open_kiro_project(selected_path)
                return

    def _create_new_category(self):
        """Create a new category"""
        from src.dialogs import show_create_category_dialog

        def on_create(name, description, icon, parent_category):
            if parent_category:
                parts = parent_category.split(":")
                current_level = self.window.categories
                for i, part in enumerate(parts[:-1]):
                    if part in current_level:
                        if "subcategories" not in current_level[part]:
                            current_level[part]["subcategories"] = {}
                        current_level = current_level[part]["subcategories"]

                parent_name = parts[-1]
                if parent_name in current_level:
                    if "subcategories" not in current_level[parent_name]:
                        current_level[parent_name]["subcategories"] = {}
                    current_level[parent_name]["subcategories"][name] = {
                        "description": description,
                        "icon": icon
                    }
            else:
                self.window.categories[name] = {
                    "description": description,
                    "icon": icon,
                    "subcategories": {}
                }

            self.window.config.save_categories(self.window.categories)
            self.window.reload_interface()

        show_create_category_dialog(self.window, self.window.categories, on_create)

    def _add_project(self):
        """Add a new project"""
        from src.dialogs import show_add_project_dialog

        def on_add(name, project_info):
            self.window.projects[name] = project_info
            self.window.config.save_projects(self.window.projects)
            self.window.reload_interface()

        show_add_project_dialog(self.window, self.window.categories, on_add)

    def _toggle_favorite(self):
        """Toggle favorite status of selected item"""
        if not self.window.columns:
            return

        for column in reversed(self.window.columns):
            selected_path = column.get_selected_path()
            if selected_path:
                selection = column.treeview.get_selection()
                model, iter = selection.get_selected()
                if iter:
                    icon = model.get_value(iter, 3)

                    # Determine item type
                    if selected_path.startswith("cat:"):
                        item_type = "category"
                    elif icon == "text-x-generic":
                        item_type = "file"
                    else:
                        item_type = "project"

                    is_fav = self.window.config.toggle_favorite(selected_path, item_type)
                    status = "added to" if is_fav else "removed from"
                    logger.info(f"Item {status} favorites: {selected_path}")

                    # Refresh the column to show star icon
                    current_path = column.current_path

                    # Check if we're in the root categories view or a nested view
                    if current_path is None or current_path == "categories":
                        # Root level - use load_hierarchy_level with None
                        column.load_hierarchy_level(
                            self.window.categories,
                            None,
                            self.window.projects,
                            self.window.files
                        )
                    elif current_path and current_path.startswith("cat:"):
                        # We're in a category view - use load_mixed_content
                        column.load_mixed_content(
                            self.window.categories,
                            current_path,
                            self.window.projects,
                            self.window.files
                        )
                    else:
                        # Fallback
                        if hasattr(column, 'load_mixed_content'):
                            column.load_mixed_content(
                                self.window.categories,
                                column.current_path,
                                self.window.projects,
                                self.window.files
                            )
                        elif hasattr(column, 'load_hierarchy_level'):
                            column.load_hierarchy_level(
                                self.window.categories,
                                column.current_path,
                                self.window.projects,
                                self.window.files
                            )
                return

    def _show_recents(self):
        """Show recent items in search"""
        if hasattr(self.window, 'search_entry'):
            self.window.search_entry.set_text("@recent")
            self.window.search_entry.grab_focus()

    def _save_current_selection(self, column_index):
        """Save the current selection for a column"""
        if column_index < len(self.window.columns):
            column = self.window.columns[column_index]
            selection = column.treeview.get_selection()
            model, iter = selection.get_selected()
            if iter:
                path = model.get_path(iter)
                self.column_selections[column_index] = path
                # Update breadcrumb trail after saving
                self._update_breadcrumb_trail()

    def _restore_selection(self, column_index):
        """Restore the saved selection for a column"""
        if column_index < len(self.window.columns):
            column = self.window.columns[column_index]

            # Try to restore saved selection
            if column_index in self.column_selections:
                try:
                    saved_path = self.column_selections[column_index]
                    selection = column.treeview.get_selection()
                    selection.select_path(saved_path)
                    column.treeview.set_cursor(saved_path, None, False)
                    column.treeview.scroll_to_cell(saved_path, None, False, 0, 0)
                    # Update breadcrumb trail after restoring
                    self._update_breadcrumb_trail()
                    return True
                except:
                    pass

            # If no saved selection or it failed, select first item
            selection = column.treeview.get_selection()
            first_iter = column.store.get_iter_first()
            if first_iter:
                path = column.store.get_path(first_iter)
                selection.select_iter(first_iter)
                column.treeview.set_cursor(path, None, False)
                column.treeview.scroll_to_cell(path, None, False, 0, 0)
                return True

            return False

    def _navigate_left(self):
        """Navigate to previous column"""
        if len(self.window.columns) > 1:
            # Focus previous column
            for i, column in enumerate(self.window.columns):
                if column.treeview.has_focus() and i > 0:
                    # Save current selection before leaving
                    self._save_current_selection(i)

                    prev_column = self.window.columns[i-1]
                    prev_column.treeview.grab_focus()

                    # Restore previous selection
                    self._restore_selection(i-1)
                    return

    def _navigate_right(self):
        """Navigate to next column"""
        if len(self.window.columns) > 1:
            # Focus next column
            for i, column in enumerate(self.window.columns):
                if column.treeview.has_focus() and i < len(self.window.columns) - 1:
                    next_column = self.window.columns[i+1]

                    # Check if next column is empty
                    if not next_column.store.get_iter_first():
                        # Column is empty, don't navigate
                        return

                    # Save current selection before leaving
                    self._save_current_selection(i)

                    next_column.treeview.grab_focus()

                    # Restore next column selection
                    self._restore_selection(i+1)
                    return

    def _navigate_up(self):
        """Navigate up in current column or to search if at top"""
        # Check if search entry has focus
        if hasattr(self.window, 'search_entry') and self.window.search_entry.has_focus():
            # Don't do anything, let search handle it
            return

        # Check if we're in a column
        focused_column = None
        focused_column_index = None
        for i, column in enumerate(self.window.columns):
            if column.treeview.has_focus():
                focused_column = column
                focused_column_index = i
                break

        if focused_column:
            selection = focused_column.treeview.get_selection()
            model, iter = selection.get_selected()

            if iter:
                # Check if we're at the top
                path = model.get_path(iter)
                if path.get_indices()[0] == 0:
                    # At the top, move to search and remember this column and item
                    self.last_focused_column_index = focused_column_index
                    self._save_current_selection(focused_column_index)
                    if hasattr(self.window, 'search_entry'):
                        self.window.search_entry.grab_focus()
                        # Position cursor at end of text
                        self.window.search_entry.set_position(-1)
                    return

                # Move to previous item
                if path.get_indices()[0] > 0:
                    prev_path = Gtk.TreePath.new_from_indices([path.get_indices()[0] - 1])
                    selection.select_path(prev_path)
                    focused_column.treeview.set_cursor(prev_path, None, False)
                    focused_column.treeview.scroll_to_cell(prev_path, None, False, 0, 0)
            else:
                # No selection, select first item
                first_iter = model.get_iter_first()
                if first_iter:
                    path = model.get_path(first_iter)
                    selection.select_iter(first_iter)
                    focused_column.treeview.set_cursor(path, None, False)
                    focused_column.treeview.scroll_to_cell(path, None, False, 0, 0)

    def _navigate_down(self):
        """Navigate down in current column or from search to first column"""
        # Check if search entry has focus
        if hasattr(self.window, 'search_entry') and self.window.search_entry.has_focus():
            # Move focus to the column we came from, or first column if none remembered
            if self.window.columns:
                # Use remembered column index, or default to first column
                target_index = self.last_focused_column_index if self.last_focused_column_index is not None else 0

                # Make sure the index is valid
                if target_index >= len(self.window.columns):
                    target_index = 0

                target_column = self.window.columns[target_index]

                # Check if target column is empty
                if not target_column.store.get_iter_first():
                    # Column is empty, don't navigate
                    return

                target_column.treeview.grab_focus()

                # Restore the saved selection for this column
                self._restore_selection(target_index)
            return

        # Check if we're in a column
        focused_column = None
        for column in self.window.columns:
            if column.treeview.has_focus():
                focused_column = column
                break

        if focused_column:
            selection = focused_column.treeview.get_selection()
            model, iter = selection.get_selected()

            if iter:
                # Move to next item
                next_iter = model.iter_next(iter)
                if next_iter:
                    next_path = model.get_path(next_iter)
                    selection.select_path(next_path)
                    focused_column.treeview.set_cursor(next_path, None, False)
                    focused_column.treeview.scroll_to_cell(next_path, None, False, 0, 0)
            else:
                # No selection, select first item
                first_iter = model.get_iter_first()
                if first_iter:
                    path = model.get_path(first_iter)
                    selection.select_iter(first_iter)
                    focused_column.treeview.set_cursor(path, None, False)
                    focused_column.treeview.scroll_to_cell(path, None, False, 0, 0)

    def _select_item_by_index(self, index):
        """Select item by index (0-8) in focused column"""
        for column in self.window.columns:
            if column.treeview.has_focus():
                model = column.store
                iter = model.get_iter_first()
                current_index = 0

                while iter and current_index < index:
                    iter = model.iter_next(iter)
                    current_index += 1

                if iter:
                    selection = column.treeview.get_selection()
                    selection.select_iter(iter)
                    path = model.get_path(iter)
                    column.treeview.scroll_to_cell(path, None, False, 0, 0)
                return
