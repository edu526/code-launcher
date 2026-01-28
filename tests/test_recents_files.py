#!/usr/bin/env python3
"""
Test that files are added to recents when opened
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import ConfigManager


class TestRecentsFiles(unittest.TestCase):
    """Test recents functionality for files"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = ConfigManager()
        # Clear recents before each test
        self.config.save_recents([])

    def tearDown(self):
        """Clean up after tests"""
        self.config.save_recents([])

    def test_add_file_to_recents(self):
        """Test that files are added to recents"""
        file_path = "/home/user/test.txt"
        file_name = "test.txt"

        self.config.add_recent(file_path, file_name, "file")

        recents = self.config.load_recents()
        self.assertEqual(len(recents), 1)
        self.assertEqual(recents[0]['path'], file_path)
        self.assertEqual(recents[0]['name'], file_name)
        self.assertEqual(recents[0]['type'], "file")

    def test_add_multiple_files_to_recents(self):
        """Test adding multiple files to recents"""
        files = [
            ("/home/user/file1.txt", "file1.txt"),
            ("/home/user/file2.py", "file2.py"),
            ("/home/user/file3.md", "file3.md"),
        ]

        for path, name in files:
            self.config.add_recent(path, name, "file")

        recents = self.config.load_recents()
        self.assertEqual(len(recents), 3)
        # Most recent should be first
        self.assertEqual(recents[0]['name'], "file3.md")
        self.assertEqual(recents[1]['name'], "file2.py")
        self.assertEqual(recents[2]['name'], "file1.txt")

    def test_duplicate_file_moves_to_front(self):
        """Test that opening a file again moves it to front"""
        self.config.add_recent("/home/user/file1.txt", "file1.txt", "file")
        self.config.add_recent("/home/user/file2.txt", "file2.txt", "file")
        self.config.add_recent("/home/user/file1.txt", "file1.txt", "file")

        recents = self.config.load_recents()
        self.assertEqual(len(recents), 2)  # No duplicates
        self.assertEqual(recents[0]['name'], "file1.txt")  # Moved to front

    def test_mixed_projects_and_files_in_recents(self):
        """Test that projects and files can coexist in recents"""
        self.config.add_recent("/home/user/project1", "Project 1", "project")
        self.config.add_recent("/home/user/file1.txt", "file1.txt", "file")
        self.config.add_recent("/home/user/project2", "Project 2", "project")

        recents = self.config.load_recents()
        self.assertEqual(len(recents), 3)
        self.assertEqual(recents[0]['type'], "project")
        self.assertEqual(recents[1]['type'], "file")
        self.assertEqual(recents[2]['type'], "project")


if __name__ == '__main__':
    unittest.main()
