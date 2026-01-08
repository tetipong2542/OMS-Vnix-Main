#!/usr/bin/env python3
"""
Convert SQLite database to Turso-compatible format

This script:
1. Checks database integrity
2. Converts to WAL mode (required by Turso)
3. Checkpoints WAL to consolidate data
4. Vacuums database to optimize
5. Creates converted file ready for Turso upload

Usage:
    python convert_db_for_turso.py input.db output.db

Example:
    python convert_db_for_turso.py data-tetipong2542.db data-tetipong2542-converted.db
"""

import sqlite3
import sys
import os
import shutil

def convert_database_for_turso(input_path, output_path):
    """Convert database to Turso-compatible format"""

    print("=" * 70)
    print("🔧 Converting SQLite Database for Turso")
    print("=" * 70)

    # Step 0: Validate input file
    if not os.path.exists(input_path):
        print(f"❌ Error: Input file '{input_path}' not found!")
        return False

    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    print(f"\n📁 Input file: {input_path}")
    print(f"📊 Size: {input_size_mb:.2f} MB")

    # Copy to output first
    try:
        print(f"\n📋 Copying to: {output_path}")
        shutil.copy2(input_path, output_path)
        print("✓ File copied successfully")
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False

    # Work on output file
    try:
        print("\n" + "-" * 70)
        print("🔍 Step 1: Checking database integrity...")
        print("-" * 70)

        # Set timeout to avoid lock issues
        conn = sqlite3.connect(output_path, timeout=30.0)

        # Enable immediate mode to avoid lock issues
        conn.execute("PRAGMA locking_mode=EXCLUSIVE")

        cursor = conn.cursor()

        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]

        if integrity_result != "ok":
            print(f"❌ Database integrity check failed: {integrity_result}")
            conn.close()
            os.remove(output_path)
            return False

        print("✓ Integrity check: OK")

        # Step 2: Check current mode
        print("\n" + "-" * 70)
        print("🔄 Step 2: Converting to WAL mode...")
        print("-" * 70)

        cursor.execute("PRAGMA journal_mode")
        current_mode = cursor.fetchone()[0]
        print(f"Current mode: {current_mode}")

        if current_mode.lower() != 'wal':
            cursor.execute("PRAGMA journal_mode=WAL")
            new_mode = cursor.fetchone()[0]
            print(f"✓ Converted from {current_mode} to {new_mode} mode")
        else:
            print("✓ Already in WAL mode")

        # Step 3: Checkpoint
        print("\n" + "-" * 70)
        print("📦 Step 3: Checkpointing WAL...")
        print("-" * 70)

        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        checkpoint_result = cursor.fetchall()
        print(f"✓ Checkpoint completed: {checkpoint_result}")

        # Step 4: Vacuum
        print("\n" + "-" * 70)
        print("🧹 Step 4: Vacuuming database...")
        print("-" * 70)

        cursor.execute("VACUUM")
        print("✓ Database vacuumed successfully")

        # Step 5: Final verification
        print("\n" + "-" * 70)
        print("✅ Step 5: Final verification...")
        print("-" * 70)

        cursor.execute("PRAGMA integrity_check")
        final_check = cursor.fetchone()[0]

        if final_check != "ok":
            print(f"❌ Final integrity check failed: {final_check}")
            conn.close()
            os.remove(output_path)
            return False

        print("✓ Final integrity check: OK")

        # Get some statistics
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"✓ Tables: {table_count}")

        conn.commit()
        conn.close()

        # Final file size
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        print("\n" + "=" * 70)
        print("✅ Conversion completed successfully!")
        print("=" * 70)
        print(f"\n📁 Output file: {output_path}")
        print(f"📊 Size: {output_size_mb:.2f} MB")
        print(f"💾 Size change: {output_size_mb - input_size_mb:+.2f} MB")

        print("\n" + "=" * 70)
        print("🚀 Next Steps:")
        print("=" * 70)
        print(f"1. Go to https://vnix-erp.up.railway.app/system-status")
        print(f"2. Find the Turso database you want to replace")
        print(f"3. Click 'Upload & Sync to Turso'")
        print(f"4. Select the converted file: {output_path}")
        print(f"5. Wait for upload and sync to complete")
        print("\n⚠️  WARNING: This will REPLACE all data in Turso Cloud!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_db_for_turso.py <input.db> <output.db>")
        print("\nExample:")
        print("  python convert_db_for_turso.py data-tetipong2542.db data-converted.db")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Prevent overwriting input
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        print("❌ Error: Output file cannot be the same as input file!")
        print("Please use a different output filename.")
        sys.exit(1)

    # Check if output exists
    if os.path.exists(output_file):
        response = input(f"⚠️  Output file '{output_file}' already exists. Overwrite? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            sys.exit(0)

    success = convert_database_for_turso(input_file, output_file)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
