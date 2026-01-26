# Code Launcher

Finder-style project launcher for VSCode and Kiro with modern GTK interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Local Installation](#local-installation-recommended)
  - [DEB Package](#deb-package-debianubuntu)
  - [AppImage](#appimage-portable)
- [Usage](#usage)
  - [Starting the Application](#starting-the-application)
  - [Navigation](#navigation)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
- [Configuration](#configuration)
- [Uninstallation](#uninstallation)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🎯 Finder-style navigation with columns
- 📁 Organization by categories and subcategories
- 🔍 Smart search with text normalization
- ⚡ Keyboard shortcuts (Ctrl+F to search, Esc to exit)
- 🎨 Visual icon selector for categories
- 📝 Integrated log viewer
- ⚙️ Preferences to select default editor (Kiro/VSCode)
- 🖱️ Context menu with quick actions
- 🚀 Multiple installation options

## Requirements

- Linux (any distribution)
- Python 3.6+
- GTK 3
- VSCode and/or Kiro installed

## Installation

### Local Installation (Recommended)

```bash
make install
```

**Features:**
- Installs in `~/.local/bin`
- Runs from source code
- Ideal for development and daily use

### DEB Package (Debian/Ubuntu)

```bash
make deb
sudo dpkg -i dist/code-launcher_1.0.0_all.deb
```

**Features:**
- Automatic dependency management
- Integration with package system
- System-wide installation

### AppImage (Portable)

```bash
make appimage
chmod +x dist/CodeLauncher-1.0.0-x86_64.AppImage
./dist/CodeLauncher-1.0.0-x86_64.AppImage
```

**Features:**
- Works on any Linux distribution
- No installation required
- Portable and self-contained

### Build All Formats

```bash
make all
```

## Usage

### Starting the Application

```bash
# If installed locally
code-launcher

# Or from the applications menu
# Search for "Code Launcher"
```

### Navigation

- **Columns**: Navigate through categories → subcategories → projects
- **Search**: Press `Ctrl+F` or type in the search field
- **Double click**: Opens project with default editor
- **Right click**: Context menu with options (Open in VSCode/Kiro, Delete)
- **Esc**: Exit application

### Keyboard Shortcuts

- `Ctrl+F`: Focus search
- `Esc`: Exit
- `↑/↓`: Navigate through items
- `Enter`: Open selected project

### Smart Search

Search normalizes text automatically:
- "eportal" finds "e-portal"
- "myproject" finds "my_project"
- Searches in project and category names
- Shows all projects from found categories

## Configuration

### Using the Graphical Interface (Recommended)

1. Open the application
2. Click the configuration button (⚙️)
3. Select:
   - **Edit Categories**: Manage categories and subcategories
   - **Edit Projects**: Add or edit projects
   - **Preferences**: Select default editor (Kiro/VSCode)
   - **View Logs**: Check application history

### Manual Configuration

Configuration files are in `~/.config/code-launcher/`:

**Categories** (`categories.json`):
```json
{
  "Web": {
    "icon": "internet-web-browser",
    "description": "Web projects",
    "subcategories": {
      "Frontend": {
        "icon": "code",
        "description": "Frontend projects"
      }
    }
  }
}
```

**Projects** (`projects.json`):
```json
{
  "My Project": {
    "path": "/path/to/project",
    "category": "Web",
    "subcategory": "Frontend"
  }
}
```

**Preferences** (`preferences.json`):
```json
{
  "default_editor": "kiro"
}
```

## Uninstallation

### Local Installation
```bash
make uninstall
```

### DEB Package
```bash
sudo dpkg -r code-launcher
```

### AppImage
Simply delete the executable file.

**Note**: Configuration in `~/.config/code-launcher` is preserved.

## Troubleshooting

### GTK dependencies not found

```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3

# Arch Linux
sudo pacman -S python-gobject gtk3
```

### "No module named 'gi'" error when running from console

If you get this error when running `code-launcher` from the terminal but it works from the desktop icon:

**Cause**: You have a Python virtual environment activated that doesn't have access to system GTK packages.

**Solution 1** (Quick): Deactivate the venv before running:
```bash
deactivate  # If you have a venv active
code-launcher
```

**Solution 2** (Permanent): Recreate your project venv with system packages access:
```bash
cd /path/to/code-launcher
rm -rf .venv
make venv  # Creates venv with --system-site-packages
```

**Solution 3** (Alternative): Run directly from source:
```bash
python3 src/main.py
```

### Editor doesn't open

```bash
# Check VSCode
which code

# Check Kiro
which kiro
```

### View application logs

1. Open the application
2. Configuration (⚙️) → View Logs
3. Or manually: `~/.config/code-launcher/code-launcher.log`

### Clear configuration

```bash
rm -rf ~/.config/code-launcher
# The application will create new files on startup
```

## Development

### Project Structure

```
code-launcher/
├── src/                    # Source code
│   ├── core/              # Configuration management
│   ├── ui/                # User interface
│   ├── dialogs/           # Dialog windows
│   └── context_menu/      # Context menu system
├── utils/                  # Utilities
├── tests/                  # Test suite
├── packaging/              # Build and packaging files
│   ├── build_deb.sh       # DEB builder
│   ├── build_appimage.sh  # AppImage builder
│   ├── install_local.sh   # Local installation
│   ├── code-launcher.desktop  # Desktop entry
│   └── code-launcher.svg  # Application icon
├── Makefile               # Build automation
├── setup.py               # Python package setup
├── LICENSE                # MIT License
└── README.md              # This file
```

### Run from source

```bash
python3 src/main.py
```

### Run tests

```bash
# Run all tests (requires GTK dependencies)
make test

# Run core tests only (no GTK required)
make test-core

# Run GTK-dependent tests only
make test-gtk

# Run property-based tests only
make test-pbt

# Or use pytest directly
python3 -m pytest tests/
```

### Clean build files

```bash
make clean
```

## Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - Free for personal and commercial use.

## Author

Eduardo

## Support

To report bugs or request features, open an issue in the repository.
