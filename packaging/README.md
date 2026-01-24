# Distribution Files

This directory contains all files related to building and distributing Code Project Launcher.

## Directory Structure

```
packaging/
├── docs/                          # Build documentation
│   ├── BUILD_INSTRUCTIONS.md     # Detailed build instructions
│   ├── DISTRIBUTION_GUIDE.md     # Distribution strategies
│   └── QUICK_BUILD.md            # Quick reference
├── build_binary.sh               # Binary builder script
├── build_deb.sh                  # DEB package builder
├── build_appimage.sh             # AppImage builder
├── bin/                          # Built binaries (created by make binary)
└── packages/                     # Built packages (created by make deb/appimage)
```

## Build Commands

From the project root directory:

```bash
# Build binary
make binary
# Output: packaging/bin/code-launcher

# Build DEB package
make deb
# Output: packaging/packages/code-project-launcher_1.0.0_all.deb

# Build AppImage
make appimage
# Output: packaging/packages/CodeLauncher-1.0.0-x86_64.AppImage

# Build all formats
make all

# Clean build artifacts
make clean
```

## Documentation

- **BUILD_INSTRUCTIONS.md** - Complete build instructions with requirements
- **DISTRIBUTION_GUIDE.md** - How to distribute your application
- **QUICK_BUILD.md** - Quick reference for building

## Notes

- Build artifacts are created in `dist/bin/` and `dist/packages/`
- These directories are ignored by git (see `.gitignore`)
- Run `make clean` to remove all build artifacts
