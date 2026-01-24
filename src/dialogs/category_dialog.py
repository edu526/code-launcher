#!/usr/bin/env python3
"""
Category creation dialog
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def show_create_category_dialog(parent, categories, on_create_callback, pre_config=None):
    """Mostrar diálogo para crear nueva categoría o subcategoría

    Args:
        parent: Parent window
        categories: Categories dictionary
        on_create_callback: Callback function
        pre_config: Optional dictionary with:
            {
                'parent_category': str | None,  # Pre-select parent
                'force_subcategory': bool,      # Force subcategory mode
                'hierarchy_path': str | None    # Full hierarchy path
            }
    """
    # Extract pre-configuration parameters
    parent_category = None
    force_subcategory = False
    hierarchy_path = None

    if pre_config:
        parent_category = pre_config.get('parent_category')
        force_subcategory = pre_config.get('force_subcategory', False)
        hierarchy_path = pre_config.get('hierarchy_path')

    dialog = Gtk.Dialog(
        title="Crear Nueva Categoría/Subcategoría",
        transient_for=parent,
        flags=0,
        default_width=550,
        default_height=500
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

    # Tipo de creación
    type_label = Gtk.Label(label="Tipo:")
    content.pack_start(type_label, False, False, 0)

    type_combo = Gtk.ComboBoxText()
    type_combo.append_text("Categoría principal")
    type_combo.append_text("Subcategoría")

    # Set dialog mode based on pre-configuration
    if force_subcategory:
        type_combo.set_active(1)  # Subcategory mode
        type_combo.set_sensitive(False)  # Disable type selection
    else:
        type_combo.set_active(0)  # Category mode
        # Disable type selection if opened from context menu (pre_config exists)
        if pre_config:
            type_combo.set_sensitive(False)

    content.pack_start(type_combo, False, False, 0)

    # Categoría padre (solo para subcategorías)
    parent_label = Gtk.Label(label="Categoría padre:")
    content.pack_start(parent_label, False, False, 0)

    parent_combo = Gtk.ComboBoxText()
    for cat_name in sorted(categories.keys()):
        parent_combo.append_text(cat_name)

    # Pre-populate parent category if provided
    if parent_category:
        # Handle nested subcategories - parent_category might be "Category:Subcategory"
        if ":" in parent_category:
            # For nested subcategories, just show the full path in the combo
            # We'll need to handle this differently - for now just use the first part
            parent_parts = parent_category.split(":")
            parent_to_find = parent_parts[0]
        else:
            parent_to_find = parent_category

        if parent_to_find in categories:
            # Find the index of the parent category
            sorted_cats = sorted(categories.keys())
            try:
                parent_index = sorted_cats.index(parent_to_find)
                parent_combo.set_active(parent_index)
            except ValueError:
                if len(sorted_cats) > 0:
                    parent_combo.set_active(0)

            # Disable parent selection if pre-configured
            parent_combo.set_sensitive(False)
        else:
            # Parent category not found, select first if available
            if len(categories) > 0:
                parent_combo.set_active(0)
    else:
        # No parent category specified - don't select anything by default
        # Only set active if we're in subcategory mode
        if force_subcategory and len(categories) > 0:
            parent_combo.set_active(0)

    content.pack_start(parent_combo, False, False, 0)

    # Nombre
    name_label = Gtk.Label(label="Nombre:")
    content.pack_start(name_label, False, False, 0)

    name_entry = Gtk.Entry()
    name_entry.set_placeholder_text("Nombre de la categoría/subcategoría...")
    content.pack_start(name_entry, False, False, 0)

    # Icono fijo (sin selector)
    selected_icon = "folder"

    # Estado para validación
    state = {
        "selected_icon": "folder",
        "is_subcategory": False
    }

    # Función para actualizar visibilidad de categoría padre
    def on_type_changed(combo):
        is_subcategory = combo.get_active_text() == "Subcategoría"
        parent_label.set_visible(is_subcategory)
        parent_combo.set_visible(is_subcategory)
        state["is_subcategory"] = is_subcategory

        # Actualizar validación
        on_name_changed(None)

    # Función para validar nombre
    def on_name_changed(entry):
        name = name_entry.get_text().strip()
        ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)

        if not name:
            ok_button.set_sensitive(False)
            name_entry.get_style_context().remove_class("error")
            return

        if state["is_subcategory"]:
            # Validar subcategoría
            parent_cat = parent_combo.get_active_text()
            if (parent_cat in categories and
                "subcategories" in categories[parent_cat] and
                name in categories[parent_cat]["subcategories"]):
                ok_button.set_sensitive(False)
                name_entry.get_style_context().add_class("error")
            else:
                ok_button.set_sensitive(True)
                name_entry.get_style_context().remove_class("error")
        else:
            # Validar categoría principal
            if name in categories:
                ok_button.set_sensitive(False)
                name_entry.get_style_context().add_class("error")
            else:
                ok_button.set_sensitive(True)
                name_entry.get_style_context().remove_class("error")

    # Conectar señales
    type_combo.connect("changed", on_type_changed)
    name_entry.connect("changed", on_name_changed)

    dialog.show_all()

    # Estado inicial - show parent combo if force_subcategory is True
    # IMPORTANTE: Esto debe ir DESPUÉS de show_all() para que funcione
    if force_subcategory:
        parent_label.set_visible(True)
        parent_combo.set_visible(True)
        state["is_subcategory"] = True
    else:
        parent_label.set_visible(False)
        parent_combo.set_visible(False)

    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        name = name_entry.get_text().strip()
        description = ""  # Sin descripción
        is_subcategory = type_combo.get_active_text() == "Subcategoría"

        if name:
            if is_subcategory:
                parent_cat = parent_combo.get_active_text()
                if on_create_callback:
                    on_create_callback(name, description, selected_icon, parent_cat)
            else:
                if on_create_callback:
                    on_create_callback(name, description, selected_icon, None)

    dialog.destroy()
