# Project Structure

## Directory Layout

```
code-launcher/
├── src/                    # Source code
│   ├── core/              # Configuration management
│   ├── ui/                # User interface components
│   ├── dialogs/           # Dialog windows
│   └── context_menu/      # Context menu system
├── utils/                  # Utility modules
├── tests/                  # Test suite
├── packaging/              # Build and packaging scripts
├── Makefile               # Build automation
└── setup.py               # Python package configuration
```

## Module Organization

### src/core/
Configuration management and data persistence:
- `config.py` - ConfigManager class, file paths, category/project loading

### src/ui/
Main interface components:
- `window.py` - FinderStyleWindow (main application window)
- `column_browser.py` - Column-based navigation
- `keyboard_handler.py` - Keyboard shortcuts (Ctrl+F, Esc)
- `search_manager.py` - Search functionality
- `navigation_manager.py` - Column navigation logic

### src/dialogs/
Dialog windows for user input:
- `category_dialog.py` - Create/edit categories
- `project_dialog.py` - Add/edit projects
- `config_dialog.py` - Preferences and configuration

### src/context_menu/
Right-click context menu system:
- `handler.py` - ContextMenuHandler class
- `context_detector.py` - Detect click context (ROOT_COLUMN, CHILD_COLUMN, CATEGORY_ITEM, PROJECT_ITEM)
- `actions.py` - Menu actions (create, delete, rename, open)

### utils/
Shared utilities:
- `validation.py` - Input validation
- `vscode_utils.py` - Editor integration

### tests/
Comprehensive test coverage:
- Unit tests for all major components
- Integration tests for workflows
- Mock-based GTK testing

## Architecture Patterns

### Manager Pattern
UI logic separated into manager classes (SearchManager, KeyboardHandler, NavigationManager) that operate on the main window.

### Event-Driven
GTK signal/callback architecture for user interactions.

### Configuration as Data
Categories and projects stored as JSON, loaded/saved via ConfigManager.

### Context Detection
Context menu system detects click location and item type to show appropriate actions.

## Code Style

- **Indentation**: 2 spaces (per .editorconfig)
- **Line Endings**: LF
- **Encoding**: UTF-8
- **Docstrings**: Module-level and class-level documentation
- **Imports**: Standard library → third-party → local modules
- **Logging**: Configured in main.py, used throughout for debugging
