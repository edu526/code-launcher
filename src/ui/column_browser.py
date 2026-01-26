#!/usr/bin/env python3
"""
Finder-style column browser module
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GLib
import os
from src.context_menu.handler import ContextMenuHandler

class ColumnBrowser(Gtk.ScrolledWindow):
    """Finder-style individual column widget"""
    def __init__(self, callback, column_type="directory", parent_window=None):
        super().__init__()
        self.callback = callback
        self.parent_window = parent_window  # Reference to main window
        self.current_path = None
        self.column_type = column_type  # "directory", "categories", "projects"

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_min_content_width(200)
        self.set_shadow_type(Gtk.ShadowType.IN)

        # Item list
        self.store = Gtk.ListStore(str, str, bool, str)  # display_name, full_path, is_dir, icon_name
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_headers_visible(False)
        self.treeview.set_enable_search(False)

        # Column with icon and name
        column = Gtk.TreeViewColumn()

        # Icon renderer
        icon_renderer = Gtk.CellRendererPixbuf()
        column.pack_start(icon_renderer, False)
        column.set_cell_data_func(icon_renderer, self.icon_data_func)

        # Text renderer
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
        column.pack_start(text_renderer, True)
        column.add_attribute(text_renderer, "text", 0)

        self.treeview.append_column(column)

        # Selection
        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_selection_changed)

        # Double click
        self.treeview.connect("row-activated", self.on_row_activated)

        # Context menu setup
        self.context_menu_handler = None
        if parent_window:
            self.context_menu_handler = ContextMenuHandler(self, parent_window)
            self.treeview.connect("button-press-event", self.context_menu_handler.on_button_press)

        self.add(self.treeview)

    def icon_data_func(self, column, cell, model, iter, data):
        """Assign icon based on type"""
        icon_name = model.get_value(iter, 3)
        cell.set_property("icon-name", icon_name)

    def on_selection_changed(self, selection):
        """When an item is selected"""
        model, iter = selection.get_selected()
        if iter:
            path = model.get_value(iter, 1)
            self.callback(path, True)

    def on_row_activated(self, treeview, path, column):
        """Double click on an item"""
        model = treeview.get_model()
        iter = model.get_iter(path)
        full_path = model.get_value(iter, 1)

        # If it's a category (starts with "cat:"), navigate to it
        if full_path and full_path.startswith("cat:"):
            # Exit search mode and navigate to category
            if self.parent_window:
                # Clear search
                if hasattr(self.parent_window, 'search_entry'):
                    self.parent_window.search_entry.set_text("")

                # Reload normal interface
                self.parent_window.reload_interface()

                # Navigate to selected category
                # Use GLib.idle_add to ensure interface reloaded first
                GLib.idle_add(self._navigate_to_category, full_path)
        else:
            # It's a project - open with default editor
            if self.parent_window:
                default_editor = getattr(self.parent_window, 'default_editor', 'kiro')
                if default_editor == "vscode":
                    self.parent_window.open_vscode_project(full_path)
                else:
                    self.parent_window.open_kiro_project(full_path)

    def _navigate_to_category(self, category_path):
        """
        Navigate to a specific category after interface reload

        Args:
            category_path: Category path (e.g., "cat:Web:Frontend")
        """
        # Parse category path
        parts = category_path.split(":")[1:]  # Remove "cat:" prefix

        if not parts:
            return False

        # Navigate level by level
        current_path = None
        for i, part in enumerate(parts):
            if i == 0:
                # First level - select in first column
                current_path = f"cat:{part}"
            else:
                # Nested levels
                current_path = f"{current_path}:{part}"

            # Find corresponding column
            if i < len(self.parent_window.columns):
                column = self.parent_window.columns[i]

                # Find item in column
                iter = column.store.get_iter_first()
                while iter:
                    item_path = column.store.get_value(iter, 1)
                    if item_path == current_path:
                        # Select this item
                        selection = column.treeview.get_selection()
                        selection.select_iter(iter)

                        # Trigger selection event
                        self.parent_window.navigation_manager.on_column_selection(current_path, True)
                        break
                    iter = column.store.iter_next(iter)

        return False



    def load_directory(self, path):
        """Load directory contents - only show directories"""
        self.store.clear()
        self.current_path = path

        if not path or not os.path.exists(path):
            return

        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                # Skip hidden files
                if item.startswith('.'):
                    continue

                # Only show directories
                if not os.path.isdir(item_path):
                    continue

                items.append((item, item_path))

            # Sort alphabetically
            items.sort(key=lambda x: x[0].lower())

            for display_name, full_path in items:
                self.store.append([display_name, full_path, True, "folder"])

        except PermissionError:
            pass

    def load_categories(self, categories):
        """Load only main categories in column"""
        self.store.clear()
        self.current_path = "categories"

        # Sort categories alphabetically
        sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())

        for category_name, category_info in sorted_categories:
            icon_name = category_info.get("icon", "folder")
            self.store.append([category_name, f"category:{category_name}", True, icon_name])

    def load_hierarchy_level(self, categories, hierarchy_path=None):
        """Load a specific level of the hierarchy"""
        self.store.clear()

        if hierarchy_path is None:
            # Root level: show main categories
            self.current_path = "categories"

            sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())
            for category_name, category_info in sorted_categories:
                icon_name = category_info.get("icon", "folder")
                self.store.append([category_name, f"cat:{category_name}", True, icon_name])
        else:
            # Nested level: parse path
            parts = hierarchy_path.split(":")[1:]  # Ignore first "cat"

            if len(parts) == 1:
                # Second level: subcategories of main category
                category_name = parts[0]
                self.current_path = f"cat:{category_name}"

                if category_name in categories:
                    cat_info = categories[category_name]

                    # Load subcategories
                    subcategories = cat_info.get("subcategories", {})
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                    for sub_name, sub_info in sorted_subcats:
                        sub_icon = sub_info.get("icon", "folder")
                        self.store.append([sub_name, f"cat:{category_name}:{sub_name}", True, sub_icon])
            else:
                # Deeper levels: nested subcategories
                current_categories = categories
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:  # Not the last element
                        if part in current_categories:
                            current_categories = current_categories[part].get("subcategories", {})
                        else:
                            current_categories = {}
                            break
                    else:  # Last element
                        if part in current_categories:
                            subcat_info = current_categories[part]
                            subcategories = subcat_info.get("subcategories", {})
                            sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                            for sub_name, sub_info in sorted_subcats:
                                sub_icon = sub_info.get("icon", "folder")
                                full_path = f"cat:{':'.join(parts)}:{sub_name}"
                                self.store.append([sub_name, full_path, True, sub_icon])

        self.current_path = hierarchy_path or "categories"

    def load_projects_at_level(self, hierarchy_path, projects):
        """Load projects corresponding to current hierarchy level"""
        self.store.clear()
        self.current_path = f"projects:{hierarchy_path}"

        # Parse hierarchy path
        if not hierarchy_path or hierarchy_path == "categories":
            # Projects without category (root)
            category_name = None
            subcategory_path = None
        else:
            parts = hierarchy_path.split(":")[1:]  # Ignore first "cat"
            if len(parts) == 1:
                category_name = parts[0]
                subcategory_path = None
            else:
                category_name = parts[0]
                subcategory_path = ":".join(parts[1:])

        # Filter projects
        category_projects = []
        for project_name, project_info in projects.items():
            if isinstance(project_info, str):
                project_path = project_info
                project_category = None
                project_subcategory = None
            else:
                project_path = project_info.get("path", "")
                project_category = project_info.get("category", None)
                project_subcategory = project_info.get("subcategory", None)

            # Filter by hierarchy
            if category_name:
                if project_category == category_name:
                    if subcategory_path:
                        # Check if project subcategory matches current path
                        if project_subcategory:
                            project_sub_path = project_subcategory
                            if subcategory_path == project_sub_path or project_sub_path.startswith(subcategory_path + ":"):
                                category_projects.append((project_name, project_path))
                    else:
                        # If no subcategory specified, show projects without subcategory
                        if not project_subcategory:
                            category_projects.append((project_name, project_path))
            else:
                # Show projects without category
                if not project_category:
                    category_projects.append((project_name, project_path))

        # Sort projects alphabetically
        category_projects.sort(key=lambda x: x[0].lower())

        for project_name, project_path in category_projects:
            self.store.append([project_name, project_path, True, "code"])



    def load_mixed_content(self, categories, hierarchy_path, projects):
        """Load subcategories and projects together in same column"""
        self.store.clear()
        self.current_path = hierarchy_path

        # Collect subcategories
        subcategories_list = []

        if not hierarchy_path or hierarchy_path == "categories":
            # Load subcategories of main categories
            sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())

            for category_name, category_info in sorted_categories:
                subcategories = category_info.get("subcategories", {})
                if subcategories:
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                    for sub_name, sub_info in sorted_subcats:
                        sub_icon = sub_info.get("icon", "folder")
                        sub_path = f"cat:{category_name}:{sub_name}"
                        subcategories_list.append((sub_name, sub_path, sub_icon))
        else:
            # Load nested subcategories
            parts = hierarchy_path.split(":")[1:]  # Ignore first "cat"
            current_categories = categories

            # Navigate to current level
            for i, part in enumerate(parts):
                if part in current_categories:
                    if i == len(parts) - 1:  # Last level
                        subcategories = current_categories[part].get("subcategories", {})
                        if subcategories:
                            sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                            for sub_name, sub_info in sorted_subcats:
                                sub_icon = sub_info.get("icon", "folder")
                                full_path = f"cat:{':'.join(parts)}:{sub_name}"
                                subcategories_list.append((sub_name, full_path, sub_icon))
                    else:
                        current_categories = current_categories[part].get("subcategories", {})

        # Collect projects at current level
        if not hierarchy_path or hierarchy_path == "categories":
            # Projects without category
            category_name = None
            subcategory_path = None
        else:
            parts = hierarchy_path.split(":")[1:]
            if len(parts) == 1:
                category_name = parts[0]
                subcategory_path = None
            else:
                category_name = parts[0]
                subcategory_path = ":".join(parts[1:])

        # Filter and collect projects
        category_projects = []
        for project_name, project_info in projects.items():
            if isinstance(project_info, str):
                project_path = project_info
                project_category = None
                project_subcategory = None
            else:
                project_path = project_info.get("path", "")
                project_category = project_info.get("category", None)
                project_subcategory = project_info.get("subcategory", None)

            # Check if project belongs to current level
            belongs_to_level = False
            if category_name:
                if project_category == category_name:
                    if subcategory_path:
                        if project_subcategory:
                            project_sub_path = project_subcategory
                            if subcategory_path == project_sub_path or project_sub_path.startswith(subcategory_path + ":"):
                                belongs_to_level = True
                    else:
                        # If no subcategory specified, show projects without subcategory
                        if not project_subcategory:
                            belongs_to_level = True
            else:
                # Show projects without category
                if not project_category:
                    belongs_to_level = True

            if belongs_to_level:
                category_projects.append((project_name, project_path))

        # Sort projects alphabetically
        category_projects.sort(key=lambda x: x[0].lower())

        # Add subcategories FIRST (prioritized at top)
        for sub_name, sub_path, sub_icon in subcategories_list:
            self.store.append([sub_name, sub_path, True, sub_icon])

        # Then add projects (below subcategories)
        for project_name, project_path in category_projects:
            self.store.append([project_name, project_path, True, "code"])

    def get_selected_path(self):
        """Get currently selected path"""
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            return model.get_value(iter, 1)
        return None

    def select_first_item(self):
        """Select first item in list"""
        first_iter = self.store.get_iter_first()
        if first_iter:
            selection = self.treeview.get_selection()
            selection.select_iter(first_iter)

            # Manually trigger selection event
            path = self.store.get_value(first_iter, 1)
            self.callback(path, True)

    def get_item_at_position(self, x, y):
        """
        Get the item (if any) at the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of (TreePath, TreeViewColumn) or (None, None)
        """
        path_info = self.treeview.get_path_at_pos(int(x), int(y))
        if path_info is not None:
            tree_path, column, cell_x, cell_y = path_info
            return (tree_path, column)
        return (None, None)

    def is_root_column(self):
        """
        Check if this column is the root categories column

        Returns:
            True if current_path is "categories" or None
        """
        return self.current_path is None or self.current_path == "categories"

    def get_hierarchy_info(self):
        """
        Extract hierarchy information from current_path

        Returns:
            Dictionary with:
            {
                'level': int,  # 0 for root, 1+ for nested
                'category': str | None,
                'subcategory_path': str | None,
                'full_path': str
            }
        """
        hierarchy_info = {
            'level': 0,
            'category': None,
            'subcategory_path': None,
            'full_path': self.current_path or ""
        }

        current_path = self.current_path

        if not current_path or current_path == "categories":
            # Root level
            hierarchy_info['level'] = 0
            return hierarchy_info

        # Parse the hierarchy path
        if current_path.startswith("cat:"):
            parts = current_path.split(":")[1:]  # Remove "cat:" prefix
            hierarchy_info['level'] = len(parts)

            if len(parts) >= 1:
                hierarchy_info['category'] = parts[0]

            if len(parts) > 1:
                hierarchy_info['subcategory_path'] = ":".join(parts[1:])

        elif current_path.startswith("projects:"):
            # Projects view - extract the category path
            cat_path = current_path.split(":", 1)[1]
            if cat_path.startswith("cat:"):
                parts = cat_path.split(":")[1:]
                hierarchy_info['level'] = len(parts)
                if len(parts) >= 1:
                    hierarchy_info['category'] = parts[0]
                if len(parts) > 1:
                    hierarchy_info['subcategory_path'] = ":".join(parts[1:])

        return hierarchy_info