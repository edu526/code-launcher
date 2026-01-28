#!/usr/bin/env python3
"""
Context Menu Handler for Finder-style Column Browser
Manages right-click context menus based on column and item context
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import logging

from .context_detector import (
    detect_context,
    ROOT_COLUMN,
    CHILD_COLUMN,
    CATEGORY_ITEM,
    PROJECT_ITEM,
    FILE_ITEM
)
from .actions import (
    create_category_action,
    add_project_action,
    add_file_action,
    open_vscode_action,
    open_kiro_action,
    open_file_action,
    open_in_terminal,
    delete_category_action,
    rename_category_action,
    delete_project_action,
    delete_file_action
)

logger = logging.getLogger(__name__)


class ContextMenuHandler:
    """
    Handles context menu creation and display for the column browser.
    Detects context from right-click events and shows appropriate menu options.
    """

    def __init__(self, column_browser, parent_window):
        """
        Initialize context menu handler

        Args:
            column_browser: ColumnBrowser instance
            parent_window: FinderStyleWindow instance
        """
        self.column_browser = column_browser
        self.parent_window = parent_window
        logger.debug("ContextMenuHandler initialized")

    def create_context_menu(self, context):
        """
        Create appropriate context menu based on context type

        Args:
            context: Dictionary from detect_context() with context information

        Returns:
            Gtk.Menu configured with appropriate menu items
        """
        menu = Gtk.Menu()
        context_type = context['type']

        logger.debug(f"Creating context menu for type: {context_type}")

        if context_type == ROOT_COLUMN:
            # Root column menu: "Create category", "Add project", and "Add file"
            self._add_menu_item(menu, "Create category",
                              lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add file",
                              lambda w: add_file_action(context, self.column_browser, self.parent_window))

        elif context_type == CHILD_COLUMN:
            # Child column menu: "Add subcategory", "Add project", and "Add file"
            # Only show "Add subcategory" if we're not at level 2 (max depth)
            from .context_detector import get_hierarchy_info
            hierarchy_info = get_hierarchy_info(context.get('hierarchy_path'))
            if hierarchy_info['level'] < 2:
                self._add_menu_item(menu, "Add subcategory",
                                  lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add file",
                              lambda w: add_file_action(context, self.column_browser, self.parent_window))

        elif context_type == CATEGORY_ITEM:
            # Category item menu: Multiple options
            # Only show "Add subcategory" if we're not at level 2 (max depth)
            from .context_detector import get_hierarchy_info
            item_path = context.get('item_path')
            hierarchy_info = get_hierarchy_info(item_path)
            if hierarchy_info['level'] < 2:
                self._add_menu_item(menu, "Add subcategory",
                                  lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add file",
                              lambda w: add_file_action(context, self.column_browser, self.parent_window))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            # Toggle favorite
            from .actions import toggle_favorite_action
            is_fav = self.parent_window.config.is_favorite(context.get('item_path'), "category")
            fav_label = "Remove from Favorites" if is_fav else "Add to Favorites"
            self._add_menu_item(menu, fav_label,
                              lambda w: toggle_favorite_action(context, self.column_browser, self.parent_window, "category"))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            self._add_menu_item(menu, "Rename",
                              lambda w: rename_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Delete",
                              lambda w: delete_category_action(context, self.column_browser, self.parent_window))

        elif context_type == PROJECT_ITEM:
            # Project item menu: Open in VSCode, Kiro, Terminal, and Delete
            self._add_menu_item(menu, "Open in VSCode",
                              lambda w: open_vscode_action(context, self.parent_window))
            self._add_menu_item(menu, "Open in Kiro",
                              lambda w: open_kiro_action(context, self.parent_window))

            # Add "Open In Terminal" if terminals are available
            if self._has_available_terminals():
                self._add_menu_item(menu, "Open In Terminal",
                                  lambda w: open_in_terminal(context, self.parent_window))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            # Toggle favorite
            from .actions import toggle_favorite_action
            is_fav = self.parent_window.config.is_favorite(context.get('item_path'), "project")
            fav_label = "Remove from Favorites" if is_fav else "Add to Favorites"
            self._add_menu_item(menu, fav_label,
                              lambda w: toggle_favorite_action(context, self.column_browser, self.parent_window, "project"))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            self._add_menu_item(menu, "Delete project",
                              lambda w: delete_project_action(context, self.column_browser, self.parent_window))

        elif context_type == FILE_ITEM:
            # File item menu: Open and Delete
            self._add_menu_item(menu, "Open",
                              lambda w: open_file_action(context, self.parent_window))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            # Toggle favorite
            from .actions import toggle_favorite_action
            is_fav = self.parent_window.config.is_favorite(context.get('item_path'), "file")
            fav_label = "Remove from Favorites" if is_fav else "Add to Favorites"
            self._add_menu_item(menu, fav_label,
                              lambda w: toggle_favorite_action(context, self.column_browser, self.parent_window, "file"))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            self._add_menu_item(menu, "Delete file",
                              lambda w: delete_file_action(context, self.column_browser, self.parent_window))

        menu.show_all()
        return menu

    def _add_menu_item(self, menu, label, callback):
        """
        Helper method to add a menu item to a menu

        Args:
            menu: Gtk.Menu to add item to
            label: str - Label text for the menu item
            callback: Callable - Function to call when item is activated
        """
        menu_item = Gtk.MenuItem(label=label)
        menu_item.connect("activate", callback)
        menu.append(menu_item)
        logger.debug(f"Added menu item: {label}")

    def _has_available_terminals(self):
        """
        Check if any terminals are available on the system.

        This method implements graceful degradation by safely checking
        terminal availability and handling any errors that might occur.

        Returns:
            bool: True if at least one terminal is available, False otherwise
        """
        try:
            # Get terminal manager from parent window
            terminal_manager = getattr(self.parent_window, 'terminal_manager', None)
            if not terminal_manager:
                logger.debug("Terminal manager not available")
                return False

            # Check if any terminals are available
            has_terminals = terminal_manager.has_available_terminals()
            logger.debug(f"Terminal availability check: {has_terminals}")
            return has_terminals

        except Exception as e:
            logger.error(f"Error checking terminal availability: {e}")
            # Graceful degradation: return False on any error
            return False

    def show_menu(self, menu, event):
        """
        Display the context menu at cursor position

        Args:
            menu: Gtk.Menu to display
            event: Gdk.EventButton for positioning
        """
        try:
            # Mark context menu as active
            self.column_browser.context_menu_active = True

            # Connect to menu deactivate signal to clear the flag
            menu.connect("deactivate", self._on_menu_deactivate)

            # Get the event button and time for popup
            button = event.button
            event_time = event.time

            # Use popup_at_pointer for GTK 3.22+ (handles positioning automatically)
            if hasattr(menu, 'popup_at_pointer'):
                logger.debug("Using popup_at_pointer for menu display")
                menu.popup_at_pointer(event)
            else:
                # Fallback for older GTK versions
                logger.debug("Using legacy popup for menu display")
                menu.popup(None, None, None, None, button, event_time)

            logger.debug(f"Context menu displayed at position ({event.x}, {event.y})")

        except Exception as e:
            logger.error(f"Error displaying context menu: {e}")
            self.column_browser.context_menu_active = False

    def _on_menu_deactivate(self, menu):
        """Called when context menu is closed"""
        self.column_browser.context_menu_active = False
        logger.debug("Context menu deactivated")

    def on_button_press(self, widget, event):
        """
        Handle button press events (right-click detection)

        Args:
            widget: GTK widget that received the event
            event: Gdk.EventButton

        Returns:
            True if event was handled (right-click), False otherwise
        """
        try:
            # Check if it's a right-click (button 3)
            if event.button == 3:
                logger.debug(f"Right-click detected at ({event.x}, {event.y})")

                # Get the item at the click position
                path_info = self.column_browser.treeview.get_path_at_pos(int(event.x), int(event.y))

                if path_info is not None:
                    # Clicked on an item
                    tree_path, column, cell_x, cell_y = path_info

                    # Mark context menu as active BEFORE any selection changes
                    self.column_browser.context_menu_active = True

                    # Check if the clicked item is already selected
                    selection = self.column_browser.treeview.get_selection()
                    model, selected_iter = selection.get_selected()

                    # Get the path of currently selected item (if any)
                    selected_path = None
                    if selected_iter:
                        selected_path = model.get_path(selected_iter)

                    # If clicked item is not selected, select it first
                    if selected_path != tree_path:
                        logger.debug(f"Selecting item at path {tree_path} before showing context menu")

                        # Block the selection callback temporarily to prevent navigation
                        selection.handler_block_by_func(self.column_browser.on_selection_changed)
                        selection.select_path(tree_path)
                        selection.handler_unblock_by_func(self.column_browser.on_selection_changed)
                else:
                    # Clicked on empty area - deselect any selected item
                    logger.debug("Right-click on empty area - deselecting items")
                    selection = self.column_browser.treeview.get_selection()
                    selection.unselect_all()

                # Detect the context of the click
                context = detect_context(self.column_browser, event)

                # Create the appropriate context menu
                menu = self.create_context_menu(context)

                # Display the menu at cursor position
                self.show_menu(menu, event)

                # Return True to prevent default GTK context menu
                return True

        except Exception as e:
            logger.error(f"Error handling button press event: {e}", exc_info=True)
            return True

        # Not a right-click, let other handlers process the event
        return False
