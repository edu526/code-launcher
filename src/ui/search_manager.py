#!/usr/bin/env python3
"""
Search functionality for Code Launcher
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import re


class SearchManager:
    """Manages project search functionality"""

    def __init__(self, window):
        """
        Initialize search manager

        Args:
            window: FinderStyleWindow instance
        """
        self.window = window

    def _normalize_text(self, text):
        """
        Normalize text for search by removing special characters and converting to lowercase

        Args:
            text: Text to normalize

        Returns:
            Normalized text (lowercase, no special chars)
        """
        # Convert to lowercase
        text = text.lower()
        # Remove special characters (keep only alphanumeric)
        text = re.sub(r'[^a-z0-9]', '', text)
        return text

    def on_search_changed(self, entry):
        """
        Handle search text changes

        Args:
            entry: Gtk.SearchEntry widget
        """
        search_text = entry.get_text().lower()

        if not search_text:
            # Restore normal view
            self.window.reload_interface()
            return

        # Check for special @recent command
        if search_text.strip() == "@recent":
            self.show_recent_items()
            return

        # Normalize search text for flexible matching
        normalized_search = self._normalize_text(search_text)

        # Search for matching projects, files and categories
        matching_projects = self._find_matching_projects(normalized_search)
        matching_files = self._find_matching_files(normalized_search)
        matching_categories = self._find_matching_categories(normalized_search, self.window.categories)

        # For each found category, add all its projects
        category_projects = self._get_projects_from_categories(matching_categories)

        # Combine directly found projects + projects from found categories
        # Use dict to avoid duplicates (key = project_name)
        all_projects = {}

        # Add projects matching by name
        for project_name, project_path, category in matching_projects:
            all_projects[project_name] = (project_name, project_path, category)

        # Add projects from found categories
        for project_name, project_path, category in category_projects:
            if project_name not in all_projects:
                all_projects[project_name] = (project_name, project_path, category)

        # Convert dict to list and sort alphabetically
        final_projects = sorted(list(all_projects.values()), key=lambda x: x[0].lower())

        if final_projects or matching_files or matching_categories:
            self.show_search_results(final_projects, matching_files, matching_categories)
        else:
            # No results - show empty column
            self.show_search_results([], [], [])

    def _find_matching_projects(self, normalized_search):
        """
        Find projects matching search text

        Args:
            normalized_search: Normalized search query (lowercase, no special chars)

        Returns:
            List of tuples (project_name, project_path, category)
        """
        matching_projects = []

        for project_name, project_info in self.window.projects.items():
            # Normalize project name for comparison
            normalized_name = self._normalize_text(project_name)

            if normalized_search in normalized_name:
                if isinstance(project_info, str):
                    matching_projects.append((project_name, project_info, "Otros"))
                else:
                    matching_projects.append((
                        project_name,
                        project_info.get("path", ""),
                        project_info.get("category", "Otros")
                    ))

        return matching_projects

    def _find_matching_files(self, normalized_search):
        """
        Find files matching search text

        Args:
            normalized_search: Normalized search query (lowercase, no special chars)

        Returns:
            List of tuples (file_name, file_path, category)
        """
        matching_files = []

        for file_name, file_info in self.window.files.items():
            # Normalize file name for comparison
            normalized_name = self._normalize_text(file_name)

            if normalized_search in normalized_name:
                if isinstance(file_info, str):
                    matching_files.append((file_name, file_info, "Otros"))
                else:
                    matching_files.append((
                        file_name,
                        file_info.get("path", ""),
                        file_info.get("category", "Otros")
                    ))

        return matching_files

    def _find_matching_categories(self, normalized_search, categories, prefix=""):
        """
        Find categories matching search text (recursive)

        Args:
            normalized_search: Normalized search query (lowercase, no special chars)
            categories: Categories dictionary
            prefix: Current category prefix for nested categories

        Returns:
            List of tuples (category_name, category_path, type)
        """
        matching_categories = []

        for cat_name, cat_info in categories.items():
            full_name = f"{prefix}{cat_name}" if prefix else cat_name

            # Normalize category name for comparison
            normalized_cat_name = self._normalize_text(cat_name)

            # Check if category name matches
            if normalized_search in normalized_cat_name:
                cat_path = f"cat:{full_name.replace('/', ':')}"
                matching_categories.append((cat_name, cat_path, "Category"))

            # Search in subcategories recursively
            subcategories = cat_info.get("subcategories", {})
            if subcategories:
                sub_matches = self._find_matching_categories(
                    normalized_search,
                    subcategories,
                    f"{full_name}/"
                )
                matching_categories.extend(sub_matches)

        return matching_categories

    def _get_projects_from_categories(self, matching_categories):
        """
        Get all projects that belong to the matching categories

        Args:
            matching_categories: List of tuples (category_name, category_path, type)

        Returns:
            List of tuples (project_name, project_path, category)
        """
        category_projects = []

        # Extract category paths from matching categories
        category_paths = []
        for cat_name, cat_path, cat_type in matching_categories:
            # Remove "cat:" prefix and convert to category path format
            if cat_path.startswith("cat:"):
                clean_path = cat_path[4:]  # Remove "cat:"
                category_paths.append(clean_path)

        # Find all projects that belong to these categories
        for project_name, project_info in self.window.projects.items():
            if isinstance(project_info, dict):
                project_category = project_info.get('category', '')
                project_subcategory = project_info.get('subcategory', '')

                # Build full project category path
                if project_subcategory:
                    full_project_path = f"{project_category}:{project_subcategory}"
                else:
                    full_project_path = project_category

                # Check if project belongs to any of the matching categories
                for cat_path in category_paths:
                    # Convert "/" to ":" for comparison
                    cat_path_normalized = cat_path.replace("/", ":")

                    # Check if project belongs to this category or any subcategory
                    if full_project_path == cat_path_normalized or full_project_path.startswith(cat_path_normalized + ":"):
                        category_projects.append((
                            project_name,
                            project_info.get("path", ""),
                            project_info.get("category", "Others")
                        ))
                        break  # Don't add the same project multiple times

        return category_projects

    def show_search_results(self, projects, files, categories):
        """
        Display search results in a column

        Args:
            projects: List of tuples (project_name, project_path, category)
            files: List of tuples (file_name, file_path, category)
            categories: List of tuples (category_name, category_path, type)
        """
        # Clear existing columns
        for column in self.window.columns:
            self.window.columns_box.remove(column)
        self.window.columns.clear()

        # Create results column manually (don't use add_column)
        from src.ui.column_browser import ColumnBrowser

        results_column = ColumnBrowser(
            self.window.navigation_manager.on_column_selection,
            "search_results",
            self.window
        )
        results_column.current_path = "search_results"
        results_column.store.clear()

        # Add categories first (sorted alphabetically)
        sorted_categories = sorted(categories, key=lambda x: x[0].lower())
        for cat_name, cat_path, cat_type in sorted_categories:
            is_fav = self.window.config.is_favorite(cat_path, "category")
            results_column.store.append([f"📁 {cat_name}", cat_path, True, "folder", is_fav])

        # Add projects (sorted alphabetically)
        sorted_projects = sorted(projects, key=lambda x: x[0].lower())
        for project_name, project_path, category in sorted_projects:
            is_fav = self.window.config.is_favorite(project_path, "project")
            results_column.store.append([f"📄 {project_name}", project_path, True, "code", is_fav])

        # Add files (sorted alphabetically)
        sorted_files = sorted(files, key=lambda x: x[0].lower())
        for file_name, file_path, category in sorted_files:
            is_fav = self.window.config.is_favorite(file_path, "file")
            results_column.store.append([f"📄 {file_name}", file_path, True, "text-x-generic", is_fav])

        # If no results, show message
        if not projects and not files and not categories:
            results_column.store.append(["No results found", "", False, "dialog-information", False])

        # Add column to interface
        self.window.columns.append(results_column)
        self.window.columns_box.pack_start(results_column, True, True, 1)
        results_column.show_all()

    def show_recent_items(self):
        """Display recently opened items"""
        recents = self.window.config.load_recents()

        # Clear existing columns
        for column in self.window.columns:
            self.window.columns_box.remove(column)
        self.window.columns.clear()

        # Create results column
        from src.ui.column_browser import ColumnBrowser

        results_column = ColumnBrowser(
            self.window.navigation_manager.on_column_selection,
            "recent_items",
            self.window
        )
        results_column.current_path = "recent_items"
        results_column.store.clear()

        if not recents:
            results_column.store.append(["No recent items", "", False, "dialog-information", False])
        else:
            for item in recents:
                item_name = item.get("name", "Unknown")
                item_path = item.get("path", "")
                item_type = item.get("type", "project")

                icon = "text-x-generic" if item_type == "file" else "code"
                is_fav = self.window.config.is_favorite(item_path, item_type)

                results_column.store.append([item_name, item_path, True, icon, is_fav])

        # Add column to interface
        self.window.columns.append(results_column)
        self.window.columns_box.pack_start(results_column, True, True, 1)
        results_column.show_all()
