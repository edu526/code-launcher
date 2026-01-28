#!/usr/bin/env python3
"""
Visual test for shortcuts dialog
Run this manually to see the dialog: python3 test_shortcuts_visual.py
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dialogs.shortcuts_dialog import show_shortcuts_dialog


def main():
    """Show shortcuts dialog for visual testing"""
    # Create a dummy window
    window = Gtk.Window(title="Test Window")
    window.set_default_size(200, 100)

    # Show shortcuts dialog
    show_shortcuts_dialog(window)

    print("Dialog closed")


if __name__ == '__main__':
    main()
