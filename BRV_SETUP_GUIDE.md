# Byterover CLI Setup Guide for VNIX Order Management

## 🎯 Purpose
ใช้ Byterover CLI (brv) ร่วมกับ Claude Code เพื่อ:
1. Curate (จัดระเบียบ) ความรู้จาก PRD files
2. Query (ถาม) ข้อมูลเกี่ยวกับระบบเมื่อต้องการ
3. ให้ Claude Code เข้าใจ Context ของโปรเจคครบวงจร

---

## 📋 Prerequisites (ตรวจสอบแล้ว ✅)
- ✅ Byterover CLI 1.0.4 ติดตั้งแล้ว
- ✅ Node.js v23.11.0
- ✅ Logged in as: pond.vnix@gmail.com
- ✅ Connected to: Vnix-WMS project
- ✅ PRD Files ready: PRD-Frontend.md, PRD-Backend.md

---

## 🚀 Step-by-Step Guide

### Step 1: Curate PRD Documents (สำคัญที่สุด)

ให้ Claude Code รันคำสั่งนี้:

```
====================================
โปรดใช้ brv curate เพื่อวิเคราะห์เอกสาร PRD
====================================

คุณเป็น AI Coding Agent ที่ทำงานร่วมกับ Byterover CLI

กรุณาวิเคราะห์และจัดระเบียบเนื้อหาจากไฟล์ PRD 2 ไฟล์:

ไฟล์ที่ต้องวิเคราะห์:
1. PRD-Frontend.md (578 บรรทัด)
2. PRD-Backend.md (1,431 บรรทัด)

โฟกัสที่เนื้อหาสำคัญเหล่านี้:

📊 Executive Summary (ภาพรวมธุรกิจ)
- คุณค่าทางธุรกิจ (Business Value)
- User Personas (ผู้ใช้งานหลัก: Warehouse Manager, Price Analyst, Admin)
- Key Business Rules (กฎธุรกิจ 4 ข้อ)

🏗️ System Architecture
- Multi-Database Architecture (data.db, price.db, supplier_stock.db)
- Flask Framework + SQLAlchemy ORM
- Frontend: Bootstrap 5 + DataTables

📋 Database Schema
- 12 Tables ใน data.db (Orders, Products, Stocks, Users, ฯลฯ)
- 11 Tables ใน price.db (SKU Pricing, Market Prices, Brand Controls)
- 3 Tables ใน supplier_stock.db (Supplier SKU Master, Config)

🔄 Core Workflows
1. Order Allocation Logic (จัดสรรสต็อกตาม Priority)
2. SLA Calculation (คำนวณวันทำการ)
3. Price Management (ตั้งราคาขายหลาย Tier)
4. Import/Export Process

🚀 Scalability Roadmap
- Phase 1: Database Migration → PostgreSQL (3 เดือน)
- Phase 2: Redis Caching (6 เดือน)
- Phase 3: Real-time + Celery (12 เดือน)
- Phase 4: Microservices + K8s (18 เดือน)
- Phase 5: AI & Analytics (24 เดือน)

📈 API Endpoints (7 กลุ่ม)
- Authentication (Login/Logout)
- Dashboard (GET /, POST /api/accept)
- Reports (Warehouse, Picking, Low Stock, ฯลฯ)
- Import (Products, Stock, Orders, Sales)
- Price Dashboard
- Supplier Stock
- Admin (Shops, Users)

🎯 User Flows
- Warehouse Manager Flow
- Price Analyst Flow
- Admin/Owner Flow

📊 Performance Targets
- API Response: < 200ms
- System Uptime: > 99%
- Concurrent Users: 50-500 (ตาม Phase)

จัดระเบียบเป็น structured domains:
1. business_overview (ภาพรวมธุรกิจ)
2. system_architecture (สถาปัตยกรรม)
3. database_design (การออกแบบฐานข้อมูล)
4. api_endpoints (API ทั้งหมด)
5. core_workflows (การทำงานหลัก)
6. scalability_roadmap (แผนขยายระบบ)
7. performance_metrics (ตัวชี้วัด)
8. user_personas (ผู้ใช้งาน)

รอบรู้: รายละเอียดทั้งหมดที่เกี่ยวข้องกับการพัฒนา
และขยายระบบ VNIX Order Management

หลังจากเสร็จ รายงาน:
1. จำนวน bullets ที่สร้าง
2. จำนวน domains ที่จัดระเบียบ
3. Context ใดบ้างที่เพิ่มเข้าไป
====================================
```

---

### Step 2: Query Context (เมื่อต้องการถาม)

เมื่อต้องการถามข้อมูลเกี่ยวกับระบบ ให้ใช้ prompt:

```
====================================
ใช้ brv query เพื่อถามข้อมูล
====================================

ใช้ brv query เพื่อตอบคำถามนี้:

[ใส่คำถามของคุณที่นี่]

ตัวอย่างคำถาม:
- "ระบบคำนวณ SLA อย่างไร?"
- "มีฐานข้อมูลกี่ตัว และใช้ทำอะไรบ้าง?"
- "Scalability Phase 1 ทำอะไรบ้าง?"
- "API สำหรับรับออเดอร์มี endpoints อะไรบ้าง?"
- "User Flow ของ Warehouse Manager คืออะไร?"

ให้ตอบเป็นภาษาไทย และอ้างอิง context จาก PRD
====================================
```

---

## 📝 Quick Reference Commands

### สำหรับ Claude Code

```
# 1. Curate context จาก PRD
"ใช้ brv curate เพื่อวิเคราะห์ PRD-Frontend.md และ PRD-Backend.md
 เฉพาะส่วนที่เกี่ยวข้องกับ [หัวข้อที่ต้องการ]"

# 2. Query context
"ใช้ brv query ถามว่า [คำถามของคุณ]"

# 3. ตรวจสอบสถานะ
"ใช้ brv status เพื่อดูว่ามี context อะไรในระบบแล้วบ้าง"
```

### สำหรับ brv REPL (Direct)

```
brv                    # เริ่ม REPL
Tab                    # สลับไป Console tab
/status                # ดูสถานะ
/curate [prompt]       # เพิ่ม context
/query [question]      # ถาม context
/login                 # Login (ถ้ายังไม่ได้)
/init                  # Initialize project (ถ้ายังไม่ได้)
```

---

## 🎯 Example Use Cases

### Use Case 1: Developer ใหม่ต้องการเข้าใจระบบ

```
ใช้ brv query ถามว่า:
"ภาพรวมระบบ VNIX Order Management ทำงานอย่างไร?
เน้นส่วน Architecture และ Database Design"
```

### Use Case 2: วางแผนพัฒนา Feature ใหม่

```
ใช้ brv query ถามว่า:
"มี API endpoints อะไรบ้างที่เกี่ยวข้องกับการรับออเดอร์?
และ Business Rules ที่เกี่ยวข้องคืออะไร?"
```

### Use Case 3: วางแผนขยายระบบ

```
ใช้ brv query ถามว่า:
"Scalability Roadmap ทั้ง 5 Phases ทำอะไรบ้าง?
และ Phase 1 ต้อง Migration อะไรบ้าง?"
```

---

## ✅ Check status ได้ทันที

```bash
brv status
```

ผลลัพธ์:
```
CLI Version: 1.0.4
Status: Logged in as pond.vnix@gmail.com
Current Directory: /Users/pond-dev/Downloads/V.6.3/V.6.2
Project Status: Connected to Default Organization-mdc0oz/Vnix-WMS
Context Tree: No changes
```

---

## 📚 Resources

- 📖 [Byterover Quickstart](https://docs.byterover.dev/quickstart)
- 📖 [Byterover Docs](https://docs.byterover.dev/)
- 📖 [PRD-Frontend.md](./PRD-Frontend.md)
- 📖 [PRD-Backend.md](./PRD-Backend.md)

---

## 🤝 Tips

1. **Curate ทีละหัวข้อ** เพื่อให้ context เป็นระเบียบ
2. **Query บ่อยๆ** เพื่อทดสอบว่า context ครบหรือยัง
3. **Update context** เมื่อมีการเปลี่ยนแปลง PRD
4. **ใช้ร่วมกับ Claude Code** เพื่อประสิทธิภาพสูงสุด

---

*Created for VNIX Order Management Project*
*Last Updated: 2026-01-05*
