# Makefile for Code Launcher

VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip3

.PHONY: help install uninstall clean deb appimage all venv test test-core test-gtk test-gtk-full test-pbt

help:
	@echo "Code Launcher - Build options"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  venv       - Create virtual environment for building"
	@echo "  install    - Install locally (recommended)"
	@echo "  deb        - Create .deb package for Debian/Ubuntu"
	@echo "  appimage   - Create portable AppImage"
	@echo "  all        - Create all formats (deb + appimage)"
	@echo "  test       - Run all tests (requires GTK dependencies)"
	@echo "  test-core  - Run core tests (no GTK required)"
	@echo "  test-gtk   - Run GTK-dependent tests (stable subset)"
	@echo "  test-gtk-full - Run ALL GTK tests (including problematic ones)"
	@echo "  test-pbt   - Run property-based tests only"
	@echo "  uninstall  - Uninstall the application"
	@echo "  clean      - Clean build files"

venv:
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)
	@$(PIP) install --upgrade pip
	@echo "Virtual environment created at $(VENV_DIR)"

install:
	@echo "Installing Code Launcher..."
	@bash packaging/install_local.sh

deb:
	@echo "Creating .deb package..."
	@bash packaging/build_deb.sh

appimage: venv
	@echo "Creating AppImage..."
	@bash packaging/build_appimage.sh

all: venv
	@echo "Creating all formats..."
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

# Test targets
test:
	@echo "Running all tests (including GTK-dependent tests)..."
	@echo "Note: This requires GTK dependencies to be installed"
	@echo "Install with: sudo apt install python3-gi gir1.2-gtk-3.0 (Ubuntu/Debian)"
	@echo "             sudo dnf install python3-gobject gtk3 (Fedora)"
	@echo "             sudo pacman -S python-gobject gtk3 (Arch)"
	@echo ""
	@$(PYTHON) -m pytest tests/ -v --tb=short
	@echo ""
	@echo "All tests completed!"

test-core:
	@echo "Running core tests (no GTK dependencies required)..."
	@$(PYTHON) -m pytest \
		tests/test_terminal_detector.py \
		tests/test_terminal_manager.py \
		tests/test_config.py \
		tests/test_terminal_preferences.py \
		tests/test_terminal_action.py \
		tests/test_terminal_error_handling.py \
		-v --tb=short
	@echo ""
	@echo "Core tests completed!"

test-gtk:
	@echo "Running GTK-dependent tests..."
	@echo "Note: This requires GTK dependencies to be installed"
	@$(PYTHON) -m pytest \
		tests/test_integration_wiring.py \
		tests/test_terminal_integration_simple.py \
		tests/test_terminal_integration_workflow.py \
		tests/test_graceful_degradation.py \
		-v --tb=short
	@echo ""
	@echo "GTK tests completed!"

test-gtk-full:
	@echo "Running ALL GTK-dependent tests (including problematic persistence tests)..."
	@echo "Note: This requires GTK dependencies to be installed"
	@$(PYTHON) -m pytest \
		tests/test_integration_wiring.py \
		tests/test_terminal_integration_simple.py \
		tests/test_terminal_integration_workflow.py \
		tests/test_terminal_complete_workflow.py \
		tests/test_terminal_workflow_final.py \
		tests/test_graceful_degradation.py \
		-v --tb=short
	@echo ""
	@echo "All GTK tests completed!"

test-pbt:
	@echo "Running property-based tests..."
	@$(PYTHON) -m pytest \
		tests/test_terminal_preferences_properties.py \
		tests/test_context_menu_integration_properties.py \
		tests/test_terminal_error_handling_properties.py \
		-v --tb=short
	@echo ""
	@echo "Property-based tests completed!"
