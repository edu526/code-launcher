#!/usr/bin/env python3
"""
Configuration module for Code Launcher
Management of categories, projects and general configuration
"""

import os
import json

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/code-launcher")
PROJECTS_FILE = os.path.expanduser("~/.config/code-launcher/projects.json")
CATEGORIES_FILE = os.path.expanduser("~/.config/code-launcher/categories.json")
PREFERENCES_FILE = os.path.expanduser("~/.config/code-launcher/preferences.json")
LOCK_FILE = os.path.expanduser("~/.config/code-launcher/launcher.lock")
PID_FILE = os.path.expanduser("~/.config/code-launcher/launcher.pid")

class ConfigManager:
    """Manages all launcher configuration"""

    def __init__(self):
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        os.makedirs(CONFIG_DIR, exist_ok=True)

    def load_categories(self):
        """Load categories from configuration"""
        default_categories = {}

        if os.path.exists(CATEGORIES_FILE):
            try:
                with open(CATEGORIES_FILE, 'r') as f:
                    loaded_categories = json.load(f)
                    return loaded_categories
            except:
                pass

        # Save defaults
        self.save_categories(default_categories)
        return default_categories

    def save_categories(self, categories):
        """Save categories"""
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(categories, f, indent=2)

    def load_projects(self):
        """Load projects from configuration"""
        if os.path.exists(PROJECTS_FILE):
            try:
                with open(PROJECTS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_projects(self, projects):
        """Save projects"""
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=2)

    def load_preferences(self):
        """Load user preferences with validation and defaults"""
        default_preferences = {
            "default_editor": "kiro",  # "kiro" or "vscode"
            "close_on_open": False,  # Close launcher when opening a project
            "terminal": {
                "preferred": None,
                "available": {},
                "last_detected": None
            }
        }

        if os.path.exists(PREFERENCES_FILE):
            try:
                with open(PREFERENCES_FILE, 'r') as f:
                    loaded_prefs = json.load(f)
                    # Start with defaults and carefully merge valid values
                    merged_prefs = {**default_preferences}

                    # Validate and merge non-terminal preferences
                    for key, value in loaded_prefs.items():
                        if key == "terminal":
                            # Handle terminal configuration separately with validation
                            if isinstance(value, dict):
                                terminal_config = {**default_preferences["terminal"]}

                                # Validate each terminal configuration key
                                if "preferred" in value:
                                    if value["preferred"] is None or isinstance(value["preferred"], str):
                                        terminal_config["preferred"] = value["preferred"]

                                if "available" in value:
                                    if isinstance(value["available"], dict):
                                        # Validate that all keys and values in available are strings
                                        valid_available = {}
                                        for term_name, term_path in value["available"].items():
                                            if isinstance(term_name, str) and isinstance(term_path, str):
                                                valid_available[term_name] = term_path
                                        terminal_config["available"] = valid_available

                                if "last_detected" in value:
                                    if value["last_detected"] is None or isinstance(value["last_detected"], str):
                                        terminal_config["last_detected"] = value["last_detected"]

                                merged_prefs["terminal"] = terminal_config
                        elif key == "default_editor":
                            # Validate default_editor is a string
                            if isinstance(value, str):
                                merged_prefs[key] = value
                        else:
                            # For other keys, preserve if they are basic types
                            if isinstance(value, (str, int, bool, list)):
                                merged_prefs[key] = value

                    return merged_prefs
            except:
                pass

        # Save defaults
        self.save_preferences(default_preferences)
        return default_preferences

    def save_preferences(self, preferences):
        """Save user preferences"""
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)

    def get_terminal_preferences(self):
        """Get terminal-specific preferences"""
        preferences = self.load_preferences()
        return preferences.get("terminal", {
            "preferred": None,
            "available": {},
            "last_detected": None
        })

    def set_terminal_preferences(self, terminal_prefs):
        """Set terminal-specific preferences"""
        preferences = self.load_preferences()
        preferences["terminal"] = terminal_prefs
        self.save_preferences(preferences)

    def get_preferred_terminal(self):
        """Get the user's preferred terminal"""
        terminal_prefs = self.get_terminal_preferences()
        return terminal_prefs.get("preferred")

    def set_preferred_terminal(self, terminal_name):
        """Set the user's preferred terminal"""
        terminal_prefs = self.get_terminal_preferences()
        terminal_prefs["preferred"] = terminal_name
        self.set_terminal_preferences(terminal_prefs)

    def get_available_terminals(self):
        """Get the list of available terminals"""
        terminal_prefs = self.get_terminal_preferences()
        return terminal_prefs.get("available", {})

    def set_available_terminals(self, available_terminals):
        """Set the list of available terminals"""
        terminal_prefs = self.get_terminal_preferences()
        terminal_prefs["available"] = available_terminals
        self.set_terminal_preferences(terminal_prefs)

    def get_last_detected_time(self):
        """Get the last terminal detection timestamp"""
        terminal_prefs = self.get_terminal_preferences()
        return terminal_prefs.get("last_detected")

    def set_last_detected_time(self, timestamp):
        """Set the last terminal detection timestamp"""
        terminal_prefs = self.get_terminal_preferences()
        terminal_prefs["last_detected"] = timestamp
        self.set_terminal_preferences(terminal_prefs)

    def get_category_hierarchy(self, categories):
        """Get complete hierarchy of categories and subcategories"""
        hierarchy = []

        for cat_name, cat_info in sorted(categories.items(), key=lambda x: x[0].lower()):
            category_item = {
                "name": cat_name,
                "path": f"category:{cat_name}",
                "description": cat_info.get("description", ""),
                "icon": cat_info.get("icon", "folder"),
                "type": "category",
                "level": 0
            }
            hierarchy.append(category_item)

            # Add subcategories if they exist
            subcategories = cat_info.get("subcategories", {})
            for sub_name, sub_info in sorted(subcategories.items(), key=lambda x: x[0].lower()):
                subcategory_item = {
                    "name": sub_name,
                    "path": f"category:{cat_name}:{sub_name}",
                    "description": sub_info.get("description", ""),
                    "icon": sub_info.get("icon", "folder"),
                    "type": "subcategory",
                    "level": 1,
                    "parent": cat_name
                }
                hierarchy.append(subcategory_item)

        return hierarchy

    def find_category_path(self, categories, full_path):
        """Find category/subcategory information from path"""
        parts = full_path.split(":")

        if len(parts) == 2:  # category:name
            cat_name = parts[1]
            if cat_name in categories:
                return {
                    "type": "category",
                    "name": cat_name,
                    "info": categories[cat_name],
                    "path": full_path
                }
        elif len(parts) == 3:  # category:cat:sub
            cat_name = parts[1]
            sub_name = parts[2]
            if cat_name in categories and "subcategories" in categories[cat_name]:
                subcategories = categories[cat_name]["subcategories"]
                if sub_name in subcategories:
                    return {
                        "type": "subcategory",
                        "name": sub_name,
                        "parent": cat_name,
                        "info": subcategories[sub_name],
                        "path": full_path
                    }

        return None

def get_available_icons():
    """Get list of common system icons"""
    common_icons = [
        "folder", "user-home", "document", "text-x-generic",
        "application-x-executable", "code", "office", "network",
        "education", "system", "utilities", "preferences",
        "internet-web-browser", "email", "calendar", "camera",
        "multimedia-player", "audio-headphones", "video-display",
        "image-x-generic", "archive", "package", "download",
        "emblem-system", "emblem-default", "emblem-important",
        "star", "favorite", "bookmark", "tag", "flag",
        "dialog-information", "dialog-warning", "dialog-error",
        "list-add", "list-remove", "edit", "delete", "search",
        "go-home", "go-next", "go-previous", "go-up", "go-down",
        "media-playback-start", "media-playback-pause", "media-playback-stop"
    ]
    return common_icons