#!/usr/bin/env python3
"""
Check and fix favorites.json format
"""

import json
import os

favorites_file = os.path.expanduser("~/.config/code-launcher/favorites.json")

print("Checking favorites file...")
print(f"Location: {favorites_file}")

if os.path.exists(favorites_file):
    with open(favorites_file, 'r') as f:
        favorites = json.load(f)

    print("\nCurrent favorites:")
    print(json.dumps(favorites, indent=2))

    # Check if it has the new format with categories
    if "categories" not in favorites:
        print("\n⚠️  Old format detected! Adding 'categories' key...")
        favorites["categories"] = []
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f, indent=2)
        print("✓ Fixed!")
    else:
        print("\n✓ Format is correct")

    # Show summary
    print(f"\nSummary:")
    print(f"  Categories: {len(favorites.get('categories', []))}")
    print(f"  Projects: {len(favorites.get('projects', []))}")
    print(f"  Files: {len(favorites.get('files', []))}")

else:
    print("\n⚠️  Favorites file doesn't exist yet")
    print("It will be created when you add your first favorite")
