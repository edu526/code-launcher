# New Features

## 1. Favorites/Pinning ⭐

Mark your most-used categories, projects and files as favorites for quick access.

### Features:
- **Star Icon**: Favorited items show a ★ prefix in the column view
- **Priority Sorting**: Favorites appear at the top within their type
- **Sorting Order**: ★ Categories → Categories → ★ Projects → Projects → ★ Files → Files
- **All Item Types**: Works with categories, subcategories, projects, and files
- **Context Menu**: Right-click any item to add/remove from favorites
- **Keyboard Shortcut**: Press `Ctrl+D` to toggle favorite on selected item
- **Persistent**: Favorites are saved in `~/.config/code-launcher/favorites.json`

### Usage:
1. Right-click on any category, project, or file
2. Select "Add to Favorites" or "Remove from Favorites"
3. Or select an item and press `Ctrl+D`

### Sorting Behavior:
Items are sorted in this order:
1. Favorite categories (alphabetically)
2. Regular categories (alphabetically)
3. Favorite projects (alphabetically)
4. Regular projects (alphabetically)
5. Favorite files (alphabetically)
6. Regular files (alphabetically)

---

## 2. Enhanced Keyboard Shortcuts ⌨️

Navigate and control the launcher entirely from your keyboard.

### New Shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus search bar |
| `Ctrl+N` | Create new category |
| `Ctrl+P` | Add new project |
| `Ctrl+D` | Toggle favorite on selected item |
| `Ctrl+R` | Show recent items |
| `Ctrl+O` | Open selected item |
| `Enter` | Open selected item |
| `Esc` | Close launcher |
| `←` | Navigate to previous column |
| `→` | Navigate to next column |
| `↑` | Select previous item in column |
| `↓` | Select next item in column |
| `1-9` | Jump to item by number (1st-9th) |

### Navigation Flow:
1. Press `Ctrl+F` to search
2. Use arrow keys to navigate columns and items
3. Press `Enter` to open
4. Press `Esc` to close

---

## 3. Recent Projects List 📋

Quickly access your recently opened projects and files.

### Features:
- **Automatic Tracking**: Every opened project/file is automatically added to recents
- **Last 20 Items**: Keeps track of your 20 most recent items
- **Timestamp**: Items are ordered by when they were last opened
- **Mixed View**: Shows both projects and files together
- **Special Search**: Type `@recent` in search to view recents
- **Keyboard Access**: Press `Ctrl+R` to instantly show recents
- **Persistent**: Recents are saved in `~/.config/code-launcher/recents.json`

### Usage:
1. Press `Ctrl+R` or type `@recent` in search
2. View your recently opened items
3. Double-click or press Enter to open

---

## Configuration Files

The new features add two new configuration files:

- `~/.config/code-launcher/favorites.json` - Stores favorited categories, projects and files
- `~/.config/code-launcher/recents.json` - Stores recently opened items

Both files are automatically created and managed by the application.

### Favorites Structure:
```json
{
  "categories": ["cat:Work", "cat:Personal:Projects"],
  "projects": ["/home/user/project1", "/home/user/project2"],
  "files": ["/home/user/notes.txt"]
}
```

---

## Implementation Details

### Favorites System:
- Favorites are stored separately from categories/projects/files
- Supports three item types: categories, projects, and files
- Items are marked with a boolean flag in the column store
- Sorting prioritizes favorites within each type (categories → projects → files)
- Within each type, favorites appear first, then regular items (both alphabetically)
- Toggle action refreshes only the affected column for performance
- Categories use their path format (e.g., "cat:Work:Backend") as identifier

### Keyboard Handler:
- Centralized keyboard event handling in `KeyboardHandler` class
- Supports column navigation and item selection
- Integrates with existing managers (SearchManager, NavigationManager)
- Graceful fallbacks for edge cases

### Recents Tracking:
- Automatically records when projects/files are opened (both types supported)
- Stores item path, name, type, and timestamp
- Limited to 20 most recent items (configurable)
- Displayed through search manager with special `@recent` command
- Shows favorite status for recent items
- Files are tracked when opened via double-click, keyboard shortcut, or context menu

---

## User Experience Improvements

1. **Faster Access**: Favorites and recents reduce time to find frequently used items
2. **Keyboard Efficiency**: Complete keyboard navigation eliminates mouse dependency
3. **Visual Feedback**: Star icons clearly indicate favorited items
4. **Smart Sorting**: Favorites appear first, making them easier to find
5. **Persistent State**: All preferences survive application restarts
