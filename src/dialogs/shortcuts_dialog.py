#!/usr/bin/env python3
"""
Keyboard shortcuts reference dialog
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def show_shortcuts_dialog(parent):
    """Show keyboard shortcuts reference dialog"""
    dialog = Gtk.Dialog(
        title="Keyboard Shortcuts",
        flags=0,
        default_width=550,
        default_height=500
    )
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_modal(True)
    dialog.set_transient_for(parent)
    dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

    content = dialog.get_content_area()
    content.set_spacing(10)
    content.set_margin_start(20)
    content.set_margin_end(20)
    content.set_margin_top(20)
    content.set_margin_bottom(20)

    # Title
    title_label = Gtk.Label()
    title_label.set_markup("<big><b>Keyboard Shortcuts</b></big>")
    title_label.set_halign(Gtk.Align.START)
    content.pack_start(title_label, False, False, 0)

    # Scrolled window for shortcuts list
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.set_vexpand(True)

    # Grid for shortcuts
    grid = Gtk.Grid()
    grid.set_column_spacing(30)
    grid.set_row_spacing(10)
    grid.set_margin_start(10)
    grid.set_margin_top(10)

    # Shortcuts data: (shortcut, description, category)
    shortcuts = [
        ("Navigation", "", "header"),
        ("←", "Navigate to previous column", "normal"),
        ("→", "Navigate to next column", "normal"),
        ("↑", "Select previous item in column", "normal"),
        ("↓", "Select next item in column", "normal"),
        ("1-9", "Jump to item by number (1st-9th)", "normal"),
        ("", "", "separator"),

        ("Search & Quick Access", "", "header"),
        ("Ctrl+F", "Focus search bar", "normal"),
        ("Ctrl+R", "Show recent items", "normal"),
        ("@recent", "Type in search to show recents", "normal"),
        ("", "", "separator"),

        ("Actions", "", "header"),
        ("Ctrl+O / Enter", "Open selected item", "normal"),
        ("Ctrl+N", "Create new category", "normal"),
        ("Ctrl+P", "Add new project", "normal"),
        ("Ctrl+D", "Toggle favorite on selected item", "normal"),
        ("Esc", "Close launcher", "normal"),
    ]

    row = 0
    for shortcut, description, category in shortcuts:
        if category == "header":
            # Section header
            header_label = Gtk.Label()
            header_label.set_markup(f"<b>{shortcut}</b>")
            header_label.set_halign(Gtk.Align.START)
            header_label.set_margin_top(15 if row > 0 else 5)
            grid.attach(header_label, 0, row, 2, 1)
            row += 1
        elif category == "separator":
            # Empty row for spacing
            row += 1
        else:
            # Shortcut key
            key_label = Gtk.Label()
            key_label.set_markup(f"<tt><b>{shortcut}</b></tt>")
            key_label.set_halign(Gtk.Align.START)
            key_label.set_margin_start(20)
            key_label.set_width_chars(20)
            grid.attach(key_label, 0, row, 1, 1)

            # Description
            desc_label = Gtk.Label(label=description)
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_line_wrap(True)
            desc_label.set_max_width_chars(50)
            grid.attach(desc_label, 1, row, 1, 1)
            row += 1

    scrolled.add(grid)
    content.pack_start(scrolled, True, True, 0)

    # Info label at bottom
    info_label = Gtk.Label()
    info_label.set_markup("<small><i>These shortcuts are always available when the launcher is focused.</i></small>")
    info_label.set_halign(Gtk.Align.START)
    info_label.set_line_wrap(True)
    content.pack_start(info_label, False, False, 5)

    dialog.show_all()
    dialog.run()
    dialog.destroy()
