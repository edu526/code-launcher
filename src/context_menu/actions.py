#!/usr/bin/env python3
"""
Context menu actions
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import logging
from src.dialogs import show_create_category_dialog, show_add_project_dialog
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
                        first_column.load_hierarchy_level(parent_window.categories, None)
                else:
                    # Creating a subcategory - reload the current column with mixed content
                    if hasattr(column_browser, 'load_mixed_content'):
                        column_browser.load_mixed_content(
                            parent_window.categories,
                            column_browser.current_path,
                            parent_window.projects
                        )

                logger.info(f"Category created: {name} (parent: {parent_category})")

            except Exception as e:
                logger.error(f"Error creating category: {e}", exc_info=True)
                show_error_dialog(parent_window, f"Error al crear categoría: {e}")

        # Call show_create_category_dialog with pre_config
        show_create_category_dialog(
            parent_window,
            parent_window.categories,
            on_create_callback,
            pre_config=pre_config
        )

    except Exception as e:
        logger.error(f"Error in create category action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error al abrir diálogo de categoría: {e}")


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
            # Root column - no category pre-selected
            pre_config['category'] = None
            pre_config['subcategory'] = None
            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CHILD_COLUMN:
            # Child column - pre-select category and subcategory based on current hierarchy
            hierarchy_info = get_hierarchy_info(hierarchy_path)

            # Set category
            pre_config['category'] = hierarchy_info['category']

            # Set subcategory if we're in a nested level
            pre_config['subcategory'] = hierarchy_info['subcategory_path']

            pre_config['hierarchy_path'] = hierarchy_path

        elif context_type == CATEGORY_ITEM:
            # Category item - pre-select based on the clicked item
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
                    # In root column - need to refresh the child column if it exists
                    project_category = project_info.get('category')

                    if project_category and len(parent_window.columns) > 1:
                        # There's a second column showing content for a category
                        # Check if it matches the project's category
                        second_column = parent_window.columns[1]
                        if second_column.current_path and second_column.current_path.startswith(f"cat:{project_category}"):
                            # Refresh the second column to show the new project
                            second_column.load_mixed_content(
                                parent_window.categories,
                                second_column.current_path,
                                parent_window.projects
                            )
                            logger.info(f"Refreshed second column for category: {project_category}")

                    logger.info(f"Project added from root: {name}")
                else:
                    # In a child column - refresh to show the new project
                    if hasattr(column_browser, 'load_mixed_content'):
                        column_browser.load_mixed_content(
                            parent_window.categories,
                            column_browser.current_path,
                            parent_window.projects
                        )

                logger.info(f"Project added: {name} (category: {project_info.get('category')}, subcategory: {project_info.get('subcategory')})")

            except Exception as e:
                logger.error(f"Error adding project: {e}", exc_info=True)
                show_error_dialog(parent_window, f"Error al agregar proyecto: {e}")

        # Call show_add_project_dialog with pre_config
        show_add_project_dialog(
            parent_window,
            parent_window.categories,
            on_add_callback,
            pre_config=pre_config
        )

    except Exception as e:
        logger.error(f"Error in add project action: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error al abrir diálogo de proyecto: {e}")


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
            show_error_dialog(parent_window, "Error: No se encontró la ruta del proyecto")
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
        show_error_dialog(parent_window, f"Error al abrir proyecto en VSCode: {e}")


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
            show_error_dialog(parent_window, "Error: No se encontró la ruta del proyecto")
            return

        logger.debug(f"Opening project in Kiro: {project_path}")

        # Open Kiro with the project path
        import subprocess
        try:
            subprocess.Popen(['kiro', project_path])
            logger.info(f"Successfully opened project in Kiro: {project_path}")
        except FileNotFoundError:
            logger.error("Kiro command not found")
            show_error_dialog(parent_window, "Error: Kiro no está instalado o no está en el PATH")
        except Exception as e:
            logger.error(f"Error launching Kiro: {e}")
            show_error_dialog(parent_window, f"Error al abrir Kiro: {e}")

    except Exception as e:
        logger.error(f"Error opening project in Kiro: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error al abrir proyecto en Kiro: {e}")


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
            message_parts.append(f"{subcategories_count} subcategoría(s)")
        if len(projects_to_delete) > 0:
            message_parts.append(f"{len(projects_to_delete)} proyecto(s)")

        if message_parts:
            secondary_text = f"Esta acción eliminará:\n- " + "\n- ".join(message_parts) + "\n\n¿Continuar?"
        else:
            secondary_text = "Esta categoría está vacía. ¿Eliminarla?"

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"¿Eliminar categoría '{parts[-1]}'?"
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
        show_error_dialog(parent_window, f"Error al eliminar categoría: {e}")


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
            title="Renombrar Categoría",
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

        label = Gtk.Label(label=f"Nuevo nombre para '{old_name}':")
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

        # Save changes
        parent_window.config.save_categories(parent_window.categories)

        # Refresh interface
        parent_window.reload_interface()

    except Exception as e:
        logger.error(f"Error renaming category: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error al renombrar categoría: {e}")


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
            show_error_dialog(parent_window, "No se encontró el proyecto")
            return

        # Confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"¿Eliminar proyecto '{project_name}'?"
        )
        dialog.format_secondary_text(
            "Esta acción solo eliminará el proyecto de la lista.\n"
            "Los archivos en el disco NO serán eliminados."
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
                    parent_window.projects
                )

    except Exception as e:
        logger.error(f"Error deleting project: {e}", exc_info=True)
        show_error_dialog(parent_window, f"Error al eliminar proyecto: {e}")
