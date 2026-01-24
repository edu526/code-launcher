#!/usr/bin/env python3
"""
Navigation and column management for VSCode Project Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from src.ui.column_browser import ColumnBrowser


class NavigationManager:
    """Manages column navigation and hierarchy"""

    def __init__(self, window):
        """
        Initialize navigation manager

        Args:
            window: FinderStyleWindow instance
        """
        self.window = window

    def add_column(self, path=None, column_type="directory"):
        """
        Add a new column to the interface

        Args:
            path: Path for the column content
            column_type: Type of column (categories, hierarchy, mixed, projects, directory)

        Returns:
            ColumnBrowser instance
        """
        if column_type not in ["categories", "hierarchy", "mixed", "projects", "directory"]:
            raise ValueError(f"Invalid column_type: {column_type}")

        column = ColumnBrowser(self.on_column_selection, column_type, self.window)

        # Mapeo de tipos a métodos de carga
        loaders = {
            "categories": lambda: column.load_hierarchy_level(self.window.categories, None),
            "hierarchy": lambda: column.load_hierarchy_level(self.window.categories, path),
            "mixed": lambda: column.load_mixed_content(self.window.categories, path, self.window.projects),
            "projects": lambda: column.load_projects_at_level(path, self.window.projects),
            "directory": lambda: column.load_directory(path)
        }

        loaders[column_type]()
        self._pack_column(column)
        return column

    def _pack_column(self, column):
        """
        Pack and display a column

        Args:
            column: ColumnBrowser instance
        """
        self.window.columns.append(column)
        self.window.columns_box.pack_start(column, True, True, 1)
        column.show_all()

    def on_column_selection(self, path, is_dir):
        """
        Handle column selection events

        Args:
            path: Selected path
            is_dir: Whether the selection is a directory
        """
        self.window.selected_path = path

        # Determinar qué hacer según el tipo de selección
        if path and path.startswith("cat:"):
            self._handle_category_selection(path)
        elif path and path.startswith("categories"):
            # Se está en la vista de categorías
            pass
        else:
            # Es un proyecto o directorio normal - no expandir más
            pass

    def _handle_category_selection(self, hierarchy_path):
        """
        Handle category/subcategory selection

        Args:
            hierarchy_path: Hierarchy path (e.g., "cat:Web:Frontend")
        """
        # Analizar el path para determinar el nivel
        path_parts = hierarchy_path.split(":")
        if len(path_parts) < 2:
            return

        # Determinar el nivel de profundidad
        depth_level = len(path_parts) - 1

        # Eliminar columnas a la derecha del nivel seleccionado
        target_columns_count = depth_level + 1

        while len(self.window.columns) > target_columns_count:
            old_column = self.window.columns.pop()
            self.window.columns_box.remove(old_column)

        # Crear o recargar columna para el contenido
        if len(self.window.columns) == target_columns_count - 1:
            # Crear nueva columna mixta
            mixed_column = self.add_column(hierarchy_path, "mixed")
            mixed_column.current_path = hierarchy_path
        else:
            # Recargar columna existente
            if len(self.window.columns) > 0 and len(self.window.columns) > depth_level:
                existing_column = self.window.columns[depth_level]
                existing_column.load_mixed_content(
                    self.window.categories,
                    hierarchy_path,
                    self.window.projects
                )
                existing_column.current_path = hierarchy_path

    def reload_interface(self):
        """Reload the entire interface"""
        # Limpiar columnas
        for column in self.window.columns:
            self.window.columns_box.remove(column)
        self.window.columns.clear()

        # Recargar configuración
        self.window.categories = self.window.config.load_categories()
        self.window.projects = self.window.config.load_projects()

        # Crear primera columna con categorías
        self.add_column(None, "categories")

    def select_first_category(self):
        """Select the first category automatically"""
        if self.window.columns and len(self.window.columns) > 0:
            first_column = self.window.columns[0]
            if first_column.current_path == "categories":
                first_column.select_first_item()
        return False
