#!/usr/bin/env python3
"""
Configuration dialogs for categories, projects, and logs
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
from src.core.config import CONFIG_DIR


def show_categories_dialog(parent, categories, on_save_callback):
    """Show categories editor dialog"""
    dialog = Gtk.Dialog(
        title="Edit Categories",
        flags=0,
        default_width=600,
        default_height=500
    )
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_modal(True)
    dialog.set_transient_for(parent)
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

    label = Gtk.Label(label="Categories (format: name:icon:description):")
    content.pack_start(label, False, False, 0)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_min_content_height(300)

    textview = Gtk.TextView()
    textview.set_wrap_mode(Gtk.WrapMode.NONE)
    buffer = textview.get_buffer()

    # Build categories text
    cat_text = ""
    for cat_name, cat_info in categories.items():
        icon = cat_info.get("icon", "folder")
        desc = cat_info.get("description", "")
        cat_text += f"{cat_name}:{icon}:{desc}\n"

        # Add subcategories
        subcategories = cat_info.get("subcategories", {})
        for sub_name, sub_info in subcategories.items():
            sub_icon = sub_info.get("icon", "folder")
            sub_desc = sub_info.get("description", "")
            cat_text += f"  {sub_name}:{sub_icon}:{sub_desc}\n"

    buffer.set_text(cat_text.strip())
    scrolled.add(textview)
    content.pack_start(scrolled, True, True, 0)

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        # Parse categories
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        cat_text = buffer.get_text(start, end, True)

        new_categories = {}
        current_category = None

        for line in cat_text.split('\n'):
            if not line.strip():
                continue

            if line.startswith('  '):  # Subcategory
                line = line.strip()
                if line and ':' in line and current_category:
                    parts = line.split(':', 2)
                    sub_name = parts[0].strip()
                    sub_icon = parts[1].strip() if len(parts) > 1 else "folder"
                    sub_desc = parts[2].strip() if len(parts) > 2 else ""

                    if "subcategories" not in new_categories[current_category]:
                        new_categories[current_category]["subcategories"] = {}
                    new_categories[current_category]["subcategories"][sub_name] = {
                        "icon": sub_icon,
                        "description": sub_desc
                    }
            else:  # Main category
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':', 2)
                    cat_name = parts[0].strip()
                    icon = parts[1].strip() if len(parts) > 1 else "folder"
                    desc = parts[2].strip() if len(parts) > 2 else ""

                    current_category = cat_name
                    new_categories[cat_name] = {
                        "icon": icon,
                        "description": desc,
                        "subcategories": {}
                    }

        if on_save_callback:
            on_save_callback(new_categories)

    dialog.destroy()


def show_projects_dialog(parent, projects, on_save_callback):
    """Show projects editor dialog"""
    dialog = Gtk.Dialog(
        title="Edit Projects",
        flags=0,
        default_width=600,
        default_height=500
    )
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_modal(True)
    dialog.set_transient_for(parent)
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

    label = Gtk.Label(label="Projects (format: name:path:category:subcategory):")
    content.pack_start(label, False, False, 0)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_min_content_height(300)

    textview = Gtk.TextView()
    textview.set_wrap_mode(Gtk.WrapMode.NONE)
    buffer = textview.get_buffer()

    # Build projects text
    proj_text = ""
    for proj_name, proj_info in projects.items():
        if isinstance(proj_info, str):
            proj_text += f"{proj_name}:{proj_info}:Others:\n"
        else:
            path = proj_info.get("path", "")
            category = proj_info.get("category", "Others")
            subcategory = proj_info.get("subcategory", "")
            proj_text += f"{proj_name}:{path}:{category}:{subcategory}\n"

    buffer.set_text(proj_text.strip())
    scrolled.add(textview)
    content.pack_start(scrolled, True, True, 0)

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        # Parse projects
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        proj_text = buffer.get_text(start, end, True)

        new_projects = {}
        for line in proj_text.split('\n'):
            line = line.strip()
            if line and ':' in line:
                parts = line.split(':', 3)
                if len(parts) >= 2:
                    proj_name = parts[0].strip()
                    path = parts[1].strip()
                    category = parts[2].strip() if len(parts) > 2 else "Others"
                    subcategory = parts[3].strip() if len(parts) > 3 else ""

                    project_info = {
                        "path": path,
                        "category": category
                    }

                    # Only add subcategory if it's not empty
                    if subcategory:
                        project_info["subcategory"] = subcategory

                    new_projects[proj_name] = project_info

        if on_save_callback:
            on_save_callback(new_projects)

    dialog.destroy()


def show_logs_dialog(parent):
    """Show logs viewer dialog"""
    dialog = Gtk.Dialog(
        title="View Logs",
        flags=0,
        default_width=800,
        default_height=600
    )
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_modal(True)
    dialog.set_transient_for(parent)
    dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

    content = dialog.get_content_area()
    content.set_spacing(10)
    content.set_margin_start(10)
    content.set_margin_end(10)
    content.set_margin_top(10)
    content.set_margin_bottom(10)

    label = Gtk.Label(label="Application logs:")
    content.pack_start(label, False, False, 0)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_min_content_height(400)

    textview = Gtk.TextView()
    textview.set_wrap_mode(Gtk.WrapMode.NONE)
    textview.set_editable(False)
    textview.set_cursor_visible(False)
    buffer = textview.get_buffer()

    # Read log file
    log_file = os.path.join(CONFIG_DIR, "code-launcher.log")
    logs_text = ""
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                logs_text = ''.join(lines[-500:])
        except Exception as e:
            logs_text = f"Error reading logs: {e}"
    else:
        logs_text = "No logs available yet."

    buffer.set_text(logs_text)
    scrolled.add(textview)
    content.pack_start(scrolled, True, True, 0)

    # Buttons
    buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

    refresh_btn = Gtk.Button(label="Refresh")
    refresh_btn.connect("clicked", lambda w: _refresh_logs(buffer, log_file))
    buttons_box.pack_start(refresh_btn, False, False, 0)

    clear_btn = Gtk.Button(label="Clear Logs")
    clear_btn.connect("clicked", lambda w: _clear_logs(buffer, log_file))
    buttons_box.pack_start(clear_btn, False, False, 0)

    copy_btn = Gtk.Button(label="Copy to Clipboard")
    copy_btn.connect("clicked", lambda w: _copy_logs_to_clipboard(buffer))
    buttons_box.pack_start(copy_btn, False, False, 0)

    content.pack_start(buttons_box, False, False, 0)

    dialog.show_all()
    dialog.run()
    dialog.destroy()


def _refresh_logs(logs_buffer, log_file):
    """Refresh logs display"""
    logs_text = ""
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                logs_text = ''.join(lines[-500:])
        except Exception as e:
            logs_text = f"Error reading logs: {e}"
    else:
        logs_text = "No logs available yet."

    logs_buffer.set_text(logs_text)


def _clear_logs(logs_buffer, log_file):
    """Clear logs file"""
    try:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write("")
            logs_buffer.set_text("Logs cleared.")
    except Exception as e:
        logs_buffer.set_text(f"Error clearing logs: {e}")


def _copy_logs_to_clipboard(logs_buffer):
    """Copy logs to clipboard"""
    start = logs_buffer.get_start_iter()
    end = logs_buffer.get_end_iter()
    logs_text = logs_buffer.get_text(start, end, True)

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(logs_text, -1)


def show_preferences_dialog(parent, config_manager, terminal_manager=None):
    """Show preferences dialog for selecting default editor and terminal"""
    dialog = Gtk.Dialog(
        title="Preferences",
        flags=0,
        default_width=450,
        default_height=300
    )
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_modal(True)
    dialog.set_transient_for(parent)
    dialog.add_buttons(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OK, Gtk.ResponseType.OK
    )

    content = dialog.get_content_area()
    content.set_spacing(15)
    content.set_margin_start(20)
    content.set_margin_end(20)
    content.set_margin_top(20)
    content.set_margin_bottom(20)

    # Load current preferences
    preferences = config_manager.load_preferences()
    current_editor = preferences.get("default_editor", "kiro")

    # Editor Preferences Section
    editor_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # Editor section label
    editor_label = Gtk.Label()
    editor_label.set_markup("<b>Editor Preferences:</b>")
    editor_label.set_halign(Gtk.Align.START)
    editor_section.pack_start(editor_label, False, False, 0)

    # Editor selection container
    editor_selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    # Editor selection label
    editor_select_label = Gtk.Label(label="Default editor:")
    editor_select_label.set_halign(Gtk.Align.START)
    editor_selection_box.pack_start(editor_select_label, False, False, 0)

    # Editor dropdown
    editor_combo = Gtk.ComboBoxText()
    editor_combo.set_hexpand(True)
    editor_combo.append_text("Kiro")
    editor_combo.append_text("VSCode")

    # Set current selection
    if current_editor == "kiro":
        editor_combo.set_active(0)
    else:
        editor_combo.set_active(1)

    editor_selection_box.pack_start(editor_combo, True, True, 0)
    editor_section.pack_start(editor_selection_box, False, False, 0)

    # Editor info label
    editor_info_label = Gtk.Label()
    editor_info_label.set_markup("<small><i>The selected editor will open on double click on a project.</i></small>")
    editor_info_label.set_halign(Gtk.Align.START)
    editor_info_label.set_line_wrap(True)
    editor_section.pack_start(editor_info_label, False, False, 5)

    content.pack_start(editor_section, False, False, 0)

    # Terminal Preferences Section (if terminal_manager is provided and functional)
    terminal_preferences = None
    if terminal_manager:
        try:
            from src.dialogs.terminal_preferences import TerminalPreferences
            terminal_preferences = TerminalPreferences(dialog, terminal_manager)
            terminal_section = terminal_preferences.create_terminal_section()
            content.pack_start(terminal_section, False, False, 0)
        except Exception as e:
            # Graceful degradation: log error but continue without terminal preferences
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create terminal preferences section: {e}")
            logger.info("Terminal preferences will not be available in this session")

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        # Get editor preference from combobox
        selected_editor_index = editor_combo.get_active()
        selected_editor = "kiro" if selected_editor_index == 0 else "vscode"

        # Apply terminal selection if terminal preferences are available
        if terminal_preferences:
            try:
                terminal_success = terminal_preferences.apply_terminal_selection()
                if not terminal_success:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning("Failed to apply terminal selection, but continuing with editor preference save")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error applying terminal selection: {e}")

        # Load current preferences AFTER applying terminal selection to get the updated values
        current_preferences = config_manager.load_preferences()
        current_preferences["default_editor"] = selected_editor
        config_manager.save_preferences(current_preferences)

        # Update parent window's preference
        if hasattr(parent, 'default_editor'):
            parent.default_editor = selected_editor

    elif response == Gtk.ResponseType.CANCEL:
        # Cancel any pending terminal selection
        if terminal_preferences:
            try:
                terminal_preferences.cancel_terminal_selection()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error cancelling terminal selection: {e}")

    dialog.destroy()
