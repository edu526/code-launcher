#!/bin/bash
#
# Script to create an AppImage (portable binary for Linux)
#

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "================================================"
echo "   AppImage Generator - Code Project Launcher"
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
APP_NAME="CodeLauncher"
VERSION="1.0.0"
BUILD_DIR="packaging/build_appimage"
APPDIR="$BUILD_DIR/$APP_NAME.AppDir"

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR"

echo "Creating AppImage structure..."

# Create directory structure
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/lib/code-launcher"

# Copy source code
echo "Copying files..."
cp -r src "$APPDIR/usr/lib/code-launcher/"
cp -r utils "$APPDIR/usr/lib/code-launcher/"

# Create executable script
cat > "$APPDIR/usr/bin/code-launcher" << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add installation directory to path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(app_dir, 'lib', 'code-launcher'))

from src.main import main

if __name__ == '__main__':
    main()
EOF

chmod +x "$APPDIR/usr/bin/code-launcher"

# Copy .desktop file
cp launcher/code-launcher.desktop "$APPDIR/usr/share/applications/"
sed -i 's|Exec=.*|Exec=code-launcher|g' "$APPDIR/usr/share/applications/code-launcher.desktop"

# Create AppRun
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/lib/code-launcher:${PYTHONPATH}"
exec "${HERE}/usr/bin/code-launcher" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# Create icon (using system icon)
cp launcher/code-launcher.desktop "$APPDIR/"
sed -i 's|Exec=.*|Exec=code-launcher|g' "$APPDIR/code-launcher.desktop"

# Download appimagetool if it doesn't exist
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    print_warning "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
echo ""
echo "Creating AppImage..."

# Create packages directory
mkdir -p packaging/packages

ARCH=x86_64 ./appimagetool-x86_64.AppImage "$APPDIR" "packaging/packages/$APP_NAME-$VERSION-x86_64.AppImage"

if [ $? -eq 0 ]; then
    print_status "AppImage created successfully"

    # Clean up
    rm -rf "$BUILD_DIR"

    echo ""
    echo "================================================"
    echo "   AppImage created successfully!"
    echo "================================================"
    echo ""
    echo "📦 File: ${YELLOW}packaging/packages/$APP_NAME-$VERSION-x86_64.AppImage${NC}"
    echo ""
    echo "To run:"
    echo "  ${YELLOW}chmod +x packaging/packages/$APP_NAME-$VERSION-x86_64.AppImage${NC}"
    echo "  ${YELLOW}./packaging/packages/$APP_NAME-$VERSION-x86_64.AppImage${NC}"
    echo ""
    echo "This file is portable and can run on any Linux distribution"
    echo ""
else
    print_error "Error creating AppImage"
    exit 1
fi
