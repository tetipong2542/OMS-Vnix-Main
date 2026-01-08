# Railway Deployment Guide for VNIX ERP with Turso (3 Separate Databases)

## ⚠️ IMPORTANT: ปัญหาที่พบบ่อย

หาก Railway logs แสดง:
```
[INFO] Using local SQLite database files
[DEBUG] Main DB path: /app/data.db
```

แสดงว่า **Environment Variables สำหรับ Turso ไม่ได้ถูกตั้งค่า!** ต้องแก้ทันทีตามขั้นตอนด้านล่าง

---

## Prerequisites

- Railway account
- Turso 3 databases created: `data`, `price`, `supplier-stock`
- Turso auth tokens (แบบ `rw` - read/write)

## 🚀 Quick Fix: Environment Variables

ไปที่ **Railway Dashboard → Settings → Variables** แล้วตั้งค่าตามนี้:

### ✅ Required Variables (สำคัญมาก!)

```bash
# ==== DATA DB ====
DATA_DB_URL=libsql://data-tetipong2542.aws-ap-northeast-1.turso.io
DATA_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzMDksImlkIjoiMTY3YTExNDUtZGM0NC00MzIwLTk0MmMtMDM3ZjFiNTRjZjgxIiwicmlkIjoiZWE0ZjEzN2EtYTI0ZS00N2YyLWIxOWEtMWZjNTIzYmE2Y2JjIn0.hocKljFNemkcyZ4lYeYD7FUD3hMlDIEo-Xj0kpbCsEzOwe4h1EKHh0j68IjuOWwYZQ5IutCbIekP6B2Lqn9gBQ
DATA_DB_LOCAL=/data/data.db

# ==== PRICE DB ====
PRICE_DB_URL=libsql://price-tetipong2542.aws-ap-northeast-1.turso.io
PRICE_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzNzUsImlkIjoiZDhlNWZiYjktOWI3YS00YzU1LWIxMWMtODNhOTBiYjNiZGUwIiwicmlkIjoiMDhhOWRlNzAtNjI4Ny00MzQ5LWE1M2MtYzYxZTI1Mjc4Y2UxIn0.hgTCaKN3iFx--UuYvmUR6T9YP5iWDkY2NNFLe5BBY382ZOWaSnv6M-cz7hP51OWTWTv1Hu2S4sJZS2RZMTg7AQ
PRICE_DB_LOCAL=/data/price.db

# ==== SUPPLIER DB ====
SUPPLIER_DB_URL=libsql://supplier-stock-tetipong2542.aws-ap-northeast-1.turso.io
SUPPLIER_DB_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc4NDIzODksImlkIjoiODBkYTFlZmItZmM1Ni00OGQ3LWEwMzctODgyMWI3NGRhZTcwIiwicmlkIjoiMzA4M2VmMDUtZDM0NS00YWY1LWJlZTQtYjQ3OGZlNjcyMTk5In0.tF_3StAUdbz0wxuGgGl6XZe1TFvFL2N2XGZ01YNB5YODkWfvMC2Iz_UiNfCKf69v_lyuRwwz1LKyTRCJA-CTBw
SUPPLIER_DB_LOCAL=/data/supplier_stock.db

# ==== Railway Volume (ถ้ามี) ====
RAILWAY_VOLUME_MOUNT_PATH=/data

# ==== Application Settings ====
APP_NAME=VNIX ERP
SECRET_KEY=your-production-secret-key-here
```

### ⚠️ สำคัญมาก!
- ใช้ `/data/data.db` **ไม่ใช่** `data.db` (ต้องมี `/data/` prefix)
- ใช้ `/data/price.db` **ไม่ใช่** `price.db`
- ใช้ `/data/supplier_stock.db` **ไม่ใช่** `supplier_stock.db`

### Optional Variables (for Dual Database Mode)

```bash
# Enable Dual Database Mode (only if you want to access old SQLite files)
ENABLE_DUAL_DB_MODE=true

# Railway Volume (if you have old SQLite files in persistent storage)
RAILWAY_VOLUME_MOUNT_PATH=/data
```

### Google Sheets Integration (Optional)

```bash
GOOGLE_PRIVATE_KEY=your-google-private-key
GOOGLE_CLIENT_EMAIL=your-service-account-email
```

## Deployment Steps

### 1. Push Updated Code to Git

```bash
# Make sure you have the latest changes
git add requirements.txt app.py db_helpers.py

git commit -m "Add Turso embedded replica support with sqlalchemy-libsql"

git push origin main
```

### 2. Railway will Auto-Deploy

Railway will automatically:
- Install `sqlalchemy-libsql==0.2.0` from requirements.txt
- Use embedded replica mode (better performance)
- Create local `vnix-erp.db` file that syncs with Turso

### 3. Verify Deployment

Check Railway logs for:

```
[INFO] Using Turso (libSQL) database
[DEBUG] Turso URL: libsql://vnix-erp-tetipong2542.aws-ap-northeast-1.turso.io
[DEBUG] Full DB URI: sqlite+libsql:///vnix-erp.db?sync_url=libsql://...
[DEBUG] Using single Turso database for all binds
```

✅ You should see `sqlite+libsql://` (not `libsql+libsql://`)

## Troubleshooting

### Error: "Can't load plugin: sqlalchemy.dialects:libsql.libsql"

**Cause**: Missing `sqlalchemy-libsql` in dependencies

**Solution**:
1. Verify `requirements.txt` includes:
   ```
   sqlalchemy-libsql==0.2.0
   ```
2. Redeploy to Railway

### Error: "Hrana: api error: status=308 Permanent Redirect"

**Cause**: Using direct remote connection instead of embedded replica

**Solution**:
1. Set `LOCAL_DB=vnix-erp.db` in Railway environment variables
2. Make sure you're using the updated `app.py` with embedded replica code

### Slow Performance

**Solution**: Embedded replica mode is already enabled, which provides:
- Local reads (fast)
- Background sync to Turso
- Automatic failover

### Database Not Syncing

**Check**:
1. Turso auth token is correct
2. Internet connectivity from Railway
3. Turso database exists and is accessible

## Performance Optimization

### Embedded Replica Benefits

- ✅ Local reads (no network latency)
- ✅ Automatic sync on write operations
- ✅ Offline capability
- ✅ Better resilience

### Storage Considerations

The embedded replica file (`vnix-erp.db`) will grow over time. Monitor Railway disk usage.

## Persistent Storage (Optional)

If you need to persist old SQLite databases on Railway:

### 1. Add Railway Volume

1. Go to Railway project settings
2. Add a volume at `/data`
3. Upload old database files to volume:
   - `/data/data.db`
   - `/data/price.db`
   - `/data/supplier_stock.db`

### 2. Enable Dual Database Mode

Set environment variable:
```bash
ENABLE_DUAL_DB_MODE=true
RAILWAY_VOLUME_MOUNT_PATH=/data
```

## Migration from Old SQLite to Turso

### Phase 1: Current Setup (Local SQLite)
```
Railway → SQLite files in volume
```

### Phase 2: Dual Mode (Transition)
```
Railway → Old SQLite (read-only) + Turso (read/write)
```

### Phase 3: Full Turso (Target)
```
Railway → Turso only (no old SQLite needed)
```

## Monitoring

### Check Database Status

View Railway logs for:
- Database connection status
- Sync operations
- Query performance
- Error messages

### Turso Dashboard

Monitor from Turso dashboard:
- Database size
- Query count
- Bandwidth usage
- Sync status

## Rollback Plan

If deployment fails:

### 1. Quick Rollback
```bash
# Railway Dashboard → Deployments → Previous deployment → Redeploy
```

### 2. Environment Variables Rollback

Remove/change:
- `LOCAL_DB`
- `TURSO_DATABASE_URL`
- `TURSO_AUTH_TOKEN`

This will fall back to local SQLite mode.

## Support

For issues:
1. Check Railway logs
2. Verify environment variables
3. Test connection with Turso CLI:
   ```bash
   turso db shell vnix-erp
   ```

---

**Last Updated**: 2026-01-07
**Version**: 1.0.0
