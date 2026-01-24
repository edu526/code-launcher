# Build and Installation Instructions

This document explains how to create different types of installers and binaries for Code Project Launcher.

## Available Options

### 1. Local Installation (Recommended for development)

The quickest way to install:

```bash
make install
# or
bash launcher/install.sh
```

**Features:**
- Installation in `~/.local/bin`
- Automatic update with Git hooks
- Configuration in `~/.config/code-launcher`
- Shortcut in applications menu

---

### 2. Executable Binary (PyInstaller)

Creates a single executable file:

```bash
make binary
# or
bash build_binary.sh
```

**Requirements:**
- PyInstaller: `pip3 install pyinstaller`

**Result:**
- File: `dist/code-launcher`
- Size: ~50-100 MB (includes all dependencies)

**Installation:**
```bash
sudo cp dist/code-launcher /usr/local/bin/
```

**Advantages:**
- Single executable file
- Doesn't require Python installed on target system
- Easy to distribute

**Disadvantages:**
- Large file
- Slower startup time

---

### 3. DEB Package (Debian/Ubuntu)

Creates a `.deb` package for Debian-based systems:

```bash
make deb
# or
bash build_deb.sh
```

**Requirements:**
- `dpkg-deb` (usually already installed)

**Result:**
- File: `code-project-launcher_1.0.0_all.deb`

**Installation:**
```bash
sudo dpkg -i code-project-launcher_1.0.0_all.deb
sudo apt-get install -f  # If there are missing dependencies
```

**Uninstallation:**
```bash
sudo dpkg -r code-project-launcher
```

**Advantages:**
- Automatic dependency management
- Integration with package system
- Easy update and uninstallation
- Small size (~50 KB)

**Disadvantages:**
- Only for Debian/Ubuntu systems
- Requires Python and GTK on the system

---

### 4. AppImage (Portable)

Creates a portable file that works on any Linux distribution:

```bash
make appimage
# or
bash build_appimage.sh
```

**Requirements:**
- `wget` to download appimagetool

**Result:**
- File: `CodeLauncher-1.0.0-x86_64.AppImage`

**Usage:**
```bash
chmod +x CodeLauncher-1.0.0-x86_64.AppImage
./CodeLauncher-1.0.0-x86_64.AppImage
```

**Advantages:**
- Portable (single file)
- Works on any Linux distribution
- Doesn't require installation
- Doesn't require root permissions

**Disadvantages:**
- Large file (~100-150 MB)
- Requires GTK installed on the system

---

### 5. Create All Formats

```bash
make all
```

This will create:
- Executable binary
- .deb package
- AppImage

---

## Method Comparison

| Method | Size | Portability | Installation | Best For |
|--------|------|-------------|--------------|----------|
| **Local Installation** | ~100 KB | Low | Easy | Development |
| **Binary** | ~50-100 MB | Medium | Very easy | Simple distribution |
| **DEB** | ~50 KB | Low | Easy | Debian/Ubuntu |
| **AppImage** | ~100-150 MB | High | Very easy | Universal distribution |

---

## System Dependencies

### To run the application:
```bash
# Debian/Ubuntu
sudo apt install python3 python3-gi gir1.2-gtk-3.0

# Fedora
sudo dnf install python3 python3-gobject gtk3

# Arch Linux
sudo pacman -S python python-gobject gtk3
```

### To build:
```bash
# PyInstaller (for binary)
pip3 install pyinstaller

# dpkg-deb (for .deb) - usually already installed
sudo apt install dpkg-dev

# wget (for AppImage)
sudo apt install wget
```

---

## Cleanup

To clean all build files:

```bash
make clean
```

This will remove:
- Directories `build/`, `dist/`
- `.deb` files
- `.AppImage` files
- Temporary files

---

## Uninstallation

### Local installation:
```bash
make uninstall
```

### DEB package:
```bash
sudo dpkg -r code-project-launcher
```

### Binary/AppImage:
Simply delete the executable file.

**Note:** Configuration in `~/.config/code-launcher` is preserved in all cases.

---

## Distribution

### To distribute your application:

1. **Technical users**: DEB package
   - Easy to install with dependency management
   - Small size

2. **General users**: AppImage
   - Doesn't require installation
   - Works on any distribution
   - Portable

3. **Maximum compatibility**: PyInstaller binary
   - Single file
   - Doesn't require Python installed

---

## Troubleshooting

### Error: "PyInstaller not found"
```bash
pip3 install --user pyinstaller
```

### Error: "dpkg-deb: command not found"
```bash
sudo apt install dpkg-dev
```

### Error: "GTK not found"
```bash
sudo apt install python3-gi gir1.2-gtk-3.0
```

### Binary doesn't execute
```bash
chmod +x dist/code-launcher
# or
chmod +x CodeLauncher-1.0.0-x86_64.AppImage
```

---

## Recommendations

- **For development**: Use `make install`
- **For Debian/Ubuntu distribution**: Use `make deb`
- **For universal distribution**: Use `make appimage`
- **For maximum simplicity**: Use `make binary`

---

## Version Update

To change the version, edit these files:
- `setup.py` - line `version="1.0.0"`
- `build_deb.sh` - line `VERSION="1.0.0"`
- `build_appimage.sh` - line `VERSION="1.0.0"`
