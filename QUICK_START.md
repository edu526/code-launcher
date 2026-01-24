# Quick Start Guide

## Run the Project

### Option 1: Run directly
```bash
python3 src/main.py
```

### Option 2: Run as module
```bash
python3 -m src.main
```

## Verify Installation

### 1. Verify compilation
```bash
python3 -m py_compile src/**/*.py
```

### 2. Run tests
```bash
python3 -m pytest tests/
```

## Project Structure

```
src/
├── main.py                    # Entry point - run this file
├── core/                      # Business logic
├── ui/                        # Interface components
├── dialogs/                   # User dialogs
└── context_menu/              # Context menu system
```

## Configuration Files

Configuration files are saved in:
```
~/.config/code-launcher/
├── categories.json            # Categories and subcategories
└── projects.json              # Configured projects
```

## Development

### Add a new dialog
1. Create file in `src/dialogs/`
2. Implement `show_*_dialog()` function
3. Export in `src/dialogs/__init__.py`
4. Import where needed

### Add a new menu action
1. Add function in `src/context_menu/actions.py`
2. Export in `src/context_menu/__init__.py`
3. Use in `src/context_menu/handler.py`

### Modify the interface
1. Edit `src/ui/column_browser.py` for the browser
2. Edit `src/main.py` for the main window

## Troubleshooting

### Error: ModuleNotFoundError
```bash
# Make sure you're in the project root directory
cd /path/to/code-launcher
python3 src/main.py
```

### Error: No module named 'gi'
```bash
# Install PyGObject
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Error: VSCode not found
```bash
# Verify that VSCode is installed
which code

# If not installed, install VSCode
# https://code.visualstudio.com/
```

## Additional Documentation

- `README.md` - Main project documentation
- `PROJECT_STRUCTURE.md` - Detailed code structure
- `REFACTORING_SUMMARY.md` - Refactoring summary
- `REFACTORING_COMPLETE.md` - Complete refactoring details
