# Dual Database Mode Guide

## Overview

Dual Database Mode allows VNIX ERP to operate with both old SQLite databases (read-only) and new Turso cloud database (read/write) simultaneously. This is particularly useful during migration from local SQLite to cloud-based Turso database.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VNIX ERP Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐              ┌────────────────────┐  │
│  │   OLD DATABASES  │              │   NEW DATABASE     │  │
│  │   (Read-Only)    │              │   (Read/Write)     │  │
│  ├──────────────────┤              ├────────────────────┤  │
│  │  data.db         │◄────Query────┤  Turso Cloud DB    │  │
│  │  price.db        │              │  (vnix-erp.db)     │  │
│  │  supplier_stock  │              │  + Embedded Replica│  │
│  │        .db       │              │                    │  │
│  └──────────────────┘              └────────────────────┘  │
│         SQLite3                       libSQL/Turso         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Seamless Data Access**: Query historical data from old SQLite databases while writing new data to Turso
- **Zero Downtime Migration**: Gradually migrate to cloud database without interrupting operations
- **Data Comparison**: Compare old and new data for validation
- **Embedded Replica**: Local sync of Turso database for better performance and offline capability

## Setup

### 1. Install Dependencies

```bash
pip install sqlalchemy-libsql libsql-experimental flask-sqlalchemy
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Enable Dual Database Mode
ENABLE_DUAL_DB_MODE=true

# Turso Configuration
TURSO_DATABASE_URL=libsql://vnix-erp-tetipong2542.aws-ap-northeast-1.turso.io
TURSO_AUTH_TOKEN=your-auth-token-here

# Local embedded replica file
LOCAL_DB=vnix-erp.db
```

### 3. Ensure Old Databases Exist

Make sure these files exist in your project directory:
- `data.db`
- `price.db`
- `supplier_stock.db`

### 4. Run the Application

```bash
python app.py
```

You should see:
```
[INFO] ⚙️  DUAL DATABASE MODE ENABLED
[INFO] Using Turso (libSQL) for NEW data (read/write)
[INFO] Using SQLite for OLD data (read-only)
```

## Database Binds

The following database binds are available:

| Bind Key       | Database Type | Access Mode | Purpose                    |
|---------------|---------------|-------------|----------------------------|
| `default`     | Turso         | Read/Write  | New main data (products, orders, etc.) |
| `price`       | Turso         | Read/Write  | New price data             |
| `supplier`    | Turso         | Read/Write  | New supplier data          |
| `data_old`    | SQLite        | Read-Only   | Old main data (historical) |
| `price_old`   | SQLite        | Read-Only   | Old price data (historical)|
| `supplier_old`| SQLite        | Read-Only   | Old supplier data (historical)|

## Usage

### Using Dual Query Helpers

The `db_helpers.py` module provides convenient functions for querying both databases:

```python
from db_helpers import dual_query_auto, dual_query_price, dual_query_supplier
from models import Product, SkuPricing, SupplierSkuMaster

# Query products from both old and new databases
all_products = dual_query_auto(Product, order_by='sku')
print(f"Total products: {len(all_products)}")

# Query with filters
samsung_products = dual_query_auto(
    Product,
    filters={'brand': 'Samsung'},
    order_by='sku'
)

# Query prices from both databases
all_prices = dual_query_price(SkuPricing, order_by='sku')

# Query suppliers from both databases
all_suppliers = dual_query_supplier(SupplierSkuMaster)
```

### Writing New Data

All write operations automatically go to Turso (new database):

```python
# This will write to Turso, not to old SQLite databases
new_product = Product(sku='NEW-SKU-001', brand='NewBrand', model='Model X')
db.session.add(new_product)
db.session.commit()
```

### Reading Old Data Only

If you need to query only old databases:

```python
from models import db, Product
from sqlalchemy import text

# Query old data.db directly
engine_old = db.engines.get('data_old')
with engine_old.connect() as conn:
    result = conn.execute(text("SELECT * FROM products WHERE brand = 'Samsung'"))
    old_samsung_products = result.fetchall()
```

## Testing

Run the test script to verify your configuration:

```bash
python test_dual_db_connection.py
```

Expected output:
```
✅ Connected! Found X products in old data.db
✅ Connected! Found X SKU pricing records in old price.db
✅ Connected! Found X supplier SKU records in old supplier_stock.db
✅ Main DB connected! Found X products in Turso
✅ Price bind connected! Found X SKU pricing records in Turso
✅ Supplier bind connected! Found X supplier SKU records in Turso
✅ Found X total products from both databases
```

## Migration Strategy

### Phase 1: Setup (Current)
- Enable Dual Database Mode
- Verify both old and new databases are accessible
- Test dual query functions

### Phase 2: Gradual Migration
- Use `upload_to_turso.py` or similar scripts to copy old data to Turso
- Validate data consistency between old and new databases
- Update application logic to write to Turso

### Phase 3: Full Switch
- Once all data is migrated and validated
- Disable Dual Database Mode: `ENABLE_DUAL_DB_MODE=false`
- Keep old databases as backup
- Use Turso exclusively

## Helper Functions Reference

### `is_dual_mode_enabled()`
Check if Dual Database Mode is enabled.

```python
from db_helpers import is_dual_mode_enabled

if is_dual_mode_enabled():
    print("Dual mode is active")
```

### `dual_query(model, bind_old, filters, order_by)`
Generic dual query function.

```python
from db_helpers import dual_query
from models import Product

products = dual_query(
    Product,
    bind_old='data_old',
    filters={'brand': 'Samsung'},
    order_by='sku'
)
```

### `dual_query_auto(model, filters, order_by)`
Automatically determines the correct old bind based on model's `__bind_key__`.

```python
from db_helpers import dual_query_auto
from models import Product, SkuPricing

# Automatically uses data_old for Product
products = dual_query_auto(Product)

# Automatically uses price_old for SkuPricing
prices = dual_query_auto(SkuPricing)
```

### `dual_count(model, bind_old, filters)`
Count records from both databases.

```python
from db_helpers import dual_count
from models import Product

total_count = dual_count(Product, bind_old='data_old')
print(f"Total products: {total_count}")

samsung_count = dual_count(
    Product,
    bind_old='data_old',
    filters={'brand': 'Samsung'}
)
```

## Troubleshooting

### Error: "Can't load plugin: sqlalchemy.dialects:libsql"

Install the required package:
```bash
pip install sqlalchemy-libsql
```

### Error: "Hrana: api error: status=308 Permanent Redirect"

This means you're using remote connection. Switch to embedded replica mode:
```bash
LOCAL_DB=vnix-erp.db  # This enables embedded replica
```

### Old databases not found

Make sure the database files exist in your project directory or update the paths in `app.py`.

### Embedded replica not syncing

Check your internet connection and Turso auth token. The embedded replica syncs automatically on write operations.

## Performance Considerations

- **Embedded Replica**: Uses local file (`vnix-erp.db`) that syncs with Turso, providing better read performance
- **Old Databases**: Accessed directly from local SQLite files (fast)
- **Write Operations**: Go to embedded replica first, then sync to Turso
- **Network**: Only required for sync operations, not for every query

## Security Notes

- Old SQLite databases are mounted as READ-ONLY to prevent accidental modifications
- Turso auth token should be kept secret (use environment variables, never commit to git)
- Embedded replica file should be backed up regularly

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Run `test_dual_db_connection.py` to diagnose connection issues
3. Verify environment variables are set correctly
4. Check Turso dashboard for database status

---

**Last Updated**: 2026-01-07
**Version**: 1.0.0
