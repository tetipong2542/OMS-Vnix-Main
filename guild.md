# =========================================================
# 🧭 VNIX-ERP (1 เว็บ) + 🗄️ Multi-DB (แยกตาม Department)
# =========================================================

👤 User เปิดเว็บ
  ↓
🌐 vnix-erp.com (Single Application / Single UI)
  ↓
🔐 Auth Module (Shared) ตรวจสอบตัวตน
  ↓
🗄️ Shared DB (Core)
  ├─ users
  ├─ departments
  ├─ permissions
  └─ audit_logs
  ↓
🧩 Permission Engine (RBAC)
  ├─ อ่าน role/department ของ user จาก Shared DB
  ├─ สร้าง "เมนู Sidebar แบบ Dynamic" ตามสิทธิ์
  └─ ทุก route ตรวจสิทธิ์ซ้ำ (กันเปิด URL ตรง)
  ↓
🧱 เข้าใช้งานโมดูลตามแผนก (Blueprint)
  ├─ 🛒 Online Blueprint      → Online DB
  ├─ 📦 Warehouse Blueprint   → Warehouse DB
  ├─ 💰 Sales Blueprint       → Sales DB
  ├─ 🛍️ Purchasing Blueprint  → Purchasing DB
  ├─ 💵 Accounting Blueprint  → Accounting DB
  └─ 👥 HR Blueprint          → HR DB


# =========================================================
# 🗄️ DB Mapping (แนะนำจากเอกสาร)
# =========================================================

🗄️ Shared DB (Core)
  └─ users / departments / permissions / audit_logs

🗄️ Online DB
  ├─ orders
  ├─ marketplace_prices
  ├─ shops
  └─ stock_allocation

🗄️ Warehouse DB
  ├─ inventory
  ├─ stock_movements
  ├─ picking_tasks
  └─ warehouse_locations

🗄️ Sales DB
  ├─ sales_orders
  ├─ customers
  ├─ quotations
  └─ invoices

🗄️ Purchasing DB
  ├─ purchase_orders
  ├─ suppliers
  ├─ requisitions
  └─ receiving

🗄️ Accounting DB
  ├─ gl_accounts
  ├─ journal_entries
  ├─ payments
  └─ reconciliations

🗄️ HR DB
  ├─ employees
  ├─ attendance
  ├─ payroll
  └─ leave_requests


# =========================================================
# 🔁 Core Flow: Online → Warehouse (ส่งงานให้คลังแบบปลอดภัย)
# =========================================================

🛒 Online: Import Orders (จาก Marketplace)
  ↓
✅ Order Validation & Quality Check (กันข้อมูลพังตั้งแต่ต้น)
  - missing fields / SKU ไม่ตรง master / qty ผิดปกติ / duplicate
  ↓
🧾 บันทึกลง Online DB: online.orders
  ↓
🧊 Stock Reservation (กัน overselling)
  - reserve ทันที (reserved/pending_qty)
  - available = physical - reserved
  - auto-release ถ้าไม่พิมพ์ใน X ชั่วโมง
  ↓
📣 Create Event/Message: "ORDER_ACCEPTED / READY_TO_PICK"
  ↓
📨 Message Queue (ทางเลือก) หรือ Service call ภายในระบบ
  ↓
📦 Warehouse: Consume Event
  ↓
🧩 สร้างงานหยิบ: warehouse.picking_tasks
  ↓
📲 Mobile/PWA Scan (ถ้ามี) หรือหน้า Quick Scan
  ↓
✅ ยืนยันผลหยิบ (ครบ/ขาด/ปัญหา)
  ├─ ถ้าขาด → Flag กลับ Online + note เหตุผล
  └─ ถ้าครบ → ไปขั้น Pack/Ship
  ↓
📌 Update สถานะกลับ Online (Timeline)
  - Import → Validated → Reserved → Picked → Packed → Shipped


# =========================================================
# ⚠️ จุดที่ต้อง "ล็อค/ทรานแซคชัน" (เพื่อความชัวร์)
# =========================================================

🧷 เมื่อมีการ "Accept/Reserve/ตัดสต็อก" (หลายตาราง/หลายขั้น)
  ↓
🔁 ใช้ Transaction ทุก bulk operation
  - begin_nested + rollback on error
  ↓
🔒 Stock Locking (กัน 2 คนรับพร้อมกันแล้วขายเกิน)
  - with_for_update() (pessimistic) สำหรับจุดเสี่ยงสูง


# =========================================================
# 🚀 Migration Flow (จากระบบเดิม app.py ใหญ่ → แบบ Modular)
# =========================================================

📦 Step 1: Extract Online Module
  ↓
🧱 ย้ายเข้า apps/online/ + สร้าง Blueprint
  ↓
🔐 Step 2: Shared Authentication
  ↓
🗄️ ย้าย users/login/permissions ไป Shared DB
  ↓
➕ Step 3: Add Modules ทีละตัว
  ↓
📦 Warehouse → 💰 Sales → 🛍️ Purchasing → 💵 Accounting → 👥 HR
  ↓
🔗 Step 4: Integration
  ↓
🧠 Service Layer + Event/Message เชื่อมข้ามแผนก
