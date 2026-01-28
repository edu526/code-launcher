#!/usr/bin/env python3
"""
Test search functionality with files
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.search_manager import SearchManager


class TestSearchFiles(unittest.TestCase):
    """Test search functionality for files"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock window
        self.window = Mock()
        self.window.projects = {
            "project1": {"path": "/home/user/project1", "category": "Work"},
            "project2": {"path": "/home/user/project2", "category": "Personal"},
        }
        self.window.files = {
            "notes.txt": {"path": "/home/user/notes.txt", "category": "Work"},
            "readme.md": {"path": "/home/user/readme.md", "category": "Personal"},
            "config.json": {"path": "/home/user/config.json", "category": "Work"},
        }
        self.window.categories = {}
        self.window.config = Mock()
        self.window.config.is_favorite = Mock(return_value=False)

        self.search_manager = SearchManager(self.window)

    def test_find_matching_files(self):
        """Test finding files by name"""
        results = self.search_manager._find_matching_files("notes")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "notes.txt")
        self.assertEqual(results[0][1], "/home/user/notes.txt")

    def test_find_multiple_matching_files(self):
        """Test finding multiple files"""
        # Add more files
        self.window.files["notes2.txt"] = {"path": "/home/user/notes2.txt", "category": "Work"}

        results = self.search_manager._find_matching_files("notes")

        self.assertEqual(len(results), 2)
        file_names = [r[0] for r in results]
        self.assertIn("notes.txt", file_names)
        self.assertIn("notes2.txt", file_names)

    def test_normalize_search_for_files(self):
        """Test that search normalization works for files"""
        # Search for "readme" should find "readme.md"
        results = self.search_manager._find_matching_files("readme")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "readme.md")

    def test_case_insensitive_file_search(self):
        """Test case insensitive search"""
        # _find_matching_files expects normalized input
        normalized_search = self.search_manager._normalize_text("README")
        results = self.search_manager._find_matching_files(normalized_search)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "readme.md")

    def test_partial_match_file_search(self):
        """Test partial match in file names"""
        results = self.search_manager._find_matching_files("conf")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "config.json")


if __name__ == '__main__':
    unittest.main()
