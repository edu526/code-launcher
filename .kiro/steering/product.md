# Product Overview

Code Launcher is a GTK-based project launcher for Linux that provides a Finder-style interface for organizing and opening development projects in VSCode or Kiro, as well as individual files in text editors.

## Core Features

- Finder-style column navigation with hierarchical categories and subcategories
- Support for both projects (folders) and individual files
- Smart search with text normalization (finds "e-portal" when searching "eportal")
- Special search commands (@recent to show recently opened items)
- Context menu system for quick actions (add, delete, rename, open)
- Visual icon selector for categories
- Drag and drop support for adding projects and files from file manager
- Favorites/pinning system with star icons and priority sorting
- Recent items tracking (last 20 opened projects/files)
- Comprehensive keyboard shortcuts for navigation and actions
- Configurable default editor preferences:
  - Project editor (Kiro or VSCode) for folders
  - Text editor (gnome-text-editor, gedit, kate, nano, vim, emacs, VSCode, Kiro) for files
- Single-instance application with window focus management

## User Workflow

Users organize projects and files into categories → subcategories → projects/files, navigate through columns, and double-click or use context menus to open them in their preferred editor. Projects and files can also be added by dragging them from the file manager directly into the application window.

## Configuration

All user data stored in `~/.config/code-launcher/`:
- `categories.json` - Category hierarchy with icons and descriptions
- `projects.json` - Project paths mapped to categories
- `files.json` - File paths mapped to categories
- `preferences.json` - User preferences (default editors)
- `favorites.json` - Favorited projects and files
- `recents.json` - Recently opened items (last 20)
- `code-launcher.log` - Application logs

## Keyboard Shortcuts

- `Ctrl+F` - Focus search bar
- `Ctrl+N` - Create new category
- `Ctrl+P` - Add new project
- `Ctrl+D` - Toggle favorite on selected item
- `Ctrl+R` - Show recent items
- `Ctrl+O` / `Enter` - Open selected item
- `Esc` - Close launcher
- `←` `→` `↑` `↓` - Navigate columns and items
- `1-9` - Jump to item by number
