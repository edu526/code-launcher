"""
Property-based tests for version consistency across files.

Tests universal correctness properties of the .github/scripts/update_version.sh
script using hypothesis for property-based testing.
"""

import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings


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


def extract_version_from_setup_py(file_path):
    """Extract version from setup.py file."""
    with open(file_path, 'r') as f:
        content = f.read()
    match = re.search(r'version="([0-9.]+)"', content)
    return match.group(1) if match else None


def extract_version_from_build_script(file_path):
    """Extract version from build script (build_deb.sh or build_appimage.sh)."""
    with open(file_path, 'r') as f:
        content = f.read()
    match = re.search(r'VERSION="([0-9.]+)"', content)
    return match.group(1) if match else None


def extract_versions_from_readme(file_path):
    """Extract all version references from README.md."""
    with open(file_path, 'r') as f:
        content = f.read()

    versions = set()

    # Find versions in DEB package names
    deb_matches = re.findall(r'code-launcher_([0-9.]+)_all\.deb', content)
    versions.update(deb_matches)

    # Find versions in AppImage names
    appimage_matches = re.findall(r'CodeLauncher-([0-9.]+)-x86_64\.AppImage', content)
    versions.update(appimage_matches)

    # Find versions in version badges
    badge_matches = re.findall(r'version-([0-9.]+)', content)
    versions.update(badge_matches)

    return versions


def create_test_files(test_dir, initial_version="0.0.1"):
    """
    Create test version files in the test directory.

    Args:
        test_dir: Path to the test directory
        initial_version: Initial version to use in the files
    """
    # Create setup.py
    setup_py_content = f'''#!/usr/bin/env python3
"""Setup script for Code Launcher"""
from setuptools import setup

setup(
    name="code-project-launcher",
    version="{initial_version}",
    author="Test",
    description="Test package",
)
'''
    setup_py_path = Path(test_dir) / "setup.py"
    setup_py_path.write_text(setup_py_content)

    # Create packaging directory
    packaging_dir = Path(test_dir) / "packaging"
    packaging_dir.mkdir(exist_ok=True)

    # Create build_deb.sh
    build_deb_content = f'''#!/bin/bash
set -e

# Variables
PACKAGE_NAME="code-launcher"
VERSION="{initial_version}"
ARCH="all"

echo "Building DEB package version $VERSION"
'''
    build_deb_path = packaging_dir / "build_deb.sh"
    build_deb_path.write_text(build_deb_content)

    # Create build_appimage.sh
    build_appimage_content = f'''#!/bin/bash
set -e

# Variables
APP_NAME="CodeLauncher"
VERSION="{initial_version}"

echo "Building AppImage version $VERSION"
'''
    build_appimage_path = packaging_dir / "build_appimage.sh"
    build_appimage_path.write_text(build_appimage_content)

    # Create README.md
    readme_content = f'''# Code Launcher

## Installation

### DEB Package
```bash
sudo dpkg -i dist/code-launcher_{initial_version}_all.deb
```

### AppImage
```bash
chmod +x dist/CodeLauncher-{initial_version}-x86_64.AppImage
./dist/CodeLauncher-{initial_version}-x86_64.AppImage
```

![Version](https://img.shields.io/badge/version-{initial_version}-blue.svg)
'''
    readme_path = Path(test_dir) / "README.md"
    readme_path.write_text(readme_content)


# Strategy for generating valid semantic version numbers (MAJOR.MINOR.PATCH)
semantic_version_strategy = st.builds(
    lambda major, minor, patch: f"{major}.{minor}.{patch}",
    major=st.integers(min_value=0, max_value=999),
    minor=st.integers(min_value=0, max_value=999),
    patch=st.integers(min_value=0, max_value=999)
)


class TestVersionConsistencyProperties:
    """Property-based tests for version consistency across files."""

    @given(new_version=semantic_version_strategy)
    @settings(max_examples=100)
    def test_property_version_consistency_across_files(self, new_version):
        """
        **Property 3: Version Consistency Across Files**
        **Validates: Requirements 1.3, 1.4, 6.1, 6.2, 6.3, 6.4**

        For any version update operation, after completion, all version files
        (setup.py, build_deb.sh, build_appimage.sh, README.md) should contain
        the same version number.

        This property ensures that:
        1. The update script successfully updates all version files
        2. All files contain the exact same version number after update
        3. No file is left with an old or incorrect version
        4. The version format is preserved correctly in each file
        5. The script exits with success code (0)
        """
        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files with an initial version different from new_version
            initial_version = "0.0.1"
            create_test_files(temp_dir, initial_version)

            # Run the version update script
            stdout, stderr, exit_code = run_update_version(new_version, temp_dir)

            # Property assertion 1: Script should succeed
            assert exit_code == 0, (
                f"Version update script should succeed for version '{new_version}', "
                f"but failed with exit code {exit_code}. "
                f"stderr: {stderr}"
            )

            # Extract versions from all files
            setup_py_path = Path(temp_dir) / "setup.py"
            build_deb_path = Path(temp_dir) / "packaging" / "build_deb.sh"
            build_appimage_path = Path(temp_dir) / "packaging" / "build_appimage.sh"
            readme_path = Path(temp_dir) / "README.md"

            setup_version = extract_version_from_setup_py(setup_py_path)
            deb_version = extract_version_from_build_script(build_deb_path)
            appimage_version = extract_version_from_build_script(build_appimage_path)
            readme_versions = extract_versions_from_readme(readme_path)

            # Property assertion 2: All files should have been updated
            assert setup_version is not None, (
                f"Failed to extract version from setup.py after update to '{new_version}'"
            )
            assert deb_version is not None, (
                f"Failed to extract version from build_deb.sh after update to '{new_version}'"
            )
            assert appimage_version is not None, (
                f"Failed to extract version from build_appimage.sh after update to '{new_version}'"
            )
            assert len(readme_versions) > 0, (
                f"Failed to extract any version from README.md after update to '{new_version}'"
            )

            # Property assertion 3: setup.py should have the new version
            assert setup_version == new_version, (
                f"setup.py version mismatch. "
                f"Expected '{new_version}', got '{setup_version}'"
            )

            # Property assertion 4: build_deb.sh should have the new version
            assert deb_version == new_version, (
                f"build_deb.sh version mismatch. "
                f"Expected '{new_version}', got '{deb_version}'"
            )

            # Property assertion 5: build_appimage.sh should have the new version
            assert appimage_version == new_version, (
                f"build_appimage.sh version mismatch. "
                f"Expected '{new_version}', got '{appimage_version}'"
            )

            # Property assertion 6: README.md should only have the new version
            assert readme_versions == {new_version}, (
                f"README.md version mismatch. "
                f"Expected only '{new_version}', but found versions: {readme_versions}"
            )

            # Property assertion 7: All versions should be consistent
            all_versions = {setup_version, deb_version, appimage_version}
            all_versions.update(readme_versions)

            assert len(all_versions) == 1, (
                f"Version inconsistency detected across files. "
                f"Found different versions: {all_versions}. "
                f"All files should have version '{new_version}'"
            )

            assert new_version in all_versions, (
                f"None of the files contain the expected version '{new_version}'. "
                f"Found versions: {all_versions}"
            )

            # Property assertion 8: Old version should not remain in any file
            assert initial_version not in all_versions, (
                f"Old version '{initial_version}' still found in files after update. "
                f"All occurrences should have been replaced with '{new_version}'"
            )
