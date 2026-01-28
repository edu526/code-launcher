#!/usr/bin/env python3
"""
Main window for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import subprocess
import logging

from src.core.config import ConfigManager
from src.ui.search_manager import SearchManager
from src.ui.keyboard_handler import KeyboardHandler
from src.ui.navigation_manager import NavigationManager
from utils import open_project_in_vscode

logger = logging.getLogger(__name__)


class FinderStyleWindow(Gtk.Window):
    """Main application window"""

    def __init__(self):
        super().__init__(title="Code Launcher")
        self.set_default_size(900, 500)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(0)

        # Set as normal window (not dialog) to allow proper focus
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)

        # Enable focus and urgency hints
        self.set_accept_focus(True)
        self.set_focus_on_map(True)
        self.set_urgency_hint(False)  # Don't use urgency by default

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
        self.files = self.config.load_files()

        # Load preferences
        preferences = self.config.load_preferences()
        self.default_editor = preferences.get("default_editor", "kiro")
        self.default_text_editor = preferences.get("default_text_editor", "gnome-text-editor")
        self.close_on_open = preferences.get("close_on_open", False)

        # Interface state
        self.columns = []
        self.selected_path = None

        # Initialize managers
        self.search_manager = SearchManager(self)
        self.keyboard_handler = KeyboardHandler(self)
        self.navigation_manager = NavigationManager(self)

        # Initialize terminal manager with graceful degradation
        self.terminal_manager = None
        self._initialize_terminal_manager()

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

    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        # Define target types for drag and drop
        targets = [
            Gtk.TargetEntry.new("text/uri-list", 0, 0)
        ]

        # Enable drag and drop on the columns container
        self.columns_box.drag_dest_set(
            Gtk.DestDefaults.ALL,
            targets,
            Gdk.DragAction.COPY
        )

        # Connect drag and drop signals
        self.columns_box.connect("drag-data-received", self._on_drag_data_received)
        self.columns_box.connect("drag-motion", self._on_drag_motion)

    def _on_drag_motion(self, widget, context, x, y, time):
        """Handle drag motion to show visual feedback"""
        Gdk.drag_status(context, Gdk.DragAction.COPY, time)
        return True

    def _get_drop_target_column(self, x, y):
        """Determine which column the drop occurred on"""
        try:
            # Get the column at the drop position
            for column in self.columns:
                allocation = column.get_allocation()
                if x >= allocation.x and x <= allocation.x + allocation.width:
                    return column
            # Default to first column if no match
            return self.columns[0] if self.columns else None
        except Exception as e:
            logger.error(f"Error determining drop target column: {e}")
            return None

    def _get_pre_config_from_column(self, column):
        """Extract pre_config from a column's current state"""
        if not column:
            return None

        try:
            current_path = getattr(column, 'current_path', None)
            if not current_path:
                return None

            # Parse the current path to extract category/subcategory
            if current_path.startswith('cat:'):
                parts = current_path[4:].split('/')
                if len(parts) == 1:
                    # Category only
                    return {'category': parts[0], 'subcategory': None}
                elif len(parts) >= 2:
                    # Category and subcategory
                    return {'category': parts[0], 'subcategory': parts[1]}

            return None
        except Exception as e:
            logger.error(f"Error extracting pre_config from column: {e}")
            return None

    def _on_drag_data_received(self, widget, context, x, y, data, info, time):
        """Handle dropped files or folders"""
        try:
            uris = data.get_uris()
            if not uris:
                logger.warning("No URIs received in drag and drop")
                Gtk.drag_finish(context, False, False, time)
                return

            logger.info(f"Received {len(uris)} items via drag and drop")

            # Determine which column received the drop
            target_column = self._get_drop_target_column(x, y)
            pre_config = self._get_pre_config_from_column(target_column)

            # Process each dropped item
            for uri in uris:
                # Convert URI to path
                if uri.startswith('file://'):
                    path = uri[7:]  # Remove 'file://' prefix
                    # Decode URL encoding
                    import urllib.parse
                    path = urllib.parse.unquote(path)

                    logger.info(f"Processing dropped item: {path}")

                    if os.path.isdir(path):
                        self._add_project_from_drop(path, pre_config)
                    elif os.path.isfile(path):
                        self._add_file_from_drop(path, pre_config)
                    else:
                        logger.warning(f"Dropped item is neither file nor directory: {path}")

            Gtk.drag_finish(context, True, False, time)

        except Exception as e:
            logger.error(f"Error handling drag and drop: {e}", exc_info=True)
            Gtk.drag_finish(context, False, False, time)

    def _add_project_from_drop(self, path, pre_config=None):
        """Add a project from a dropped folder"""
        from src.dialogs.project_dialog import show_add_project_dialog

        # Get project name from path
        project_name = os.path.basename(path)

        # Show dialog to confirm and select category
        def on_add_callback(name, project_info):
            try:
                self.projects[name] = project_info
                self.config.save_projects(self.projects)

                # Refresh only the affected column instead of reloading everything
                project_category = project_info.get('category')
                project_subcategory = project_info.get('subcategory')

                # Find the column that should be refreshed
                if not project_category:
                    # No category - refresh root column
                    if len(self.columns) > 0:
                        first_column = self.columns[0]
                        first_column.load_hierarchy_level(self.categories, None, self.projects, self.files)
                        logger.info(f"Refreshed root column for root-level project")
                else:
                    # Has category - find and refresh the appropriate column
                    for column in self.columns:
                        if hasattr(column, 'current_path') and column.current_path:
                            # Check if this column matches the project's category/subcategory
                            if project_subcategory:
                                # Check for exact match with subcategory
                                expected_path = f"cat:{project_category}:{project_subcategory}"
                                if column.current_path == expected_path:
                                    column.load_mixed_content(
                                        self.categories,
                                        column.current_path,
                                        self.projects,
                                        self.files
                                    )
                                    logger.info(f"Refreshed column for {expected_path}")
                                    break
                            else:
                                # Check for category match
                                expected_path = f"cat:{project_category}"
                                if column.current_path == expected_path:
                                    column.load_mixed_content(
                                        self.categories,
                                        column.current_path,
                                        self.projects,
                                        self.files
                                    )
                                    logger.info(f"Refreshed column for {expected_path}")
                                    break

                logger.info(f"Added project via drag and drop: {name}")
            except Exception as e:
                logger.error(f"Error saving dropped project: {e}", exc_info=True)

        show_add_project_dialog(
            self,
            self.categories,
            on_add_callback,
            pre_config=pre_config,
            default_name=project_name,
            default_path=path
        )

    def _add_file_from_drop(self, path, pre_config=None):
        """Add a file from a dropped file"""
        from src.dialogs.file_dialog import show_add_file_dialog

        # Get file name from path
        file_name = os.path.basename(path)

        # Show dialog to confirm and select category
        def on_add_callback(name, file_info):
            try:
                self.files[name] = file_info
                self.config.save_files(self.files)

                # Refresh only the affected column instead of reloading everything
                file_category = file_info.get('category')
                file_subcategory = file_info.get('subcategory')

                # Find the column that should be refreshed
                if not file_category:
                    # No category - refresh root column
                    if len(self.columns) > 0:
                        first_column = self.columns[0]
                        first_column.load_hierarchy_level(self.categories, None, self.projects, self.files)
                        logger.info(f"Refreshed root column for root-level file")
                else:
                    # Has category - find and refresh the appropriate column
                    for column in self.columns:
                        if hasattr(column, 'current_path') and column.current_path:
                            # Check if this column matches the file's category/subcategory
                            if file_subcategory:
                                # Check for exact match with subcategory
                                expected_path = f"cat:{file_category}:{file_subcategory}"
                                if column.current_path == expected_path:
                                    column.load_mixed_content(
                                        self.categories,
                                        column.current_path,
                                        self.projects,
                                        self.files
                                    )
                                    logger.info(f"Refreshed column for {expected_path}")
                                    break
                            else:
                                # Check for category match
                                expected_path = f"cat:{file_category}"
                                if column.current_path == expected_path:
                                    column.load_mixed_content(
                                        self.categories,
                                        column.current_path,
                                        self.projects,
                                        self.files
                                    )
                                    logger.info(f"Refreshed column for {expected_path}")
                                    break

                logger.info(f"Added file via drag and drop: {name}")
            except Exception as e:
                logger.error(f"Error saving dropped file: {e}", exc_info=True)

        show_add_file_dialog(
            self,
            self.categories,
            on_add_callback,
            pre_config=pre_config,
            default_name=file_name,
            default_path=path
        )

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

        # Option: Edit Files
        files_item = Gtk.MenuItem(label="Edit Files")
        files_item.connect("activate", self._on_edit_files)
        menu.append(files_item)

        # Option: Preferences
        pref_item = Gtk.MenuItem(label="Preferences")
        pref_item.connect("activate", self._on_preferences)
        menu.append(pref_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Option: Keyboard Shortcuts
        shortcuts_item = Gtk.MenuItem(label="Keyboard Shortcuts")
        shortcuts_item.connect("activate", self._on_shortcuts)
        menu.append(shortcuts_item)

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

    def _on_edit_files(self, menu_item):
        """Open files editor dialog"""
        from src.dialogs.config_dialog import show_files_dialog

        def on_save(new_files):
            self.files = new_files
            self.config.save_files(new_files)
            self.reload_interface()

        show_files_dialog(self, self.files, on_save)

    def _on_preferences(self, menu_item):
        """Open preferences dialog"""
        from src.dialogs.config_dialog import show_preferences_dialog

        # Pass terminal manager if available, None otherwise for graceful degradation
        terminal_manager = self.terminal_manager if self.has_terminal_support() else None
        show_preferences_dialog(self, self.config, terminal_manager)

    def _on_shortcuts(self, menu_item):
        """Open keyboard shortcuts dialog"""
        from src.dialogs.shortcuts_dialog import show_shortcuts_dialog
        show_shortcuts_dialog(self)

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
            # Find project name
            project_name = self._get_project_name(project_path)

            # Add to recents
            if project_name:
                self.config.add_recent(resolved_path, project_name, "project")

            subprocess.Popen(['code', resolved_path])
            # Close launcher if preference is enabled
            if self.close_on_open:
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
            # Find project name
            project_name = self._get_project_name(project_path)

            # Add to recents
            if project_name:
                self.config.add_recent(resolved_path, project_name, "project")

            subprocess.Popen(['kiro', resolved_path])
            # Close launcher if preference is enabled
            if self.close_on_open:
                self.destroy()
            return True
        except FileNotFoundError:
            print("Error: Kiro is not installed or not in PATH")
            return False
        except Exception as e:
            print(f"Error opening Kiro: {e}")
            return False

    def _get_project_name(self, project_path):
        """Get project name from path"""
        for name, info in self.projects.items():
            if isinstance(info, str):
                if info == project_path:
                    return name
            else:
                if info.get("path") == project_path:
                    return name
        return os.path.basename(project_path)

    def _get_file_name(self, file_path):
        """Get file name from path"""
        for name, info in self.files.items():
            if isinstance(info, str):
                if info == file_path:
                    return name
            else:
                if info.get("path") == file_path:
                    return name
        return os.path.basename(file_path)

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

    def _initialize_terminal_manager(self):
        """
        Initialize terminal manager with graceful degradation.

        This method attempts to initialize the terminal manager and handles
        any failures gracefully, ensuring the application continues normal
        operation even when terminal functionality is unavailable.
        """
        try:
            logger.info("Initializing terminal manager")

            # Import terminal manager
            from utils.terminal_manager import TerminalManager

            # Create terminal manager instance
            self.terminal_manager = TerminalManager(self.config)

            # Initialize terminal detection
            self.terminal_manager.initialize()

            # Check if any terminals were detected
            if self.terminal_manager.has_available_terminals():
                available_count = len(self.terminal_manager.get_available_terminals())
                logger.info(f"Terminal manager initialized successfully with {available_count} terminals")
            else:
                logger.warning("Terminal manager initialized but no terminals detected")
                logger.info("Terminal features will be hidden from the user interface")

        except ImportError as e:
            logger.error(f"Failed to import terminal manager: {e}")
            logger.info("Terminal functionality will be unavailable")
            self.terminal_manager = None

        except Exception as e:
            logger.error(f"Failed to initialize terminal manager: {e}")
            logger.info("Terminal functionality will be unavailable, application continuing normally")
            self.terminal_manager = None

    def has_terminal_support(self):
        """
        Check if terminal support is available.

        Returns:
            bool: True if terminal manager is available and has terminals, False otherwise
        """
        try:
            return (self.terminal_manager is not None and
                   self.terminal_manager.has_available_terminals())
        except Exception as e:
            logger.error(f"Error checking terminal support: {e}")
            return False
