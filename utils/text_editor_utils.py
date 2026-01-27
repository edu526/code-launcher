#!/usr/bin/env python3
"""
Text editor utilities for opening files
"""

import subprocess
import logging
import os

logger = logging.getLogger(__name__)


def open_file_in_editor(file_path, editor="gnome-text-editor"):
    """
    Open a file in the specified text editor

    Args:
        file_path: Path to the file to open
        editor: Editor command (gnome-text-editor, gedit, kate, nano, vim, emacs, vscode, kiro)

    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False

    try:
        editor_lower = editor.lower()

        if editor_lower == "vscode":
            cmd = ["code", file_path]
        elif editor_lower == "kiro":
            cmd = ["kiro", file_path]
        elif editor_lower in ["nano", "vim", "emacs"]:
            # Terminal editors need to run in a terminal
            # Try common terminal emulators
            terminals = [
                ["gnome-terminal", "--", editor_lower, file_path],
                ["konsole", "-e", editor_lower, file_path],
                ["xterm", "-e", editor_lower, file_path],
            ]

            for term_cmd in terminals:
                try:
                    subprocess.Popen(term_cmd)
                    logger.info(f"Opened {file_path} in {editor_lower} via {term_cmd[0]}")
                    return True
                except FileNotFoundError:
                    continue

            logger.error(f"No terminal emulator found to open {editor_lower}")
            return False
        else:
            # GUI editors (gnome-text-editor, gedit, kate, etc.)
            cmd = [editor_lower, file_path]

        subprocess.Popen(cmd)
        logger.info(f"Opened {file_path} in {editor}")
        return True

    except FileNotFoundError:
        logger.error(f"Editor not found: {editor}")
        return False
    except Exception as e:
        logger.error(f"Error opening file in {editor}: {e}")
        return False
