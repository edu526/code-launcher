#!/usr/bin/env python3
"""
Project addition dialog
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os


def show_add_project_dialog(parent, categories, on_add_callback, pre_config=None):
    """Mostrar diálogo para añadir nuevo proyecto

    Args:
        parent: Parent window
        categories: Categories dictionary
        on_add_callback: Callback function
        pre_config: Optional dictionary with:
            {
                'category': str | None,         # Pre-select category
                'subcategory': str | None,      # Pre-select subcategory
                'hierarchy_path': str | None    # Full hierarchy path
            }
    """
    # Extract pre-configuration parameters
    pre_category = None
    pre_subcategory = None
    hierarchy_path = None
    disable_selection = False

    if pre_config:
        pre_category = pre_config.get('category')
        pre_subcategory = pre_config.get('subcategory')
        hierarchy_path = pre_config.get('hierarchy_path')
        # Disable selection if ANY pre-configuration is provided (from context menu)
        disable_selection = pre_config is not None and (pre_category is not None or hierarchy_path is not None)

    dialog = Gtk.Dialog(
        title="Añadir Nuevo Proyecto",
        transient_for=parent,
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

    # Nombre del proyecto
    name_label = Gtk.Label(label="Nombre del proyecto:")
    content.pack_start(name_label, False, False, 0)

    name_entry = Gtk.Entry()
    name_entry.set_sensitive(False)  # Disabled - se llena automáticamente
    name_entry.set_placeholder_text("Se llenará automáticamente al seleccionar carpeta")
    content.pack_start(name_entry, False, False, 0)

    # Ruta del proyecto
    path_label = Gtk.Label(label="Ruta del proyecto:")
    content.pack_start(path_label, False, False, 0)

    path_entry = Gtk.Entry()
    path_entry.set_sensitive(False)  # Disabled - se llena automáticamente
    path_entry.set_placeholder_text("Se llenará automáticamente al seleccionar carpeta")
    content.pack_start(path_entry, False, False, 0)

    # Botón para seleccionar carpeta
    def on_select_folder(button):
        folder_dialog = Gtk.FileChooserDialog(
            title="Seleccionar Carpeta del Proyecto",
            parent=parent,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        folder_dialog.set_transient_for(parent)
        folder_dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        folder_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        response = folder_dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = folder_dialog.get_filename()
            path_entry.set_text(folder)

            # Auto-populate project name from directory name
            dir_name = os.path.basename(folder)
            if dir_name:
                name_entry.set_text(dir_name)

        folder_dialog.destroy()

    folder_btn = Gtk.Button(label="Seleccionar Carpeta...")
    folder_btn.connect("clicked", on_select_folder)
    content.pack_start(folder_btn, False, False, 0)

    # Categoría y Subcategoría
    cat_label = Gtk.Label(label="Categoría:")
    content.pack_start(cat_label, False, False, 0)

    cat_combo = Gtk.ComboBoxText()
    sorted_categories = sorted(categories.keys())
    for cat_name in sorted_categories:
        cat_combo.append_text(cat_name)

    # Pre-select category if provided
    if pre_category and pre_category in categories:
        try:
            cat_index = sorted_categories.index(pre_category)
            cat_combo.set_active(cat_index)
        except ValueError:
            cat_combo.set_active(0)
    else:
        cat_combo.set_active(0)

    # Disable category selection if pre-configured
    if disable_selection:
        cat_combo.set_sensitive(False)

    content.pack_start(cat_combo, False, False, 0)

    subcat_label = Gtk.Label(label="Subcategoría (opcional):")
    content.pack_start(subcat_label, False, False, 0)

    subcat_combo = Gtk.ComboBoxText()
    subcat_combo.append_text("")  # Opción vacía para sin subcategoría

    def update_subcategories(combo):
        """Actualizar subcategorías basadas en la categoría seleccionada"""
        cat_name = cat_combo.get_active_text()
        subcat_combo.remove_all()
        subcat_combo.append_text("")  # Opción vacía

        if cat_name and cat_name in categories:
            subcategories = categories[cat_name].get("subcategories", {})
            sorted_subcats = sorted(subcategories.keys())
            for sub_name in sorted_subcats:
                subcat_combo.append_text(sub_name)

            # Pre-select subcategory if provided and category matches
            if pre_subcategory and pre_subcategory in subcategories:
                try:
                    # +1 because index 0 is the empty option
                    sub_index = sorted_subcats.index(pre_subcategory) + 1
                    subcat_combo.set_active(sub_index)
                except ValueError:
                    subcat_combo.set_active(0)
            else:
                subcat_combo.set_active(0)

            # Disable subcategory selection if pre-configured
            if disable_selection:
                subcat_combo.set_sensitive(False)
        else:
            subcat_combo.set_active(0)

    cat_combo.connect("changed", update_subcategories)
    update_subcategories(None)  # Cargar subcategorías iniciales

    content.pack_start(subcat_combo, False, False, 0)

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        name = name_entry.get_text().strip()
        path = path_entry.get_text().strip()
        category = cat_combo.get_active_text()
        subcategory = subcat_combo.get_active_text()

        if name and path:
            project_info = {
                "path": path,
                "category": category
            }
            if subcategory:
                project_info["subcategory"] = subcategory

            if on_add_callback:
                on_add_callback(name, project_info)

    dialog.destroy()
