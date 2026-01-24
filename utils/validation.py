"""
Path validation utilities for Code Launcher
"""

import os

def is_project_path(path):
    """Validate if a path is a valid project (not a category)"""
    if not path:
        return False

    # Exclude categories and special elements
    if (path.startswith("category:") or
        path.startswith("categories") or
        path.startswith("cat:") or
        path.startswith("projects:")):
        return False

    # Accept real project paths
    if (path.startswith("/") or
        path.startswith("~/") or
        (":" not in path and not path.startswith("cat"))):
        return True

    return False

def resolve_project_path(selected_path, projects_config):
    """Resolve real project path from configuration"""
    if os.path.exists(selected_path):
        return selected_path

    # Search in projects configuration
    for project_name, project_info in projects_config.items():
        if isinstance(project_info, str):
            if project_info == selected_path:
                return project_info
        else:
            if project_info.get("path", "") == selected_path:
                return project_info.get("path", "")

    return None