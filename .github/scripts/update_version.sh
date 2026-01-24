#!/bin/bash
#
# Version Update Script for GitHub Actions
# Updates version strings across all project files
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if version argument is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 <version>"
    print_error "Example: $0 1.2.3"
    exit 1
fi

NEW_VERSION="$1"

# Validate version format (should be MAJOR.MINOR.PATCH)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format: $NEW_VERSION"
    print_error "Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
    exit 1
fi

echo "================================================"
echo "   Version Update Script"
echo "================================================"
echo ""
echo "Updating version to: $NEW_VERSION"
echo ""

# Update setup.py
if [ -f "setup.py" ]; then
    print_status "Updating setup.py..."
    sed -i "s/version=\"[0-9.]*\"/version=\"$NEW_VERSION\"/" setup.py

    # Verify the update
    if grep -q "version=\"$NEW_VERSION\"" setup.py; then
        print_status "setup.py updated successfully"
    else
        print_error "Failed to update setup.py"
        exit 1
    fi
else
    print_warning "setup.py not found, skipping..."
fi

# Update packaging/build_deb.sh
if [ -f "packaging/build_deb.sh" ]; then
    print_status "Updating packaging/build_deb.sh..."
    sed -i "s/VERSION=\"[0-9.]*\"/VERSION=\"$NEW_VERSION\"/" packaging/build_deb.sh

    # Verify the update
    if grep -q "VERSION=\"$NEW_VERSION\"" packaging/build_deb.sh; then
        print_status "packaging/build_deb.sh updated successfully"
    else
        print_error "Failed to update packaging/build_deb.sh"
        exit 1
    fi
else
    print_warning "packaging/build_deb.sh not found, skipping..."
fi

# Update packaging/build_appimage.sh
if [ -f "packaging/build_appimage.sh" ]; then
    print_status "Updating packaging/build_appimage.sh..."
    sed -i "s/VERSION=\"[0-9.]*\"/VERSION=\"$NEW_VERSION\"/" packaging/build_appimage.sh

    # Verify the update
    if grep -q "VERSION=\"$NEW_VERSION\"" packaging/build_appimage.sh; then
        print_status "packaging/build_appimage.sh updated successfully"
    else
        print_error "Failed to update packaging/build_appimage.sh"
        exit 1
    fi
else
    print_warning "packaging/build_appimage.sh not found, skipping..."
fi

# Update README.md version references
if [ -f "README.md" ]; then
    print_status "Updating README.md..."

    # Update version in DEB package installation command
    sed -i "s/code-launcher_[0-9.]*_all\.deb/code-launcher_${NEW_VERSION}_all.deb/g" README.md

    # Update version in AppImage filename
    sed -i "s/CodeLauncher-[0-9.]*-x86_64\.AppImage/CodeLauncher-${NEW_VERSION}-x86_64.AppImage/g" README.md

    # Update version badges if they exist (e.g., version-1.0.0)
    sed -i "s/version-[0-9.]*/version-${NEW_VERSION}/g" README.md

    print_status "README.md updated successfully"
else
    print_warning "README.md not found, skipping..."
fi

echo ""
echo "================================================"
echo "   Version Update Complete"
echo "================================================"
echo ""
echo "Updated files:"
echo "  - setup.py"
echo "  - packaging/build_deb.sh"
echo "  - packaging/build_appimage.sh"
echo "  - README.md"
echo ""

# Git operations (only if running in CI environment)
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    print_status "Committing version updates..."

    # Configure git
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"

    # Add updated files
    git add setup.py packaging/build_deb.sh packaging/build_appimage.sh README.md

    # Commit changes
    if git diff --staged --quiet; then
        print_warning "No changes to commit"
    else
        git commit -m "chore: bump version to $NEW_VERSION"
        print_status "Changes committed"

        # Push changes
        print_status "Pushing changes..."
        git push
        print_status "Changes pushed successfully"
    fi
else
    print_warning "Not running in CI environment, skipping git operations"
    print_warning "To commit manually, run:"
    echo ""
    echo "  git add setup.py packaging/build_deb.sh packaging/build_appimage.sh README.md"
    echo "  git commit -m \"chore: bump version to $NEW_VERSION\""
    echo "  git push"
    echo ""
fi

print_status "Version update script completed successfully!"
