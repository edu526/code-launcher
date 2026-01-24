#!/bin/bash

# Release Notes Generation Script
# Generates formatted release notes from git commits between tags
# Usage: ./generate_release_notes.sh <version> <current_tag> [previous_tag]
# Example: ./generate_release_notes.sh 1.2.3 v1.2.3 v1.2.2
# Output: Markdown-formatted release notes

set -e  # Exit on error
set -u  # Exit on undefined variable

# Check if required arguments are provided
if [ $# -lt 2 ]; then
  echo "Error: Version and current tag are required" >&2
  echo "Usage: $0 <version> <current_tag> [previous_tag]" >&2
  echo "Example: $0 1.2.3 v1.2.3 v1.2.2" >&2
  exit 1
fi

VERSION="$1"
CURRENT_TAG="$2"
PREVIOUS_TAG="${3:-}"

# If no previous tag provided, try to find the most recent tag before current
if [ -z "$PREVIOUS_TAG" ]; then
  # Get the tag before the current one
  PREVIOUS_TAG=$(git describe --tags --abbrev=0 "$CURRENT_TAG^" 2>/dev/null || echo "")

  # If still no previous tag, use the first commit
  if [ -z "$PREVIOUS_TAG" ]; then
    PREVIOUS_TAG=$(git rev-list --max-parents=0 HEAD)
  fi
fi

# Extract commits between tags
# Format: one commit message per line
if [ -n "$PREVIOUS_TAG" ]; then
  COMMITS=$(git log --pretty=format:"- %s" "${PREVIOUS_TAG}..${CURRENT_TAG}" 2>/dev/null || echo "")
else
  COMMITS=$(git log --pretty=format:"- %s" "$CURRENT_TAG" 2>/dev/null || echo "")
fi

# If no commits found, provide a default message
if [ -z "$COMMITS" ]; then
  COMMITS="- Initial release"
fi

# Get repository information for the changelog link
REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')

# Generate release notes in markdown format
cat << EOF
# Code Launcher ${CURRENT_TAG}

## What's Changed

${COMMITS}

## Downloads

- **DEB Package** (Debian/Ubuntu): \`code-launcher_${VERSION}_all.deb\`
- **AppImage** (Universal Linux): \`CodeLauncher-${VERSION}-x86_64.AppImage\`

## Installation

### DEB Package
\`\`\`bash
sudo dpkg -i code-launcher_${VERSION}_all.deb
sudo apt-get install -f  # Install dependencies if needed
\`\`\`

### AppImage
\`\`\`bash
chmod +x CodeLauncher-${VERSION}-x86_64.AppImage
./CodeLauncher-${VERSION}-x86_64.AppImage
\`\`\`

---

**Full Changelog**: ${REPO_URL}/compare/${PREVIOUS_TAG}...${CURRENT_TAG}
EOF
