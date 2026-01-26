# Technology Stack

## Core Technologies

- **Language**: Python 3.6+
- **GUI Framework**: GTK 3 (via PyGObject/gi)
- **Platform**: Linux only
- **Package Manager**: setuptools

## Key Dependencies

- `PyGObject>=3.30.0` - Python bindings for GTK 3
- `gi.repository.Gtk` - GTK 3 interface
- `gi.repository.Gdk` - GDK for event handling

## Build System

The project uses a Makefile for build automation with multiple installation options:

### Common Commands

```bash
# Development
python3 src/main.py              # Run from source
python3 -m pytest tests/         # Run test suite

# Installation
make install                     # Local install (~/.local/bin)
make uninstall                   # Remove local install

# Packaging
make deb                         # Build .deb package
make appimage                    # Build AppImage (requires venv)
make all                         # Build all formats
make venv                        # Create virtual environment

# Cleanup
make clean                       # Remove build artifacts
```

## Testing

- **Framework**: pytest
- **Test Location**: `tests/` directory
- **Mocking**: unittest.mock for GTK components
- Tests cover UI components, context menus, dialogs, and integration workflows

## Entry Point

Application starts via `src/main.py` which:
1. Configures GTK 3.0 requirement
2. Sets up logging to `~/.config/code-launcher/code-launcher.log`
3. Implements single-instance lock using fcntl
4. Creates main window and starts GTK main loop
