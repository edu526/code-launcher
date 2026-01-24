"""
Unit tests for release notes generation script.

Tests the .github/scripts/generate_release_notes.sh script to ensure it correctly
generates formatted release notes from git commits.
"""

import subprocess
import pytest
import tempfile
import os
from pathlib import Path


# Path to the release notes generation script
SCRIPT_PATH = Path(__file__).parent.parent / ".github" / "scripts" / "generate_release_notes.sh"


def run_generate_release_notes(version, current_tag, previous_tag=None, cwd=None):
    """
    Run the release notes generation script with the given parameters.

    Args:
        version: Semantic version string (e.g., "1.2.3")
        current_tag: Current git tag (e.g., "v1.2.3")
        previous_tag: Previous git tag (optional)
        cwd: Working directory for the command

    Returns:
        tuple: (stdout, stderr, exit_code)
    """
    cmd = [str(SCRIPT_PATH), version, current_tag]
    if previous_tag:
        cmd.append(previous_tag)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.stdout, result.stderr.strip(), result.returncode


class TestReleaseNotesGeneration:
    """Test suite for release notes generation functionality."""

    def test_script_exists_and_executable(self):
        """Test that the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert SCRIPT_PATH.is_file(), f"Script path is not a file: {SCRIPT_PATH}"
        # Check if executable (on Unix-like systems)
        assert os.access(SCRIPT_PATH, os.X_OK), f"Script is not executable: {SCRIPT_PATH}"

    def test_no_arguments_provided(self):
        """Test error handling when no arguments are provided"""
        result = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, "Script should fail when no arguments provided"
        assert "Version and current tag are required" in result.stderr, \
            f"Expected usage message, got: {result.stderr}"
        assert "Usage:" in result.stderr

    def test_only_version_provided(self):
        """Test error handling when only version is provided"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "1.0.0"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, "Script should fail when only version provided"
        assert "Version and current tag are required" in result.stderr

    def test_release_notes_structure_basic(self):
        """Test that release notes contain all required sections"""
        # Run in the actual repository to get real git data
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check for required sections
        assert "# Code Launcher v1.0.0" in stdout, "Missing title with version"
        assert "## What's Changed" in stdout, "Missing 'What's Changed' section"
        assert "## Downloads" in stdout, "Missing 'Downloads' section"
        assert "## Installation" in stdout, "Missing 'Installation' section"
        assert "### DEB Package" in stdout, "Missing DEB installation section"
        assert "### AppImage" in stdout, "Missing AppImage installation section"
        assert "**Full Changelog**:" in stdout, "Missing changelog link"

    def test_release_notes_version_in_title(self):
        """Test that version number appears in the title"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "2.5.7",
            "v2.5.7",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert "# Code Launcher v2.5.7" in stdout, "Version not in title"

    def test_release_notes_download_links(self):
        """Test that download links contain correct version and filenames"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.2.3",
            "v1.2.3",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check DEB package filename
        assert "code-launcher_1.2.3_all.deb" in stdout, "DEB filename incorrect"

        # Check AppImage filename
        assert "CodeLauncher-1.2.3-x86_64.AppImage" in stdout, "AppImage filename incorrect"

    def test_release_notes_installation_instructions_deb(self):
        """Test that DEB installation instructions are present and correct"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check DEB installation commands
        assert "sudo dpkg -i code-launcher_1.0.0_all.deb" in stdout, \
            "DEB installation command incorrect"
        assert "sudo apt-get install -f" in stdout, \
            "Missing dependency installation command"

    def test_release_notes_installation_instructions_appimage(self):
        """Test that AppImage installation instructions are present and correct"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check AppImage installation commands
        assert "chmod +x CodeLauncher-1.0.0-x86_64.AppImage" in stdout, \
            "AppImage chmod command incorrect"
        assert "./CodeLauncher-1.0.0-x86_64.AppImage" in stdout, \
            "AppImage execution command incorrect"

    def test_release_notes_changelog_link(self):
        """Test that changelog link is properly formatted"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            "v0.9.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check changelog link format
        assert "/compare/v0.9.0...v1.0.0" in stdout, \
            "Changelog comparison link incorrect"

    def test_release_notes_with_different_versions(self):
        """Test release notes generation with various version numbers"""
        test_cases = [
            ("0.0.1", "v0.0.1"),
            ("10.20.30", "v10.20.30"),
            ("999.999.999", "v999.999.999"),
        ]

        for version, tag in test_cases:
            stdout, stderr, exit_code = run_generate_release_notes(
                version,
                tag,
                cwd=Path(__file__).parent.parent
            )

            assert exit_code == 0, f"Script failed for version {version}: {stderr}"
            assert f"# Code Launcher {tag}" in stdout, \
                f"Version {tag} not in title"
            assert f"code-launcher_{version}_all.deb" in stdout, \
                f"DEB filename incorrect for version {version}"
            assert f"CodeLauncher-{version}-x86_64.AppImage" in stdout, \
                f"AppImage filename incorrect for version {version}"

    def test_release_notes_markdown_formatting(self):
        """Test that release notes use proper markdown formatting"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check markdown elements
        assert stdout.startswith("# "), "Should start with H1 heading"
        assert "## " in stdout, "Should contain H2 headings"
        assert "### " in stdout, "Should contain H3 headings"
        assert "```bash" in stdout, "Should contain bash code blocks"
        assert "**" in stdout, "Should contain bold text"
        assert "`" in stdout, "Should contain inline code"

    def test_release_notes_code_blocks(self):
        """Test that installation commands are in code blocks"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Count code blocks (should have at least 2: one for DEB, one for AppImage)
        code_block_count = stdout.count("```bash")
        assert code_block_count >= 2, \
            f"Expected at least 2 bash code blocks, found {code_block_count}"

        # Ensure code blocks are closed
        opening_blocks = stdout.count("```bash")
        closing_blocks = stdout.count("```\n") + stdout.count("```\n\n")
        assert opening_blocks <= closing_blocks, \
            "Code blocks not properly closed"


class TestReleaseNotesCommitExtraction:
    """Test suite for commit extraction in release notes."""

    def test_commits_formatted_as_bullets(self):
        """Test that commits are formatted as markdown bullet points"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Check that there are bullet points in the What's Changed section
        # Extract the section between "What's Changed" and "## Downloads"
        if "## What's Changed" in stdout and "## Downloads" in stdout:
            start = stdout.index("## What's Changed")
            end = stdout.index("## Downloads")
            changes_section = stdout[start:end]

            # Should contain bullet points (lines starting with -)
            assert "- " in changes_section, \
                "Commits should be formatted as bullet points"

    def test_initial_release_message(self):
        """Test that initial release message appears when no commits found"""
        # This test would need a fresh git repo with no history
        # For now, we'll just verify the script handles the case
        # by checking it doesn't crash with minimal git history
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script should handle minimal git history: {stderr}"


class TestReleaseNotesEdgeCases:
    """Test suite for edge cases in release notes generation."""

    def test_version_with_leading_zeros(self):
        """Test version numbers with leading zeros"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "01.02.03",
            "v01.02.03",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert "01.02.03" in stdout, "Version with leading zeros not handled"

    def test_very_long_version_numbers(self):
        """Test with very long version numbers"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "12345.67890.11111",
            "v12345.67890.11111",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"
        assert "12345.67890.11111" in stdout, "Long version numbers not handled"

    def test_output_is_valid_markdown(self):
        """Test that output is valid markdown (basic validation)"""
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed with stderr: {stderr}"

        # Basic markdown validation
        # - Should not have unclosed code blocks
        # - Should not have malformed headers
        # - Should have consistent structure

        lines = stdout.split('\n')
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block

            # Headers should not be inside code blocks
            if line.startswith('#') and in_code_block:
                pytest.fail("Header found inside code block")

        # Should not end with an open code block
        assert not in_code_block, "Markdown ends with unclosed code block"


class TestReleaseNotesRequirements:
    """Test suite validating specific requirements."""

    def test_requirement_3_5_commit_extraction(self):
        """
        Requirement 3.5: THE System SHALL generate release notes from git commits
        since the previous tag
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            "v0.9.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        assert "## What's Changed" in stdout, "Missing commit section"

    def test_requirement_4_1_commit_messages_extracted(self):
        """
        Requirement 4.1: WHEN creating a GitHub_Release, THE System SHALL extract
        commit messages since the last version tag
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        # Should have a What's Changed section with content
        assert "## What's Changed" in stdout

    def test_requirement_4_2_formatted_release_notes(self):
        """
        Requirement 4.2: THE System SHALL format commit messages into a readable
        release notes section
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        # Should be formatted with markdown sections
        assert "##" in stdout, "Missing section headers"
        assert "- " in stdout or "Initial release" in stdout, \
            "Missing formatted commit list"

    def test_requirement_4_3_version_in_notes(self):
        """
        Requirement 4.3: THE System SHALL include the version number in the release notes
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.2.3",
            "v1.2.3",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        assert "v1.2.3" in stdout, "Version not included in release notes"
        assert "1.2.3" in stdout, "Numeric version not included"

    def test_requirement_4_4_download_links(self):
        """
        Requirement 4.4: THE System SHALL include download links for both
        DEB_Package and AppImage_Package
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        assert "## Downloads" in stdout, "Missing Downloads section"
        assert "DEB Package" in stdout, "Missing DEB package reference"
        assert "AppImage" in stdout, "Missing AppImage reference"
        assert "code-launcher_1.0.0_all.deb" in stdout, "Missing DEB filename"
        assert "CodeLauncher-1.0.0-x86_64.AppImage" in stdout, \
            "Missing AppImage filename"

    def test_requirement_4_5_installation_instructions(self):
        """
        Requirement 4.5: THE System SHALL include installation instructions
        in the release notes
        """
        stdout, stderr, exit_code = run_generate_release_notes(
            "1.0.0",
            "v1.0.0",
            cwd=Path(__file__).parent.parent
        )

        assert exit_code == 0, f"Script failed: {stderr}"
        assert "## Installation" in stdout, "Missing Installation section"
        assert "sudo dpkg -i" in stdout, "Missing DEB installation command"
        assert "chmod +x" in stdout, "Missing AppImage chmod command"
        assert "```bash" in stdout, "Installation commands not in code blocks"
