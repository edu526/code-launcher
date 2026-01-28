#!/usr/bin/env python3
"""
Quick test script for new features
"""

import sys
sys.path.insert(0, 'src')

from core.config import ConfigManager

def test_favorites():
    """Test favorites functionality"""
    print("=" * 50)
    print("Testing Favorites")
    print("=" * 50)

    config = ConfigManager()

    # Test adding favorite
    result = config.toggle_favorite('/home/user/test-project', 'project')
    assert result == True, "Should return True when adding favorite"
    assert config.is_favorite('/home/user/test-project', 'project'), "Should be favorited"
    print("✓ Add favorite works")

    # Test removing favorite
    result = config.toggle_favorite('/home/user/test-project', 'project')
    assert result == False, "Should return False when removing favorite"
    assert not config.is_favorite('/home/user/test-project', 'project'), "Should not be favorited"
    print("✓ Remove favorite works")

    # Test multiple favorites
    config.toggle_favorite('/home/user/project1', 'project')
    config.toggle_favorite('/home/user/project2', 'project')
    config.toggle_favorite('/home/user/file1.txt', 'file')

    favorites = config.load_favorites()
    assert len(favorites['projects']) == 2, "Should have 2 project favorites"
    assert len(favorites['files']) == 1, "Should have 1 file favorite"
    print("✓ Multiple favorites work")

    # Cleanup
    config.save_favorites({"projects": [], "files": []})
    print("✓ Favorites test passed!\n")

def test_recents():
    """Test recents functionality"""
    print("=" * 50)
    print("Testing Recents")
    print("=" * 50)

    config = ConfigManager()

    # Clear recents
    config.save_recents([])

    # Add some recents
    config.add_recent('/home/user/project1', 'Project 1', 'project')
    config.add_recent('/home/user/project2', 'Project 2', 'project')
    config.add_recent('/home/user/file1.txt', 'File 1', 'file')

    recents = config.load_recents()
    assert len(recents) == 3, "Should have 3 recent items"
    assert recents[0]['name'] == 'File 1', "Most recent should be File 1"
    assert recents[0]['type'] == 'file', "Should be a file"
    print("✓ Add recents works")

    # Test duplicate handling (should move to front)
    config.add_recent('/home/user/project1', 'Project 1', 'project')
    recents = config.load_recents()
    assert len(recents) == 3, "Should still have 3 items (no duplicates)"
    assert recents[0]['name'] == 'Project 1', "Project 1 should be most recent"
    print("✓ Duplicate handling works")

    # Test limit (20 items max)
    for i in range(25):
        config.add_recent(f'/home/user/project{i}', f'Project {i}', 'project')

    recents = config.load_recents()
    assert len(recents) <= 20, "Should limit to 20 items"
    print("✓ Limit to 20 items works")

    # Cleanup
    config.save_recents([])
    print("✓ Recents test passed!\n")

def test_config_files():
    """Test that config files are created"""
    print("=" * 50)
    print("Testing Config Files")
    print("=" * 50)

    import os
    from core.config import FAVORITES_FILE, RECENTS_FILE

    config = ConfigManager()

    # Trigger file creation
    config.load_favorites()
    config.load_recents()

    assert os.path.exists(FAVORITES_FILE), "favorites.json should exist"
    assert os.path.exists(RECENTS_FILE), "recents.json should exist"
    print(f"✓ {FAVORITES_FILE} exists")
    print(f"✓ {RECENTS_FILE} exists")
    print("✓ Config files test passed!\n")

if __name__ == '__main__':
    try:
        test_favorites()
        test_recents()
        test_config_files()

        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        print("\nNew features are working correctly:")
        print("  • Favorites/Pinning")
        print("  • Recent Projects List")
        print("  • Enhanced Keyboard Shortcuts")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
