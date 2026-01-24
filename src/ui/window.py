#!/usr/bin/env python3
"""
Main window for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import subprocess

from src.core.config import ConfigManager
from src.ui.search_manager import SearchManager
from src.ui.keyboard_handler import KeyboardHandler
from src.ui.navigation_manager import NavigationManager
from utils import open_project_in_vscode


class FinderStyleWindow(Gtk.Window):
    """Main application window"""

    def __init__(self):
        super().__init__(title="Code Launcher")
        self.set_default_size(900, 500)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(0)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        # Configure icon
        try:
            self.set_icon_name("code")
        except:
            pass

        # Center when shown
        self.connect("show", self.on_show_center)

        # Initialize configuration
        self.config = ConfigManager()
        self.categories = self.config.load_categories()
        self.projects = self.config.load_projects()

        # Load preferences
        preferences = self.config.load_preferences()
        self.default_editor = preferences.get("default_editor", "kiro")

        # Interface state
        self.columns = []
        self.selected_path = None

        # Initialize managers
        self.search_manager = SearchManager(self)
        self.keyboard_handler = KeyboardHandler(self)
        self.navigation_manager = NavigationManager(self)

        # Create UI
        self.setup_ui()

        # Keyboard shortcuts
        self.connect("key-press-event", self.keyboard_handler.on_key_press)

    def setup_ui(self):
        """Configure the user interface"""
        # Main layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Header bar
        self._setup_header()

        # Search bar
        self._setup_search_bar(vbox)

        # Container for columns
        self._setup_columns_container(vbox)

        # Create first column with categories
        self.navigation_manager.add_column(None, "categories")

        # Automatically select the first category
        GLib.timeout_add(100, self.navigation_manager.select_first_category)

    def _setup_header(self):
        """Setup header bar with buttons"""
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Code Launcher")
        header.set_subtitle("Navigate and open projects by categories")

        # Configuration button
        config_btn = Gtk.Button()
        config_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.BUTTON)
        config_btn.set_image(config_icon)
        config_btn.set_tooltip_text("Configure categories and projects")
        config_btn.connect("clicked", self.on_config_clicked)
        header.pack_end(config_btn)

        self.set_titlebar(header)

    def _setup_search_bar(self, vbox):
        """Setup search bar"""
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        search_box.set_margin_start(10)
        search_box.set_margin_end(10)
        search_box.set_margin_top(10)
        search_box.set_margin_bottom(5)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search projects...")
        self.search_entry.connect("search-changed", self.search_manager.on_search_changed)

        search_box.pack_start(self.search_entry, True, True, 0)

        vbox.pack_start(search_box, False, False, 0)

    def _setup_columns_container(self, vbox):
        """Setup columns container"""
        self.columns_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.columns_box.set_homogeneous(False)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.add(self.columns_box)

        vbox.pack_start(scroll, True, True, 0)

    def on_show_center(self, widget):
        """Center window when shown"""
        GLib.timeout_add(50, self.center_window)

    def center_window(self):
        """Center window on screen"""
        try:
            display = Gdk.Display.get_default()
            monitor = display.get_monitor(0)
            geometry = monitor.get_geometry()
            screen_width = geometry.width
            screen_height = geometry.height
            window_width, window_height = self.get_size()

            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            self.move(x, y)
        except:
            pass
        return False

    def add_column(self, path=None, column_type="directory"):
        """Delegate to navigation manager"""
        return self.navigation_manager.add_column(path, column_type)

    def reload_interface(self):
        """Delegate to navigation manager"""
        self.navigation_manager.reload_interface()

    def on_config_clicked(self, button):
        """Show configuration menu"""
        menu = Gtk.Menu()

        # Option: Edit Categories
        cat_item = Gtk.MenuItem(label="Edit Categories")
        cat_item.connect("activate", self._on_edit_categories)
        menu.append(cat_item)

        # Option: Edit Projects
        proj_item = Gtk.MenuItem(label="Edit Projects")
        proj_item.connect("activate", self._on_edit_projects)
        menu.append(proj_item)

        # Option: Preferences
        pref_item = Gtk.MenuItem(label="Preferences")
        pref_item.connect("activate", self._on_preferences)
        menu.append(pref_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Option: View Logs
        logs_item = Gtk.MenuItem(label="View Logs")
        logs_item.connect("activate", self._on_view_logs)
        menu.append(logs_item)

        menu.show_all()
        menu.popup_at_widget(button, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)

    def _on_edit_categories(self, menu_item):
        """Open categories editor dialog"""
        from src.dialogs.config_dialog import show_categories_dialog

        def on_save(new_categories):
            self.categories = new_categories
            self.config.save_categories(new_categories)
            self.reload_interface()

        show_categories_dialog(self, self.categories, on_save)

    def _on_edit_projects(self, menu_item):
        """Open projects editor dialog"""
        from src.dialogs.config_dialog import show_projects_dialog

        def on_save(new_projects):
            self.projects = new_projects
            self.config.save_projects(new_projects)
            self.reload_interface()

        show_projects_dialog(self, self.projects, on_save)

    def _on_preferences(self, menu_item):
        """Open preferences dialog"""
        from src.dialogs.config_dialog import show_preferences_dialog
        show_preferences_dialog(self, self.config)

    def _on_view_logs(self, menu_item):
        """Open logs viewer dialog"""
        from src.dialogs.config_dialog import show_logs_dialog
        show_logs_dialog(self)

    def open_vscode_project(self, project_path):
        """Open project in VSCode"""
        if not self._is_project_path(project_path):
            return False

        resolved_path = self._resolve_project_path(project_path)
        if not resolved_path:
            print(f"Error: Project '{project_path}' not found")
            return False

        try:
            subprocess.Popen(['code', resolved_path])
            self.destroy()
            return True
        except Exception as e:
            print(f"Error opening VSCode: {e}")
            return False

    def open_kiro_project(self, project_path):
        """Open project in Kiro"""
        if not self._is_project_path(project_path):
            return False

        resolved_path = self._resolve_project_path(project_path)
        if not resolved_path:
            print(f"Error: Project '{project_path}' not found")
            return False

        try:
            subprocess.Popen(['kiro', resolved_path])
            self.destroy()
            return True
        except FileNotFoundError:
            print("Error: Kiro is not installed or not in PATH")
            return False
        except Exception as e:
            print(f"Error opening Kiro: {e}")
            return False
            return False

    def _is_project_path(self, path):
        """Validate if path is a valid project"""
        if (path.startswith("/") or
            path.startswith("~/") or
            (":" not in path and not path.startswith("cat"))):
            return True
        return False

    def _resolve_project_path(self, selected_path):
        """Resolve real project path from configuration"""
        if os.path.exists(selected_path):
            return selected_path

        for project_name, project_info in self.projects.items():
            if isinstance(project_info, str):
                if project_info == selected_path:
                    return project_info
            else:
                if project_info.get("path", "") == selected_path:
                    return project_info.get("path", "")

        return None
