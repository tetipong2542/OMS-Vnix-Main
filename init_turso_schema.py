#!/usr/bin/env python3
"""
Initialize Turso database schema
Creates all tables if they don't exist
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import sqlalchemy_libsql first
try:
    import sqlalchemy_libsql
    print("✅ sqlalchemy_libsql loaded")
except ImportError:
    print("⚠️  sqlalchemy_libsql not found")

from sqlalchemy import create_engine, inspect
from models import db, Shop, Product, Stock, Sales, User, UserPreference, OrderLine

def build_turso_uri(sync_url, auth_token, local_file=None):
    """Build SQLAlchemy URI for Turso database"""
    if not sync_url.startswith("libsql://"):
        if sync_url.startswith("https://"):
            sync_url = sync_url.replace("https://", "libsql://", 1)
    
    if not local_file or not local_file.strip():
        db_name = sync_url.split('/')[-1].split('.')[0]
        local_file = f"/tmp/{db_name}.db"
    elif local_file.startswith("file:"):
        local_file = local_file[5:]
    
    return f"sqlite+libsql:///{local_file}?sync_url={sync_url}&authToken={auth_token}"

def init_database(engine, bind_key=None):
    """Initialize database schema"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"\n📋 Existing tables: {existing_tables if existing_tables else 'None'}")
    
    # Import Flask app to use db.create_all()
    from app import create_app
    app = create_app()
    
    with app.app_context():
        if bind_key:
            print(f"\n🔧 Creating tables for bind_key: {bind_key}")
            db.create_all(bind_key=bind_key)
        else:
            print(f"\n🔧 Creating main database tables")
            db.create_all()
    
    # Verify
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print(f"\n✅ Tables after creation: {new_tables}")
    
    return new_tables

def main():
    print("=" * 60)
    print("Initialize Turso Database Schema")
    print("=" * 60)
    
    # Get credentials
    data_url = os.environ.get("DATA_DB_URL")
    data_token = os.environ.get("DATA_DB_AUTH_TOKEN")
    data_local = os.environ.get("DATA_DB_LOCAL")
    
    price_url = os.environ.get("PRICE_DB_URL")
    price_token = os.environ.get("PRICE_DB_AUTH_TOKEN")
    price_local = os.environ.get("PRICE_DB_LOCAL")
    
    supplier_url = os.environ.get("SUPPLIER_DB_URL")
    supplier_token = os.environ.get("SUPPLIER_DB_AUTH_TOKEN")
    supplier_local = os.environ.get("SUPPLIER_DB_LOCAL")
    
    if not all([data_url, data_token, price_url, price_token, supplier_url, supplier_token]):
        print("\n❌ Missing Turso credentials")
        sys.exit(1)
    
    try:
        # Initialize data database
        print(f"\n[1/3] Data Database")
        print(f"   URL: {data_url}")
        data_uri = build_turso_uri(data_url, data_token, data_local)
        data_engine = create_engine(data_uri)
        init_database(data_engine, bind_key=None)
        data_engine.dispose()
        
        # Initialize price database
        print(f"\n[2/3] Price Database")
        print(f"   URL: {price_url}")
        price_uri = build_turso_uri(price_url, price_token, price_local)
        price_engine = create_engine(price_uri)
        init_database(price_engine, bind_key="price")
        price_engine.dispose()
        
        # Initialize supplier database
        print(f"\n[3/3] Supplier Database")
        print(f"   URL: {supplier_url}")
        supplier_uri = build_turso_uri(supplier_url, supplier_token, supplier_local)
        supplier_engine = create_engine(supplier_uri)
        init_database(supplier_engine, bind_key="supplier")
        supplier_engine.dispose()
        
        print("\n" + "=" * 60)
        print("✅ All databases initialized successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
