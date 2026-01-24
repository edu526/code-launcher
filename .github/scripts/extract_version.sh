#!/bin/bash

# Version Extraction Script
# Extracts semantic version from git tag and validates format
# Usage: ./extract_version.sh <tag_name>
# Example: ./extract_version.sh v1.2.3
# Output: 1.2.3

set -e  # Exit on error
set -u  # Exit on undefined variable

# Check if tag name is provided
if [ $# -ne 1 ]; then
  echo "Error: Tag name is required" >&2
  echo "Usage: $0 <tag_name>" >&2
  echo "Example: $0 v1.2.3" >&2
  exit 1
fi

TAG_NAME="$1"

# Validate tag format: v[0-9]+.[0-9]+.[0-9]+
# This regex ensures semantic versioning format
if ! echo "$TAG_NAME" | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: Invalid version tag format: $TAG_NAME" >&2
  echo "Expected format: v[MAJOR].[MINOR].[PATCH]" >&2
  echo "Examples: v1.0.0, v2.15.3, v10.0.1" >&2
  exit 1
fi

# Extract version by removing 'v' prefix
VERSION="${TAG_NAME#v}"

# Validate that version was extracted successfully
if [ -z "$VERSION" ]; then
  echo "Error: Failed to extract version from tag: $TAG_NAME" >&2
  exit 1
fi

# Output the extracted version
echo "$VERSION"
