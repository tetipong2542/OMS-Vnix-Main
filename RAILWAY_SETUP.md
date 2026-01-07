# 🚂 Railway Deployment Guide

คู่มือการ deploy OMS Vnix V2 ไปยัง Railway พร้อมการตั้งค่า Turso database

---

## 📋 Prerequisites

- ✅ GitHub repository: https://github.com/tetipong2542/OMS-Vnix-Main
- ✅ Turso database: `vnix-erp` (อัปโหลดข้อมูลเรียบร้อยแล้ว)
- ✅ Railway account: https://railway.app

---

## 🔧 ขั้นตอนที่ 1: สร้าง Project ใน Railway

1. เข้า https://railway.app และ Login
2. คลิก **"New Project"**
3. เลือก **"Deploy from GitHub repo"**
4. เลือก repository: **`tetipong2542/OMS-Vnix-Main`**
5. Railway จะเริ่มสร้าง project และ deploy โดยอัตโนมัติ

---

## ⚙️ ขั้นตอนที่ 2: ตั้งค่า Environment Variables

ใน Railway Dashboard:

1. คลิกที่ project ที่สร้างไว้
2. ไปที่แท็บ **"Variables"**
3. เพิ่ม environment variables ต่อไปนี้:

### 🔐 Required Variables (สำคัญ!)

```bash
# Turso Database Configuration
TURSO_DATABASE_URL=libsql://vnix-erp-tetipong2542.aws-ap-northeast-1.turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Njc3NzczMzUsImlkIjoiOGE2OGM2ZjgtODEzMS00Yjg3LWI4NjktMjk1OWFkN2RlZDAwIiwicmlkIjoiYTg5YjZlODItNmU1Yi00MmUzLWEzMjItODY3YjhlMDk1YzU5In0.yyXVYnsXy86xE5tSmu9h0x27hRdjccSpWMupOj6E97jj7jeUxuc1ZZ8TxtIeCyfFBDnWYj42Is7fU7Y2dV03BA

# Application Secret Key (สร้าง random string)
SECRET_KEY=vnix-production-secret-key-2026

# Google Sheets API (ใช้จาก .env file)
GOOGLE_CLIENT_EMAIL=vnix-sheet-importer@vnix-oms.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDNaBfT19Jfva7a\npakNfdccVCnmIKSDFDfR/u+rt8cfWObZt9VJbRWDMc2lEd5l2VYkVq3NTq4yjlxw\n91ng/+qKtYM0cp+TnT8G739sC6nr36A7KQp0ViZud87KSaFGpoqVFPjHlNhZrSK6\nF0P2Oc2l0hAQvQRqSaFtCeeRSgevgTxaLbde6nFloxUE7bUcx3uj8p9zdYAwM+dC\nDEbWECuGPmVI/tiCOT9HcdFZigr0/n6G5OQLJOjWT79wwRf1tTddefONfqroS6jh\nM7SWlFAkhZvLRp5iJMaLtfKfT+5+P+bDLmoXVYbZRSd2U5ITPo8UzCBkhKHWoYka\n3CiZ3qe1AgMBAAECggEAUUWG6/xgUh5gkUVroplwY9aPL20p+m0k+vM2TEiuQiJw\nUKOSgfdlxB+QAOiViNHZ6g3bvbiMZxd5zv6ncsV/PPu9mqJhrkvQ1MMtNQhWZqv4\nH4BJESfHE/1WdiZ059ncSkled8VWZwEAlQXAj6tmSV5Yme7X0OAqPVTmaU+Tw+YV\nl/ATRlbW02S8qJGIZrstE6MwVKxczk6fukgY883R91ZDZOKxZbeIwXhIlvMYumI6\nqyqWrFsKG8Y6Uj4vW8+Ef4yAZWV35LzUxHQ8ebclm6Jz/5WXx2Iq6s+9sSPkavnn\n7llDLrCVO9e4HmUsq0fYghKulczsF9xltGfvXa/uTwKBgQD+NuOpUYUR6o2zajlp\nraHquvzmtB0s+eD4Dn7CK0qGP5wzaiwYeEpQUTgB+1ZBbyaYIQ7ZsJsX41o7RJs9\nyHtO+9CJI9tn+m+wRE80nDxWzT14kTu5KXZaDGIPEkoIIHTrn1/6KE0QShAcqFlZ\n63TqLXby/jtCsZkeHqtVGcgNGwKBgQDO2XDkMY7YjOmnvueuelTh0oCLdWDFblEZ\nBbxuJNLY88LcW58HsI7Qi2J/xzWzYkNcs5b3YlXm26qY+WSe8kYF8viHpC2m4vj6\nBFJ+3N92KqcAZqVT+MqtEups5hyvZHVm2092EepCQqVlpo7y1zpB5cuw0/Xri1PM\nj/Yqb897bwKBgQDg0N4JUWSjcZEbSCe6A6ocEn2x8TuUGPARr4/+W5aunvaeqZiR\nk1/1I76qUgH4IDo7c5DUh9DBEXkszQGVZAVY1m2XurRAgkPf2KlLV5gtE5j3VUlB\n+R8Hh8f4mC4MfdeowOt6KcXtT/JrxZ4vXYGpz8dQIfF6i+Fjt6/BtOksXQKBgQCs\nbkbVcxqJGq6Mz2+C2yd3OGs/1hFdg6DHIyj5CGlbwZhm6Vmgp2XmIstxiTcS2o8c\n7/ihMLA7SlLkQsHGXmBRBUJ4kDweKocyo/fBGY6Oiu+8PdUEMxmBPYt+TDUNYMkd\nfSS4YCbQJY6LNlVjylceJ9mtBoSyXer1U+z5Y0uqsQKBgQCm1UWGLHr7FD65PDFk\nIBXi/5XaHQmR1v/dTbqyk4KDT1azGpfjwPF1quFYxzTBIUofDgWRZInCuRStYmqX\nbdzwDCs6MwG15rqdgTBGa7w7kexLklHMKB2s+CLuWLRBxt1g6apLVMOpPHOKlpni\nmfVe0NXx5FDEevHcgZZZPK0AqQ==\n-----END PRIVATE KEY-----\n
GOOGLE_PROJECT_ID=vnix-oms
```

### 📝 Optional Variables

```bash
# App name (แสดงใน UI)
APP_NAME=VNIX ERP

# Python version (ถ้า Railway ไม่ตรวจจับอัตโนมัติ)
PYTHON_VERSION=3.11.12
```

---

## 🚀 ขั้นตอนที่ 3: Deploy

1. หลังจากตั้งค่า environment variables เสร็จ
2. Railway จะ **redeploy อัตโนมัติ**
3. รอประมาณ 2-3 นาที
4. ตรวจสอบ deployment logs ว่ามี error หรือไม่

### ✅ ตรวจสอบ Logs ว่า Deploy สำเร็จ

ใน deployment logs ควรเห็น:
```
[INFO] Using Turso (libSQL) database
[DEBUG] Turso URL: libsql://vnix-erp-tetipong2542.aws-ap-northeast-1.turso.io
[DEBUG] Using single Turso database for all binds
```

---

## 🌐 ขั้นตอนที่ 4: เข้าใช้งาน

1. Railway จะสร้าง public URL ให้อัตโนมัติ (เช่น `https://your-app.up.railway.app`)
2. คลิกที่ URL เพื่อเปิดแอปพลิเคชัน
3. Login ด้วย username/password ที่มีอยู่ใน database

---

## 🔍 Troubleshooting

### ❌ ปัญหา: "Unable to connect to database"

**วิธีแก้:**
- ตรวจสอบว่า `TURSO_DATABASE_URL` และ `TURSO_AUTH_TOKEN` ถูกต้อง
- ตรวจสอบว่า Turso database มีตารางข้อมูลครบถ้วน:
  ```bash
  turso db shell vnix-erp "SELECT name FROM sqlite_master WHERE type='table';"
  ```

### ❌ ปัญหา: "Module not found: sqlalchemy-libsql"

**วิธีแก้:**
- ตรวจสอบว่า `requirements.txt` มี `sqlalchemy-libsql>=0.1.0`
- Railway อาจต้อง rebuild - ลอง trigger redeploy ใหม่

### ❌ ปัญหา: "Google Sheets API error"

**วิธีแก้:**
- ตรวจสอบว่า `GOOGLE_PRIVATE_KEY` มี `\n` (newline characters) ถูกต้อง
- ใน Railway variables ให้ใส่ **ทั้งก้อน** โดยไม่ต้อง escape

---

## 📊 Database Architecture

```
┌─────────────────────────────────────┐
│   Railway Application (Flask)       │
│   ├── app.py                         │
│   └── models.py                      │
└────────────┬────────────────────────┘
             │
             │ TURSO_DATABASE_URL
             │ TURSO_AUTH_TOKEN
             ↓
┌─────────────────────────────────────┐
│   Turso Database (vnix-erp)         │
│   ├── order_lines (data)            │
│   ├── products (data)                │
│   ├── shops (data)                   │
│   ├── users (data)                   │
│   ├── stocks (data)                  │
│   ├── sales (data)                   │
│   ├── supplier_sku_master (supplier)│
│   ├── supplier_configs (supplier)   │
│   └── ... (price tables)             │
└─────────────────────────────────────┘
```

**หมายเหตุ:** ทั้ง 3 databases (data, price, supplier_stock) ถูกรวมไว้ใน Turso database เดียวกัน เพื่อความสะดวกในการจัดการ

---

## 🔄 การอัปเดตโค้ด

เมื่อต้องการอัปเดตโค้ด:

1. แก้ไขโค้ดใน local repository
2. Commit และ push ไป GitHub:
   ```bash
   git add .
   git commit -m "Update feature X"
   git push origin main
   ```
3. Railway จะ **auto-deploy** ให้อัตโนมัติ

---

## 📞 Support

ถ้ามีปัญหาหรือข้อสงสัย:
- ตรวจสอบ Railway logs
- ตรวจสอบ Turso database connectivity
- ดูเอกสารเพิ่มเติม: https://docs.railway.app

---

**สร้างโดย:** Claude Code
**วันที่:** 2026-01-07
