#!/usr/bin/env python3
"""
Test script to verify connections to all 3 Turso databases
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("Testing Turso 3 Separate Databases with Embedded Replicas")
print("=" * 80)

# Check environment variables
data_url = os.environ.get("DATA_DB_URL")
data_token = os.environ.get("DATA_DB_AUTH_TOKEN")
data_local = os.environ.get("DATA_DB_LOCAL", "data.db")

price_url = os.environ.get("PRICE_DB_URL")
price_token = os.environ.get("PRICE_DB_AUTH_TOKEN")
price_local = os.environ.get("PRICE_DB_LOCAL", "price.db")

supplier_url = os.environ.get("SUPPLIER_DB_URL")
supplier_token = os.environ.get("SUPPLIER_DB_AUTH_TOKEN")
supplier_local = os.environ.get("SUPPLIER_DB_LOCAL", "supplier_stock.db")

print("\n[1] Environment Variables Check:")
print(f"✓ DATA_DB_URL: {data_url}")
print(f"✓ DATA_DB_AUTH_TOKEN: {'***' + data_token[-10:] if data_token else 'NOT SET'}")
print(f"✓ DATA_DB_LOCAL: {data_local}")
print(f"✓ PRICE_DB_URL: {price_url}")
print(f"✓ PRICE_DB_AUTH_TOKEN: {'***' + price_token[-10:] if price_token else 'NOT SET'}")
print(f"✓ PRICE_DB_LOCAL: {price_local}")
print(f"✓ SUPPLIER_DB_URL: {supplier_url}")
print(f"✓ SUPPLIER_DB_AUTH_TOKEN: {'***' + supplier_token[-10:] if supplier_token else 'NOT SET'}")
print(f"✓ SUPPLIER_DB_LOCAL: {supplier_local}")

if not all([data_url, data_token, price_url, price_token, supplier_url, supplier_token]):
    print("\n❌ Missing required environment variables!")
    exit(1)

print("\n[2] Initializing Flask App with 3 Turso databases...")
from app import create_app
app = create_app()

print("\n[3] Testing Database Connections...")
with app.app_context():
    from models import db, Product, SkuPricing

    # Test Data DB (default bind)
    print("\n--- Testing DATA DB ---")
    try:
        product_count = Product.query.count()
        print(f"✅ Data DB connected successfully!")
        print(f"   → Found {product_count} products")
    except Exception as e:
        print(f"❌ Data DB connection failed: {e}")

    # Test Price DB
    print("\n--- Testing PRICE DB ---")
    try:
        pricing_count = SkuPricing.query.count()
        print(f"✅ Price DB connected successfully!")
        print(f"   → Found {pricing_count} SKU pricings")
    except Exception as e:
        print(f"❌ Price DB connection failed: {e}")

    # Test Supplier DB
    print("\n--- Testing SUPPLIER DB ---")
    try:
        # Import supplier model
        from models import SupplierSkuMaster
        supplier_count = SupplierSkuMaster.query.count()
        print(f"✅ Supplier DB connected successfully!")
        print(f"   → Found {supplier_count} supplier SKUs")
    except Exception as e:
        print(f"❌ Supplier DB connection failed: {e}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
