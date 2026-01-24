# Code Project Launcher

Finder-style project launcher for VSCode and Kiro with modern GTK interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## Features

- 🎯 Finder-style navigation with columns
- 📁 Organization by categories and subcategories
- 🔍 Smart search with text normalization
- ⚡ Keyboard shortcuts (Ctrl+F to search, Esc to exit)
- 🎨 Visual icon selector for categories
- 📝 Integrated log viewer
- ⚙️ Preferences to select default editor (Kiro/VSCode)
- 🖱️ Context menu with quick actions
- 🚀 Multiple installation options (local, binary, .deb, AppImage)

## Requirements

- Linux (any distribution)
- Python 3.6+
- GTK 3
- VSCode and/or Kiro installed

## Quick Installation

```bash
# Method 1: Local installation (recommended)
make install

# Method 2: Using the script directly
bash launcher/install.sh
```

## Installation Options

### 1. Local Installation (Development)
```bash
make install
```
- Installs in `~/.local/bin`
- Automatic updates with Git
- Ideal for development

### 2. Executable Binary
```bash
make binary
```
- Creates a single executable file
- Doesn't require Python on target system
- File: `packaging/bin/code-launcher`

### 3. DEB Package (Debian/Ubuntu)
```bash
make deb
```
- Automatic dependency management
- Easy installation: `sudo dpkg -i code-project-launcher_1.0.0_all.deb`
- Integration with package system

### 4. AppImage (Portable)
```bash
make appimage
```
- Works on any Linux distribution
- No installation required
- Portable and self-contained

### 5. Create All Formats
```bash
make all
```

For detailed build instructions, see [packaging/docs/BUILD_INSTRUCTIONS.md](packaging/docs/BUILD_INSTRUCTIONS.md)

---

## Documentation

- **README.md** - This file (getting started guide)
- **QUICK_START.md** - Quick start guide
- **LICENSE** - MIT License
- **packaging/docs/** - Build and distribution documentation
  - BUILD_INSTRUCTIONS.md - Detailed build instructions
  - DISTRIBUTION_GUIDE.md - Distribution strategies
  - QUICK_BUILD.md - Quick build reference

## Project Structure

```
code-launcher/
├── src/                    # Source code
│   ├── core/              # Configuration management
│   ├── ui/                # User interface
│   ├── dialogs/           # Dialog windows
│   └── context_menu/      # Context menu system
├── utils/                  # Utilities
├── tests/                  # Test suite
├── launcher/               # Installation files
├── packaging/              # Build and packaging files
│   ├── docs/              # Build documentation
│   ├── build_binary.sh    # Binary builder
│   ├── build_deb.sh       # DEB builder
│   └── build_appimage.sh  # AppImage builder
├── Makefile               # Build automation
├── setup.py               # Python package setup
├── LICENSE                # MIT License
└── README.md              # This file
```

---

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

#### Categories (`categories.json`)
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

#### Projects (`projects.json`)
```json
{
  "My Project": {
    "path": "/path/to/project",
    "category": "Web",
    "subcategory": "Frontend"
  }
}
```

#### Preferences (`preferences.json`)
```json
{
  "default_editor": "kiro"
}
```

## Usage

### Starting the Application

```bash
# If installed locally
code-launcher

# Or from the applications menu
# Search for "Code Project Launcher"
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

Search normalizes text, so:
- "eportal" finds "e-portal"
- "myproject" finds "my_project"
- Searches in project and category names
- Shows all projects from found categories

## Uninstallation

### Local Installation
```bash
make uninstall
```

### DEB Package
```bash
sudo dpkg -r code-project-launcher
```

### Binary/AppImage
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

## Project Structure

```
.
├── src/                        # Source code
│   ├── core/                   # Configuration and core logic
│   ├── ui/                     # User interface
│   ├── dialogs/                # Configuration dialogs
│   └── context_menu/           # Context menu
├── utils/                      # Utilities
├── tests/                      # Tests
├── launcher/                   # Installation files
├── Makefile                    # Build commands
├── setup.py                    # Python package configuration
├── build_binary.sh             # Script to create binary
├── build_deb.sh                # Script to create .deb
├── build_appimage.sh           # Script to create AppImage
└── BUILD_INSTRUCTIONS.md       # Detailed instructions
```

## Configuration Files

```
~/.config/code-launcher/
├── categories.json             # Categories and subcategories
├── projects.json               # Projects
├── preferences.json            # User preferences
└── code-launcher.log           # Application logs
```

## Development

### Run from source code
```bash
python3 src/main.py
```

### Run tests
```bash
python3 -m pytest tests/
```

### Clean build files
```bash
make clean
```

## Contributing

Contributions are welcome. Please:
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
