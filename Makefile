# Makefile for Code Launcher

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip3

.PHONY: help install uninstall clean binary deb appimage all venv

help:
	@echo "Code Launcher - Build options"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  venv       - Create virtual environment for building"
	@echo "  install    - Install locally (quick method)"
	@echo "  binary     - Create executable binary with PyInstaller"
	@echo "  deb        - Create .deb package for Debian/Ubuntu"
	@echo "  appimage   - Create portable AppImage"
	@echo "  all        - Create all formats"
	@echo "  uninstall  - Uninstall the application"
	@echo "  clean      - Clean build files"

venv:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)
	@$(PIP) install --upgrade pip
	@$(PIP) install pyinstaller
	@echo "Virtual environment created at $(VENV_DIR)"

install:
	@echo "Installing Code Launcher..."
	@bash packaging/install_local.sh

binary: venv
	@echo "Creating executable binary..."
	@bash packaging/build_binary.sh

deb:
	@echo "Creating .deb package..."
	@bash packaging/build_deb.sh

appimage:
	@echo "Creating AppImage..."
	@bash packaging/build_appimage.sh

all: venv
	@echo "Creating all formats..."
	@bash packaging/build_binary.sh
	@bash packaging/build_deb.sh
	@bash packaging/build_appimage.sh
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
	@rm -rf build dist packaging/build_*
	@rm -rf $(VENV_DIR)
	@rm -f *.spec
	@rm -f appimagetool-x86_64.AppImage
	@echo "Cleanup completed"
