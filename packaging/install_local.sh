#!/bin/bash
#
# Local installation script for Code Launcher
# Installs from source code for development
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo "================================================"
echo "   Code Launcher - Local Install"
echo "================================================"
echo ""

# Verify we're in the project directory
if [ ! -f "src/main.py" ]; then
    print_error "Error: src/main.py not found. Run from project root."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is required. Please install it first."
    exit 1
fi
print_status "Python3 found"

# Check GTK dependencies
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" &> /dev/null 2>&1; then
    print_error "GTK dependencies missing. Install with:"
    echo "  Debian/Ubuntu: sudo apt install python3-gi gir1.2-gtk-3.0"
    echo "  Fedora: sudo dnf install python3-gobject gtk3"
    echo "  Arch: sudo pacman -S python-gobject gtk3"
    exit 1
fi
print_status "GTK dependencies found"

# Installation directories
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/code-launcher"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"
PROJECT_DIR="$(pwd)"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$PIXMAPS_DIR"

# Create launcher script
cat > "$INSTALL_DIR/code-launcher" << EOF
#!/usr/bin/env python3
import sys
sys.path.insert(0, '$PROJECT_DIR')
from src.main import main
if __name__ == '__main__':
    main()
EOF

chmod +x "$INSTALL_DIR/code-launcher"
print_status "Launcher installed to $INSTALL_DIR/code-launcher"

# Install icon
if [ -f "packaging/code-launcher.svg" ]; then
    cp "packaging/code-launcher.svg" "$ICON_DIR/code-launcher.svg"
    cp "packaging/code-launcher.svg" "$PIXMAPS_DIR/code-launcher.svg"
    print_status "Icon installed"
fi

# Create desktop entry
if [ -f "packaging/code-launcher.desktop" ]; then
    sed -e "s|Exec=.*|Exec=$INSTALL_DIR/code-launcher|g" \
        -e "s|Icon=.*|Icon=code-launcher|g" \
        packaging/code-launcher.desktop > "$DESKTOP_DIR/code-launcher.desktop"
    print_status "Desktop entry created"
fi

# Create empty config files if they don't exist
[ ! -f "$CONFIG_DIR/projects.json" ] && echo "{}" > "$CONFIG_DIR/projects.json"
[ ! -f "$CONFIG_DIR/categories.json" ] && echo "{}" > "$CONFIG_DIR/categories.json"
[ ! -f "$CONFIG_DIR/preferences.json" ] && echo '{"default_editor":"kiro"}' > "$CONFIG_DIR/preferences.json"
print_status "Configuration directory ready: $CONFIG_DIR"

# Check PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "~/.local/bin is not in your PATH"
    echo "  Add to ~/.bashrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "================================================"
echo "   Installation Complete!"
echo "================================================"
echo ""
echo -e "Run: ${GREEN}code-launcher${NC}"
echo -e "Config: ${YELLOW}$CONFIG_DIR${NC}"
echo ""
echo -e "To uninstall: ${YELLOW}make uninstall${NC}"
echo ""

