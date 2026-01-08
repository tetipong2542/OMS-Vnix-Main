#!/usr/bin/env python3
"""
Force sync Turso databases by removing local cache files
Run this on Railway to force fresh sync from Turso cloud
"""

import os
import sys
import glob

def remove_local_db_files():
    """Remove all local database files in /tmp to force fresh sync"""
    print("=" * 60)
    print("Force Sync Turso Databases")
    print("=" * 60)
    
    # Patterns to match
    patterns = [
        "/tmp/*.db",
        "/tmp/*.db-shm",
        "/tmp/*.db-wal",
        "/tmp/*-tetipong2542.db*",
    ]
    
    removed_count = 0
    
    for pattern in patterns:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    print(f"🗑️  Removing: {file_path}")
                    os.remove(file_path)
                    removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")
    
    print(f"\n✅ Removed {removed_count} cache files")
    print("\n" + "=" * 60)
    print("✅ Cache cleared successfully!")
    print("=" * 60)
    print("\n🔄 Next step: Restart the application")
    print("   The app will sync fresh data from Turso on startup")
    
    return removed_count

if __name__ == "__main__":
    try:
        count = remove_local_db_files()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
