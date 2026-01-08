#!/usr/bin/env python3
"""
Migrate shops table schema to add is_system_config column
Run this on Railway after deployment to update Turso database schema
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import sqlalchemy_libsql first to register the dialect
try:
    import sqlalchemy_libsql
    print("✅ sqlalchemy_libsql loaded")
except ImportError:
    print("⚠️  sqlalchemy_libsql not found - Turso features may not work")

from sqlalchemy import create_engine, text, inspect

def build_turso_uri(sync_url, auth_token, local_file=None):
    """Build SQLAlchemy URI for Turso database with embedded replica"""
    if not sync_url.startswith("libsql://"):
        if sync_url.startswith("https://"):
            sync_url = sync_url.replace("https://", "libsql://", 1)
    
    if not local_file or not local_file.strip():
        db_name = sync_url.split('/')[-1].split('.')[0]
        local_file = f"/tmp/{db_name}.db"
    elif local_file.startswith("file:"):
        local_file = local_file[5:]
    
    return f"sqlite+libsql:///{local_file}?sync_url={sync_url}&authToken={auth_token}"

def migrate_shops_table(engine):
    """Add is_system_config column to shops table if it doesn't exist"""
    print("\n" + "=" * 60)
    print("Migrating shops table schema")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check current columns
        inspector = inspect(engine)
        
        try:
            columns = [col['name'] for col in inspector.get_columns('shops')]
            print(f"\n📋 Current columns in shops table:")
            for col in columns:
                print(f"   - {col}")
        except Exception as e:
            print(f"❌ Error reading table schema: {e}")
            return False
        
        # Add is_system_config if missing
        if 'is_system_config' not in columns:
            print(f"\n🔧 Adding missing column: is_system_config")
            try:
                conn.execute(text("ALTER TABLE shops ADD COLUMN is_system_config INTEGER DEFAULT 0"))
                conn.commit()
                print("   ✅ Column added successfully")
                
                # Create index
                print(f"\n🔧 Creating index on is_system_config")
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_shops_is_system_config ON shops(is_system_config)"))
                conn.commit()
                print("   ✅ Index created successfully")
                
                return True
            except Exception as e:
                print(f"   ❌ Error adding column: {e}")
                return False
        else:
            print(f"\n✅ Column is_system_config already exists - no migration needed")
            return True

def main():
    print("=" * 60)
    print("VNIX ERP - Database Schema Migration")
    print("=" * 60)
    
    # Get Turso credentials from environment
    data_url = os.environ.get("DATA_DB_URL")
    data_token = os.environ.get("DATA_DB_AUTH_TOKEN")
    data_local = os.environ.get("DATA_DB_LOCAL")
    
    if not data_url or not data_token:
        print("\n❌ ERROR: Missing Turso credentials")
        print("   Required environment variables:")
        print("   - DATA_DB_URL")
        print("   - DATA_DB_AUTH_TOKEN")
        print("\n   Please set these in Railway dashboard or .env file")
        sys.exit(1)
    
    print(f"\n📡 Connecting to Turso database...")
    print(f"   URL: {data_url}")
    if data_local:
        print(f"   Local file: {data_local}")
    else:
        print(f"   Local file: /tmp/{data_url.split('/')[-1].split('.')[0]}.db")
    
    # Build URI and create engine
    try:
        uri = build_turso_uri(data_url, data_token, data_local)
        engine = create_engine(uri)
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)
    
    # Run migration
    try:
        success = migrate_shops_table(engine)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\n🚀 You can now restart your application")
            sys.exit(0)
        else:
            print("❌ Migration failed!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
