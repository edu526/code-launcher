#!/bin/bash
#
# Script to create an executable binary using PyInstaller
#

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

echo "================================================"
echo "   Binary Generator - Code Launcher"
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

# Use virtual environment if available
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    PYTHON="$VENV_DIR/bin/python3"
    PYINSTALLER="$VENV_DIR/bin/pyinstaller"
    print_status "Using virtual environment"
else
    PYTHON="python3"
    PYINSTALLER="pyinstaller"
fi

# Verify Python
if ! command -v $PYTHON &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

# Check PyInstaller
if ! $PYTHON -c "import PyInstaller" &> /dev/null 2>&1; then
    print_error "PyInstaller is not installed. Run 'make venv' first."
    exit 1
fi

print_status "PyInstaller available"

# Create output directory
echo ""
echo "Creating binary..."

# Create the binary with PyInstaller
$PYINSTALLER --onefile \
    --name code-launcher \
    --add-data "src:src" \
    --add-data "utils:utils" \
    --hidden-import gi \
    --hidden-import gi.repository.Gtk \
    --hidden-import gi.repository.Gdk \
    --hidden-import gi.repository.GLib \
    --hidden-import gi.repository.Pango \
    --windowed \
    --distpath dist \
    --workpath build \
    src/main.py

if [ $? -eq 0 ]; then
    print_status "Binary created successfully: dist/code-launcher"

    echo ""
    echo "================================================"
    echo "   Binary created successfully!"
    echo "================================================"
    echo ""
    echo -e "📦 Location: ${YELLOW}dist/code-launcher${NC}"
    echo ""
    echo "To install:"
    echo -e "  ${YELLOW}sudo cp dist/code-launcher /usr/local/bin/${NC}"
    echo ""
    echo "To run:"
    echo -e "  ${YELLOW}./dist/code-launcher${NC}"
    echo ""
else
    print_error "Error creating binary"
    exit 1
fi
