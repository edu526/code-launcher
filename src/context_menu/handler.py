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
    PROJECT_ITEM
)
from .actions import (
    create_category_action,
    add_project_action,
    open_vscode_action,
    open_kiro_action,
    delete_category_action,
    rename_category_action,
    delete_project_action
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
            # Root column menu: "Create category" and "Add project"
            self._add_menu_item(menu, "Create category",
                              lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))

        elif context_type == CHILD_COLUMN:
            # Child column menu: "Add subcategory" and "Add project"
            self._add_menu_item(menu, "Add subcategory",
                              lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))

        elif context_type == CATEGORY_ITEM:
            # Category item menu: Multiple options
            self._add_menu_item(menu, "Add subcategory",
                              lambda w: create_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Add project",
                              lambda w: add_project_action(context, self.column_browser, self.parent_window))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            self._add_menu_item(menu, "Rename",
                              lambda w: rename_category_action(context, self.column_browser, self.parent_window))
            self._add_menu_item(menu, "Delete",
                              lambda w: delete_category_action(context, self.column_browser, self.parent_window))

        elif context_type == PROJECT_ITEM:
            # Project item menu: Open in VSCode or Kiro, and Delete
            self._add_menu_item(menu, "Open in VSCode",
                              lambda w: open_vscode_action(context, self.parent_window))
            self._add_menu_item(menu, "Open in Kiro",
                              lambda w: open_kiro_action(context, self.parent_window))

            # Separator
            menu.append(Gtk.SeparatorMenuItem())

            self._add_menu_item(menu, "Delete project",
                              lambda w: delete_project_action(context, self.column_browser, self.parent_window))

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

    def show_menu(self, menu, event):
        """
        Display the context menu at cursor position

        Args:
            menu: Gtk.Menu to display
            event: Gdk.EventButton for positioning
        """
        try:
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
