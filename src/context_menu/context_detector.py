#!/usr/bin/env python3
"""
Context detection for right-click events
"""

import logging

logger = logging.getLogger(__name__)

# Context type constants
ROOT_COLUMN = "root_column"
CHILD_COLUMN = "child_column"
CATEGORY_ITEM = "category_item"
PROJECT_ITEM = "project_item"


def detect_context(column_browser, event):
    """
    Detect the context of the right-click event

    Args:
        column_browser: ColumnBrowser instance
        event: Gdk.EventButton from right-click

    Returns:
        Dictionary with context information:
        {
            'type': str,  # ROOT_COLUMN, CHILD_COLUMN, CATEGORY_ITEM, PROJECT_ITEM
            'hierarchy_path': str,  # Current hierarchy path
            'item_path': str | None,  # Path of clicked item (if any)
            'is_project': bool  # True if clicked item is a project
        }
    """
    context = {
        'type': None,
        'hierarchy_path': None,
        'item_path': None,
        'is_project': False
    }

    # Get the current hierarchy path from the column
    current_path = column_browser.current_path
    context['hierarchy_path'] = current_path

    # Try to get the item at the click position using helper method
    tree_path, column = column_browser.get_item_at_position(event.x, event.y)

    if tree_path is not None:
        # Clicked on an item
        model = column_browser.treeview.get_model()
        iter = model.get_iter(tree_path)
        item_path = model.get_value(iter, 1)  # full_path column
        context['item_path'] = item_path

        # Determine if it's a project or category item
        if item_path.startswith("cat:"):
            context['type'] = CATEGORY_ITEM
            context['is_project'] = False
        else:
            # It's a project (path doesn't start with "cat:")
            context['type'] = PROJECT_ITEM
            context['is_project'] = True
    else:
        # Clicked on empty area of column
        # Determine if it's root or child column using helper method
        if column_browser.is_root_column():
            context['type'] = ROOT_COLUMN
        else:
            context['type'] = CHILD_COLUMN

    logger.debug(f"Detected context: {context}")
    return context


def get_hierarchy_info(hierarchy_path):
    """
    Parse hierarchy path to extract level and category information

    Args:
        hierarchy_path: str - Hierarchy path (e.g., "cat:Web:Frontend")

    Returns:
        Dictionary with:
        {
            'level': int,  # 0 for root, 1+ for nested
            'category': str | None,  # Main category name
            'subcategory_path': str | None,  # Subcategory path
            'full_path': str  # Full hierarchy path
        }
    """
    hierarchy_info = {
        'level': 0,
        'category': None,
        'subcategory_path': None,
        'full_path': hierarchy_path or ""
    }

    if not hierarchy_path or hierarchy_path == "categories":
        # Root level
        hierarchy_info['level'] = 0
        return hierarchy_info

    # Parse the hierarchy path
    if hierarchy_path.startswith("cat:"):
        parts = hierarchy_path.split(":")[1:]  # Remove "cat:" prefix
        hierarchy_info['level'] = len(parts)

        if len(parts) >= 1:
            hierarchy_info['category'] = parts[0]

        if len(parts) > 1:
            hierarchy_info['subcategory_path'] = ":".join(parts[1:])

    elif hierarchy_path.startswith("projects:"):
        # Projects view - extract the category path
        cat_path = hierarchy_path.split(":", 1)[1]
        if cat_path.startswith("cat:"):
            parts = cat_path.split(":")[1:]
            hierarchy_info['level'] = len(parts)
            if len(parts) >= 1:
                hierarchy_info['category'] = parts[0]
            if len(parts) > 1:
                hierarchy_info['subcategory_path'] = ":".join(parts[1:])

    logger.debug(f"Hierarchy info for '{hierarchy_path}': {hierarchy_info}")
    return hierarchy_info
