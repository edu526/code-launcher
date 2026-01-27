# Product Overview

Code Launcher is a GTK-based project launcher for Linux that provides a Finder-style interface for organizing and opening development projects in VSCode or Kiro, as well as individual files in text editors.

## Core Features

- Finder-style column navigation with hierarchical categories and subcategories
- Support for both projects (folders) and individual files
- Smart search with text normalization (finds "e-portal" when searching "eportal")
- Context menu system for quick actions (add, delete, rename, open)
- Visual icon selector for categories
- Configurable default editor preferences:
  - Project editor (Kiro or VSCode) for folders
  - Text editor (gedit, kate, nano, vim, emacs, VSCode, Kiro) for files
- Single-instance application with window focus management

## User Workflow

Users organize projects and files into categories → subcategories → projects/files, navigate through columns, and double-click or use context menus to open them in their preferred editor.

## Configuration

All user data stored in `~/.config/code-launcher/`:
- `categories.json` - Category hierarchy with icons and descriptions
- `projects.json` - Project paths mapped to categories
- `files.json` - File paths mapped to categories
- `preferences.json` - User preferences (default editors)
- `code-launcher.log` - Application logs
