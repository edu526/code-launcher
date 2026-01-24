"""
VSCode integration utilities for VSCode Launcher
"""

import subprocess
from .validation import is_project_path, resolve_project_path

def open_project_in_vscode(selected_path, projects_config, callback_on_success=None, error_callback=None):
    """Función unificada para abrir proyecto en VSCode"""
    # Validar que sea un proyecto
    if not is_project_path(selected_path):
        if error_callback:
            error_callback("No es un proyecto válido")
        return False

    # Resolver path real
    resolved_path = resolve_project_path(selected_path, projects_config)
    if not resolved_path:
        if error_callback:
            error_callback(f"No se encontró el proyecto '{selected_path}'")
        return False

    try:
        subprocess.Popen(['code', resolved_path])
        if callback_on_success:
            callback_on_success()
        return True
    except Exception as e:
        if error_callback:
            error_callback(f"Error abriendo VSCode: {e}")
        return False