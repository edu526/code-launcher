"""
Unit tests for version file update script.

Tests the .github/scripts/update_version.sh script to ensure it correctly
updates version strings in all project files.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest


# Path to the version update script
SCRIPT_PATH = Path(__file__).parent.parent / ".github" / "scripts" / "update_version.sh"


def run_update_version(version, test_dir):
    """
    Run the version update script with the given version in a test directory.

    Args:
        version: The version string to update to (e.g., "1.2.3")
        test_dir: Path to the test directory containing the files

    Returns:
        tuple: (stdout, stderr, exit_code)
    """
    result = subprocess.run(
        [str(SCRIPT_PATH), version],
        capture_output=True,
        text=True,
        cwd=test_dir
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestSetupPyUpdates:
    """Test suite for setup.py version updates."""

    def test_setup_py_updated_correctly(self):
        """Test that setup.py version is updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create setup.py with initial version
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('''#!/usr/bin/env python3
from setuptools import setup

setup(
    name="code-project-launcher",
    version="1.0.0",
    author="Test Author",
    description="Test package",
)
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("2.5.3", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = setup_py_path.read_text()
            assert 'version="2.5.3"' in content, "Version not updated in setup.py"
            assert 'version="1.0.0"' not in content, "Old version still present"

    def test_setup_py_version_pattern_matched(self):
        """Test that version pattern in setup.py is correctly matched"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create setup.py with various spacing
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('''
setup(
    name="test",
    version="0.0.1",
    description="test"
)
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("3.14.159", temp_dir)

            # Verify the pattern was matched and replaced
            assert exit_code == 0
            content = setup_py_path.read_text()
            assert 'version="3.14.159"' in content

    def test_setup_py_missing_file(self):
        """Test behavior when setup.py doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Don't create setup.py
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should still succeed (with warning)
            assert exit_code == 0, "Script should succeed even if setup.py is missing"
            assert "setup.py not found" in stdout or "skipping" in stdout.lower()

    def test_setup_py_no_version_pattern(self):
        """Test behavior when setup.py exists but has no version pattern"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create setup.py without version field
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('''
setup(
    name="test",
    description="test without version"
)
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should fail because verification will fail
            assert exit_code == 1, "Script should fail when version pattern not found"
            assert "Failed to update setup.py" in stdout or "Failed to update setup.py" in stderr


class TestBuildDebShUpdates:
    """Test suite for packaging/build_deb.sh version updates."""

    def test_build_deb_updated_correctly(self):
        """Test that build_deb.sh version is updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create packaging directory and build_deb.sh
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_deb_path = packaging_dir / "build_deb.sh"
            build_deb_path.write_text('''#!/bin/bash
set -e

PACKAGE_NAME="code-launcher"
VERSION="1.0.0"
ARCH="all"

echo "Building DEB package version $VERSION"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("2.1.0", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = build_deb_path.read_text()
            assert 'VERSION="2.1.0"' in content, "Version not updated in build_deb.sh"
            assert 'VERSION="1.0.0"' not in content, "Old version still present"

    def test_build_deb_version_pattern_matched(self):
        """Test that VERSION variable pattern is correctly matched"""
        with tempfile.TemporaryDirectory() as temp_dir:
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_deb_path = packaging_dir / "build_deb.sh"
            build_deb_path.write_text('''#!/bin/bash
VERSION="0.0.1"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("5.6.7", temp_dir)

            # Verify the pattern was matched
            assert exit_code == 0
            content = build_deb_path.read_text()
            assert 'VERSION="5.6.7"' in content

    def test_build_deb_missing_file(self):
        """Test behavior when build_deb.sh doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Don't create packaging directory or build_deb.sh
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should still succeed (with warning)
            assert exit_code == 0, "Script should succeed even if build_deb.sh is missing"
            assert "build_deb.sh not found" in stdout or "skipping" in stdout.lower()

    def test_build_deb_no_version_pattern(self):
        """Test behavior when build_deb.sh exists but has no VERSION variable"""
        with tempfile.TemporaryDirectory() as temp_dir:
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_deb_path = packaging_dir / "build_deb.sh"
            build_deb_path.write_text('''#!/bin/bash
PACKAGE_NAME="code-launcher"
echo "Building package"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should fail because verification will fail
            assert exit_code == 1, "Script should fail when VERSION pattern not found"
            assert "Failed to update" in stdout or "Failed to update" in stderr


class TestBuildAppImageShUpdates:
    """Test suite for packaging/build_appimage.sh version updates."""

    def test_build_appimage_updated_correctly(self):
        """Test that build_appimage.sh version is updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create packaging directory and build_appimage.sh
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_appimage_path = packaging_dir / "build_appimage.sh"
            build_appimage_path.write_text('''#!/bin/bash
set -e

APP_NAME="CodeLauncher"
VERSION="1.0.0"

echo "Building AppImage version $VERSION"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("3.2.1", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = build_appimage_path.read_text()
            assert 'VERSION="3.2.1"' in content, "Version not updated in build_appimage.sh"
            assert 'VERSION="1.0.0"' not in content, "Old version still present"

    def test_build_appimage_version_pattern_matched(self):
        """Test that VERSION variable pattern is correctly matched"""
        with tempfile.TemporaryDirectory() as temp_dir:
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_appimage_path = packaging_dir / "build_appimage.sh"
            build_appimage_path.write_text('''#!/bin/bash
VERSION="0.0.1"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("9.8.7", temp_dir)

            # Verify the pattern was matched
            assert exit_code == 0
            content = build_appimage_path.read_text()
            assert 'VERSION="9.8.7"' in content

    def test_build_appimage_missing_file(self):
        """Test behavior when build_appimage.sh doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Don't create packaging directory or build_appimage.sh
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should still succeed (with warning)
            assert exit_code == 0, "Script should succeed even if build_appimage.sh is missing"
            assert "build_appimage.sh not found" in stdout or "skipping" in stdout.lower()

    def test_build_appimage_no_version_pattern(self):
        """Test behavior when build_appimage.sh exists but has no VERSION variable"""
        with tempfile.TemporaryDirectory() as temp_dir:
            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()
            build_appimage_path = packaging_dir / "build_appimage.sh"
            build_appimage_path.write_text('''#!/bin/bash
APP_NAME="CodeLauncher"
echo "Building AppImage"
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should fail because verification will fail
            assert exit_code == 1, "Script should fail when VERSION pattern not found"
            assert "Failed to update" in stdout or "Failed to update" in stderr


class TestReadmeUpdates:
    """Test suite for README.md version updates."""

    def test_readme_deb_package_name_updated(self):
        """Test that DEB package name in README.md is updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''# Code Launcher

## Installation

### DEB Package
```bash
sudo dpkg -i dist/code-launcher_1.0.0_all.deb
```
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("2.0.0", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = readme_path.read_text()
            assert 'code-launcher_2.0.0_all.deb' in content, "DEB package name not updated"
            assert 'code-launcher_1.0.0_all.deb' not in content, "Old DEB package name still present"

    def test_readme_appimage_name_updated(self):
        """Test that AppImage filename in README.md is updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''# Code Launcher

## Installation

### AppImage
```bash
chmod +x dist/CodeLauncher-1.0.0-x86_64.AppImage
./dist/CodeLauncher-1.0.0-x86_64.AppImage
```
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("3.5.0", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = readme_path.read_text()
            assert 'CodeLauncher-3.5.0-x86_64.AppImage' in content, "AppImage name not updated"
            assert 'CodeLauncher-1.0.0-x86_64.AppImage' not in content, "Old AppImage name still present"

    def test_readme_version_badge_updated(self):
        """Test that version badges in README.md are updated correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''# Code Launcher

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Release](https://img.shields.io/badge/release-version-1.0.0-green.svg)
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("4.2.1", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify file content
            content = readme_path.read_text()
            assert 'version-4.2.1' in content, "Version badge not updated"
            assert 'version-1.0.0' not in content, "Old version badge still present"

    def test_readme_multiple_version_references_updated(self):
        """Test that all version references in README.md are updated"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''# Code Launcher

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

## Installation

### DEB Package
```bash
sudo dpkg -i dist/code-launcher_1.0.0_all.deb
```

### AppImage
```bash
chmod +x dist/CodeLauncher-1.0.0-x86_64.AppImage
./dist/CodeLauncher-1.0.0-x86_64.AppImage
```
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("5.0.0", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify all references updated
            content = readme_path.read_text()
            assert 'version-5.0.0' in content, "Version badge not updated"
            assert 'code-launcher_5.0.0_all.deb' in content, "DEB package name not updated"
            assert 'CodeLauncher-5.0.0-x86_64.AppImage' in content, "AppImage name not updated"
            assert '1.0.0' not in content, "Old version still present somewhere"

    def test_readme_missing_file(self):
        """Test behavior when README.md doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Don't create README.md
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should still succeed (with warning)
            assert exit_code == 0, "Script should succeed even if README.md is missing"
            assert "README.md not found" in stdout or "skipping" in stdout.lower()

    def test_readme_no_version_references(self):
        """Test behavior when README.md exists but has no version references"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''# Code Launcher

A simple project launcher.

## Features
- Fast
- Easy to use
''')

            # Run update script
            stdout, stderr, exit_code = run_update_version("1.0.0", temp_dir)

            # Script should succeed (README updates don't have verification)
            assert exit_code == 0, "Script should succeed even if no version patterns found in README"


class TestVersionPatternMatching:
    """Test suite for version pattern matching across all files."""

    def test_version_pattern_with_leading_zeros(self):
        """Test that versions with leading zeros are handled correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('setup(version="0.0.1")')

            stdout, stderr, exit_code = run_update_version("0.0.2", temp_dir)

            assert exit_code == 0
            content = setup_py_path.read_text()
            assert 'version="0.0.2"' in content

    def test_version_pattern_with_large_numbers(self):
        """Test that versions with large numbers are handled correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('setup(version="1.0.0")')

            stdout, stderr, exit_code = run_update_version("999.888.777", temp_dir)

            assert exit_code == 0
            content = setup_py_path.read_text()
            assert 'version="999.888.777"' in content

    def test_version_pattern_does_not_match_similar_strings(self):
        """Test that version pattern doesn't incorrectly match similar strings"""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_py_path = Path(temp_dir) / "setup.py"
            # Include a comment with a version-like string that shouldn't be changed
            setup_py_path.write_text('''
# This is version 9.9.9 in a comment
setup(
    name="test",
    version="1.0.0",
    description="test"
)
''')

            stdout, stderr, exit_code = run_update_version("2.0.0", temp_dir)

            assert exit_code == 0
            content = setup_py_path.read_text()
            # The actual version should be updated
            assert 'version="2.0.0"' in content
            # The comment should remain unchanged
            assert 'version 9.9.9 in a comment' in content


class TestAllFilesIntegration:
    """Integration tests for updating all files together."""

    def test_all_files_updated_together(self):
        """Test that all files are updated in a single script run"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create all files
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('setup(version="1.0.0")')

            packaging_dir = Path(temp_dir) / "packaging"
            packaging_dir.mkdir()

            build_deb_path = packaging_dir / "build_deb.sh"
            build_deb_path.write_text('VERSION="1.0.0"')

            build_appimage_path = packaging_dir / "build_appimage.sh"
            build_appimage_path.write_text('VERSION="1.0.0"')

            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('''
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
code-launcher_1.0.0_all.deb
CodeLauncher-1.0.0-x86_64.AppImage
''')

            # Run update script once
            stdout, stderr, exit_code = run_update_version("7.8.9", temp_dir)

            # Verify success
            assert exit_code == 0, f"Script failed: {stderr}"

            # Verify all files updated
            assert 'version="7.8.9"' in setup_py_path.read_text()
            assert 'VERSION="7.8.9"' in build_deb_path.read_text()
            assert 'VERSION="7.8.9"' in build_appimage_path.read_text()
            readme_content = readme_path.read_text()
            assert 'version-7.8.9' in readme_content
            assert 'code-launcher_7.8.9_all.deb' in readme_content
            assert 'CodeLauncher-7.8.9-x86_64.AppImage' in readme_content

            # Verify old version is gone from all files
            assert '1.0.0' not in setup_py_path.read_text()
            assert '1.0.0' not in build_deb_path.read_text()
            assert '1.0.0' not in build_appimage_path.read_text()
            assert '1.0.0' not in readme_path.read_text()

    def test_partial_files_present(self):
        """Test that script succeeds when only some files are present"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Only create setup.py and README.md
            setup_py_path = Path(temp_dir) / "setup.py"
            setup_py_path.write_text('setup(version="1.0.0")')

            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text('version-1.0.0')

            # Run update script
            stdout, stderr, exit_code = run_update_version("2.0.0", temp_dir)

            # Should succeed with warnings about missing files
            assert exit_code == 0, f"Script should succeed with partial files: {stderr}"
            assert "not found" in stdout or "skipping" in stdout.lower()

            # Verify present files were updated
            assert 'version="2.0.0"' in setup_py_path.read_text()
            assert 'version-2.0.0' in readme_path.read_text()


class TestErrorHandling:
    """Test suite for error handling scenarios."""

    def test_invalid_version_format_rejected(self):
        """Test that invalid version formats are rejected"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try various invalid formats
            invalid_versions = [
                "v1.0.0",      # Has 'v' prefix
                "1.0",         # Incomplete
                "1.0.0.0",     # Too many parts
                "1.0.0-beta",  # Has suffix
                "abc.def.ghi", # Non-numeric
            ]

            for invalid_version in invalid_versions:
                stdout, stderr, exit_code = run_update_version(invalid_version, temp_dir)
                assert exit_code == 1, f"Should reject invalid version: {invalid_version}"
                assert "Invalid version format" in stdout or "Invalid version format" in stderr

    def test_no_version_argument(self):
        """Test that script fails when no version argument provided"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            assert result.returncode == 1, "Script should fail without version argument"
            assert "Usage:" in result.stdout or "Usage:" in result.stderr

    def test_script_exists_and_executable(self):
        """Test that the update script exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert SCRIPT_PATH.is_file(), f"Script path is not a file: {SCRIPT_PATH}"
        import os
        assert os.access(SCRIPT_PATH, os.X_OK), f"Script is not executable: {SCRIPT_PATH}"
