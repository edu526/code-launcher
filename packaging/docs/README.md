# Distribution Documentation

This directory contains comprehensive documentation for building and distributing Code Project Launcher.

## Available Documentation

### 📋 BUILD_INSTRUCTIONS.md
Detailed step-by-step instructions for building the application in various formats:
- Creating executable binaries with PyInstaller
- Building .deb packages for Debian/Ubuntu
- Creating portable AppImage files
- System requirements and dependencies

### 📦 DISTRIBUTION_GUIDE.md
Complete guide for distributing Code Project Launcher:
- Package format comparison and recommendations
- Installation methods for different Linux distributions
- Distribution best practices
- Repository setup and maintenance

### ⚡ QUICK_BUILD.md
Quick reference guide for common build tasks:
- Fast build commands using the Makefile
- Common build scenarios
- Troubleshooting tips
- Quick installation methods

## Build Output Locations

All build artifacts are organized in the `dist/` directory:

- **dist/bin/** - Executable binaries (PyInstaller output)
- **dist/packages/** - Distribution packages (.deb, .AppImage)
- **dist/build_*/** - Temporary build directories (auto-cleaned)

## Quick Start

For most users, the quickest way to build is:

```bash
# Build all formats
make all

# Or build specific format
make deb        # Debian/Ubuntu package
make appimage   # Portable AppImage
make binary     # Standalone binary
```

See QUICK_BUILD.md for more details.
