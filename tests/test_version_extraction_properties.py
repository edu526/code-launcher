"""
Property-based tests for version extraction script.

Tests universal correctness properties of the .github/scripts/extract_version.sh
script using hypothesis for property-based testing.
"""

import subprocess
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings


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


# Strategy for generating valid semantic version numbers (MAJOR.MINOR.PATCH)
# Each component is a non-negative integer
semantic_version_strategy = st.builds(
    lambda major, minor, patch: f"{major}.{minor}.{patch}",
    major=st.integers(min_value=0, max_value=999),
    minor=st.integers(min_value=0, max_value=999),
    patch=st.integers(min_value=0, max_value=999)
)


class TestVersionExtractionProperties:
    """Property-based tests for version extraction correctness."""

    @given(version=semantic_version_strategy)
    @settings(max_examples=100)
    def test_property_version_extraction_correctness(self, version):
        """
        **Property 1: Version Extraction Correctness**
        **Validates: Requirements 1.1**

        For any valid semantic version tag in the format v[MAJOR].[MINOR].[PATCH],
        extracting the version should return the numeric portion without the 'v' prefix.

        This property ensures that:
        1. The script successfully extracts the version from valid tags
        2. The extracted version matches the numeric portion exactly
        3. The 'v' prefix is correctly removed
        4. The script exits with success code (0)
        """
        # Construct the tag with 'v' prefix
        tag = f"v{version}"

        # Run the extraction script
        stdout, stderr, exit_code = run_extract_version(tag)

        # Property assertions
        assert exit_code == 0, (
            f"Script should succeed for valid tag '{tag}', "
            f"but failed with exit code {exit_code}. "
            f"stderr: {stderr}"
        )

        assert stdout == version, (
            f"Extracted version should match the numeric portion. "
            f"Expected '{version}', got '{stdout}' for tag '{tag}'"
        )

        assert stderr == "", (
            f"No error output expected for valid tag '{tag}', "
            f"but got stderr: {stderr}"
        )

        # Verify the 'v' prefix was removed
        assert not stdout.startswith('v'), (
            f"Extracted version should not contain 'v' prefix. "
            f"Got '{stdout}' for tag '{tag}'"
        )

        # Verify the extracted version is a valid semantic version format
        parts = stdout.split('.')
        assert len(parts) == 3, (
            f"Extracted version should have exactly 3 parts (MAJOR.MINOR.PATCH). "
            f"Got {len(parts)} parts: '{stdout}'"
        )

        # Verify each part is numeric
        for i, part in enumerate(parts):
            assert part.isdigit(), (
                f"Part {i} of extracted version should be numeric. "
                f"Got '{part}' in version '{stdout}'"
            )


class TestVersionTagValidationProperties:
    """Property-based tests for version tag validation."""

    @given(tag=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=0, max_size=100))
    @settings(max_examples=100)
    def test_property_version_tag_validation(self, tag):
        """
        **Property 2: Version Tag Validation**
        **Validates: Requirements 1.2, 1.5**

        For any string, the version tag validator should accept it if and only if
        it matches the pattern v[0-9]+.[0-9]+.[0-9]+.

        This property ensures that:
        1. Valid semantic version tags (v[MAJOR].[MINOR].[PATCH]) are accepted
        2. Invalid tags are rejected with non-zero exit code
        3. The validation is consistent and deterministic
        4. Edge cases are handled correctly
        """
        # Run the extraction script
        stdout, stderr, exit_code = run_extract_version(tag)

        # Check if the tag matches the valid pattern
        import re
        is_valid = bool(re.match(r'^v[0-9]+\.[0-9]+\.[0-9]+$', tag))

        if is_valid:
            # Valid tags should succeed
            assert exit_code == 0, (
                f"Script should succeed for valid tag '{tag}', "
                f"but failed with exit code {exit_code}. "
                f"stderr: {stderr}"
            )

            # Should extract the version correctly
            expected_version = tag[1:]  # Remove 'v' prefix
            assert stdout == expected_version, (
                f"Extracted version should match the numeric portion. "
                f"Expected '{expected_version}', got '{stdout}' for tag '{tag}'"
            )

            # No error output for valid tags
            assert stderr == "", (
                f"No error output expected for valid tag '{tag}', "
                f"but got stderr: {stderr}"
            )
        else:
            # Invalid tags should fail
            assert exit_code != 0, (
                f"Script should fail for invalid tag '{tag}', "
                f"but succeeded with exit code {exit_code}. "
                f"stdout: {stdout}"
            )

            # Should have error message in stderr
            assert stderr != "", (
                f"Error message expected in stderr for invalid tag '{tag}', "
                f"but stderr was empty"
            )

            # Should not output a version to stdout
            # (or if it does, it should be an error message)
            # The script should not extract a version from invalid tags
