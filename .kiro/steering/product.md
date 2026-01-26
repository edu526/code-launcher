# Product Overview

Code Launcher is a GTK-based project launcher for Linux that provides a Finder-style interface for organizing and opening development projects in VSCode or Kiro.

## Core Features

- Finder-style column navigation with hierarchical categories and subcategories
- Smart search with text normalization (finds "e-portal" when searching "eportal")
- Context menu system for quick actions (add, delete, rename, open)
- Visual icon selector for categories
- Configurable default editor preference (Kiro or VSCode)
- Single-instance application with window focus management

## User Workflow

Users organize projects into categories → subcategories → projects, navigate through columns, and double-click or use context menus to open projects in their preferred editor.

## Configuration

All user data stored in `~/.config/code-launcher/`:
- `categories.json` - Category hierarchy with icons and descriptions
- `projects.json` - Project paths mapped to categories
- `preferences.json` - User preferences (default editor)
- `code-launcher.log` - Application logs
