#!/usr/bin/env python3
"""
Test script for Dual Database Mode

This script tests the connection to both:
1. Old databases (SQLite): data.db, price.db, supplier_stock.db
2. New database (Turso/libSQL)

Usage:
    python test_dual_db_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set ENABLE_DUAL_DB_MODE for testing
os.environ["ENABLE_DUAL_DB_MODE"] = "true"

def test_connections():
    """Test database connections."""
    print("=" * 70)
    print("DUAL DATABASE MODE CONNECTION TEST")
    print("=" * 70)
    print()

    # Import app instance (already created at module level in app.py)
    from app import app
    from models import db, Product, SkuPricing, SupplierSkuMaster

    with app.app_context():
        print("\n" + "=" * 70)
        print("DATABASE CONFIGURATION")
        print("=" * 70)

        # Check configuration
        print(f"Main DB URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
        print(f"Binds: {list(app.config.get('SQLALCHEMY_BINDS', {}).keys())}")
        print()

        # Test 1: Test OLD SQLite databases
        print("\n" + "=" * 70)
        print("TEST 1: Old SQLite Databases (Read-Only)")
        print("=" * 70)

        try:
            # Test data_old
            print("\n[data_old] Testing connection to old data.db...")
            engine_data_old = db.get_engine(bind='data_old')
            with engine_data_old.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) as count FROM products"))
                count = result.scalar()
                print(f"  ✅ Connected! Found {count} products in old data.db")
        except Exception as e:
            print(f"  ❌ Error connecting to data_old: {e}")

        try:
            # Test price_old
            print("\n[price_old] Testing connection to old price.db...")
            engine_price_old = db.get_engine(bind='price_old')
            with engine_price_old.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) as count FROM sku_pricing"))
                count = result.scalar()
                print(f"  ✅ Connected! Found {count} SKU pricing records in old price.db")
        except Exception as e:
            print(f"  ❌ Error connecting to price_old: {e}")

        try:
            # Test supplier_old
            print("\n[supplier_old] Testing connection to old supplier_stock.db...")
            engine_supplier_old = db.get_engine(bind='supplier_old')
            with engine_supplier_old.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) as count FROM supplier_sku_master"))
                count = result.scalar()
                print(f"  ✅ Connected! Found {count} supplier SKU records in old supplier_stock.db")
        except Exception as e:
            print(f"  ❌ Error connecting to supplier_old: {e}")

        # Test 2: Test NEW Turso database
        print("\n" + "=" * 70)
        print("TEST 2: New Turso Database (Read/Write)")
        print("=" * 70)

        try:
            print("\n[Turso/libSQL] Testing connection to new database...")

            # Test main database (data)
            product_count = Product.query.count()
            print(f"  ✅ Main DB connected! Found {product_count} products in Turso")

            # Test price bind
            price_count = SkuPricing.query.count()
            print(f"  ✅ Price bind connected! Found {price_count} SKU pricing records in Turso")

            # Test supplier bind
            supplier_count = SupplierSkuMaster.query.count()
            print(f"  ✅ Supplier bind connected! Found {supplier_count} supplier SKU records in Turso")

        except Exception as e:
            print(f"  ❌ Error connecting to Turso: {e}")
            import traceback
            traceback.print_exc()

        # Test 3: Test dual query helpers
        print("\n" + "=" * 70)
        print("TEST 3: Dual Query Helpers")
        print("=" * 70)

        try:
            from db_helpers import dual_query_auto, is_dual_mode_enabled

            print(f"\n[Dual Mode] Enabled: {is_dual_mode_enabled()}")

            # Test dual query for products (data)
            print("\n[dual_query_auto] Testing Product query from both databases...")
            products = dual_query_auto(Product, order_by='sku')
            print(f"  ✅ Found {len(products)} total products from both databases")
            if products:
                print(f"  📦 Sample: {products[0].sku} - {products[0].brand}")

            # Test dual query for prices
            print("\n[dual_query_auto] Testing SkuPricing query from both databases...")
            prices = dual_query_auto(SkuPricing, order_by='sku')
            print(f"  ✅ Found {len(prices)} total SKU pricing records from both databases")
            if prices:
                print(f"  💰 Sample: {prices[0].sku}")

        except Exception as e:
            print(f"  ❌ Error testing dual query helpers: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        print()


def check_environment():
    """Check environment variables."""
    print("\n" + "=" * 70)
    print("ENVIRONMENT VARIABLES")
    print("=" * 70)

    required_vars = [
        "TURSO_DATABASE_URL",
        "TURSO_AUTH_TOKEN",
        "ENABLE_DUAL_DB_MODE"
    ]

    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if "TOKEN" in var or "AUTH" in var:
                masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET")

    print()


if __name__ == "__main__":
    try:
        check_environment()
        test_connections()
        print("\n✅ All tests completed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
