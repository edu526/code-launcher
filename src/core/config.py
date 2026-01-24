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
        """Load user preferences"""
        default_preferences = {
            "default_editor": "kiro"  # "kiro" or "vscode"
        }

        if os.path.exists(PREFERENCES_FILE):
            try:
                with open(PREFERENCES_FILE, 'r') as f:
                    loaded_prefs = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**default_preferences, **loaded_prefs}
            except:
                pass

        # Save defaults
        self.save_preferences(default_preferences)
        return default_preferences

    def save_preferences(self, preferences):
        """Save user preferences"""
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)

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