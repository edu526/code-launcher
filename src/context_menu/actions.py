#!/usr/bin/env python3
"""
Context menu actions
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import logging
import os
import subprocess
from src.dialogs import show_create_category_dialog, show_add_project_dialog, show_add_file_dialog
from .context_detector import get_hierarchy_info, ROOT_COLUMN, CHILD_COLUMN, CATEGORY_ITEM

logger = logging.getLogger(__name__)


def create_category_action(context, column_browser, parent_window):
    """
    Handle create category/subcategory action from context menu

    Args:
        context: Context dictionary with hierarchy information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Create category action triggered with context: {context}")

        # Extract hierarchy info from context
        hierarchy_path = context.get('hierarchy_path')
        context_type = context.get('type')
        item_path = context.get('item_path')

        # Check hierarchy level to enforce 2-level limit
        hierarchy_info = get_hierarchy_info(hierarchy_path if hierarchy_path else item_path)
        current_level = hierarchy_info['level']

        # If we're at level 2 (subcategory), don't allow creating another subcategory
        if current_level >= 2:
            logger.warning(f"Cannot create subcategory at level {current_level} - maximum 2 levels allowed")
            show_error_dialog(parent_window, "Maximum category depth reached.\nOnly 2 levels of categories are allowed:\nCategory → Subcategory")
            return

        # Build pre_config dict based on context
        pre_config = {}

        if context_type == ROOT_COLUMN:
            # Root column - creating a main category (no parent)
            pre_config['parent_category'] = None
            pre_config['force_subcategory'] = False
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CHILD_COLUMN:
            # Child column - creating a subcategory under current hierarchy
            hierarchy_info = get_hierarchy_info(hierarchy_path)

            # Build the parent category path
            if hierarchy_info['subcategory_path']:
                # We're in a nested subcategory, parent is the full path
                parent_category = f"{hierarchy_info['category']}:{hierarchy_info['subcategory_path']}"
            else:
                # We're in a first-level category, parent is just the category
                parent_category = hierarchy_info['category']

            pre_config['parent_category'] = parent_category
            pre_config['force_subcategory'] = True
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CATEGORY_ITEM:
            # Category item - creating a subcategory under the selected category
            # Extract the category name from the item_path
            if item_path and item_path.startswith("cat:"):
                # Remove "cat:" prefix and use the rest as parent
                parent_parts = item_path.split(":")[1:]
                parent_category = ":".join(parent_parts)
            else:
                parent_category = None

            pre_config['parent_category'] = parent_category
            pre_config['force_subcategory'] = True
            pre_config['hierarchy_path'] = item_path

        else:
            # Fallback - no pre-configuration
            pre_config['parent_category'] = None
            pre_config['force_subcategory'] = False
            pre_config['hierarchy_path'] = hierarchy_path

        logger.debug(f"Pre-config for create category dialog: {pre_config}")

        # Get the callback from parent window
        def on_create_callback(name, description, icon, parent_category):
            """Wrapper callback that delegates to parent window's logic"""
            try:
                if parent_category:
                    # Parse parent_category to handle nested subcategories
                    parts = parent_category.split(":")

                    # Navigate to the correct level in the categories dict
                    current_level = parent_window.categories
                    for i, part in enumerate(parts[:-1]):
                        if part in current_level:
                            if "subcategories" not in current_level[part]:
                                current_level[part]["subcategories"] = {}
                            current_level = current_level[part]["subcategories"]

                    # Add the subcategory at the correct level
                    parent_name = parts[-1]
                    if parent_name in current_level:
                        if "subcategories" not in current_level[parent_name]:
                            current_level[parent_name]["subcategories"] = {}

                        current_level[parent_name]["subcategories"][name] = {
                            "description": description,
                            "icon": icon
                        }
                else:
                    # Create main category
                    if name not in parent_window.categories:
                        parent_window.categories[name] = {
                            "description": description,
                            "icon": icon,
                            "subcategories": {}
                        }
                    else:
                        # Category exists, ensure it has subcategories dict
                        if "subcategories" not in parent_window.categories[name]:
                            parent_window.categories[name]["subcategories"] = {}

                # Save and reload
                parent_window.config.save_categories(parent_window.categories)

                # Refresh only the current column instead of reloading everything
                if parent_category is None:
                    # Creating a root category - reload the first column
                    if len(parent_window.columns) > 0:
                        first_column = parent_window.columns[0]
                        first_column.load_hierarchy_level(parent_window.categories, None, parent_window.projects, parent_window.files)
                else:
                    # Creating a subcategory - reload the current column with mixed content
                    if hasattr(column_browser, 'load_mixed_content'):
                        column_browser.load_mixed_content(
                            parent_window.categories,
                            column_browser.current_path,
                            parent_window.projects,
                            parent_window.files
                        )

                logger.info(f"Category created: {name} (parent: {parent_category})")

            except Exception as e:
                logger.error(f"Error creating category: {e}", exc_info=True)
                show_error_dialog(parent_window, f"Error creating category: {e}")

        # Call show_create_category_dialog with pre_config
        show_create_category_dialog(
            parent_window,
            parent_window.categories,
            on_create_callback,
            pre_config=pre_config
        )

    except Exception as e:
        logger.error(f"Error in create category action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening category dialog: {e}")


def add_project_action(context, column_browser, parent_window):
    """
    Handle add project action from context menu

    Args:
        context: Context dictionary with hierarchy information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Add project action triggered with context: {context}")

        # Extract hierarchy info from context
        hierarchy_path = context.get('hierarchy_path')
        context_type = context.get('type')

        # Build pre_config dict based on context
        pre_config = {}

        if context_type == ROOT_COLUMN:
            # Root column empty area - add to root (no category)
            pre_config['category'] = None
            pre_config['subcategory'] = None
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CHILD_COLUMN:
            # Child column empty area - add under the parent category being viewed
            hierarchy_info = get_hierarchy_info(hierarchy_path)

            # Pre-select the category/subcategory based on current hierarchy
            pre_config['category'] = hierarchy_info['category']
            pre_config['subcategory'] = hierarchy_info['subcategory_path']
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CATEGORY_ITEM:
            # Category item clicked - pre-select that category
            item_path = context.get('item_path')

            if item_path and item_path.startswith("cat:"):
                # Parse the category item path
                parts = item_path.split(":")[1:]  # Remove "cat:" prefix

                if len(parts) >= 1:
                    pre_config['category'] = parts[0]

                    # If there are more parts, it's a subcategory
                    if len(parts) > 1:
                        pre_config['subcategory'] = ":".join(parts[1:])
                    else:
                        pre_config['subcategory'] = None
                else:
                    pre_config['category'] = None
                    pre_config['subcategory'] = None
            else:
                pre_config['category'] = None
                pre_config['subcategory'] = None

            pre_config['hierarchy_path'] = item_path

        else:
            # Fallback - no pre-configuration
            pre_config['category'] = None
            pre_config['subcategory'] = None
            pre_config['hierarchy_path'] = hierarchy_path

        logger.debug(f"Pre-config for add project dialog: {pre_config}")

        # Get the callback from parent window
        def on_add_callback(name, project_info):
            """Wrapper callback that delegates to parent window's logic"""
            try:
                # Add the project to the projects dictionary
                parent_window.projects[name] = project_info

                # Save and reload
                parent_window.config.save_projects(parent_window.projects)

                # Refresh the appropriate column
                # Check if we're in root column (categories view)
                if column_browser.current_path == "categories" or column_browser.current_path is None:
                    # In root column - need to refresh it if project has no category, or refresh child column if it has category
                    project_category = project_info.get('category')

                    if not project_category:
                        # No category - refresh the root column to show the new project
                        if len(parent_window.columns) > 0:
                            first_column = parent_window.columns[0]
                            first_column.load_hierarchy_level(parent_window.categories, None, parent_window.projects, parent_window.files)
                            logger.info(f"Refreshed root column for root-level project")
                    elif project_category and len(parent_window.columns) > 1:
                        # There's a second column showing content for a category
                        # Check if it matches the project's category
                        second_column = parent_window.columns[1]
                        if second_column.current_path and second_column.current_path.startswith(f"cat:{project_category}"):
                            # Refresh the second column to show the new project
                            second_column.load_mixed_content(
                                parent_window.categories,
                                second_column.current_path,
                                parent_window.projects,
                                parent_window.files
                            )
                            logger.info(f"Refreshed second column for category: {project_category}")

                    logger.info(f"Project added from root: {name}")
                else:
                    # In a child column - refresh to show the new project
                    if hasattr(column_browser, 'load_mixed_content'):
                        column_browser.load_mixed_content(
                            parent_window.categories,
                            column_browser.current_path,
                            parent_window.projects,
                            parent_window.files
                        )

                logger.info(f"Project added: {name} (category: {project_info.get('category')}, subcategory: {project_info.get('subcategory')})")

            except Exception as e:
                logger.error(f"Error adding project: {e}", exc_info=True)
                show_error_dialog(parent_window, f"Error adding project: {e}")

        # Call show_add_project_dialog with pre_config
        show_add_project_dialog(
            parent_window,
            parent_window.categories,
            on_add_callback,
            pre_config=pre_config
        )

    except Exception as e:
        logger.error(f"Error in add project action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening project dialog: {e}")


def add_file_action(context, column_browser, parent_window):
    """
    Handle add file action from context menu

    Args:
        context: Context dictionary with hierarchy information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Add file action triggered with context: {context}")

        hierarchy_path = context.get('hierarchy_path')
        context_type = context.get('type')

        pre_config = {}

        if context_type == ROOT_COLUMN:
            # Root column empty area - add to root (no category)
            pre_config['category'] = None
            pre_config['subcategory'] = None
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CHILD_COLUMN:
            # Child column empty area - add under the parent category being viewed
            hierarchy_info = get_hierarchy_info(hierarchy_path)

            # Pre-select the category/subcategory based on current hierarchy
            pre_config['category'] = hierarchy_info['category']
            pre_config['subcategory'] = hierarchy_info['subcategory_path']
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CATEGORY_ITEM:
            # Category item clicked - pre-select that category
            item_path = context.get('item_path')

            if item_path and item_path.startswith("cat:"):
                parts = item_path.split(":")[1:]

                if len(parts) >= 1:
                    pre_config['category'] = parts[0]
                    if len(parts) > 1:
                        pre_config['subcategory'] = ":".join(parts[1:])
                    else:
                        pre_config['subcategory'] = None
                else:
                    pre_config['category'] = None
                    pre_config['subcategory'] = None
            else:
                pre_config['category'] = None
                pre_config['subcategory'] = None

            pre_config['hierarchy_path'] = item_path

        else:
            pre_config['category'] = None
            pre_config['subcategory'] = None
            pre_config['hierarchy_path'] = hierarchy_path

        logger.debug(f"Pre-config for add file dialog: {pre_config}")

        logger.debug(f"Pre-config for add file dialog: {pre_config}")

        def on_add_callback(name, file_info):
            """Wrapper callback for adding files"""
            try:
                if not hasattr(parent_window, 'files'):
                    parent_window.files = {}

                parent_window.files[name] = file_info
                parent_window.config.save_files(parent_window.files)

                # Refresh the appropriate column
                if column_browser.current_path == "categories" or column_browser.current_path is None:
                    file_category = file_info.get('category')

                    if not file_category:
                        # No category - refresh the root column to show the new file
                        if len(parent_window.columns) > 0:
                            first_column = parent_window.columns[0]
                            first_column.load_hierarchy_level(parent_window.categories, None, parent_window.projects, parent_window.files)
                            logger.info(f"Refreshed root column for root-level file")
                    elif file_category and len(parent_window.columns) > 1:
                        second_column = parent_window.columns[1]
                        if second_column.current_path and second_column.current_path.startswith(f"cat:{file_category}"):
                            second_column.load_mixed_content(
                                parent_window.categories,
                                second_column.current_path,
                                parent_window.projects,
                                parent_window.files
                            )
                            logger.info(f"Refreshed second column for category: {file_category}")

                    logger.info(f"File added from root: {name}")
                else:
                    if hasattr(column_browser, 'load_mixed_content'):
                        column_browser.load_mixed_content(
                            parent_window.categories,
                            column_browser.current_path,
                            parent_window.projects,
                            parent_window.files
                        )

                logger.info(f"File added: {name} (category: {file_info.get('category')}, subcategory: {file_info.get('subcategory')})")

            except Exception as e:
                logger.error(f"Error adding file: {e}", exc_info=True)
                show_error_dialog(parent_window, f"Error adding file: {e}")

        show_add_file_dialog(
            parent_window,
            parent_window.categories,
            on_add_callback,
            pre_config=pre_config
        )

    except Exception as e:
        logger.error(f"Error in add file action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening file dialog: {e}")


def open_vscode_action(context, parent_window):
    """
    Handle open VSCode action from context menu

    Args:
        context: Context dictionary with project path
        parent_window: FinderStyleWindow instance
    """
    logger.info(f"Open VSCode action triggered with context: {context}")

    try:
        # Extract project path from context
        project_path = context.get('item_path')

        if not project_path:
            logger.error("No project path found in context")
            show_error_dialog(parent_window, "Error: Project path not found")
            return

        logger.debug(f"Opening project in VSCode: {project_path}")

        # Call parent_window.open_vscode_project(path)
        success = parent_window.open_vscode_project(project_path)

        if success:
            logger.info(f"Successfully opened project in VSCode: {project_path}")
        else:
            logger.warning(f"Failed to open project in VSCode: {project_path}")

    except Exception as e:
        logger.error(f"Error opening project in VSCode: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening project in VSCode: {e}")


def open_kiro_action(context, parent_window):
    """
    Handle open Kiro action from context menu

    Args:
        context: Context dictionary with project path
        parent_window: FinderStyleWindow instance
    """
    logger.info(f"Open Kiro action triggered with context: {context}")

    try:
        # Extract project path from context
        project_path = context.get('item_path')

        if not project_path:
            logger.error("No project path found in context")
            show_error_dialog(parent_window, "Error: Project path not found")
            return

        logger.debug(f"Opening project in Kiro: {project_path}")

        # Call parent_window.open_kiro_project(path)
        success = parent_window.open_kiro_project(project_path)

        if success:
            logger.info(f"Successfully opened project in Kiro: {project_path}")
        else:
            logger.warning(f"Failed to open project in Kiro: {project_path}")

    except Exception as e:
        logger.error(f"Error opening project in Kiro: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening project in Kiro: {e}")


def open_file_action(context, parent_window):
    """
    Handle open file action from context menu

    Args:
        context: Context dictionary with file path
        parent_window: FinderStyleWindow instance
    """
    logger.info(f"Open file action triggered with context: {context}")

    try:
        file_path = context.get('item_path')

        if not file_path:
            logger.error("No file path found in context")
            show_error_dialog(parent_window, "Error: File path not found")
            return

        logger.debug(f"Opening file: {file_path}")

        # Get the default text editor from preferences
        preferences = parent_window.config.load_preferences()
        text_editor = preferences.get("default_text_editor", "gnome-text-editor")

        # Import text editor utils
        from utils.text_editor_utils import open_file_in_editor

        success = open_file_in_editor(file_path, text_editor)

        if success:
            logger.info(f"Successfully opened file in {text_editor}: {file_path}")

            # Add to recents
            file_name = parent_window._get_file_name(file_path)
            if file_name:
                parent_window.config.add_recent(file_path, file_name, "file")

            # Close launcher if preference is set
            if hasattr(parent_window, 'close_on_open') and parent_window.close_on_open:
                parent_window.destroy()
        else:
            logger.warning(f"Failed to open file in {text_editor}: {file_path}")
            show_error_dialog(parent_window, f"Error: Could not open file with {text_editor}")

    except Exception as e:
        logger.error(f"Error opening file: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening file: {e}")


def open_in_terminal(context, parent_window):
    """
    Handle open in terminal action from context menu with graceful degradation.

    Args:
        context: Context dictionary with project path
        parent_window: FinderStyleWindow instance
    """
    logger.info(f"Open in terminal action triggered with context: {context}")

    try:
        # Extract project path from context
        project_path = context.get('item_path')

        if not project_path:
            logger.error("No project path found in context")
            show_error_dialog(parent_window, "Error: Project path not found")
            return

        logger.debug(f"Opening terminal for project: {project_path}")

        # Get terminal manager from parent window with graceful degradation
        terminal_manager = getattr(parent_window, 'terminal_manager', None)
        if not terminal_manager:
            logger.error("Terminal manager not available")
            show_error_dialog(parent_window, "Error: Terminal functionality not available")
            return

        # Check if any terminals are available with graceful degradation
        try:
            if not terminal_manager.has_available_terminals():
                logger.error("No terminals available on system")
                show_error_dialog(parent_window, "Error: No terminal applications found on system")
                return
        except Exception as e:
            logger.error(f"Error checking terminal availability: {e}")
            show_error_dialog(parent_window, "Error: Unable to check terminal availability")
            return

        # Launch terminal in project directory with comprehensive error handling
        try:
            success, error_message = terminal_manager.open_terminal(project_path)

            if success:
                logger.info(f"Successfully opened terminal for project: {project_path}")
            else:
                logger.warning(f"Failed to open terminal for project: {project_path} - {error_message}")
                show_error_dialog(parent_window, f"Error: {error_message}")

        except Exception as e:
            logger.error(f"Unexpected error launching terminal: {e}")
            show_error_dialog(parent_window, "Error: Unexpected error launching terminal")

    except Exception as e:
        logger.error(f"Error in open_in_terminal action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening terminal: {e}")


def show_error_dialog(parent_window, message):
    """
    Display an error dialog to the user

    Args:
        parent_window: Parent window
        message: Error message to display
    """
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk

        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dialog.run()
        dialog.destroy()
        logger.debug(f"Error dialog displayed: {message}")
    except Exception as e:
        logger.error(f"Failed to show error dialog: {e}", exc_info=True)



def delete_category_action(context, column_browser, parent_window):
    """
    Handle delete category/subcategory action

    Args:
        context: Context dictionary with hierarchy information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Delete category action triggered with context: {context}")

        item_path = context.get('item_path')

        if not item_path or not item_path.startswith("cat:"):
            logger.error("Invalid item path for delete category")
            return

        # Parse category path
        parts = item_path.split(":")[1:]  # Remove "cat:" prefix
        category_name = ":".join(parts)

        # Count projects and subcategories that will be deleted
        projects_to_delete = []
        subcategories_count = 0

        # Find all projects that belong to this category or its subcategories
        for project_name, project_info in parent_window.projects.items():
            if isinstance(project_info, dict):
                project_category = project_info.get('category', '')
                project_subcategory = project_info.get('subcategory', '')

                # Build full project category path
                if project_subcategory:
                    full_project_path = f"{project_category}:{project_subcategory}"
                else:
                    full_project_path = project_category

                # Check if project belongs to this category or any subcategory
                if len(parts) == 1:
                    # Deleting main category - check if project's category matches
                    if project_category == parts[0]:
                        projects_to_delete.append(project_name)
                else:
                    # Deleting subcategory - check if project's full path starts with this path
                    if full_project_path == category_name or full_project_path.startswith(category_name + ":"):
                        projects_to_delete.append(project_name)

        # Count subcategories recursively
        def count_subcategories(cat_dict):
            count = 0
            for cat_name, cat_info in cat_dict.items():
                count += 1
                if "subcategories" in cat_info and cat_info["subcategories"]:
                    count += count_subcategories(cat_info["subcategories"])
            return count

        # Get the category dict to count subcategories
        if len(parts) == 1:
            # Main category
            if parts[0] in parent_window.categories:
                cat_info = parent_window.categories[parts[0]]
                if "subcategories" in cat_info:
                    subcategories_count = count_subcategories(cat_info["subcategories"])
        else:
            # Subcategory
            current_level = parent_window.categories
            for i, part in enumerate(parts[:-1]):
                if part in current_level:
                    if i == 0:
                        current_level = current_level[part].get("subcategories", {})
                    else:
                        current_level = current_level[part].get("subcategories", {})

            if parts[-1] in current_level:
                cat_info = current_level[parts[-1]]
                if "subcategories" in cat_info:
                    subcategories_count = count_subcategories(cat_info["subcategories"])

        # Build confirmation message
        message_parts = []
        if subcategories_count > 0:
            message_parts.append(f"{subcategories_count} subcategory(ies)")
        if len(projects_to_delete) > 0:
            message_parts.append(f"{len(projects_to_delete)} project(s)")

        if message_parts:
            secondary_text = f"This action will delete:\n- " + "\n- ".join(message_parts) + "\n\nContinue?"
        else:
            secondary_text = "This category is empty. Delete it?"

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete category '{parts[-1]}'?"
        )
        dialog.format_secondary_text(secondary_text)
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        # Delete projects first
        for project_name in projects_to_delete:
            if project_name in parent_window.projects:
                del parent_window.projects[project_name]
                logger.info(f"Deleted project: {project_name}")

        # Save projects
        if projects_to_delete:
            parent_window.config.save_projects(parent_window.projects)

        # Delete the category
        if len(parts) == 1:
            # Delete main category
            if parts[0] in parent_window.categories:
                del parent_window.categories[parts[0]]
                logger.info(f"Deleted main category: {parts[0]}")
        else:
            # Delete subcategory
            current_level = parent_window.categories
            for i, part in enumerate(parts[:-1]):
                if part in current_level:
                    if i == 0:
                        current_level = current_level[part].get("subcategories", {})
                    else:
                        current_level = current_level[part].get("subcategories", {})
                else:
                    logger.error(f"Category path not found: {category_name}")
                    return

            # Delete the last subcategory
            if parts[-1] in current_level:
                del current_level[parts[-1]]
                logger.info(f"Deleted subcategory: {category_name}")

        # Save changes
        parent_window.config.save_categories(parent_window.categories)

        # Refresh interface
        parent_window.reload_interface()

    except Exception as e:
        logger.error(f"Error deleting category: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error deleting category: {e}")


def rename_category_action(context, column_browser, parent_window):
    """
    Handle rename category/subcategory action

    Args:
        context: Context dictionary with hierarchy information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Rename category action triggered with context: {context}")

        item_path = context.get('item_path')

        if not item_path or not item_path.startswith("cat:"):
            logger.error("Invalid item path for rename category")
            return

        # Parse category path
        parts = item_path.split(":")[1:]  # Remove "cat:" prefix
        old_name = parts[-1]

        # Input dialog
        dialog = Gtk.Dialog(
            title="Rename Category",
            transient_for=parent_window,
            flags=0
        )
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)

        label = Gtk.Label(label=f"New name for '{old_name}':")
        content.pack_start(label, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(old_name)
        entry.set_activates_default(True)
        content.pack_start(entry, False, False, 0)

        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()

        response = dialog.run()
        new_name = entry.get_text().strip()
        dialog.destroy()

        if response != Gtk.ResponseType.OK or not new_name or new_name == old_name:
            return

        # Rename the category
        if len(parts) == 1:
            # Rename main category
            if parts[0] in parent_window.categories:
                parent_window.categories[new_name] = parent_window.categories.pop(parts[0])
                logger.info(f"Renamed main category: {parts[0]} -> {new_name}")

                # Update all projects that reference this category
                for project_name, project_info in parent_window.projects.items():
                    if isinstance(project_info, dict):
                        if project_info.get('category') == parts[0]:
                            project_info['category'] = new_name
                            logger.info(f"Updated project {project_name} category reference")

                # Update all files that reference this category
                for file_name, file_info in parent_window.files.items():
                    if isinstance(file_info, dict):
                        if file_info.get('category') == parts[0]:
                            file_info['category'] = new_name
                            logger.info(f"Updated file {file_name} category reference")
        else:
            # Rename subcategory
            current_level = parent_window.categories
            for i, part in enumerate(parts[:-1]):
                if part in current_level:
                    if i == 0:
                        current_level = current_level[part].get("subcategories", {})
                    else:
                        current_level = current_level[part].get("subcategories", {})
                else:
                    logger.error(f"Category path not found: {':'.join(parts)}")
                    return

            # Rename the last subcategory
            if parts[-1] in current_level:
                current_level[new_name] = current_level.pop(parts[-1])
                logger.info(f"Renamed subcategory: {parts[-1]} -> {new_name}")

                # Build the old and new subcategory paths
                old_subcat_path = parts[-1]
                new_subcat_path = new_name
                category_name = parts[0]

                # If there are intermediate subcategories, build the full path
                if len(parts) > 2:
                    intermediate_path = ':'.join(parts[1:-1])
                    old_subcat_path = f"{intermediate_path}:{old_subcat_path}"
                    new_subcat_path = f"{intermediate_path}:{new_subcat_path}"

                # Update all projects that reference this subcategory
                for project_name, project_info in parent_window.projects.items():
                    if isinstance(project_info, dict):
                        if (project_info.get('category') == category_name and
                            project_info.get('subcategory') == old_subcat_path):
                            project_info['subcategory'] = new_subcat_path
                            logger.info(f"Updated project {project_name} subcategory reference")

                # Update all files that reference this subcategory
                for file_name, file_info in parent_window.files.items():
                    if isinstance(file_info, dict):
                        if (file_info.get('category') == category_name and
                            file_info.get('subcategory') == old_subcat_path):
                            file_info['subcategory'] = new_subcat_path
                            logger.info(f"Updated file {file_name} subcategory reference")

        # Save all changes
        parent_window.config.save_categories(parent_window.categories)
        parent_window.config.save_projects(parent_window.projects)
        parent_window.config.save_files(parent_window.files)

        # Refresh only the affected columns instead of reloading everything
        # Find and refresh columns that show this category
        for column in parent_window.columns:
            if hasattr(column, 'current_path') and column.current_path:
                # Check if this column is affected by the rename
                if len(parts) == 1:
                    # Main category renamed - refresh root column and any column showing this category
                    if column.current_path == "categories" or column.current_path is None:
                        column.load_hierarchy_level(parent_window.categories, None, parent_window.projects, parent_window.files)
                        logger.info("Refreshed root column after category rename")
                    elif column.current_path.startswith(f"cat:{parts[0]}"):
                        # Update the current_path to reflect the new name
                        old_path = column.current_path
                        new_path = old_path.replace(f"cat:{parts[0]}", f"cat:{new_name}", 1)
                        column.current_path = new_path
                        column.load_mixed_content(parent_window.categories, new_path, parent_window.projects, parent_window.files)
                        logger.info(f"Refreshed column: {old_path} -> {new_path}")
                else:
                    # Subcategory renamed - refresh parent column and this column
                    parent_path = f"cat:{':'.join(parts[:-1])}"
                    current_path = f"cat:{':'.join(parts)}"

                    if column.current_path == parent_path:
                        column.load_mixed_content(parent_window.categories, parent_path, parent_window.projects, parent_window.files)
                        logger.info(f"Refreshed parent column: {parent_path}")
                    elif column.current_path.startswith(current_path):
                        # Update the current_path to reflect the new name
                        old_path = column.current_path
                        new_path = old_path.replace(current_path, f"cat:{':'.join(parts[:-1])}:{new_name}", 1)
                        column.current_path = new_path
                        column.load_mixed_content(parent_window.categories, new_path, parent_window.projects, parent_window.files)
                        logger.info(f"Refreshed column: {old_path} -> {new_path}")

    except Exception as e:
        logger.error(f"Error renaming category: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error renaming category: {e}")


def delete_project_action(context, column_browser, parent_window):
    """
    Handle delete project action

    Args:
        context: Context dictionary with project information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Delete project action triggered with context: {context}")

        project_path = context.get('item_path')

        if not project_path:
            logger.error("No project path found in context")
            return

        # Find project name
        project_name = None
        for name, info in parent_window.projects.items():
            if isinstance(info, str):
                if info == project_path:
                    project_name = name
                    break
            else:
                if info.get("path") == project_path:
                    project_name = name
                    break

        if not project_name:
            logger.error(f"Project not found for path: {project_path}")
            show_error_dialog(parent_window, "Project not found")
            return

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete project '{project_name}'?"
        )
        dialog.format_secondary_text(
            "This action will only remove the project from the list.\n"
            "Files on disk will NOT be deleted."
        )
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        # Delete the project
        if project_name in parent_window.projects:
            del parent_window.projects[project_name]
            logger.info(f"Deleted project: {project_name}")

            # Save changes
            parent_window.config.save_projects(parent_window.projects)

            # Refresh current column
            if hasattr(column_browser, 'load_mixed_content'):
                column_browser.load_mixed_content(
                    parent_window.categories,
                    column_browser.current_path,
                    parent_window.projects,
                    parent_window.files
                )

    except Exception as e:
        logger.error(f"Error deleting project: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error deleting project: {e}")


def delete_file_action(context, column_browser, parent_window):
    """
    Handle delete file action

    Args:
        context: Context dictionary with file information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
    """
    try:
        logger.info(f"Delete file action triggered with context: {context}")

        file_path = context.get('item_path')

        if not file_path:
            logger.error("No file path found in context")
            return

        # Find file name
        file_name = None
        if hasattr(parent_window, 'files'):
            for name, info in parent_window.files.items():
                if isinstance(info, str):
                    if info == file_path:
                        file_name = name
                        break
                else:
                    if info.get("path") == file_path:
                        file_name = name
                        break

        if not file_name:
            logger.error(f"File not found for path: {file_path}")
            show_error_dialog(parent_window, "File not found")
            return

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete file '{file_name}'?"
        )
        dialog.format_secondary_text(
            "This action will only remove the file from the list.\n"
            "The file on disk will NOT be deleted."
        )
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        # Delete the file
        if file_name in parent_window.files:
            del parent_window.files[file_name]
            logger.info(f"Deleted file: {file_name}")

            # Save changes
            parent_window.config.save_files(parent_window.files)

            # Refresh current column
            if hasattr(column_browser, 'load_mixed_content'):
                column_browser.load_mixed_content(
                    parent_window.categories,
                    column_browser.current_path,
                    parent_window.projects,
                    parent_window.files
                )

    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error deleting file: {e}")


def toggle_favorite_action(context, column_browser, parent_window, item_type="project"):
    """
    Handle toggle favorite action

    Args:
        context: Context dictionary with item information
        column_browser: ColumnBrowser instance
        parent_window: FinderStyleWindow instance
        item_type: "project", "file", or "category"
    """
    try:
        logger.info(f"Toggle favorite action triggered for {item_type} with context: {context}")

        item_path = context.get('item_path')

        if not item_path:
            logger.error("No item path found in context")
            return

        # Toggle favorite status
        is_fav = parent_window.config.toggle_favorite(item_path, item_type)
        status = "added to" if is_fav else "removed from"
        logger.info(f"Item {status} favorites: {item_path}")

        # Determine the correct refresh method based on current_path
        current_path = column_browser.current_path
        logger.debug(f"Reloading column with current_path: {current_path}")

        # Check if we're in the root categories view or a nested view
        if current_path is None or current_path == "categories":
            # Root level - use load_hierarchy_level
            logger.debug("Reloading root level with load_hierarchy_level")
            column_browser.load_hierarchy_level(
                parent_window.categories,
                None,
                parent_window.projects,
                parent_window.files
            )
        elif current_path and current_path.startswith("cat:"):
            # We're in a category view - use load_mixed_content
            logger.debug(f"Reloading category view with load_mixed_content: {current_path}")
            column_browser.load_mixed_content(
                parent_window.categories,
                current_path,
                parent_window.projects,
                parent_window.files
            )
        else:
            # Fallback - try load_mixed_content
            logger.debug(f"Fallback reload with load_mixed_content: {current_path}")
            if hasattr(column_browser, 'load_mixed_content'):
                column_browser.load_mixed_content(
                    parent_window.categories,
                    column_browser.current_path,
                    parent_window.projects,
                    parent_window.files
                )

    except Exception as e:
        logger.error(f"Error toggling favorite: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error toggling favorite: {e}")


def open_directory_action(context, parent_window):
    """
    Handle open directory action from context menu
    For projects: opens the project directory
    For files: opens the directory containing the file

    Args:
        context: Context dictionary with item path
        parent_window: FinderStyleWindow instance
    """
    logger.info(f"Open directory action triggered with context: {context}")

    try:
        item_path = context.get('item_path')
        is_file = context.get('is_file', False)

        if not item_path:
            logger.error("No item path found in context")
            show_error_dialog(parent_window, "Error: Item path not found")
            return

        # Determine the directory to open
        if is_file:
            # For files, open the directory containing the file
            directory = os.path.dirname(item_path)
            logger.debug(f"Opening directory containing file: {directory}")
        else:
            # For projects, open the project directory itself
            directory = item_path
            logger.debug(f"Opening project directory: {directory}")

        # Check if directory exists
        if not os.path.exists(directory):
            logger.error(f"Directory does not exist: {directory}")
            show_error_dialog(parent_window, f"Error: Directory not found\n{directory}")
            return

        if not os.path.isdir(directory):
            logger.error(f"Path is not a directory: {directory}")
            show_error_dialog(parent_window, f"Error: Not a directory\n{directory}")
            return

        # Open the directory in the default file manager
        try:
            # Try xdg-open first (works on most Linux systems)
            subprocess.Popen(['xdg-open', directory])
            logger.info(f"Successfully opened directory: {directory}")
        except FileNotFoundError:
            # Fallback to nautilus if xdg-open is not available
            try:
                subprocess.Popen(['nautilus', directory])
                logger.info(f"Successfully opened directory with nautilus: {directory}")
            except FileNotFoundError:
                # Last resort: try thunar
                try:
                    subprocess.Popen(['thunar', directory])
                    logger.info(f"Successfully opened directory with thunar: {directory}")
                except FileNotFoundError:
                    logger.error("No file manager found (xdg-open, nautilus, thunar)")
                    show_error_dialog(parent_window, "Error: No file manager found on system")

    except Exception as e:
        logger.error(f"Error opening directory: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error opening directory: {e}")

