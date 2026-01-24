# Makefile for Code Launcher

.PHONY: help install uninstall clean binary deb appimage all

help:
	@echo "Code Launcher - Build options"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install locally (quick method)"
	@echo "  binary     - Create executable binary with PyInstaller"
	@echo "  deb        - Create .deb package for Debian/Ubuntu"
	@echo "  appimage   - Create portable AppImage"
	@echo "  all        - Create all formats"
	@echo "  uninstall  - Uninstall the application"
	@echo "  clean      - Clean build files"

install:
	@echo "Installing Code Launcher..."
	@bash launcher/install.sh

binary:
	@echo "Creating executable binary..."
	@bash packaging/build_binary.sh

deb:
	@echo "Creating .deb package..."
	@bash packaging/build_deb.sh

appimage:
	@echo "Creating AppImage..."
	@bash packaging/build_appimage.sh

all: binary deb appimage
	@echo ""
	@echo "All formats created successfully"

uninstall:
	@echo "Uninstalling Code Launcher..."
	@rm -f ~/.local/bin/code-launcher
	@rm -f ~/.local/share/applications/code-launcher.desktop
	@rm -f ~/.local/share/icons/hicolor/scalable/apps/code-launcher.svg
	@rm -f ~/.local/share/pixmaps/code-launcher.svg
	@echo "Uninstalled (configuration preserved in ~/.config/code-launcher)"

clean:
	@echo "Cleaning build files..."
	@rm -rf build packaging/bin packaging/packages packaging/build_*
	@rm -f *.spec
	@rm -f appimagetool-x86_64.AppImage
	@echo "Cleanup completed"
