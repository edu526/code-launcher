#!/usr/bin/env python3
"""
Módulo del navegador de columnas estilo Finder
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GLib
import os
from src.context_menu.handler import ContextMenuHandler

class ColumnBrowser(Gtk.ScrolledWindow):
    """Widget de columna individual estilo Finder"""
    def __init__(self, callback, column_type="directory", parent_window=None):
        super().__init__()
        self.callback = callback
        self.parent_window = parent_window  # Referencia a la ventana principal
        self.current_path = None
        self.column_type = column_type  # "directory", "categories", "projects"

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_min_content_width(200)
        self.set_shadow_type(Gtk.ShadowType.IN)

        # Lista de items
        self.store = Gtk.ListStore(str, str, bool, str)  # display_name, full_path, is_dir, icon_name
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_headers_visible(False)
        self.treeview.set_enable_search(False)

        # Columna con icono y nombre
        column = Gtk.TreeViewColumn()

        # Renderer para icono
        icon_renderer = Gtk.CellRendererPixbuf()
        column.pack_start(icon_renderer, False)
        column.set_cell_data_func(icon_renderer, self.icon_data_func)

        # Renderer para texto
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
        column.pack_start(text_renderer, True)
        column.add_attribute(text_renderer, "text", 0)

        self.treeview.append_column(column)

        # Selección
        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_selection_changed)

        # Doble clic
        self.treeview.connect("row-activated", self.on_row_activated)

        # Context menu setup
        self.context_menu_handler = None
        if parent_window:
            self.context_menu_handler = ContextMenuHandler(self, parent_window)
            self.treeview.connect("button-press-event", self.context_menu_handler.on_button_press)

        self.add(self.treeview)

    def icon_data_func(self, column, cell, model, iter, data):
        """Asignar icono según el tipo"""
        icon_name = model.get_value(iter, 3)
        cell.set_property("icon-name", icon_name)

    def on_selection_changed(self, selection):
        """Cuando se selecciona un item"""
        model, iter = selection.get_selected()
        if iter:
            path = model.get_value(iter, 1)
            self.callback(path, True)

    def on_row_activated(self, treeview, path, column):
        """Doble clic en un item"""
        model = treeview.get_model()
        iter = model.get_iter(path)
        full_path = model.get_value(iter, 1)

        # Si es una categoría (empieza con "cat:"), navegar a ella
        if full_path and full_path.startswith("cat:"):
            # Salir del modo búsqueda y navegar a la categoría
            if self.parent_window:
                # Limpiar la búsqueda
                if hasattr(self.parent_window, 'search_entry'):
                    self.parent_window.search_entry.set_text("")

                # Recargar la interfaz normal
                self.parent_window.reload_interface()

                # Navegar a la categoría seleccionada
                # Usar GLib.idle_add para asegurar que la interfaz se recargó primero
                GLib.idle_add(self._navigate_to_category, full_path)
        else:
            # Es un proyecto - abrir con el editor por defecto
            if self.parent_window:
                default_editor = getattr(self.parent_window, 'default_editor', 'kiro')
                if default_editor == "vscode":
                    self.parent_window.open_vscode_project(full_path)
                else:
                    self.parent_window.open_kiro_project(full_path)

    def _navigate_to_category(self, category_path):
        """
        Navigate to a specific category after interface reload

        Args:
            category_path: Category path (e.g., "cat:Web:Frontend")
        """
        # Parsear el path de la categoría
        parts = category_path.split(":")[1:]  # Remove "cat:" prefix

        if not parts:
            return False

        # Navegar nivel por nivel
        current_path = None
        for i, part in enumerate(parts):
            if i == 0:
                # Primer nivel - seleccionar en la primera columna
                current_path = f"cat:{part}"
            else:
                # Niveles anidados
                current_path = f"{current_path}:{part}"

            # Buscar la columna correspondiente
            if i < len(self.parent_window.columns):
                column = self.parent_window.columns[i]

                # Buscar el item en la columna
                iter = column.store.get_iter_first()
                while iter:
                    item_path = column.store.get_value(iter, 1)
                    if item_path == current_path:
                        # Seleccionar este item
                        selection = column.treeview.get_selection()
                        selection.select_iter(iter)

                        # Disparar el evento de selección
                        self.parent_window.navigation_manager.on_column_selection(current_path, True)
                        break
                    iter = column.store.iter_next(iter)

        return False



    def load_directory(self, path):
        """Cargar contenido de un directorio - solo mostrar directorios"""
        self.store.clear()
        self.current_path = path

        if not path or not os.path.exists(path):
            return

        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                # Saltar archivos ocultos
                if item.startswith('.'):
                    continue

                # Solo mostrar directorios
                if not os.path.isdir(item_path):
                    continue

                items.append((item, item_path))

            # Ordenar alfabéticamente
            items.sort(key=lambda x: x[0].lower())

            for display_name, full_path in items:
                self.store.append([display_name, full_path, True, "folder"])

        except PermissionError:
            pass

    def load_categories(self, categories):
        """Cargar solo categorías principales en la columna"""
        self.store.clear()
        self.current_path = "categories"

        # Ordenar categorías alfabéticamente
        sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())

        for category_name, category_info in sorted_categories:
            icon_name = category_info.get("icon", "folder")
            self.store.append([category_name, f"category:{category_name}", True, icon_name])

    def load_hierarchy_level(self, categories, hierarchy_path=None):
        """Cargar un nivel específico de la jerarquía"""
        self.store.clear()

        if hierarchy_path is None:
            # Nivel raíz: mostrar categorías principales
            self.current_path = "categories"

            sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())
            for category_name, category_info in sorted_categories:
                icon_name = category_info.get("icon", "folder")
                self.store.append([category_name, f"cat:{category_name}", True, icon_name])
        else:
            # Nivel anidado: parsear el path
            parts = hierarchy_path.split(":")[1:]  # Ignorar el primer "cat"

            if len(parts) == 1:
                # Segundo nivel: subcategorías de categoría principal
                category_name = parts[0]
                self.current_path = f"cat:{category_name}"

                if category_name in categories:
                    cat_info = categories[category_name]

                    # Cargar subcategorías
                    subcategories = cat_info.get("subcategories", {})
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                    for sub_name, sub_info in sorted_subcats:
                        sub_icon = sub_info.get("icon", "folder")
                        self.store.append([sub_name, f"cat:{category_name}:{sub_name}", True, sub_icon])
            else:
                # Niveles más profundos: subcategorías anidadas
                current_categories = categories
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:  # No el último elemento
                        if part in current_categories:
                            current_categories = current_categories[part].get("subcategories", {})
                        else:
                            current_categories = {}
                            break
                    else:  # Último elemento
                        if part in current_categories:
                            subcat_info = current_categories[part]
                            subcategories = subcat_info.get("subcategories", {})
                            sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                            for sub_name, sub_info in sorted_subcats:
                                sub_icon = sub_info.get("icon", "folder")
                                full_path = f"cat:{':'.join(parts)}:{sub_name}"
                                self.store.append([sub_name, full_path, True, sub_icon])

        self.current_path = hierarchy_path or "categories"

    def load_projects_at_level(self, hierarchy_path, projects):
        """Cargar proyectos correspondientes al nivel actual de jerarquía"""
        self.store.clear()
        self.current_path = f"projects:{hierarchy_path}"

        # Parsear el path de jerarquía
        if not hierarchy_path or hierarchy_path == "categories":
            # Proyectos sin categoría (raíz)
            category_name = None
            subcategory_path = None
        else:
            parts = hierarchy_path.split(":")[1:]  # Ignorar el primer "cat"
            if len(parts) == 1:
                category_name = parts[0]
                subcategory_path = None
            else:
                category_name = parts[0]
                subcategory_path = ":".join(parts[1:])

        # Filtrar proyectos
        category_projects = []
        for project_name, project_info in projects.items():
            if isinstance(project_info, str):
                project_path = project_info
                project_category = None
                project_subcategory = None
            else:
                project_path = project_info.get("path", "")
                project_category = project_info.get("category", None)
                project_subcategory = project_info.get("subcategory", None)

            # Filtrar por jerarquía
            if category_name:
                if project_category == category_name:
                    if subcategory_path:
                        # Verificar si la subcategoría del proyecto coincide con el path actual
                        if project_subcategory:
                            project_sub_path = project_subcategory
                            if subcategory_path == project_sub_path or project_sub_path.startswith(subcategory_path + ":"):
                                category_projects.append((project_name, project_path))
                    else:
                        # Si no hay subcategoría especificada, mostrar proyectos sin subcategoría
                        if not project_subcategory:
                            category_projects.append((project_name, project_path))
            else:
                # Mostrar proyectos sin categoría
                if not project_category:
                    category_projects.append((project_name, project_path))

        # Ordenar proyectos alfabéticamente
        category_projects.sort(key=lambda x: x[0].lower())

        for project_name, project_path in category_projects:
            self.store.append([project_name, project_path, True, "code"])



    def load_mixed_content(self, categories, hierarchy_path, projects):
        """Cargar subcategorías y proyectos juntos en la misma columna"""
        self.store.clear()
        self.current_path = hierarchy_path

        # Cargar subcategorías primero
        if not hierarchy_path or hierarchy_path == "categories":
            # Cargar subcategorías de categorías principales
            sorted_categories = sorted(categories.items(), key=lambda x: x[0].lower())

            for category_name, category_info in sorted_categories:
                subcategories = category_info.get("subcategories", {})
                if subcategories:
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                    for sub_name, sub_info in sorted_subcats:
                        sub_icon = sub_info.get("icon", "folder")
                        sub_path = f"cat:{category_name}:{sub_name}"
                        self.store.append([sub_name, sub_path, True, sub_icon])
        else:
            # Cargar subcategorías anidadas
            parts = hierarchy_path.split(":")[1:]  # Ignorar el primer "cat"
            current_categories = categories

            # Navegar hasta el nivel actual
            for i, part in enumerate(parts):
                if part in current_categories:
                    if i == len(parts) - 1:  # Último nivel
                        subcategories = current_categories[part].get("subcategories", {})
                        if subcategories:
                            sorted_subcats = sorted(subcategories.items(), key=lambda x: x[0].lower())

                            for sub_name, sub_info in sorted_subcats:
                                sub_icon = sub_info.get("icon", "folder")
                                full_path = f"cat:{':'.join(parts)}:{sub_name}"
                                self.store.append([sub_name, full_path, True, sub_icon])
                    else:
                        current_categories = current_categories[part].get("subcategories", {})

        # Cargar proyectos del nivel actual
        if not hierarchy_path or hierarchy_path == "categories":
            # Proyectos sin categoría
            category_name = None
            subcategory_path = None
        else:
            parts = hierarchy_path.split(":")[1:]
            if len(parts) == 1:
                category_name = parts[0]
                subcategory_path = None
            else:
                category_name = parts[0]
                subcategory_path = ":".join(parts[1:])

        # Filtrar y agregar proyectos
        for project_name, project_info in projects.items():
            if isinstance(project_info, str):
                project_path = project_info
                project_category = None
                project_subcategory = None
            else:
                project_path = project_info.get("path", "")
                project_category = project_info.get("category", None)
                project_subcategory = project_info.get("subcategory", None)

            # Verificar si el proyecto pertenece al nivel actual
            belongs_to_level = False
            if category_name:
                if project_category == category_name:
                    if subcategory_path:
                        if project_subcategory:
                            project_sub_path = project_subcategory
                            if subcategory_path == project_sub_path or project_sub_path.startswith(subcategory_path + ":"):
                                belongs_to_level = True
                    else:
                        # Si no hay subcategoría especificada, mostrar proyectos sin subcategoría
                        if not project_subcategory:
                            belongs_to_level = True
            else:
                # Mostrar proyectos sin categoría
                if not project_category:
                    belongs_to_level = True

            if belongs_to_level:
                self.store.append([project_name, project_path, True, "code"])

    def get_selected_path(self):
        """Obtener el path seleccionado actualmente"""
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            return model.get_value(iter, 1)
        return None

    def select_first_item(self):
        """Seleccionar el primer item de la lista"""
        first_iter = self.store.get_iter_first()
        if first_iter:
            selection = self.treeview.get_selection()
            selection.select_iter(first_iter)

            # Disparar el evento de selección manualmente
            path = self.store.get_value(first_iter, 1)
            self.callback(path, True)

    def get_item_at_position(self, x, y):
        """
        Get the item (if any) at the given coordinates

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of (TreePath, TreeViewColumn) or (None, None)
        """
        path_info = self.treeview.get_path_at_pos(int(x), int(y))
        if path_info is not None:
            tree_path, column, cell_x, cell_y = path_info
            return (tree_path, column)
        return (None, None)

    def is_root_column(self):
        """
        Check if this column is the root categories column

        Returns:
            True if current_path is "categories" or None
        """
        return self.current_path is None or self.current_path == "categories"

    def get_hierarchy_info(self):
        """
        Extract hierarchy information from current_path

        Returns:
            Dictionary with:
            {
                'level': int,  # 0 for root, 1+ for nested
                'category': str | None,
                'subcategory_path': str | None,
                'full_path': str
            }
        """
        hierarchy_info = {
            'level': 0,
            'category': None,
            'subcategory_path': None,
            'full_path': self.current_path or ""
        }

        current_path = self.current_path

        if not current_path or current_path == "categories":
            # Root level
            hierarchy_info['level'] = 0
            return hierarchy_info

        # Parse the hierarchy path
        if current_path.startswith("cat:"):
            parts = current_path.split(":")[1:]  # Remove "cat:" prefix
            hierarchy_info['level'] = len(parts)

            if len(parts) >= 1:
                hierarchy_info['category'] = parts[0]

            if len(parts) > 1:
                hierarchy_info['subcategory_path'] = ":".join(parts[1:])

        elif current_path.startswith("projects:"):
            # Projects view - extract the category path
            cat_path = current_path.split(":", 1)[1]
            if cat_path.startswith("cat:"):
                parts = cat_path.split(":")[1:]
                hierarchy_info['level'] = len(parts)
                if len(parts) >= 1:
                    hierarchy_info['category'] = parts[0]
                if len(parts) > 1:
                    hierarchy_info['subcategory_path'] = ":".join(parts[1:])

        return hierarchy_info