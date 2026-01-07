# PRD: VNIX Order Management System - Database
## Product Requirements Document - Business & Functional Requirements

**Version:** 5.52
**Document Type:** Database Specifications (Business & Functional Requirements)
**Last Updated:** 2025-12-26
**Status:** Production

---

## 1. EXECUTIVE SUMMARY

### 1.1 Database Overview
VNIX Order Management System ใช้ SQLite Database พร้อม SQLAlchemy ORM สำหรับจัดเก็บข้อมูลคำสั่งซื้อ, สต็อก, สินค้า, ผู้ใช้, และรายงานต่างๆ Database ถูกออกแบบให้รองรับการจัดสรรสต็อกแบบ Real-time, การติดตามประวัติการพิมพ์, และการจัดการข้อมูลแบบ Multi-platform

### 1.2 Database Technology Stack
- **Database Engine:** SQLite 3
- **ORM:** SQLAlchemy 2.x
- **Migration Strategy:** Runtime ALTER TABLE (automatic)
- **Location:** Volume-mounted file (data.db) สำหรับ Railway deployment
- **Size:** ~3.2 MB (production data)
- **Backup Strategy:** File-based backup (copy data.db)

### 1.3 Business Objectives
1. **Real-time Stock Allocation:** จัดสรรสต็อกแบบ Real-time โดยไม่ Over-allocate
2. **Data Integrity:** ป้องกันข้อมูลซ้ำ, ข้อมูลผิดพลาด
3. **Audit Trail:** ติดตามประวัติการเปลี่ยนแปลงข้อมูล (Created/Updated timestamps)
4. **Scalability:** รองรับการเติบโตของข้อมูล (หลายหมื่น-หลายแสน records)
5. **Data Recovery:** ระบบ Soft Delete เพื่อกู้คืนข้อมูล
6. **Performance:** Query time < 500ms สำหรับการจัดสรรสต็อก

---

## 2. DATA MODELS & ENTITY RELATIONSHIPS

### 2.1 Entity Relationship Diagram (ERD)

```
┌─────────────┐         ┌─────────────┐
│    User     │         │    Shop     │
├─────────────┤         ├─────────────┤
│ id (PK)     │         │ id (PK)     │
│ username    │         │ platform    │
│ password    │         │ name        │
│ role        │         │ sheet_url   │
│ active      │         └─────────────┘
└─────────────┘                │
       │                       │
       │                       │
       │                       ▼
       │              ┌─────────────────┐
       │              │   OrderLine     │◄────────┐
       │              ├─────────────────┤         │
       │              │ id (PK)         │         │
       │              │ platform        │         │
       │              │ shop_id (FK)    │         │
       │              │ order_id        │         │
       │              │ sku (FK)        │         │
       │              │ qty             │         │
       │              │ item_name       │         │
       │              │ order_time      │         │
       │              │ logistic_type   │         │
       │              │ import_date     │         │
       │              │ accepted        │         │
       │              │ accepted_at     │         │
       │              │ accepted_by (FK)│─────────┘
       │              │ dispatch_round  │
       │              │ scanned_at      │
       │              │ scanned_by (FK) │
       │              │ printed_* (x5)  │
       │              │ printed_*_at    │
       └──────────────│ ...timestamps   │
                      └─────────────────┘
                               │
                               │ (sku reference)
                               ▼
                      ┌─────────────┐
                      │   Product   │
                      ├─────────────┤
                      │ id (PK)     │
                      │ sku (UK)    │
                      │ brand       │
                      │ model       │
                      └─────────────┘
                               │
                               │ (sku reference)
                               ▼
                      ┌─────────────┐
                      │    Stock    │
                      ├─────────────┤
                      │ id (PK)     │
                      │ sku (UK)    │
                      │ qty         │
                      │ updated_at  │
                      └─────────────┘

┌─────────────────┐
│     Sales       │
├─────────────────┤
│ id (PK)         │
│ order_id (UK)   │
│ po_no           │
│ status          │
└─────────────────┘

┌──────────────────┐         ┌──────────────────┐
│ CancelledOrder   │         │   IssuedOrder    │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ order_id         │         │ order_id         │
│ platform         │         │ sku              │
│ ...              │         │ platform         │
└──────────────────┘         │ source           │
                             │ issued_at        │
                             └──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  DeletedOrder    │         │   ImportLog      │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ order_id         │         │ import_type      │
│ platform         │         │ filename         │
│ deleted_at       │         │ success_count    │
│ deleted_by       │         │ duplicate_count  │
│ ...              │         │ error_count      │
└──────────────────┘         │ imported_at      │
                             │ imported_by      │
                             └──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│ SkuPrintHistory  │         │  ActionDedupe    │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ sku              │         │ token (UK)       │
│ platform         │         │ created_at       │
│ shop_id          │         └──────────────────┘
│ logistic         │
│ print_count      │
│ printed_at       │
│ printed_by       │
└──────────────────┘
```

**Legend:**
- PK = Primary Key
- FK = Foreign Key
- UK = Unique Key

---

### 2.2 Core Data Models (models.py)

#### 2.2.1 User (ผู้ใช้งาน)

**Purpose:** จัดเก็บข้อมูลผู้ใช้และสิทธิ์การเข้าถึง

**Schema:**
```python
class User(Base):
    id: Integer (Primary Key, Auto-increment)
    username: String(80) (Unique, Not Null)
    password_hash: String(255) (Not Null)
    role: String(20) (Not Null, Default: 'user')
    active: Boolean (Default: True)
```

**Business Rules:**
- **Username:** ต้องไม่ซ้ำ (Unique Constraint)
- **Password:** Hash ด้วย werkzeug.security (bcrypt)
- **Role Values:**
  - `'admin'` - Full system access
  - `'user'` - Order operations only
  - `'staff'` - Shop management access (future)
- **Active:** False = Soft delete (cannot login)

**Indexes:**
- Primary Key: `id`
- Unique Index: `username`

**Sample Data:**
```python
User(
    id=1,
    username='admin',
    password_hash='$2b$12$...',
    role='admin',
    active=True
)
```

---

#### 2.2.2 Shop (ร้านค้า)

**Purpose:** จัดเก็บข้อมูลร้านค้าแต่ละร้านในแต่ละแพลตฟอร์ม

**Schema:**
```python
class Shop(Base):
    id: Integer (Primary Key, Auto-increment)
    platform: String(50) (Not Null)
    name: String(200) (Not Null)
    google_sheet_url: Text (Nullable)

    __table_args__ = (
        UniqueConstraint('platform', 'name'),
    )
```

**Business Rules:**
- **Unique Constraint:** (platform, name) - ห้ามมีร้านชื่อเดียวกันใน platform เดียวกัน
- **Platform Values:**
  - `'Shopee'`
  - `'TikTok'`
  - `'Lazada'`
  - `'Other'`
- **Google Sheet URL:** Optional, ใช้สำหรับ Auto-import

**Indexes:**
- Primary Key: `id`
- Unique Index: `(platform, name)`

**Sample Data:**
```python
Shop(
    id=1,
    platform='Shopee',
    name='VNIX Official Store',
    google_sheet_url='https://docs.google.com/spreadsheets/d/...'
)
```

**Validation Rules:**
- Cannot delete shop if there are existing OrderLine records referencing it
- Platform must be one of: Shopee, TikTok, Lazada, Other

---

#### 2.2.3 Product (สินค้า)

**Purpose:** Product Master Data - ข้อมูลสินค้าทั้งหมด

**Schema:**
```python
class Product(Base):
    id: Integer (Primary Key, Auto-increment)
    sku: String(100) (Unique, Not Null)
    brand: String(100) (Nullable)
    model: String(200) (Nullable)
```

**Business Rules:**
- **SKU:** Stock Keeping Unit - รหัสสินค้าไม่ซ้ำ (Unique)
- **Brand:** ยี่ห้อสินค้า (Optional)
- **Model:** รุ่นสินค้า (Optional)

**Indexes:**
- Primary Key: `id`
- Unique Index: `sku`

**Sample Data:**
```python
Product(
    id=1,
    sku='ABC-123',
    brand='Samsung',
    model='Galaxy S24'
)
```

**Import Rules:**
- Upsert by SKU (Insert if not exists, Update if exists)
- Skip rows with empty SKU
- Auto-detect columns: SKU, Brand, Model (Thai/English synonyms)

---

#### 2.2.4 Stock (สต็อก)

**Purpose:** จัดเก็บข้อมูลสต็อกปัจจุบัน

**Schema:**
```python
class Stock(Base):
    id: Integer (Primary Key, Auto-increment)
    sku: String(100) (Unique, Not Null)
    qty: Integer (Not Null, Default: 0)
    updated_at: DateTime (Not Null, Default: now, onupdate: now)
```

**Business Rules:**
- **SKU:** Foreign Key reference to Product (logical, not enforced)
- **Qty:** จำนวนสต็อกคงเหลือ (≥0, ห้ามติดลบ)
- **Updated_at:** Timestamp ของการอัพเดทล่าสุด (Auto-update on change)

**Indexes:**
- Primary Key: `id`
- Unique Index: `sku`

**Sample Data:**
```python
Stock(
    id=1,
    sku='ABC-123',
    qty=50,
    updated_at=datetime(2025, 12, 26, 14, 30, 0)
)
```

**Import Rules:**
- **Full Sync Mode (Default):** SKUs not in import file → qty = 0
- **Incremental Mode (Future):** Update only SKUs in import file
- Auto-detect columns: SKU, Qty (various synonyms)

**Data Integrity:**
- Qty cannot be negative (enforced in business logic)
- After allocation, remaining stock must be ≥ 0

---

#### 2.2.5 Sales (สถานะจาก SBS)

**Purpose:** สถานะคำสั่งซื้อจากระบบ SBS (Sales Backend System)

**Schema:**
```python
class Sales(Base):
    id: Integer (Primary Key, Auto-increment)
    order_id: String(100) (Unique, Not Null)
    po_no: String(100) (Nullable)
    status: String(50) (Nullable)
```

**Business Rules:**
- **Order_id:** เลขที่คำสั่งซื้อจากระบบ SBS (Unique)
- **PO_no:** Purchase Order Number
- **Status:** สถานะจากระบบ SBS (e.g., 'Completed', 'Processing', 'Cancelled')

**Indexes:**
- Primary Key: `id`
- Unique Index: `order_id`

**Import Rules:**
- Upsert by order_id
- Auto-detect columns: Order ID, PO No, Status

**Use Case:**
- ตรวจสอบสถานะจากระบบหลังบ้าน (SBS)
- Sync status ระหว่างระบบ

---

#### 2.2.6 OrderLine (คำสั่งซื้อ - Core Entity)

**Purpose:** จัดเก็บคำสั่งซื้อทั้งหมดจากทุกแพลตฟอร์ม - หัวใจหลักของระบบ

**Schema:**
```python
class OrderLine(Base):
    # Primary Key
    id: Integer (Primary Key, Auto-increment)

    # Order Identification
    platform: String(50) (Not Null)
    shop_id: Integer (Foreign Key → Shop.id, Nullable)
    order_id: String(100) (Not Null)

    # Product Information
    sku: String(100) (Not Null, Foreign Key → Product.sku, logical)
    item_name: String(500) (Nullable)
    qty: Integer (Not Null)

    # Order Details
    order_time: DateTime (Not Null, Timezone-aware)
    logistic_type: String(100) (Nullable)

    # Import Tracking
    import_date: Date (Not Null)
    imported_at: DateTime (Not Null, Default: now)

    # Acceptance Tracking
    accepted: Boolean (Default: False)
    accepted_at: DateTime (Nullable)
    accepted_by: Integer (Foreign Key → User.id, Nullable)

    # Dispatch Management
    dispatch_round: String(50) (Nullable)

    # Scan Tracking
    scanned_at: DateTime (Nullable)
    scanned_by: Integer (Foreign Key → User.id, Nullable)

    # Print Tracking (5 types)
    printed_warehouse: Boolean (Default: False)
    printed_warehouse_at: DateTime (Nullable)

    printed_picking: Boolean (Default: False)
    printed_picking_at: DateTime (Nullable)

    printed_lowstock: Boolean (Default: False)
    printed_lowstock_at: DateTime (Nullable)

    printed_nostock: Boolean (Default: False)
    printed_nostock_at: DateTime (Nullable)

    printed_notenough: Boolean (Default: False)
    printed_notenough_at: DateTime (Nullable)
```

**Business Rules:**

**1. Order Identification:**
- **Platform:** Shopee, TikTok, Lazada, Other
- **Shop_id:** Reference to Shop table (can be NULL for old data)
- **Order_id:** Platform-specific order ID (NOT unique alone, unique with platform + shop + import_date)

**2. Product Information:**
- **SKU:** Reference to Product.sku (logical, not enforced FK)
- **Item_name:** Product name from platform (may differ from Product.model)
- **Qty:** Quantity ordered (must be > 0)

**3. Order Time:**
- **Timezone:** GMT+7 (Thailand timezone)
- **Format:** ISO 8601 with timezone info
- **Use:** FIFO sorting, SLA calculation

**4. Logistic Type:**
- **Values:** Flash, Kerry, J&T, SCG, DHL, EMS, etc.
- **Nullable:** Some platforms don't specify logistic at order time

**5. Import Tracking:**
- **Import_date:** Date of import (NOT order_time date)
- **Imported_at:** Timestamp of import action
- **Duplicate Detection:** Same (order_id, platform, shop_id, import_date) = duplicate

**6. Acceptance:**
- **Accepted:** True = Order accepted by warehouse staff
- **Accepted_at:** Timestamp of acceptance
- **Accepted_by:** User ID who accepted (for audit trail)

**7. Dispatch Round:**
- **Values:** "1", "2", "3", etc. or "Morning", "Afternoon"
- **Use:** Group orders for dispatch batching

**8. Scan Tracking:**
- **Scanned_at:** Barcode scan timestamp
- **Scanned_by:** User ID who scanned

**9. Print Tracking:**
- **5 Print Types:**
  1. `printed_warehouse` - Warehouse Job Sheet
  2. `printed_picking` - Picking List
  3. `printed_lowstock` - Low Stock Report
  4. `printed_nostock` - No Stock Report
  5. `printed_notenough` - Not Enough Stock Report
- Each has boolean flag + timestamp
- **Purpose:** Prevent accidental reprints, track printing history

**Indexes:**
- Primary Key: `id`
- Index: `platform` (for filtering)
- Index: `shop_id` (for filtering)
- Index: `sku` (for allocation)
- Index: `order_time` (for FIFO sorting)
- Index: `import_date` (for duplicate detection)
- Composite Index: `(order_id, platform, shop_id, import_date)` (for duplicate detection)

**Sample Data:**
```python
OrderLine(
    id=1001,
    platform='Shopee',
    shop_id=1,
    order_id='230526ABC123XYZ',
    sku='ABC-123',
    item_name='Samsung Galaxy S24 128GB',
    qty=2,
    order_time=datetime(2025, 12, 26, 10, 30, 0, tzinfo=timezone(timedelta(hours=7))),
    logistic_type='Flash',
    import_date=date(2025, 12, 26),
    imported_at=datetime(2025, 12, 26, 14, 0, 0),
    accepted=True,
    accepted_at=datetime(2025, 12, 26, 14, 15, 0),
    accepted_by=2,
    dispatch_round='1',
    scanned_at=datetime(2025, 12, 26, 15, 0, 0),
    scanned_by=2,
    printed_warehouse=True,
    printed_warehouse_at=datetime(2025, 12, 26, 14, 30, 0)
)
```

**Validation Rules:**
- Qty > 0
- Platform in ['Shopee', 'TikTok', 'Lazada', 'Other']
- Order_time must be timezone-aware (GMT+7)
- Cannot accept if status = SHORTAGE or NOT_ENOUGH
- Cannot print warehouse if not accepted
- Cannot delete if printed_warehouse = True (must cancel first)

---

#### 2.2.7 CancelledOrder (คำสั่งซื้อที่ยกเลิก)

**Purpose:** จัดเก็บคำสั่งซื้อที่ถูกยกเลิก (for reporting & audit)

**Schema:**
```python
class CancelledOrder(Base):
    id: Integer (Primary Key, Auto-increment)
    order_id: String(100) (Not Null)
    platform: String(50) (Not Null)
    shop_id: Integer (Nullable)
    sku: String(100) (Not Null)
    qty: Integer (Not Null)
    item_name: String(500) (Nullable)
    order_time: DateTime (Not Null)
    logistic_type: String(100) (Nullable)
    cancelled_at: DateTime (Not Null, Default: now)
    # ... other fields from OrderLine
```

**Business Rules:**
- Copy all fields from OrderLine on cancel
- OrderLine remains in table but flagged (not deleted)
- Use for reporting & statistics

---

#### 2.2.8 IssuedOrder (คำสั่งซื้อที่จัดส่งแล้ว)

**Purpose:** จัดเก็บประวัติคำสั่งซื้อที่ออกจากคลังแล้ว

**Schema:**
```python
class IssuedOrder(Base):
    id: Integer (Primary Key, Auto-increment)
    order_id: String(100) (Not Null)
    platform: String(50) (Not Null)
    shop_id: Integer (Nullable)
    sku: String(100) (Not Null)
    qty: Integer (Not Null)
    source: String(50) (Not Null)  # 'print', 'import', 'manual'
    issued_at: DateTime (Not Null, Default: now)
```

**Business Rules:**
- **Source Values:**
  - `'print'` - Created when printing Warehouse Job Sheet
  - `'import'` - Created from Import Issued Orders
  - `'manual'` - Created manually by admin
- **Purpose:** Track which orders left warehouse and when

---

#### 2.2.9 DeletedOrder (Recycle Bin)

**Purpose:** Soft Delete - เก็บคำสั่งซื้อที่ถูกลบเพื่อกู้คืนได้

**Schema:**
```python
class DeletedOrder(Base):
    id: Integer (Primary Key, Auto-increment)
    # All fields from OrderLine
    deleted_at: DateTime (Not Null, Default: now)
    deleted_by: Integer (Foreign Key → User.id, Not Null)
```

**Business Rules:**
- Move OrderLine to DeletedOrder on delete
- Delete from OrderLine
- Can restore: Move back from DeletedOrder to OrderLine
- Permanent Delete: Delete from DeletedOrder (cannot undo)

---

#### 2.2.10 ImportLog (ประวัติการ Import)

**Purpose:** จัดเก็บประวัติการ Import ข้อมูลทุกครั้ง

**Schema:**
```python
class ImportLog(Base):
    id: Integer (Primary Key, Auto-increment)
    import_type: String(50) (Not Null)  # 'products', 'stock', 'sales', 'orders', 'cancel', 'issued'
    filename: String(500) (Nullable)
    success_count: Integer (Default: 0)
    duplicate_count: Integer (Default: 0)
    error_count: Integer (Default: 0)
    imported_at: DateTime (Not Null, Default: now)
    imported_by: Integer (Foreign Key → User.id, Not Null)
```

**Business Rules:**
- **Import_type Values:**
  - `'products'` - Product Master
  - `'stock'` - Stock levels
  - `'sales'` - SBS Sales status
  - `'orders'` - Order import
  - `'cancel'` - Cancelled orders
  - `'issued'` - Issued orders
- **Counts:** Success, Duplicate, Error for reporting

**Sample Data:**
```python
ImportLog(
    id=1,
    import_type='orders',
    filename='shopee_orders_20251226.xlsx',
    success_count=150,
    duplicate_count=5,
    error_count=2,
    imported_at=datetime(2025, 12, 26, 14, 0, 0),
    imported_by=1
)
```

---

#### 2.2.11 SkuPrintHistory (ประวัติการพิมพ์ Picking List)

**Purpose:** จัดเก็บจำนวนครั้งที่พิมพ์ Picking List สำหรับแต่ละ SKU

**Schema:**
```python
class SkuPrintHistory(Base):
    id: Integer (Primary Key, Auto-increment)
    sku: String(100) (Not Null)
    platform: String(50) (Not Null)
    shop_id: Integer (Nullable)
    logistic: String(100) (Nullable)
    print_count: Integer (Default: 0)
    printed_at: DateTime (Not Null, Default: now, onupdate: now)
    printed_by: Integer (Foreign Key → User.id, Not Null)
```

**Business Rules:**
- **Composite Unique Key:** (sku, platform, shop_id, logistic)
- **Print_count:** Increment on each print
- **Printed_at:** Update on each print (last print time)
- **Use:** Track SKU-level printing (not order-level)

**Sample Data:**
```python
SkuPrintHistory(
    id=1,
    sku='ABC-123',
    platform='Shopee',
    shop_id=1,
    logistic='Flash',
    print_count=3,
    printed_at=datetime(2025, 12, 26, 15, 0, 0),
    printed_by=2
)
```

---

#### 2.2.12 ActionDedupe (Idempotency Token)

**Purpose:** ป้องกันการทำ Action ซ้ำจากการ Double-click

**Schema:**
```python
class ActionDedupe(Base):
    id: Integer (Primary Key, Auto-increment)
    token: String(200) (Unique, Not Null)
    created_at: DateTime (Not Null, Default: now)
```

**Business Rules:**
- **Token Format:** `{user_id}_{action_type}_{timestamp}`
- **Expiry:** 5 minutes (cleanup old tokens)
- **Use Cases:**
  - Bulk Accept
  - Bulk Cancel
  - Print actions
  - Import actions

**Sample Data:**
```python
ActionDedupe(
    id=1,
    token='2_bulk_accept_20251226140500',
    created_at=datetime(2025, 12, 26, 14, 5, 0)
)
```

**Cleanup:**
- Auto-delete tokens older than 5 minutes (scheduled job or on-demand)

---

## 3. BUSINESS RULES & DATA LOGIC

### 3.1 Stock Allocation Engine

**Purpose:** จัดสรรสต็อกให้กับคำสั่งซื้อตามลำดับความสำคัญ

**Algorithm (allocation.py):**

```
Input: filters (platform, shop, logistic, date_range, status)
Output: (rows, kpis)

1. Fetch all OrderLine matching filters
2. Fetch all Stock (SKU → Qty mapping)
3. Initialize virtual_stock = Stock.copy()

4. Sort orders by priority:
   - Platform Priority: Shopee(1) > TikTok(2) > Lazada(3) > Other(4)
   - Time Priority: order_time ASC (FIFO)

5. For each order in sorted_orders:
   a. Get current_stock = virtual_stock[sku]
   b. Determine status:
      - If current_stock == 0:
          status = SHORTAGE
      - Elif current_stock < order.qty:
          status = NOT_ENOUGH
      - Elif current_stock >= order.qty:
          virtual_stock[sku] -= order.qty
          If virtual_stock[sku] <= 3:
              status = LOW_STOCK
          Else:
              status = READY_ACCEPT
   c. If order.accepted == True:
      status = ACCEPTED
   d. If order.printed_warehouse == True:
      status = PACKED
   e. Append order with status to results

6. Calculate KPIs:
   - Total count
   - Count by status (READY_ACCEPT, LOW_STOCK, SHORTAGE, etc.)

7. Return (results, kpis)
```

**Status Definitions:**
- **READY_ACCEPT:** สต็อกพอ, พร้อมรับ (Stock ≥ Qty และ Stock หลังจัดสรร > 3)
- **LOW_STOCK:** สต็อกพอ แต่เหลือน้อย (Stock ≥ Qty แต่ Stock หลังจัดสรร ≤ 3)
- **SHORTAGE:** ไม่มีสต็อก (Stock = 0)
- **NOT_ENOUGH:** สต็อกมีแต่ไม่พอ (0 < Stock < Qty)
- **ACCEPTED:** รับคำสั่งซื้อแล้ว (accepted = True)
- **PACKED:** แพ็คเรียบร้อย (printed_warehouse = True)
- **CANCELLED:** ยกเลิกแล้ว (exists in CancelledOrder)

**Critical Rules:**
1. **Virtual Stock:** ใช้ Virtual Stock เพื่อไม่ให้ allocate stock ซ้ำ
2. **Priority-based:** Order ที่มี Priority สูงกว่าจะได้สต็อกก่อน
3. **Real-time:** คำนวณทุกครั้งที่โหลดหน้า Dashboard (no caching)
4. **Immutable:** Allocation ไม่เปลี่ยนแปลงข้อมูลใน Database (read-only)

**Performance:**
- Time Complexity: O(n log n) - Sort orders
- Space Complexity: O(n + m) - n orders + m SKUs
- Target: < 500ms for 10,000 orders

---

### 3.2 SLA Calculation (Business-Day Aware)

**Purpose:** คำนวณ SLA (Service Level Agreement) โดยคำนึงถึงวันทำการ

**Logic (utils.py):**

```python
def compute_sla(order_time, platform):
    """
    คำนวณ SLA display string

    Args:
        order_time: datetime (timezone-aware, GMT+7)
        platform: 'Shopee', 'TikTok', 'Lazada', 'Other'

    Returns:
        str: "วันนี้", "พรุ่งนี้", "อีก N วัน", "เลยกำหนด (N วัน)"
    """
    # 1. Get current time (GMT+7)
    now = datetime.now(thailand_tz)

    # 2. Determine cutoff time based on platform
    cutoff_times = {
        'Lazada': time(11, 0),      # 11:00 AM
        'Shopee': time(12, 0),      # 12:00 PM
        'TikTok': time(12, 0),      # 12:00 PM
        'Other': time(12, 0)        # 12:00 PM
    }
    cutoff = cutoff_times[platform]

    # 3. Calculate business days between order_time and now
    business_days = count_business_days(order_time.date(), now.date())

    # 4. Check if order is before cutoff today
    if order_time.date() == now.date():
        if order_time.time() < cutoff:
            if now.time() < cutoff:
                return "วันนี้"  # Today
            else:
                return "พรุ่งนี้"  # Tomorrow
        else:
            return "พรุ่งนี้"  # Tomorrow

    # 5. Calculate days overdue/remaining
    if business_days == 1:
        return "พรุ่งนี้"
    elif business_days > 1:
        return f"เลยกำหนด ({business_days} วัน)"  # Overdue
    else:
        days_until = count_business_days(now.date(), order_time.date() + timedelta(days=1))
        if days_until == 0:
            return "วันนี้"
        elif days_until == 1:
            return "พรุ่งนี้"
        else:
            return f"อีก {days_until} วัน"  # In N days

def count_business_days(start_date, end_date):
    """
    นับจำนวนวันทำการระหว่าง start_date และ end_date

    Excludes:
    - Weekends (Saturday, Sunday)
    - Thai public holidays (configurable list)
    """
    days = 0
    current = start_date
    while current < end_date:
        # Skip weekends
        if current.weekday() < 5:  # Mon-Fri = 0-4
            # Skip holidays
            if current not in THAI_HOLIDAYS:
                days += 1
        current += timedelta(days=1)
    return days

THAI_HOLIDAYS = [
    date(2025, 1, 1),   # New Year
    date(2025, 4, 13),  # Songkran
    date(2025, 4, 14),  # Songkran
    date(2025, 4, 15),  # Songkran
    date(2025, 5, 1),   # Labour Day
    date(2025, 12, 5),  # King's Birthday
    date(2025, 12, 10), # Constitution Day
    # ... more holidays
]
```

**Business Rules:**
- **Cutoff Times:**
  - Lazada: 11:00 AM
  - Shopee/TikTok/Others: 12:00 PM (noon)
- **Business Days:** Monday-Friday only
- **Holidays:** Exclude Thai public holidays
- **SLA Display:**
  - "วันนี้" (Today) - Green
  - "พรุ่งนี้" (Tomorrow) - Yellow
  - "อีก N วัน" (In N days) - Orange
  - "เลยกำหนด (N วัน)" (Overdue: N days) - Red

**Real-time Updates:**
- Client-side JavaScript recalculates SLA every minute
- Server-side calculation on page load
- Color-coded for quick visual identification

---

### 3.3 Duplicate Detection (Import Orders)

**Purpose:** ป้องกันการ Import คำสั่งซื้อซ้ำ

**Logic:**

```python
def detect_duplicates(new_orders, existing_orders):
    """
    ตรวจจับคำสั่งซื้อซ้ำ

    Duplicate Definition:
    - Same order_id
    - Same platform
    - Same shop_id
    - Same import_date (same day)

    Returns:
        (unique_orders, duplicate_orders)
    """
    duplicate_key = lambda o: (
        o['order_id'],
        o['platform'],
        o['shop_id'],
        o['import_date']
    )

    existing_keys = {duplicate_key(o) for o in existing_orders}

    unique_orders = []
    duplicate_orders = []

    for order in new_orders:
        key = duplicate_key(order)
        if key in existing_keys:
            duplicate_orders.append(order)
        else:
            unique_orders.append(order)
            existing_keys.add(key)

    return unique_orders, duplicate_orders
```

**Business Rules:**
- **Same-day Detection:** Only detect duplicates within same import_date
- **Cross-day Allowed:** Same order_id on different days = NOT duplicate (e.g., re-import next day)
- **INSERT-ONLY:** Never update existing orders (preserve original data)
- **Reporting:** Show duplicate_count in ImportLog

---

### 3.4 Print Tracking & Idempotency

**Purpose:** ป้องกันการพิมพ์ซ้ำและติดตามประวัติการพิมพ์

**Logic:**

```python
def print_warehouse_job_sheet(order_ids, dispatch_round, user_id):
    """
    พิมพ์เอกสารคลังสินค้า

    Side Effects:
    1. Mark orders as printed_warehouse = True
    2. Set printed_warehouse_at = now
    3. Create IssuedOrder records
    4. Change status to PACKED
    5. Create ActionDedupe token
    """
    # 1. Check idempotency
    token = f"{user_id}_print_warehouse_{int(time.time())}"
    if ActionDedupe.exists(token):
        return {"error": "Duplicate action detected"}

    # 2. Create dedup token
    ActionDedupe.create(token=token)

    # 3. Update orders
    for order_id in order_ids:
        order = OrderLine.get(id=order_id)
        if not order.printed_warehouse:  # Prevent double-print
            order.printed_warehouse = True
            order.printed_warehouse_at = datetime.now()
            order.dispatch_round = dispatch_round

            # 4. Create IssuedOrder
            IssuedOrder.create(
                order_id=order.order_id,
                platform=order.platform,
                shop_id=order.shop_id,
                sku=order.sku,
                qty=order.qty,
                source='print',
                issued_at=datetime.now()
            )

    # 5. Generate Excel file
    excel_file = generate_excel(orders)

    return {"success": True, "count": len(order_ids), "file": excel_file}
```

**Idempotency Rules:**
- **Token Lifetime:** 5 minutes
- **Token Format:** `{user_id}_{action}_{timestamp}`
- **Cleanup:** Auto-delete expired tokens (older than 5 minutes)
- **Purpose:** Prevent accidental double-clicks, network retries

---

### 3.5 Soft Delete & Restore

**Purpose:** ลบคำสั่งซื้อแบบ Soft Delete เพื่อกู้คืนได้

**Logic:**

```python
def soft_delete_orders(order_ids, user_id):
    """
    Soft Delete orders to DeletedOrder table
    """
    for order_id in order_ids:
        order = OrderLine.get(id=order_id)

        # 1. Copy to DeletedOrder
        DeletedOrder.create(
            **order.to_dict(),
            deleted_at=datetime.now(),
            deleted_by=user_id
        )

        # 2. Delete from OrderLine
        order.delete()

def restore_orders(deleted_order_ids):
    """
    Restore orders from DeletedOrder back to OrderLine
    """
    for deleted_id in deleted_order_ids:
        deleted_order = DeletedOrder.get(id=deleted_id)

        # 1. Copy back to OrderLine
        OrderLine.create(**deleted_order.to_dict_without_deleted_fields())

        # 2. Delete from DeletedOrder
        deleted_order.delete()

def permanent_delete_orders(deleted_order_ids):
    """
    Permanently delete orders (cannot undo)
    """
    for deleted_id in deleted_order_ids:
        DeletedOrder.get(id=deleted_id).delete()
```

**Business Rules:**
- **Cannot Delete PACKED Orders:** Must cancel first before delete
- **Restore:** Moves data back to OrderLine with original fields
- **Permanent Delete:** Irreversible, requires confirmation modal
- **Audit Trail:** deleted_at, deleted_by tracked in DeletedOrder

---

## 4. DATA FLOWS & PROCESSES

### 4.1 Order Import Flow

```
[User uploads Excel/CSV/Google Sheets]
        ↓
[Server reads file via pandas/gspread]
        ↓
[Auto-detect columns (SKU, Qty, Order ID, etc.)]
        ↓
[Parse rows into OrderLine objects]
        ↓
[Duplicate Detection: Check existing orders with same (order_id, platform, shop_id, import_date)]
        ↓
[Filter: unique_orders, duplicate_orders]
        ↓
[Batch Insert unique_orders into OrderLine table (INSERT-ONLY)]
        ↓
[Create ImportLog record (success_count, duplicate_count, error_count)]
        ↓
[Return summary to user]
        ↓
[Display Flash Message: "นำเข้าสำเร็จ X รายการ, ซ้ำ Y รายการ"]
```

**Data Transformations:**
- **Column Detection:** Auto-detect Thai/English synonyms
  - Order ID: "เลขที่คำสั่งซื้อ", "Order ID", "Order No"
  - SKU: "รหัสสินค้า", "SKU", "Product Code"
  - Qty: "จำนวน", "Quantity", "Qty"
- **Date Parsing:** Auto-detect date formats (DD/MM/YYYY, YYYY-MM-DD, etc.)
- **Timezone Conversion:** Convert to GMT+7 for order_time
- **Data Cleaning:** Strip whitespace, normalize case for Platform names

**Error Handling:**
- Missing required columns → Show error, suggest column names
- Invalid date format → Skip row, log error
- Missing SKU → Skip row, increment error_count
- Database constraint violation → Rollback transaction, show error

---

### 4.2 Stock Allocation Flow (Real-time)

```
[User opens Dashboard with filters]
        ↓
[Server: Fetch OrderLine matching filters (platform, shop, logistic, date_range)]
        ↓
[Server: Fetch all Stock (sku → qty mapping)]
        ↓
[Server: Call compute_allocation(orders, stock)]
        ↓
[Allocation Engine:
    1. Sort orders by Platform Priority + FIFO
    2. Initialize virtual_stock = stock.copy()
    3. For each order:
       - Check virtual_stock[sku]
       - Assign status (READY_ACCEPT, LOW_STOCK, SHORTAGE, NOT_ENOUGH)
       - Deduct from virtual_stock if allocatable
    4. Calculate KPIs by status
]
        ↓
[Server: Render Dashboard with orders + KPI cards]
        ↓
[Client: Display table with color-coded rows]
```

**Performance Optimizations:**
- **Batch Fetch:** Fetch all orders + stock in 2 queries (not N+1)
- **In-memory Calculation:** Allocation logic runs in Python (no database writes)
- **Pagination:** DataTables client-side pagination (no server-side pagination needed)
- **Caching:** No caching (always real-time, but consider Redis for future)

---

### 4.3 Accept Order Flow

```
[User clicks "รับออเดอร์" or "Bulk Accept"]
        ↓
[Client: Collect selected order IDs]
        ↓
[Client: Send POST request to /bulk_accept]
        ↓
[Server: Create idempotency token]
        ↓
[Server: Check ActionDedupe table for token]
        ↓
[If duplicate token: Return error "Action already processed"]
        ↓
[Else:
    1. Insert token into ActionDedupe
    2. For each order_id:
       - Fetch OrderLine
       - Check if status allows acceptance (READY_ACCEPT or LOW_STOCK)
       - Set accepted = True
       - Set accepted_at = now()
       - Set accepted_by = current_user.id
       - Save to database
    3. Commit transaction
]
        ↓
[Server: Return success response with count]
        ↓
[Client: Show Flash Message "รับออเดอร์สำเร็จ X รายการ"]
        ↓
[Client: Refresh Dashboard (reload page or AJAX update KPIs)]
```

**Business Rules:**
- Only READY_ACCEPT and LOW_STOCK orders can be accepted
- Cannot accept SHORTAGE or NOT_ENOUGH (no stock)
- Cannot accept ACCEPTED again (already accepted)
- Cannot accept PACKED (already issued)

---

### 4.4 Print Warehouse Job Sheet Flow

```
[User navigates to /report/warehouse]
        ↓
[Server: Fetch ACCEPTED orders (accepted = True, printed_warehouse = False)]
        ↓
[Client: Display table with filters]
        ↓
[User: Applies filters (platform, shop, logistic, dispatch_round)]
        ↓
[User: Clicks "พิมพ์เอกสาร"]
        ↓
[Server:
    1. Create idempotency token
    2. Check ActionDedupe
    3. Filter orders (only ACCEPTED, not yet printed)
    4. Update each order:
       - printed_warehouse = True
       - printed_warehouse_at = now()
       - dispatch_round = input_value
    5. Create IssuedOrder records (source = 'print')
    6. Generate Excel file with Thai headers
    7. Commit transaction
]
        ↓
[Server: Send Excel file as download]
        ↓
[Client: Browser downloads file]
        ↓
[User: Prints Excel file physically]
```

**Excel Export Format:**
- **Headers (Thai):**
  - เลขที่คำสั่งซื้อ (Order ID)
  - รหัสสินค้า (SKU)
  - ชื่อสินค้า (Item Name)
  - จำนวน (Qty)
  - แพลตฟอร์ม (Platform)
  - ร้านค้า (Shop)
  - ขนส่ง (Logistic)
  - เวลาสั่งซื้อ (Order Time)
  - รอบจัดส่ง (Dispatch Round)
- **Formatting:**
  - Date: DD/MM/YYYY HH:MM (Buddhist Year)
  - Numbers: No decimals
  - Text: UTF-8 encoding (Thai support)

---

### 4.5 Low Stock Report Flow

```
[User navigates to /report/lowstock]
        ↓
[Server:
    1. Fetch all OrderLine
    2. Run allocation engine
    3. Filter results where status = LOW_STOCK
    4. Group by SKU
    5. Aggregate:
       - Total Qty per SKU
       - Current Stock
       - Remaining Stock (after allocation)
       - Order IDs (comma-separated)
]
        ↓
[Client: Display table with SKU groups]
        ↓
[User: Selects SKUs to print, enters dispatch_round]
        ↓
[User: Clicks "พิมพ์รายการที่เลือก"]
        ↓
[Server:
    1. Validate: dispatch_round required
    2. Validate: At least 1 order selected
    3. Update selected orders:
       - printed_lowstock = True
       - printed_lowstock_at = now()
       - dispatch_round = input_value
    4. Generate Excel report
]
        ↓
[Server: Send Excel file]
        ↓
[User: Downloads and prints report]
```

**Report Columns:**
- SKU
- Item Name (first occurrence)
- Current Stock
- Allocated Qty
- Remaining Stock (≤3)
- Order Count
- Order IDs (list)

---

## 5. DATA INTEGRITY & VALIDATION RULES

### 5.1 Database Constraints

**Table: User**
- ✓ username UNIQUE
- ✓ username NOT NULL
- ✓ password_hash NOT NULL
- ✓ role IN ('admin', 'user', 'staff')
- ✓ active BOOLEAN DEFAULT True

**Table: Shop**
- ✓ UNIQUE (platform, name)
- ✓ platform NOT NULL
- ✓ name NOT NULL
- ✓ platform IN ('Shopee', 'TikTok', 'Lazada', 'Other')

**Table: Product**
- ✓ sku UNIQUE
- ✓ sku NOT NULL

**Table: Stock**
- ✓ sku UNIQUE
- ✓ sku NOT NULL
- ✓ qty >= 0 (enforced in business logic)
- ✓ updated_at NOT NULL

**Table: OrderLine**
- ✓ platform NOT NULL
- ✓ order_id NOT NULL
- ✓ sku NOT NULL
- ✓ qty > 0 (enforced in business logic)
- ✓ order_time NOT NULL, timezone-aware
- ✓ import_date NOT NULL
- ✓ imported_at NOT NULL
- ✓ UNIQUE (order_id, platform, shop_id, import_date) (enforced via duplicate detection)

**Table: ImportLog**
- ✓ import_type NOT NULL
- ✓ imported_at NOT NULL
- ✓ imported_by NOT NULL

**Table: ActionDedupe**
- ✓ token UNIQUE
- ✓ token NOT NULL
- ✓ created_at NOT NULL

---

### 5.2 Business Logic Validations

**Order Import:**
```python
def validate_order_row(row):
    errors = []

    # Required fields
    if not row.get('order_id'):
        errors.append("Missing order_id")
    if not row.get('sku'):
        errors.append("Missing SKU")
    if not row.get('qty') or row['qty'] <= 0:
        errors.append("Qty must be > 0")
    if not row.get('order_time'):
        errors.append("Missing order_time")

    # Platform validation
    if row.get('platform') not in ['Shopee', 'TikTok', 'Lazada', 'Other']:
        errors.append(f"Invalid platform: {row.get('platform')}")

    # Date validation
    try:
        parse_datetime(row.get('order_time'))
    except:
        errors.append("Invalid order_time format")

    return errors
```

**Accept Order:**
```python
def validate_accept(order):
    # Check status
    status = compute_order_status(order)
    if status not in ['READY_ACCEPT', 'LOW_STOCK']:
        return False, f"Cannot accept order with status {status}"

    # Check if already accepted
    if order.accepted:
        return False, "Order already accepted"

    # Check if already packed
    if order.printed_warehouse:
        return False, "Order already packed"

    return True, None
```

**Print Validation:**
```python
def validate_print_warehouse(orders, dispatch_round):
    errors = []

    # Dispatch round required
    if not dispatch_round:
        errors.append("Dispatch round is required")

    # All orders must be accepted
    for order in orders:
        if not order.accepted:
            errors.append(f"Order {order.order_id} not accepted")
        if order.printed_warehouse:
            errors.append(f"Order {order.order_id} already printed")

    return errors
```

---

### 5.3 Data Type Validations

**DateTime Fields:**
- Must be timezone-aware (GMT+7)
- Format: ISO 8601 with timezone info
- Example: `2025-12-26T14:30:00+07:00`

**Integer Fields:**
- qty: Must be > 0
- stock.qty: Must be >= 0
- print_count: Must be >= 0

**String Fields:**
- Max lengths enforced (see schema)
- No leading/trailing whitespace (strip on input)
- Platform names: Normalize case (e.g., "shopee" → "Shopee")

**Boolean Fields:**
- Default values specified in schema
- Never NULL (except where explicitly allowed)

---

## 6. DATA IMPORT/EXPORT SPECIFICATIONS

### 6.1 Import File Formats

**Supported Formats:**
1. Excel (.xlsx, .xls)
2. CSV (.csv)
3. Google Sheets (via URL)

**Column Detection:**

**Products Import:**
```python
COLUMN_SYNONYMS = {
    'sku': ['sku', 'รหัสสินค้า', 'product code', 'item code'],
    'brand': ['brand', 'ยี่ห้อ', 'แบรนด์'],
    'model': ['model', 'รุ่น', 'product name', 'ชื่อสินค้า']
}
```

**Stock Import:**
```python
COLUMN_SYNONYMS = {
    'sku': ['sku', 'รหัสสินค้า', 'product code'],
    'qty': ['qty', 'quantity', 'จำนวน', 'stock', 'คงเหลือ']
}
```

**Orders Import:**
```python
COLUMN_SYNONYMS = {
    'order_id': ['order id', 'order no', 'เลขที่คำสั่งซื้อ', 'order number'],
    'sku': ['sku', 'รหัสสินค้า', 'product code'],
    'qty': ['qty', 'quantity', 'จำนวน'],
    'order_time': ['order time', 'order date', 'เวลาสั่งซื้อ', 'วันที่สั่ง'],
    'logistic': ['logistic', 'courier', 'ขนส่ง', 'shipping method'],
    'item_name': ['item name', 'product name', 'ชื่อสินค้า']
}
```

**Auto-detection Logic:**
1. Read first row as header
2. Normalize: lowercase, strip whitespace
3. Match against synonym dictionaries (fuzzy matching)
4. If no match: Show error with suggested column names

---

### 6.2 Export File Formats

**Excel Export (.xlsx):**

**Format:**
- Library: XlsxWriter
- Encoding: UTF-8 (Thai support)
- Sheet Name: Thai (e.g., "รายงานคลังสินค้า")
- Headers: Thai column names
- Date Format: DD/MM/YYYY (Buddhist Year)
- Number Format: No decimals (integer qty)

**Example Export (Warehouse Job Sheet):**
```
| เลขที่คำสั่งซื้อ | รหัสสินค้า | ชื่อสินค้า | จำนวน | แพลตฟอร์ม | ร้านค้า | ขนส่ง | เวลาสั่งซื้อ | รอบจัดส่ง |
|-----------------|-----------|----------|------|----------|--------|------|------------|----------|
| 230526ABC123    | ABC-123   | Samsung  | 2    | Shopee   | VNIX   | Flash| 26/12/2568 | 1        |
```

**Excel Styling:**
- Header Row: Bold, Background Color (#4472C4), White Text
- Freeze Panes: First row (header)
- Column Width: Auto-fit
- Row Height: Default (15px)

---

### 6.3 Google Sheets Integration

**Authentication:**
- Method: OAuth2 Service Account
- Library: gspread, oauth2client
- Credentials: JSON file (environment variable)

**Configuration:**
```python
# Environment Variables
GOOGLE_CREDENTIALS_JSON = '{"type": "service_account", ...}'

# Or individual fields
GOOGLE_TYPE = 'service_account'
GOOGLE_PROJECT_ID = 'vnix-oms'
GOOGLE_PRIVATE_KEY_ID = '...'
GOOGLE_PRIVATE_KEY = '...'
GOOGLE_CLIENT_EMAIL = '...@vnix-oms.iam.gserviceaccount.com'
GOOGLE_CLIENT_ID = '...'
```

**Import Process:**
```python
def import_from_google_sheets(sheet_url):
    # 1. Authenticate
    credentials = get_google_credentials()
    client = gspread.authorize(credentials)

    # 2. Open sheet
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)  # First sheet

    # 3. Get all records
    records = worksheet.get_all_records()

    # 4. Convert to pandas DataFrame
    df = pd.DataFrame(records)

    # 5. Process same as Excel import
    return process_import(df)
```

**Error Handling:**
- Invalid URL → Show error
- No access permission → Show error with instructions to share sheet
- Empty sheet → Show warning
- Network error → Retry 3 times, then fail

---

## 7. DATABASE MIGRATIONS & VERSIONING

### 7.1 Migration Strategy

**Current Approach: Runtime ALTER TABLE**

```python
# In app.py - runs on every startup
def init_db():
    # 1. Create tables if not exist
    Base.metadata.create_all(engine)

    # 2. Add new columns if missing (ALTER TABLE)
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text(
            "PRAGMA table_info(orderline)"
        )).fetchall()

        existing_columns = {row[1] for row in result}

        # Add printed_lowstock if missing
        if 'printed_lowstock' not in existing_columns:
            conn.execute(text(
                "ALTER TABLE orderline ADD COLUMN printed_lowstock BOOLEAN DEFAULT 0"
            ))
            conn.execute(text(
                "ALTER TABLE orderline ADD COLUMN printed_lowstock_at DATETIME"
            ))

        # Add more columns as needed
        # ...

    # 3. Create indexes if missing
    # ...
```

**Advantages:**
- Simple, no migration files needed
- Auto-upgrades on deployment
- Works with SQLite (limited ALTER TABLE support)

**Disadvantages:**
- No rollback capability
- No migration history
- Cannot rename/drop columns easily (SQLite limitation)

**Future Recommendation:**
- Migrate to Alembic for production
- Version-controlled migration files
- Rollback support
- Better for PostgreSQL (if upgrading from SQLite)

---

### 7.2 Database Versioning

**Current Version Tracking:**

```python
# Manual version tracking in code
DATABASE_VERSION = '5.52'

# Check on startup
def check_db_version():
    # Create version table if not exists
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS db_version (
                version TEXT PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Get current version
        result = conn.execute(text(
            "SELECT version FROM db_version ORDER BY applied_at DESC LIMIT 1"
        )).fetchone()

        if not result:
            # First run, insert current version
            conn.execute(text(
                f"INSERT INTO db_version (version) VALUES ('{DATABASE_VERSION}')"
            ))
        elif result[0] != DATABASE_VERSION:
            # Version mismatch, run migrations
            run_migrations(result[0], DATABASE_VERSION)
            conn.execute(text(
                f"INSERT INTO db_version (version) VALUES ('{DATABASE_VERSION}')"
            ))
```

---

### 7.3 Schema Evolution History

**Version 5.52 Changes:**
1. ✅ Added `printed_lowstock` + `printed_lowstock_at` to OrderLine
2. ✅ Added `printed_nostock` + `printed_nostock_at` to OrderLine
3. ✅ Added `printed_notenough` + `printed_notenough_at` to OrderLine
4. ✅ Added `dispatch_round` to OrderLine (for all print types)
5. ✅ Created `SkuPrintHistory` table
6. ✅ Created `ActionDedupe` table

**Version 5.51 (Previous):**
- Added `printed_picking` + `printed_picking_at`
- Added `scanned_at` + `scanned_by`

**Version 5.50 (Previous):**
- Added `printed_warehouse` + `printed_warehouse_at`
- Created `IssuedOrder` table

---

## 8. PERFORMANCE & OPTIMIZATION

### 8.1 Query Optimization

**Dashboard Query (Most Critical):**

```python
# BEFORE (N+1 queries)
orders = session.query(OrderLine).filter(...).all()
for order in orders:
    stock = session.query(Stock).filter_by(sku=order.sku).first()
    # Process...

# AFTER (2 queries total)
orders = session.query(OrderLine).filter(...).all()
stock_map = {s.sku: s.qty for s in session.query(Stock).all()}
for order in orders:
    stock_qty = stock_map.get(order.sku, 0)
    # Process...
```

**Performance Gain:** 10,000 orders = 10,001 queries → 2 queries (99.98% reduction)

---

**Index Optimization:**

```python
# Critical indexes for Dashboard
CREATE INDEX idx_orderline_platform ON orderline(platform);
CREATE INDEX idx_orderline_shop_id ON orderline(shop_id);
CREATE INDEX idx_orderline_sku ON orderline(sku);
CREATE INDEX idx_orderline_order_time ON orderline(order_time);
CREATE INDEX idx_orderline_import_date ON orderline(import_date);
CREATE INDEX idx_orderline_accepted ON orderline(accepted);

# Composite index for duplicate detection
CREATE UNIQUE INDEX idx_orderline_unique
ON orderline(order_id, platform, shop_id, import_date);

# Index for Stock lookups
CREATE UNIQUE INDEX idx_stock_sku ON stock(sku);
```

**Query Plan Analysis:**
```sql
EXPLAIN QUERY PLAN
SELECT * FROM orderline
WHERE platform = 'Shopee'
  AND import_date = '2025-12-26'
  AND accepted = 0
ORDER BY order_time ASC;

-- Expected: Index scan on idx_orderline_platform + idx_orderline_import_date
```

---

### 8.2 Data Volume Projections

**Current Production Data:**
- OrderLine: ~50,000 rows (3 months)
- Stock: ~2,000 rows
- Product: ~2,000 rows
- ImportLog: ~500 rows
- Database Size: ~3.2 MB

**6-Month Projection:**
- OrderLine: ~100,000 rows
- Database Size: ~6-7 MB

**1-Year Projection:**
- OrderLine: ~200,000 rows
- Database Size: ~12-15 MB

**Performance Targets:**
- Dashboard load: < 2 seconds (up to 100,000 orders)
- Allocation calculation: < 500ms (10,000 orders)
- Import: < 5 seconds (1,000 rows)
- Export: < 5 seconds (1,000 rows)

**Optimization Strategies:**
1. **Pagination:** Implement server-side pagination for large datasets
2. **Archiving:** Move old orders (>6 months) to archive table
3. **Partitioning:** Partition OrderLine by import_date (if migrating to PostgreSQL)
4. **Caching:** Cache stock data (Redis) for faster allocation
5. **Background Jobs:** Async import/export via Celery (future)

---

### 8.3 Database Backup & Recovery

**Backup Strategy:**

**Daily Backup (Automated):**
```bash
# Cron job (every day at 2 AM)
0 2 * * * cp /path/to/data.db /path/to/backups/data_$(date +\%Y\%m\%d).db

# Keep last 30 days
0 3 * * * find /path/to/backups -name "data_*.db" -mtime +30 -delete
```

**Before Deployment Backup:**
```bash
# Manual backup before Railway deployment
cp data.db data_backup_$(date +\%Y\%m\%d_\%H\%M\%S).db
```

**Restore Procedure:**
```bash
# 1. Stop application
# 2. Replace data.db with backup
cp /path/to/backups/data_20251226.db /path/to/data.db
# 3. Restart application
```

**Railway Volume Backup:**
- Volume snapshots via Railway dashboard
- Download volume to local machine
- Upload to cloud storage (S3, Google Drive)

---

## 9. DATA RETENTION & ARCHIVAL

### 9.1 Retention Policy

**Active Data (OrderLine):**
- **Retention:** 6 months (current + previous 5 months)
- **Purpose:** Active order management, reporting

**Archived Data (OrderLine_Archive):**
- **Retention:** 2 years (older than 6 months, newer than 2 years)
- **Purpose:** Historical reporting, audit compliance

**Purged Data:**
- **Retention:** None (deleted after 2 years)
- **Backup:** Final backup before purge (kept offline for 5 years)

---

### 9.2 Archival Process (Future)

**Archival Table Schema:**
```python
class OrderLineArchive(Base):
    # Same schema as OrderLine
    # Additional field:
    archived_at: DateTime (Not Null, Default: now)
```

**Archival Procedure:**
```python
def archive_old_orders():
    """
    Archive orders older than 6 months
    Run monthly via cron job
    """
    cutoff_date = date.today() - timedelta(days=180)  # 6 months

    # 1. Copy to archive
    old_orders = session.query(OrderLine).filter(
        OrderLine.import_date < cutoff_date
    ).all()

    for order in old_orders:
        OrderLineArchive.create(
            **order.to_dict(),
            archived_at=datetime.now()
        )

    # 2. Delete from active table
    session.query(OrderLine).filter(
        OrderLine.import_date < cutoff_date
    ).delete()

    session.commit()

    print(f"Archived {len(old_orders)} orders")
```

**Benefits:**
- Keeps active table small (faster queries)
- Preserves historical data
- Compliance with data retention policies

---

## 10. SECURITY & ACCESS CONTROL

### 10.1 Authentication

**Password Storage:**
- **Hashing:** werkzeug.security (bcrypt algorithm)
- **Salt:** Automatically generated per password
- **Rounds:** 12 (bcrypt default)
- **Never Store:** Plaintext passwords (NEVER!)

**Password Hash Example:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# On user creation
password_hash = generate_password_hash('my_password')
# Result: '$2b$12$...' (60 characters)

# On login
is_valid = check_password_hash(user.password_hash, input_password)
```

---

### 10.2 Session Management

**Session Configuration:**
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only (production)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

**Session Data:**
- user_id (integer)
- username (string)
- role (string)
- login_time (timestamp)

**Session Expiry:**
- 24 hours (automatic logout after inactivity)
- Manual logout: Clear session

---

### 10.3 Role-Based Access Control (RBAC)

**Roles:**
1. **Admin:**
   - Full access to all features
   - User management
   - Shop management
   - System status
   - Import data
   - All reports

2. **User:**
   - Dashboard (view orders)
   - Accept/Cancel orders
   - Print reports
   - Scan barcodes
   - **No access to:** User/Shop management

**Access Control Decorator:**
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Usage
@app.route('/admin/users')
@admin_required
def admin_users():
    # ...
```

---

### 10.4 SQL Injection Prevention

**Always Use Parameterized Queries:**

```python
# BAD (Vulnerable to SQL injection)
query = f"SELECT * FROM orderline WHERE order_id = '{user_input}'"
result = session.execute(text(query))

# GOOD (Safe)
query = text("SELECT * FROM orderline WHERE order_id = :order_id")
result = session.execute(query, {"order_id": user_input})

# BEST (SQLAlchemy ORM)
result = session.query(OrderLine).filter_by(order_id=user_input).all()
```

**No String Interpolation:**
- Never use f-strings or .format() for SQL queries
- Always use SQLAlchemy ORM or parameterized text() queries

---

### 10.5 Audit Trail

**Tracked Actions:**

**User Actions:**
- Login/Logout (session logs)
- Accept Order (accepted_at, accepted_by)
- Scan Order (scanned_at, scanned_by)
- Print Reports (printed_*_at)
- Import Data (imported_at, imported_by in ImportLog)
- Delete Order (deleted_at, deleted_by in DeletedOrder)

**System Events:**
- Database migrations (db_version table)
- Errors (application logs)

**Audit Query Examples:**
```python
# Who accepted order X?
order = OrderLine.get(order_id='...')
print(f"Accepted by {order.accepted_by} at {order.accepted_at}")

# Who imported data on date X?
logs = ImportLog.filter(
    ImportLog.imported_at >= start_date,
    ImportLog.imported_at < end_date
).all()

# Who deleted orders?
deleted = DeletedOrder.all()
for d in deleted:
    print(f"Deleted by {d.deleted_by} at {d.deleted_at}")
```

---

## 11. DATA QUALITY & MONITORING

### 11.1 Data Quality Checks

**Daily Checks (Automated):**

```python
def run_data_quality_checks():
    issues = []

    # 1. Orphan Orders (SKU not in Product table)
    orphan_orders = session.query(OrderLine).filter(
        ~OrderLine.sku.in_(session.query(Product.sku))
    ).count()
    if orphan_orders > 0:
        issues.append(f"{orphan_orders} orders with unknown SKUs")

    # 2. Negative Stock
    negative_stock = session.query(Stock).filter(Stock.qty < 0).count()
    if negative_stock > 0:
        issues.append(f"{negative_stock} SKUs with negative stock")

    # 3. Missing Order Times
    missing_times = session.query(OrderLine).filter(
        OrderLine.order_time.is_(None)
    ).count()
    if missing_times > 0:
        issues.append(f"{missing_times} orders with missing order_time")

    # 4. Duplicate Orders (same order_id, platform, shop, date)
    duplicates = session.query(
        OrderLine.order_id,
        OrderLine.platform,
        OrderLine.shop_id,
        OrderLine.import_date
    ).group_by(
        OrderLine.order_id,
        OrderLine.platform,
        OrderLine.shop_id,
        OrderLine.import_date
    ).having(func.count() > 1).count()
    if duplicates > 0:
        issues.append(f"{duplicates} duplicate orders found")

    # 5. Accepted but not printed (older than 1 day)
    stale_accepted = session.query(OrderLine).filter(
        OrderLine.accepted == True,
        OrderLine.printed_warehouse == False,
        OrderLine.accepted_at < datetime.now() - timedelta(days=1)
    ).count()
    if stale_accepted > 0:
        issues.append(f"{stale_accepted} orders accepted but not printed for >1 day")

    if issues:
        send_alert_email(issues)

    return issues
```

---

### 11.2 Monitoring Metrics

**Key Metrics to Track:**

1. **Order Volume:**
   - Orders imported per day
   - Orders accepted per day
   - Orders packed per day

2. **Stock Health:**
   - SKUs with 0 stock
   - SKUs with low stock (≤3)
   - Total stock value (if price data available)

3. **Performance:**
   - Dashboard load time
   - Allocation calculation time
   - Import/Export time

4. **Data Quality:**
   - Orphan orders count
   - Duplicate orders count
   - Missing data count (NULL fields)

5. **User Activity:**
   - Logins per day
   - Actions per user
   - Import frequency

**Dashboard (Future):**
- Grafana + Prometheus for real-time monitoring
- Alert rules for anomalies (e.g., stock suddenly drops to 0)

---

## 12. APPENDIX

### 12.1 Database Schema Diagram (Visual)

See ERD in Section 2.1

---

### 12.2 Sample SQL Queries

**Get all READY_ACCEPT orders:**
```sql
-- Note: Status is computed in Python, not stored in DB
-- This query fetches orders that could be READY_ACCEPT
SELECT o.*, s.qty AS stock_qty
FROM orderline o
LEFT JOIN stock s ON o.sku = s.sku
WHERE o.accepted = 0
  AND s.qty > 0
ORDER BY
  CASE o.platform
    WHEN 'Shopee' THEN 1
    WHEN 'TikTok' THEN 2
    WHEN 'Lazada' THEN 3
    ELSE 4
  END,
  o.order_time ASC;
```

**Get Low Stock SKUs:**
```sql
-- Requires allocation engine (Python), no direct SQL
-- Simplified version (not accurate):
SELECT sku, qty
FROM stock
WHERE qty <= 3;
```

**Get Import History:**
```sql
SELECT
  import_type,
  filename,
  success_count,
  duplicate_count,
  error_count,
  imported_at,
  (SELECT username FROM user WHERE id = imported_by) AS imported_by_name
FROM importlog
ORDER BY imported_at DESC
LIMIT 50;
```

**Get Top 10 Most Ordered SKUs:**
```sql
SELECT
  sku,
  SUM(qty) AS total_qty,
  COUNT(*) AS order_count
FROM orderline
WHERE import_date >= DATE('now', '-30 days')
GROUP BY sku
ORDER BY total_qty DESC
LIMIT 10;
```

---

### 12.3 Data Dictionary

| Table | Column | Type | Description | Example |
|-------|--------|------|-------------|---------|
| User | id | Integer | รหัสผู้ใช้ (PK) | 1 |
| User | username | String(80) | ชื่อผู้ใช้ | admin |
| User | password_hash | String(255) | รหัสผ่านที่ Hash แล้ว | $2b$12$... |
| User | role | String(20) | บทบาท (admin/user) | admin |
| User | active | Boolean | สถานะใช้งาน | True |
| Shop | id | Integer | รหัสร้านค้า (PK) | 1 |
| Shop | platform | String(50) | แพลตฟอร์ม | Shopee |
| Shop | name | String(200) | ชื่อร้าน | VNIX Official |
| Shop | google_sheet_url | Text | URL ของ Google Sheet | https://... |
| Product | id | Integer | รหัสสินค้า (PK) | 1 |
| Product | sku | String(100) | รหัส SKU (Unique) | ABC-123 |
| Product | brand | String(100) | ยี่ห้อ | Samsung |
| Product | model | String(200) | รุ่น | Galaxy S24 |
| Stock | id | Integer | รหัสสต็อก (PK) | 1 |
| Stock | sku | String(100) | รหัส SKU | ABC-123 |
| Stock | qty | Integer | จำนวนคงเหลือ | 50 |
| Stock | updated_at | DateTime | เวลาอัพเดทล่าสุด | 2025-12-26 14:30:00 |
| OrderLine | id | Integer | รหัสคำสั่งซื้อ (PK) | 1001 |
| OrderLine | platform | String(50) | แพลตฟอร์ม | Shopee |
| OrderLine | shop_id | Integer | รหัสร้าน (FK) | 1 |
| OrderLine | order_id | String(100) | เลขที่คำสั่งซื้อ | 230526ABC123 |
| OrderLine | sku | String(100) | รหัส SKU | ABC-123 |
| OrderLine | qty | Integer | จำนวน | 2 |
| OrderLine | item_name | String(500) | ชื่อสินค้า | Samsung Galaxy S24 |
| OrderLine | order_time | DateTime | เวลาสั่งซื้อ | 2025-12-26 10:30:00+07:00 |
| OrderLine | logistic_type | String(100) | ขนส่ง | Flash |
| OrderLine | import_date | Date | วันที่นำเข้า | 2025-12-26 |
| OrderLine | accepted | Boolean | สถานะรับออเดอร์ | True |
| OrderLine | accepted_at | DateTime | เวลารับออเดอร์ | 2025-12-26 14:15:00 |
| OrderLine | accepted_by | Integer | ผู้รับออเดอร์ (FK) | 2 |
| OrderLine | dispatch_round | String(50) | รอบจัดส่ง | 1 |
| OrderLine | scanned_at | DateTime | เวลาสแกน | 2025-12-26 15:00:00 |
| OrderLine | scanned_by | Integer | ผู้สแกน (FK) | 2 |
| OrderLine | printed_warehouse | Boolean | พิมพ์เอกสารคลังแล้ว | True |
| OrderLine | printed_warehouse_at | DateTime | เวลาพิมพ์ | 2025-12-26 14:30:00 |

---

### 12.4 Known Limitations

**SQLite Limitations:**
1. **No ALTER TABLE RENAME COLUMN:** Cannot rename columns (must create new, copy, drop old)
2. **No ALTER TABLE DROP COLUMN:** Cannot drop columns (must recreate table)
3. **No Advanced Indexes:** No partial indexes, expression indexes
4. **Concurrency:** Limited write concurrency (write lock entire database)
5. **Max Database Size:** 281 TB (theoretical), but performance degrades >1 GB

**Workarounds:**
- For column rename: Leave old column, use new column, ignore old in code
- For column drop: Ignore in code (SQLite doesn't waste space)
- For concurrency: Use connection pooling, limit to 1 writer at a time
- For size: Archive old data, consider PostgreSQL migration if >1 GB

---

### 12.5 Future Database Enhancements

**Short-term (3-6 months):**
1. ✅ Implement Alembic migrations
2. ✅ Add database version table
3. ✅ Implement archival process
4. ✅ Add more indexes (composite)
5. ✅ Implement Redis caching for stock

**Long-term (6-12 months):**
1. ✅ Migrate to PostgreSQL (for better concurrency, scalability)
2. ✅ Implement read replicas (for reporting)
3. ✅ Partition OrderLine by month (better performance)
4. ✅ Implement full-text search (for product names)
5. ✅ Add price data to Product (for inventory value)
6. ✅ Implement multi-warehouse support (warehouse_id FK)
7. ✅ Add customer data (customer_id, name, address)
8. ✅ Implement order tracking (tracking_number, carrier, status updates)

---

## 13. REVISION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 5.52 | 2025-12-26 | Claude Code | Initial Database PRD created from codebase analysis |

---

**End of PRD-Database.md**
