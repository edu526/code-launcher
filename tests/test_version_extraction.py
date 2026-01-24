"""
Unit tests for version extraction script.

Tests the .github/scripts/extract_version.sh script to ensure it correctly
extracts and validates semantic version tags.
"""

import subprocess
import pytest
from pathlib import Path


# Path to the version extraction script
SCRIPT_PATH = Path(__file__).parent.parent / ".github" / "scripts" / "extract_version.sh"


def run_extract_version(tag_name):
    """
    Run the version extraction script with the given tag name.

    Returns:
        tuple: (stdout, stderr, exit_code)
    """
    result = subprocess.run(
        [str(SCRIPT_PATH), tag_name],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestVersionExtraction:
    """Test suite for version extraction functionality."""

    def test_valid_semantic_version_basic(self):
        """Test extraction of basic semantic version v1.0.0"""
        stdout, stderr, exit_code = run_extract_version("v1.0.0")
        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert stdout == "1.0.0", f"Expected '1.0.0', got '{stdout}'"
        assert stderr == "", f"Unexpected stderr output: {stderr}"

    def test_valid_semantic_version_complex(self):
        """Test extraction of complex semantic version v2.15.3"""
        stdout, stderr, exit_code = run_extract_version("v2.15.3")
        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert stdout == "2.15.3", f"Expected '2.15.3', got '{stdout}'"

    def test_valid_semantic_version_large_numbers(self):
        """Test extraction with large version numbers v10.0.1"""
        stdout, stderr, exit_code = run_extract_version("v10.0.1")
        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert stdout == "10.0.1", f"Expected '10.0.1', got '{stdout}'"

    def test_edge_case_zero_version(self):
        """Test extraction of v0.0.0 (edge case)"""
        stdout, stderr, exit_code = run_extract_version("v0.0.0")
        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert stdout == "0.0.0", f"Expected '0.0.0', got '{stdout}'"

    def test_edge_case_large_version(self):
        """Test extraction of v999.999.999 (edge case)"""
        stdout, stderr, exit_code = run_extract_version("v999.999.999")
        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert stdout == "999.999.999", f"Expected '999.999.999', got '{stdout}'"

    def test_invalid_format_no_v_prefix(self):
        """Test rejection of version without 'v' prefix: 1.0.0"""
        stdout, stderr, exit_code = run_extract_version("1.0.0")
        assert exit_code == 1, "Script should fail for version without 'v' prefix"
        assert "Invalid version tag format" in stderr, f"Expected error message, got: {stderr}"
        assert "Expected format: v[MAJOR].[MINOR].[PATCH]" in stderr

    def test_invalid_format_incomplete_version(self):
        """Test rejection of incomplete version: v1.0"""
        stdout, stderr, exit_code = run_extract_version("v1.0")
        assert exit_code == 1, "Script should fail for incomplete version"
        assert "Invalid version tag format" in stderr, f"Expected error message, got: {stderr}"

    def test_invalid_format_with_suffix(self):
        """Test rejection of version with suffix: v1.0.0-beta"""
        stdout, stderr, exit_code = run_extract_version("v1.0.0-beta")
        assert exit_code == 1, "Script should fail for version with suffix"
        assert "Invalid version tag format" in stderr, f"Expected error message, got: {stderr}"

    def test_invalid_format_non_numeric(self):
        """Test rejection of non-numeric version: vX.Y.Z"""
        stdout, stderr, exit_code = run_extract_version("vX.Y.Z")
        assert exit_code == 1, "Script should fail for non-numeric version"
        assert "Invalid version tag format" in stderr, f"Expected error message, got: {stderr}"

    def test_no_argument_provided(self):
        """Test error handling when no argument is provided"""
        result = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, "Script should fail when no argument provided"
        assert "Tag name is required" in result.stderr, f"Expected usage message, got: {result.stderr}"
        assert "Usage:" in result.stderr

    def test_script_exists_and_executable(self):
        """Test that the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert SCRIPT_PATH.is_file(), f"Script path is not a file: {SCRIPT_PATH}"
        # Check if executable (on Unix-like systems)
        import os
        assert os.access(SCRIPT_PATH, os.X_OK), f"Script is not executable: {SCRIPT_PATH}"


class TestVersionValidation:
    """Test suite for version tag validation logic."""

    @pytest.mark.parametrize("tag,expected_version", [
        ("v1.0.0", "1.0.0"),
        ("v0.0.1", "0.0.1"),
        ("v10.20.30", "10.20.30"),
        ("v100.200.300", "100.200.300"),
        ("v1.2.3", "1.2.3"),
    ])
    def test_valid_versions(self, tag, expected_version):
        """Test multiple valid version formats"""
        stdout, stderr, exit_code = run_extract_version(tag)
        assert exit_code == 0, f"Script failed for valid tag {tag}: {stderr}"
        assert stdout == expected_version, f"Expected '{expected_version}', got '{stdout}'"

    @pytest.mark.parametrize("invalid_tag", [
        "1.0.0",           # Missing 'v' prefix
        "v1.0",            # Incomplete version
        "v1",              # Too short
        "v1.0.0.0",        # Too many parts
        "v1.0.0-alpha",    # With suffix
        "v1.0.0-beta.1",   # With pre-release
        "v1.0.0+build",    # With build metadata
        "vX.Y.Z",          # Non-numeric
        "va.b.c",          # Non-numeric
        "v1.0.x",          # Partially non-numeric
        "version1.0.0",    # Wrong prefix
        "V1.0.0",          # Uppercase V
        "v 1.0.0",         # Space after v
        "v1. 0.0",         # Space in version
    ])
    def test_invalid_versions(self, invalid_tag):
        """Test multiple invalid version formats"""
        stdout, stderr, exit_code = run_extract_version(invalid_tag)
        assert exit_code == 1, f"Script should reject invalid tag: {invalid_tag}"
        assert "Invalid version tag format" in stderr or "Tag name is required" in stderr, \
            f"Expected error message for {invalid_tag}, got: {stderr}"
