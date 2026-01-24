#!/bin/bash
#
# Script to create a .deb package for Debian/Ubuntu
#

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "================================================"
echo "   DEB Package Generator - Code Project Launcher"
echo "================================================"
echo ""

# Colors
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

# Variables
PACKAGE_NAME="code-project-launcher"
VERSION="1.0.0"
ARCH="all"
BUILD_DIR="packaging/build_deb"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create directory structure
echo "Creating package structure..."

mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/local/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/code-launcher/src"
mkdir -p "$BUILD_DIR/usr/share/code-launcher/utils"
mkdir -p "$BUILD_DIR/usr/share/doc/code-launcher"

# Copy files
echo "Copying files..."

# Copy source code
cp -r src/* "$BUILD_DIR/usr/share/code-launcher/src/"
cp -r utils/* "$BUILD_DIR/usr/share/code-launcher/utils/"

# Create executable script
cat > "$BUILD_DIR/usr/local/bin/code-launcher" << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add installation directory to path
sys.path.insert(0, '/usr/share/code-launcher')

from src.main import main

if __name__ == '__main__':
    main()
EOF

chmod +x "$BUILD_DIR/usr/local/bin/code-launcher"

# Copy .desktop file
cp launcher/code-launcher.desktop "$BUILD_DIR/usr/share/applications/"
sed -i 's|Exec=.*|Exec=/usr/local/bin/code-launcher|g' "$BUILD_DIR/usr/share/applications/code-launcher.desktop"

# Copy documentation
cp README.md "$BUILD_DIR/usr/share/doc/code-launcher/" 2>/dev/null || true
cp QUICK_START.md "$BUILD_DIR/usr/share/doc/code-launcher/" 2>/dev/null || true

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.6), python3-gi, gir1.2-gtk-3.0
Maintainer: Eduardo <your-email@example.com>
Description: GTK-based project launcher for VSCode and Kiro
 A modern, Finder-style project launcher with category support,
 intelligent search, and integration with VSCode and Kiro editors.
 .
 Features:
  - Category-based project organization
  - Intelligent search with flexible matching
  - Context menu actions
  - Keyboard shortcuts
  - Logs viewer
  - Preferences for default editor
EOF

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Create configuration directory
mkdir -p "$HOME/.config/code-launcher"

# Create example configuration files if they don't exist
if [ ! -f "$HOME/.config/code-launcher/projects.json" ]; then
    cat > "$HOME/.config/code-launcher/projects.json" << 'JSONEOF'
{}
JSONEOF
fi

if [ ! -f "$HOME/.config/code-launcher/categories.json" ]; then
    cat > "$HOME/.config/code-launcher/categories.json" << 'JSONEOF'
{}
JSONEOF
fi

echo "Code Project Launcher installed successfully"
echo "Run 'code-launcher' to start the application"

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Create prerm script
cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

echo "Uninstalling Code Project Launcher..."

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/prerm"

# Build the package
echo ""
echo "Building .deb package..."

# Create packages directory
mkdir -p packaging/packages

dpkg-deb --build "$BUILD_DIR" "packaging/packages/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

if [ $? -eq 0 ]; then
    print_status ".deb package created successfully"

    # Clean up
    rm -rf "$BUILD_DIR"

    echo ""
    echo "================================================"
    echo "   DEB package created successfully!"
    echo "================================================"
    echo ""
    echo "📦 File: ${YELLOW}packaging/packages/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb${NC}"
    echo ""
    echo "To install:"
    echo "  ${YELLOW}sudo dpkg -i packaging/packages/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb${NC}"
    echo "  ${YELLOW}sudo apt-get install -f${NC}  (if there are missing dependencies)"
    echo ""
    echo "To uninstall:"
    echo "  ${YELLOW}sudo dpkg -r ${PACKAGE_NAME}${NC}"
    echo ""
else
    print_error "Error creating package"
    exit 1
fi
