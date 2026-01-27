#!/usr/bin/env python3
"""
File addition dialog
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os


def show_add_file_dialog(parent, categories, on_add_callback, pre_config=None):
    """Show dialog to add new file

    Args:
        parent: Parent window
        categories: Categories dictionary
        on_add_callback: Callback function
        pre_config: Optional dictionary with:
            {
                'category': str | None,
                'subcategory': str | None,
                'hierarchy_path': str | None
            }
    """
    pre_category = None
    pre_subcategory = None
    hierarchy_path = None
    disable_selection = False

    if pre_config:
        pre_category = pre_config.get('category')
        pre_subcategory = pre_config.get('subcategory')
        hierarchy_path = pre_config.get('hierarchy_path')
        disable_selection = pre_config is not None and (pre_category is not None or hierarchy_path is not None)

    dialog = Gtk.Dialog(
        title="Add New File",
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

    # File name
    name_label = Gtk.Label(label="File name:")
    content.pack_start(name_label, False, False, 0)

    name_entry = Gtk.Entry()
    name_entry.set_sensitive(False)
    name_entry.set_placeholder_text("Will be auto-filled when selecting file")
    content.pack_start(name_entry, False, False, 0)

    # File path
    path_label = Gtk.Label(label="File path:")
    content.pack_start(path_label, False, False, 0)

    path_entry = Gtk.Entry()
    path_entry.set_sensitive(False)
    path_entry.set_placeholder_text("Will be auto-filled when selecting file")
    content.pack_start(path_entry, False, False, 0)

    # Button to select file
    def on_select_file(button):
        file_dialog = Gtk.FileChooserDialog(
            title="Select File",
            parent=parent,
            action=Gtk.FileChooserAction.OPEN
        )
        file_dialog.set_transient_for(parent)
        file_dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        file_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        response = file_dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = file_dialog.get_filename()
            path_entry.set_text(file_path)

            # Auto-populate file name
            file_name = os.path.basename(file_path)
            if file_name:
                name_entry.set_text(file_name)

        file_dialog.destroy()

    file_btn = Gtk.Button(label="Select File...")
    file_btn.connect("clicked", on_select_file)
    content.pack_start(file_btn, False, False, 0)

    # Category and Subcategory
    cat_label = Gtk.Label(label="Category:")
    content.pack_start(cat_label, False, False, 0)

    cat_combo = Gtk.ComboBoxText()

    # Add "(None)" option for root level
    cat_combo.append_text("(None)")

    sorted_categories = sorted(categories.keys())
    for cat_name in sorted_categories:
        cat_combo.append_text(cat_name)

    if pre_category and pre_category in categories:
        try:
            # +1 because index 0 is "(None)"
            cat_index = sorted_categories.index(pre_category) + 1
            cat_combo.set_active(cat_index)
        except ValueError:
            cat_combo.set_active(0)
    else:
        # No pre-selection - select "(None)" for root level
        cat_combo.set_active(0)

    if disable_selection:
        cat_combo.set_sensitive(False)

    content.pack_start(cat_combo, False, False, 0)

    subcat_label = Gtk.Label(label="Subcategory (optional):")
    content.pack_start(subcat_label, False, False, 0)

    subcat_combo = Gtk.ComboBoxText()
    subcat_combo.append_text("")

    def update_subcategories(combo):
        """Update subcategories based on selected category"""
        cat_name = cat_combo.get_active_text()
        subcat_combo.remove_all()
        subcat_combo.append_text("")

        if cat_name and cat_name in categories:
            subcategories = categories[cat_name].get("subcategories", {})
            sorted_subcats = sorted(subcategories.keys())
            for sub_name in sorted_subcats:
                subcat_combo.append_text(sub_name)

            if pre_subcategory and pre_subcategory in subcategories:
                try:
                    sub_index = sorted_subcats.index(pre_subcategory) + 1
                    subcat_combo.set_active(sub_index)
                except ValueError:
                    subcat_combo.set_active(0)
            else:
                subcat_combo.set_active(0)

            if disable_selection:
                subcat_combo.set_sensitive(False)
        else:
            subcat_combo.set_active(0)

    cat_combo.connect("changed", update_subcategories)
    update_subcategories(None)

    content.pack_start(subcat_combo, False, False, 0)

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        name = name_entry.get_text().strip()
        path = path_entry.get_text().strip()
        category = cat_combo.get_active_text()
        subcategory = subcat_combo.get_active_text()

        if name and path:
            file_info = {
                "path": path
            }

            # Only add category if it's not "(None)"
            if category and category != "(None)":
                file_info["category"] = category

                # Only add subcategory if category exists and subcategory is not empty
                if subcategory:
                    file_info["subcategory"] = subcategory

            if on_add_callback:
                on_add_callback(name, file_info)

    dialog.destroy()
