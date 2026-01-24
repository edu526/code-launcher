"""
Path validation utilities for VSCode Launcher
"""

import os

def is_project_path(path):
    """Validar si un path es un proyecto válido (no categoría)"""
    if not path:
        return False

    # Excluir categorías y elementos especiales
    if (path.startswith("category:") or
        path.startswith("categories") or
        path.startswith("cat:") or
        path.startswith("projects:")):
        return False

    # Aceptar paths reales de proyectos
    if (path.startswith("/") or
        path.startswith("~/") or
        (":" not in path and not path.startswith("cat"))):
        return True

    return False

def resolve_project_path(selected_path, projects_config):
    """Resolver path real del proyecto desde la configuración"""
    if os.path.exists(selected_path):
        return selected_path

    # Buscar en la configuración de proyectos
    for project_name, project_info in projects_config.items():
        if isinstance(project_info, str):
            if project_info == selected_path:
                return project_info
        else:
            if project_info.get("path", "") == selected_path:
                return project_info.get("path", "")

    return None