#!/bin/bash
#
# Script to create an executable binary using PyInstaller
#

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "================================================"
echo "   Binary Generator - Code Project Launcher"
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

# Verify Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

# Install PyInstaller if not installed
if ! python3 -c "import PyInstaller" &> /dev/null 2>&1; then
    print_warning "PyInstaller is not installed. Installing..."
    pip3 install --user pyinstaller
fi

print_status "PyInstaller available"

# Create output directory
mkdir -p dist/bin
mkdir -p build

echo ""
echo "Creating binary..."

# Create the binary with PyInstaller
pyinstaller --onefile \
    --name code-launcher \
    --add-data "src:src" \
    --add-data "utils:utils" \
    --hidden-import gi \
    --hidden-import gi.repository.Gtk \
    --hidden-import gi.repository.Gdk \
    --hidden-import gi.repository.GLib \
    --hidden-import gi.repository.Pango \
    --windowed \
    --distpath dist/bin \
    --workpath build \
    src/main.py

if [ $? -eq 0 ]; then
    print_status "Binary created successfully: dist/bin/code-launcher"

    echo ""
    echo "================================================"
    echo "   Binary created successfully!"
    echo "================================================"
    echo ""
    echo "📦 Location: ${YELLOW}dist/bin/code-launcher${NC}"
    echo ""
    echo "To install:"
    echo "  ${YELLOW}sudo cp dist/bin/code-launcher /usr/local/bin/${NC}"
    echo ""
    echo "To run:"
    echo "  ${YELLOW}./dist/bin/code-launcher${NC}"
    echo ""
else
    print_error "Error creating binary"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

# Install PyInstaller if not installed
if ! python3 -c "import PyInstaller" &> /dev/null 2>&1; then
    print_warning "PyInstaller is not installed. Installing..."
    pip3 install --user pyinstaller
fi

print_status "PyInstaller available"

# Create output directory
mkdir -p dist
mkdir -p build

echo ""
echo "Creating binary..."

# Create the binary with PyInstaller
pyinstaller --onefile \
    --name code-launcher \
    --add-data "src:src" \
    --add-data "utils:utils" \
    --hidden-import gi \
    --hidden-import gi.repository.Gtk \
    --hidden-import gi.repository.Gdk \
    --hidden-import gi.repository.GLib \
    --hidden-import gi.repository.Pango \
    --windowed \
    src/main.py

if [ $? -eq 0 ]; then
    print_status "Binary created successfully in: dist/code-launcher"

    echo ""
    echo "================================================"
    echo "   Binary created successfully!"
    echo "================================================"
    echo ""
    echo "📦 Location: ${YELLOW}dist/code-launcher${NC}"
    echo ""
    echo "To install:"
    echo "  ${YELLOW}sudo cp dist/code-launcher /usr/local/bin/${NC}"
    echo ""
    echo "To run:"
    echo "  ${YELLOW}./dist/code-launcher${NC}"
    echo ""
else
    print_error "Error creating binary"
    exit 1
fi
