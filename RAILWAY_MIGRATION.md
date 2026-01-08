# Railway Database Migration Guide

## ปัญหา: `ValueError: no such column: shops.is_system_config`

เมื่อ deploy ครั้งแรกหรือ update schema ใหม่ อาจพบ error นี้เพราะ Turso database ยังไม่มีคอลัมน์ใหม่

## วิธีแก้ไข

### ขั้นตอนที่ 1: Deploy Code ขึ้น Railway

```bash
git add .
git commit -m "Add migration script"
git push origin main
```

Railway จะ auto-deploy ให้อัตโนมัติ

### ขั้นตอนที่ 2: รัน Migration Script บน Railway

1. เข้า Railway Dashboard
2. เลือก Project ของคุณ
3. ไปที่แท็บ **"Deployments"**
4. คลิก **"View Logs"** ของ deployment ล่าสุด
5. คลิกปุ่ม **"Shell"** หรือ **"Terminal"** (มุมขวาบน)
6. รันคำสั่ง:

```bash
python migrate_shops_schema.py
```

### ขั้นตอนที่ 3: Restart Application

หลังจาก migration สำเร็จ ให้ restart application:

**วิธีที่ 1: ผ่าน Railway Dashboard**
- ไปที่แท็บ **"Settings"**
- คลิก **"Restart"**

**วิธีที่ 2: ผ่าน Terminal**
```bash
# Railway จะ restart อัตโนมัติหลังจาก migration เสร็จ
# หรือสามารถ trigger restart ด้วยการ redeploy
```

## ตรวจสอบว่า Migration สำเร็จ

ดู logs ควรเห็นข้อความ:

```
============================================================
VNIX ERP - Database Schema Migration
============================================================

📡 Connecting to Turso database...
   URL: libsql://data-tetipong2542.aws-ap-northeast-1.turso.io
   ✅ Connected successfully

============================================================
Migrating shops table schema
============================================================

📋 Current columns in shops table:
   - id
   - platform
   - name
   - created_at
   - google_sheet_url

🔧 Adding missing column: is_system_config
   ✅ Column added successfully

🔧 Creating index on is_system_config
   ✅ Index created successfully

============================================================
✅ Migration completed successfully!
============================================================

🚀 You can now restart your application
```

## หมายเหตุ

- Migration script จะตรวจสอบว่าคอลัมน์มีอยู่แล้วหรือไม่ ถ้ามีแล้วจะข้ามไป
- ปลอดภัยที่จะรันหลายครั้ง (idempotent)
- ไม่ลบข้อมูลเดิม เพิ่มคอลัมน์ใหม่เท่านั้น

## การ Migrate ในอนาคต

ถ้ามีการเพิ่มคอลัมน์ใหม่ใน models.py:

1. สร้าง migration script ใหม่ (คล้าย `migrate_shops_schema.py`)
2. Push ขึ้น Git
3. รัน migration script บน Railway
4. Restart application

## Troubleshooting

### ถ้า Migration ล้มเหลว

1. ตรวจสอบ Environment Variables บน Railway:
   - `DATA_DB_URL`
   - `DATA_DB_AUTH_TOKEN`
   - `DATA_DB_LOCAL` (optional)

2. ตรวจสอบ logs ว่ามี error อะไร

3. ลอง restart deployment ใหม่

### ถ้ายังเจอ Error เดิม

1. ตรวจสอบว่า migration รันสำเร็จจริง ๆ
2. ตรวจสอบว่า restart application แล้ว
3. Clear cache (ถ้ามี)
4. Redeploy ใหม่

## ติดต่อ Support

ถ้ายังมีปัญหา ติดต่อ:
- GitHub Issues: https://github.com/tetipong2542/OMS-Vnix-Main/issues
- Email: [your-email]
