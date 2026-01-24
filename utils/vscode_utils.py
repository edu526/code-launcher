"""
VSCode integration utilities for Code Launcher
"""

import subprocess
from .validation import is_project_path, resolve_project_path

def open_project_in_vscode(selected_path, projects_config, callback_on_success=None, error_callback=None):
    """Unified function to open project in VSCode"""
    # Validate that it's a project
    if not is_project_path(selected_path):
        if error_callback:
            error_callback("Not a valid project")
        return False

    # Resolve real path
    resolved_path = resolve_project_path(selected_path, projects_config)
    if not resolved_path:
        if error_callback:
            error_callback(f"Project '{selected_path}' not found")
        return False

    try:
        subprocess.Popen(['code', resolved_path])
        if callback_on_success:
            callback_on_success()
        return True
    except Exception as e:
        if error_callback:
            error_callback(f"Error opening VSCode: {e}")
        return False