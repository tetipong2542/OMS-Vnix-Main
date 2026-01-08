#!/usr/bin/env python3
"""
Script to verify Railway environment variables are set correctly
Run this locally to see what your current environment looks like
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 80)
print("Railway Environment Variables Checker")
print("=" * 80)

required_vars = {
    "DATA_DB_URL": "libsql://data-tetipong2542.aws-ap-northeast-1.turso.io",
    "DATA_DB_AUTH_TOKEN": "starts with eyJh...",
    "DATA_DB_LOCAL": "/data/data.db (Railway) or data.db (Local)",
    "PRICE_DB_URL": "libsql://price-tetipong2542.aws-ap-northeast-1.turso.io",
    "PRICE_DB_AUTH_TOKEN": "starts with eyJh...",
    "PRICE_DB_LOCAL": "/data/price.db (Railway) or price.db (Local)",
    "SUPPLIER_DB_URL": "libsql://supplier-stock-tetipong2542.aws-ap-northeast-1.turso.io",
    "SUPPLIER_DB_AUTH_TOKEN": "starts with eyJh...",
    "SUPPLIER_DB_LOCAL": "/data/supplier_stock.db (Railway) or supplier_stock.db (Local)",
}

print("\n✅ REQUIRED for Turso 3 Databases:\n")

all_set = True
for var, description in required_vars.items():
    value = os.environ.get(var)
    if value:
        # Mask sensitive tokens
        if "TOKEN" in var:
            display_value = f"***{value[-20:]}" if len(value) > 20 else "***"
        else:
            display_value = value
        print(f"✅ {var:25} = {display_value}")
    else:
        print(f"❌ {var:25} = NOT SET (Expected: {description})")
        all_set = False

print("\n" + "=" * 80)

if all_set:
    print("✅ All required variables are set!")
    print("\nFor Railway deployment, make sure:")
    print("1. DATA_DB_LOCAL=/data/data.db (not data.db)")
    print("2. PRICE_DB_LOCAL=/data/price.db (not price.db)")
    print("3. SUPPLIER_DB_LOCAL=/data/supplier_stock.db (not supplier_stock.db)")
    print("4. Railway Volume is mounted at /data")
else:
    print("❌ Some variables are missing!")
    print("\nCopy values from: env-railway-setup.md")
    print("To Railway: Dashboard → Settings → Variables")

print("=" * 80)

# Check what mode app would use
print("\n🔍 Predicted App Mode:")
data_url = os.environ.get("DATA_DB_URL")
price_url = os.environ.get("PRICE_DB_URL")
supplier_url = os.environ.get("SUPPLIER_DB_URL")

if data_url and price_url and supplier_url:
    print("✅ Would use: 3 SEPARATE TURSO DATABASES")
    print(f"   - Data: {data_url}")
    print(f"   - Price: {price_url}")
    print(f"   - Supplier: {supplier_url}")
else:
    turso_url = os.environ.get("TURSO_DATABASE_URL")
    if turso_url:
        print("⚠️  Would use: LEGACY SINGLE TURSO DATABASE")
        print(f"   - URL: {turso_url}")
    else:
        print("❌ Would use: LOCAL SQLITE FILES (No Turso!)")
        print("   This is why data doesn't show on Railway!")

print("=" * 80)
