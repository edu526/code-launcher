#!/usr/bin/env python3
"""
Test sorting logic for favorites
"""

# Simulate the sorting logic
projects = [
    ("EXTRA", "/path/to/extra", True),  # Favorite
    ("address-tagger", "/path/to/address", False),
    ("ai", "/path/to/ai", False),
    ("aliviride", "/path/to/aliviride", False),
]

print("Before sorting:")
for name, path, is_fav in projects:
    fav_marker = "★" if is_fav else " "
    print(f"  {fav_marker} {name}")

# Sort: favorites first (not is_fav gives False for favorites, True for non-favorites)
# False < True, so favorites come first
projects.sort(key=lambda x: (not x[2], x[0].lower()))

print("\nAfter sorting:")
for name, path, is_fav in projects:
    fav_marker = "★" if is_fav else " "
    print(f"  {fav_marker} {name}")

print("\nExpected order:")
print("  ★ EXTRA")
print("    address-tagger")
print("    ai")
print("    aliviride")
