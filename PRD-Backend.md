# PRD - Backend: VNIX Order Management

---

## 📋 Executive Summary (สำหรับลูกค้า)

**VNIX Order Management** ใช้สถาปัตยกรรม **Multi-Database** ที่แยกข้อมูลเชิงธุรกิจ ราคา และ Supplier ออกจากกัน เพื่อ:

✅ **ประสิทธิภาพสูงสุด** - Database แต่ละตัวทำงานเร็ว เพราะมีข้อมูลน้อยลง
✅ **Scale ได้ง่าย** - ย้ายไป PostgreSQL/Cloud ได้ทีละส่วน
✅ **กันข้อมูลเสีย** - ข้อมูลราคาไม่กระทบข้อมูลออเดอร์
✅ **Backup ง่าย** - Backup ได้ทีละฐานข้อมูลตามความสำคัญ

### Key Business Rules (กฎธุรกิจสำคัญ)
| กฎ | คำอธิบาย | ผลกระทบ |
|----|---------|---------|
| **Priority Allocation** | Shopee > TikTok > Lazada | ออเดอร์ที่มาก่อนได้รับก่อน |
| **Business Day SLA** | นับเฉพาะวันทำการ (ไม่นับเสาร์/อาทิตย์) | คำนวณ Due Date แม่นยำ |
| **Stock Deduction** | ตัดเฉพาะเมื่อกดรับ/จ่ายงานแล้ว | กันปัญหาของไม่พอ |
| **Insert-Only Orders** | ออเดอร์ซ้ำจะถูกข้าม | กันการซ้ำซ้อน |

---

## 1. ภาพรวมสถาปัตยกรรมระบบ (System Architecture)

**VNIX Order Management** เป็น Web Application ที่ใช้ **Flask** เป็น Framework หลัก พร้อมระบบ Database แบบ **Multi-Database** เพื่อแยกข้อมูลหลัก (data.db) และข้อมูลราคา (price.db) และข้อมูล Supplier (supplier_stock.db)

### เทคโนโลยีที่ใช้
- **Framework**: Flask 3.0.3
- **ORM**: SQLAlchemy (Flask-SQLAlchemy 3.1.1)
- **Database**: SQLite (3 Database Files)
  - `data.db`: ข้อมูลหลัก (Products, Orders, Users, ฯลฯ)
  - `price.db`: ข้อมูลราคา (SKU Pricing, Market Prices, Brand Controls)
  - `supplier_stock.db`: ข้อมูล Supplier SKU + Stock
- **Excel Processing**: openpyxl, pandas
- **Google Sheets Integration**: gspread, oauth2client
- **Authentication**: Werkzeug Security (Password Hashing)
- **Deployment**: Railway (Production) / Local (Development)

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Web Browser)                      │
│              Bootstrap 5 + DataTables + JS                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Flask Application Server                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Auth/Session│  │   Routes     │  │  Business Logic │   │
│  │  Middleware  │  │   (app.py)   │  │  (allocation.py)│   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────┬─────────────────┬──────────────────┬──────────────┘
          │                 │                  │
          ↓                 ↓                  ↓
    ┌─────────┐      ┌──────────┐      ┌──────────────┐
    │ data.db │      │price.db  │      │supplier_stock│
    │(Orders) │      │(Prices)  │      │    .db       │
    └─────────┘      └──────────┘      └──────────────┘
```

### 1.2 Data Flow Diagram (Import Orders)

```
┌─────────────┐
│ Upload Excel│
└──────┬──────┘
       ↓
┌─────────────────────┐
│  Parse Excel File   │
│  (pandas/openpyxl)  │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Validate Data      │
│  - Check Duplicate  │
│  - Normalize SKU    │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Insert to Database │
│  (INSERT-ONLY Mode) │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Compute Allocation │
│  (Stock Priority)   │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  Return Statistics  │
│  (Added/Duplicates) │
└─────────────────────┘
```

---

## 2. โครงสร้าง Database (Database Schema)

### 2.1 ฐานข้อมูลหลัก (data.db)

#### 2.1.1 Shops
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| platform | String(64) | Shopee/Lazada/TikTok/อื่นๆ |
| name | String(128) | ชื่อร้านค้า |
| google_sheet_url | Text | URL Google Sheet (optional) |
| created_at | DateTime | เวลาสร้าง |

**Constraints**:
- Unique: (platform, name)

#### 2.1.2 Products
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| sku | String(64) | Unique |
| brand | String(120) | แบรนด์ |
| model | String(255) | รุ่น/ชื่อสินค้า |
| stock_qty | Integer | สต็อก (denormalized) |
| created_at | DateTime | เวลาสร้าง |

#### 2.1.3 Stocks
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| sku | String(64) | SKU |
| qty | Integer | จำนวนสต็อก |
| updated_at | DateTime | เวลาอัปเดตล่าสุด |

#### 2.1.4 Sales (ใบขาย SBS)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| order_id | String(128) | Order ID |
| po_no | String(128) | เลขที่ PO |
| status | String(64) | สถานะใบขาย (เปิดใบขายครบตามจำนวนแล้ว / ยังไม่มีการเปิดใบขาย) |
| created_at | DateTime | เวลาสร้าง |

#### 2.1.5 OrderLines (รายการออเดอร์)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| platform | String(20) | Shopee/Lazada/TikTok |
| shop_id | Integer | FK to Shops |
| order_id | String(128) | Order ID |
| sku | String(64) | SKU |
| qty | Integer | จำนวน |
| item_name | String(512) | ชื่อสินค้า |
| order_time | DateTime | เวลาสั่งซื้อ (tz-aware) |
| logistic_type | String(255) | ขนส่ง |
| imported_at | DateTime | เวลานำเข้า |
| import_date | Date | วันที่นำเข้า (อ้างอิง พ.ศ.) |
| accepted | Boolean | กดรับแล้วหรือยัง |
| accepted_at | DateTime | เวลากดรับ |
| accepted_by_user_id | Integer | FK to Users |
| accepted_by_username | String(64) | ผู้กดรับ |
| dispatch_round | Integer | รอบจ่ายงาน |
| **Print Tracking Columns** |
| printed_warehouse | Integer | จำนวนครั้งที่พิมพ์ Warehouse |
| printed_warehouse_at | DateTime | เวลาพิมพ์ล่าสุด |
| printed_warehouse_by | String(64) | ผู้พิมพ์ |
| printed_picking | Integer | จำนวนครั้งที่พิมพ์ Picking |
| printed_picking_at | DateTime | เวลาพิมพ์ล่าสุด |
| printed_picking_by | String(64) | ผู้พิมพ์ |
| printed_lowstock | Integer | จำนวนครั้งที่พิมพ์ Lowstock |
| printed_lowstock_at | DateTime | เวลาพิมพ์ล่าสุด |
| printed_lowstock_by | String(64) | ผู้พิมพ์ |
| printed_nostock | Integer | จำนวนครั้งที่พิมพ์ Nostock |
| printed_nostock_at | DateTime | เวลาพิมพ์ล่าสุด |
| printed_nostock_by | String(64) | ผู้พิมพ์ |
| printed_notenough | Integer | จำนวนครั้งที่พิมพ์ Notenough |
| printed_notenough_at | DateTime | เวลาพิมพ์ล่าสุด |
| printed_notenough_by | String(64) | ผู้พิมพ์ |
| scanned_at | DateTime | เวลา Scan Barcode |
| scanned_by | String(64) | ผู้ Scan |

**Constraints**:
- Unique: (platform, shop_id, order_id, sku)

#### 2.1.6 Users
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| username | String(64) | Unique |
| password_hash | String(255) | Hash รหัสผ่าน |
| role | String(16) | admin/user |
| active | Boolean | ใช้งานอยู่หรือไม่ |
| created_at | DateTime | เวลาสร้าง |

#### 2.1.7 UserPreferences
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| user_id | Integer | FK to Users |
| key | String(64) | Key |
| value | String(255) | Value |
| updated_at | DateTime | เวลาอัปเดต |

**Constraints**:
- Unique: (user_id, key)

#### 2.1.8 CancelledOrders
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| order_id | String(128) | Unique |
| imported_at | DateTime | เวลายกเลิก |
| imported_by_user_id | Integer | FK to Users |
| note | String(255) | หมายเหตุ |

#### 2.1.9 IssuedOrders
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| order_id | String(128) | Unique |
| issued_at | DateTime | เวลาจ่ายงาน |
| issued_by_user_id | Integer | FK to Users |
| source | String(32) | import/print:picking/print:warehouse/manual |
| note | String(255) | หมายเหตุ |

#### 2.1.10 DeletedOrders
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| order_id | String(128) | Unique |
| deleted_at | DateTime | เวลาลบ |
| deleted_by_user_id | Integer | FK to Users |
| note | String(255) | หมายเหตุ |

#### 2.1.11 ImportLogs
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| import_date | Date | วันที่ import |
| platform | String(50) | Platform |
| shop_name | String(128) | ชื่อร้าน |
| filename | String(255) | ชื่อไฟล์ |
| added_count | Integer | จำนวนที่เพิ่ม |
| duplicates_count | Integer | จำนวนที่ซ้ำทั้งหมด |
| duplicates_same_day | Integer | จำนวนที่ซ้ำในวันเดียวกัน |
| failed_count | Integer | จำนวนที่ล้มเหลว |
| error_details | Text | JSON String รายการ Error |
| batch_data | Text | JSON String IDs ที่เพิ่ม/ซ้ำ/ล้มเหลว |
| created_at | DateTime | เวลาสร้าง |

#### 2.1.12 ActionDedupe
| Column | Type | Description |
|--------|------|-------------|
| token | String | PK |
| kind | String | ประเภท Action |
| created_at | DateTime | เวลาสร้าง |
| user_id | Integer | FK to Users |

---

### 2.2 ฐานข้อมูลราคา (price.db)

#### 2.2.1 SkuPricing (ข้อมูลฝั่งเรา)
| Column | Type | Description |
|--------|------|-------------|
| sku | String(64) | PK |
| brand | String(120) | แบรนด์ |
| name | String(255) | ชื่อสินค้า |
| spec_text | Text | สเปค |
| stock_qty | Integer | สต็อกรวม |
| stock_internal_qty | Integer | สต็อกฝั่งเรา |
| monthly_sales_qty | Integer | ยอดขายต่อเดือน |
| cost | Float | ต้นทุน/หน่วย |
| our_price | Float | ราคาเรา |
| floor_price | Float | ราคาต่ำสุด |
| min_margin_pct | Float | % กำไรขั้นต่ำ |
| pack_cost | Float | ค่าแพ็ค/ชิ้น |
| ship_subsidy | Float | ค่าเฉลี่ยที่ช่วยค่าส่ง |
| created_at | DateTime | เวลาสร้าง |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.2.2 BrandControl
| Column | Type | Description |
|--------|------|-------------|
| sku | String(64) | PK |
| brand | String(120) | แบรนด์ |
| name | String(255) | ชื่อสินค้า |
| price_control | Float | ราคาควบคุม |
| created_at | DateTime | เวลาสร้าง |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.2.3 PlatformFeeSettings
| Column | Type | Description |
|--------|------|-------------|
| platform | String(50) | PK |
| label | String(100) | ชื่อแสดงผล |
| is_active | Boolean | เปิด/ปิดใช้งาน |
| sort_order | Integer | ลำดับ |
| fee_pct | Float | % ค่าธรรมเนียม |
| fixed_fee | Float | ค่าคงที่/ชิ้น |
| created_at | DateTime | เวลาสร้าง |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.2.4 PriceConfig
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| platform | String(64) | Platform |
| name | String(128) | ชื่อ Config |
| url | Text | URL |
| worksheet | String(128) | ชื่อ Worksheet |
| updated_at | DateTime | เวลาอัปเดต |

**Constraints**:
- Unique: (platform, name)

#### 2.2.5 MarketItem (ราคาตลาด)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| sku | String(64) | SKU |
| platform | String(20) | Shopee/Lazada/TikTok |
| shop_name | String(255) | ชื่อร้านคู่แข่ง |
| product_url | String(1024) | URL |
| is_mall | Boolean | Mall/Official Store |
| is_active | Boolean | ใช้งานอยู่หรือไม่ |
| **Latest Snapshot** |
| latest_listed_price | Float | ราคาหน้าร้าน |
| latest_shipping_fee | Float | ค่าส่ง |
| latest_voucher_discount | Float | ส่วนลด Voucher |
| latest_coin_discount | Float | ส่วนลด Coin |
| latest_net_price | Float | ราคาสุทธิ |
| last_updated | DateTime | เวลาอัปเดตล่าสุด |
| note | String(512) | หมายเหตุ |
| created_at | DateTime | เวลาสร้าง |
| updated_at | DateTime | เวลาอัปเดต |

**Constraints**:
- Unique: (sku, platform, shop_name)
- Index: (sku, platform, latest_net_price)

#### 2.2.6 MarketPriceLog (ประวัติราคา)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| market_item_id | Integer | FK to MarketItem |
| sku | String(64) | SKU |
| platform | String(20) | Platform |
| shop_name | String(255) | ชื่อร้าน |
| listed_price | Float | ราคาหน้าร้าน |
| shipping_fee | Float | ค่าส่ง |
| voucher_discount | Float | ส่วนลด Voucher |
| coin_discount | Float | ส่วนลด Coin |
| net_price | Float | ราคาสุทธิ |
| captured_at | DateTime | เวลาเก็บ |
| checked_by | String(64) | ผู้เก็บ |
| note | String(512) | หมายเหตุ |
| created_at | DateTime | เวลาสร้าง |

**Constraints**:
- Index: (sku, platform, net_price)

#### 2.2.7 BrandOwnerSetting
| Column | Type | Description |
|--------|------|-------------|
| brand | String(120) | PK |
| owner | String(64) | ผู้ดูแล |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.2.8 PriceExportSetting
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| step_pct | Float | Step % (0-10) |
| min_profit_pct | Float | Min Profit % (0-10) |
| loss_aging3_pct | Float | Max Loss % Aging 3m (0-50) |
| loss_aging6_pct | Float | Max Loss % Aging 6m (0-50) |
| loss_aging12_pct | Float | Max Loss % Aging 12m (0-50) |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.2.9 PriceImportBatch
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| kind | String(32) | internal/market/brand_control |
| source | String(16) | file/gsheet |
| source_name | String(1024) | ชื่อไฟล์/URL |
| worksheet | String(128) | ชื่อ Worksheet |
| default_platform | String(20) | Platform (market only) |
| created_by | String(64) | ผู้สร้าง |
| created_at | DateTime | เวลาสร้าง |
| ok_rows | Integer | จำนวนสำเร็จ |
| skip_rows | Integer | จำนวนข้าม |
| undone | Boolean | Undo แล้วหรือยัง |
| undone_at | DateTime | เวลา Undo |
| undone_by | String(64) | ผู้ Undo |

#### 2.2.10 PriceImportOp
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| batch_id | Integer | FK to PriceImportBatch |
| seq | Integer | ลำดับ |
| table_name | String(64) | ชื่อตาราง |
| pk | String(255) | Primary Key |
| action | String(16) | insert/update |
| before_json | Text | ค่าก่อนแก้ (JSON) |
| created_at | DateTime | เวลาสร้าง |

**Constraints**:
- Index: (batch_id, seq)

#### 2.2.11 PriceUserPreferences
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| user_id | Integer | FK to Users (data.db) |
| key | String(64) | Key |
| value | String(255) | Value |
| updated_at | DateTime | เวลาอัปเดต |

**Constraints**:
- Unique: (user_id, key)

---

### 2.3 ฐานข้อมูล Supplier (supplier_stock.db)

#### 2.3.1 SupplierSkuMaster
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| sku | String(64) | SKU |
| sku_norm | String(96) | SKU Normalized |
| supplier | String(64) | Supplier |
| supplier_norm | String(96) | Supplier Normalized |
| sku_sup | String(128) | SKU Supplier |
| sku_sup_norm | String(160) | SKU Supplier Normalized |
| brand | String(120) | Brand |
| name | String(255) | ชื่อสินค้า |
| stock_sup_qty | Integer | สต็อก Supplier |
| stock_updated_at | DateTime | เวลาอัปเดต |
| is_active | Boolean | ใช้งานอยู่หรือไม่ |
| created_at | DateTime | เวลาสร้าง |
| updated_at | DateTime | เวลาอัปเดต |

**Constraints**:
- Unique: (supplier_norm, sku_sup_norm)
- Index: (sku_norm, supplier_norm)
- Index: (supplier_norm, sku_sup_norm)

#### 2.3.2 SupplierConfig
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| name | String(120) | Unique (GoogleSheet_SupplierSkuStock) |
| url | Text | URL |
| worksheet | String(120) | Worksheet |
| updated_at | DateTime | เวลาอัปเดต |

#### 2.3.3 SupplierImportBatch
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | PK |
| kind | String(64) | supplier_sku_stock |
| source | String(32) | file/gsheet |
| source_name | Text | ชื่อไฟล์/URL |
| worksheet | String(120) | Worksheet |
| ok_rows | Integer | จำนวนสำเร็จ |
| skip_rows | Integer | จำนวนข้าม |
| created_by | String(64) | ผู้สร้าง |
| created_at | DateTime | เวลาสร้าง |

---

## 3. API Endpoints

### 3.1 Authentication

#### POST `/login`
- **Description**: Login เข้าสู่ระบบ
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response**: Redirect to Dashboard

#### POST `/logout`
- **Description**: ออกจากระบบ
- **Response**: Redirect to Login

---

### 3.2 Dashboard

#### GET `/`
- **Description**: หน้า Dashboard หลัก
- **Query Params**:
  - `platform`: Shopee/Lazada/TikTok/All
  - `shop_id`: Shop ID
  - `import_from`, `import_to`: Import Date Range
  - `date_from`, `date_to`: Order Date Range
  - `accepted_from`, `accepted_to`: Accepted Date Range
  - `status`: Allocation Status
  - `active_only`: Show only active orders
  - `all_time`: Show all orders
- **Response**: HTML + DataTables JSON

#### POST `/api/accept`
- **Description**: กดรับออเดอร์
- **Request Body**:
  ```json
  {
    "order_ids": ["ORD001", "ORD002"],
    "allow_lowstock": false
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "accepted": 2,
    "skipped": 0
  }
  ```

#### POST `/api/cancel`
- **Description**: ยกเลิกออเดอร์
- **Request Body**:
  ```json
  {
    "order_ids": ["ORD001"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

---

### 3.3 Reports

#### GET `/report`
- **Description**: รายงานคลัง (ออเดอร์ที่รับแล้ว)
- **Query Params**: Same as Dashboard
- **Response**: HTML + DataTables JSON

#### GET `/report/lowstock`
- **Description**: รายงานสินค้าน้อย
- **Response**: HTML + DataTables JSON

#### GET `/report/nostock`
- **Description**: รายงานไม่มีสินค้า
- **Response**: HTML + DataTables JSON

#### GET `/report/notenough`
- **Description**: รายงานสินค้าไม่พอส่ง
- **Response**: HTML + DataTables JSON

#### POST `/api/print/<kind>`
- **Description**: พิมพ์รายงาน (warehouse/picking/lowstock/nostock/notenough)
- **Request Body**:
  ```json
  {
    "order_ids": ["ORD001", "ORD002"],
    "token": "unique_token"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "printed": 2
  }
  ```

#### POST `/api/issue`
- **Description**: จ่ายงาน (Mark as Issued)
- **Request Body**:
  ```json
  {
    "order_ids": ["ORD001"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "issued": 1
  }
  ```

---

### 3.4 Import APIs

#### POST `/import/products`
- **Description**: นำเข้าสินค้า
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "imported": 100
  }
  ```

#### POST `/import/stock`
- **Description**: นำเข้าสต็อก
- **Request**: Multipart/Form-Data with file
- **Query Params**:
  - `full_replace`: true/false (default: true)
- **Response**:
  ```json
  {
    "success": true,
    "updated": 50
  }
  ```

#### POST `/import/orders`
- **Description**: นำเข้าออเดอร์
- **Request**: Multipart/Form-Data with file
- **Form Data**:
  - `platform`: Shopee/Lazada/TikTok
  - `shop_name`: Shop Name
  - `import_date`: Date (YYYY-MM-DD)
- **Response**:
  ```json
  {
    "success": true,
    "added": 50,
    "duplicates": 5,
    "duplicates_old": 3,
    "duplicates_today": 2,
    "failed": 0,
    "errors": [],
    "added_ids": ["ORD001", ...],
    "duplicate_ids": ["ORD099", ...],
    "failed_ids": []
  }
  ```

#### POST `/import/sales`
- **Description**: นำเข้าใบขาย SBS
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "ids": ["ORD001", ...],
    "skipped": []
  }
  ```

---

### 3.5 Price Dashboard APIs

#### GET `/price`
- **Description**: Price Dashboard
- **Query Params**:
  - `brand_owner`: Brand Owner
  - `platform`: Platform
  - `search`: Search SKU/Name
  - `page`: Page Number
  - `per_page`: Items per page
- **Response**: HTML + JSON Rows

#### POST `/price/import/internal`
- **Description**: นำเข้าราคาฝั่งเรา
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "ok": 100,
    "skip": 5
  }
  ```

#### POST `/price/import/market`
- **Description**: นำเข้าราคาตลาด
- **Request**: Multipart/Form-Data with file
- **Form Data**:
  - `default_platform`: Platform
  - `checked_by`: Username
- **Response**:
  ```json
  {
    "success": true,
    "ok": 50,
    "skip": 2,
    "new_items": 10
  }
  ```

#### POST `/price/import/brand_control`
- **Description**: นำเข้า Brand Control
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "ok": 30,
    "skip": 0
  }
  ```

#### POST `/price/import/monthly_sales`
- **Description**: นำเข้า Monthly Sales
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "ok": 100,
    "skip": 0
  }
  ```

#### POST `/price/export`
- **Description**: Export ราคาพร้อม Sell Tiers
- **Request Body**:
  ```json
  {
    "skus": ["SKU001", "SKU002"],
    "adj_pct": 0
  }
  ```
- **Response**: Excel File

#### POST `/price/settings/fees`
- **Description**: บันทึก Platform Fee Settings
- **Request Body**:
  ```json
  {
    "fees": [
      {"platform": "Shopee", "fee_pct": 10, "fixed_fee": 0}
    ]
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

#### POST `/price/settings/export`
- **Description**: บันทึก Export Settings
- **Request Body**:
  ```json
  {
    "step_pct": 5.0,
    "min_profit_pct": 5.0,
    "loss_aging3_pct": 5.0,
    "loss_aging6_pct": 10.0,
    "loss_aging12_pct": 20.0
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

---

### 3.6 Supplier Stock APIs

#### GET `/supplier`
- **Description**: Supplier Stock Dashboard
- **Query Params**:
  - `supplier`: Supplier Name
  - `brand`: Brand
  - `search`: Search SKU
  - `page`: Page Number
- **Response**: HTML + JSON Rows

#### POST `/supplier/import`
- **Description**: นำเข้า Supplier SKU + Stock
- **Request**: Multipart/Form-Data with file
- **Response**:
  ```json
  {
    "success": true,
    "ok": 100,
    "skip": 5,
    "insert": 50,
    "update": 50,
    "conflict": 0,
    "conflicts": []
  }
  ```

---

### 3.7 Admin APIs

#### GET `/admin/shops`
- **Description**: หน้าจัดการ Shop
- **Response**: HTML

#### POST `/admin/shops`
- **Description**: เพิ่ม/แก้ไข Shop
- **Request Body**:
  ```json
  {
    "platform": "Shopee",
    "name": "My Shop",
    "google_sheet_url": "https://..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

#### DELETE `/admin/shops/<id>`
- **Description**: ลบ Shop
- **Response**:
  ```json
  {
    "success": true
  }
  ```

#### GET `/admin/users`
- **Description**: หน้าจัดการ User
- **Response**: HTML

#### POST `/admin/users`
- **Description**: เพิ่ม/แก้ไข User
- **Request Body**:
  ```json
  {
    "username": "user1",
    "password": "pass123",
    "role": "user",
    "active": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

#### POST `/api/userpref/set`
- **Description**: บันทึก User Preference
- **Request Body**:
  ```json
  {
    "key": "supplier_stock.filter_supplier",
    "value": "Supplier A"
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

#### POST `/api/userpref/clear`
- **Description**: ล้าง User Preference
- **Request Body**:
  ```json
  {
    "keys": ["supplier_stock.filter_supplier"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

---

## 4. Business Logic (Core Algorithms)

### 4.1 Allocation Logic (`allocation.py`)

**วัตถุประสงค์**: จัดสรรสต็อกให้ออเดอร์ตามลำดับความสำคัญ

**Priority Order**:
1. Shopee > TikTok > Lazada > อื่นๆ
2. Order Time (มาก่อนได้ก่อน - FIFO)

**ขั้นตอน**:

1. **โหลดข้อมูลทั้งหมด**:
   - OrderLines, Shops, Products, Stocks, Sales
   - Cancelled Orders, Issued Orders

2. **กรองข้อมูล**:
   - Platform, Shop, Date Range
   - ข้าม Packed/Cancelled (ถ้า active_only)

3. **คำนวณ AllQty**:
   - รวมยอดที่ลูกค้าสั่ง SKU นั้นทุกแพลตฟอร์ม
   - นับเฉพาะที่ยังไม่ Packed/Cancelled

4. **จัดสรรสต็อกตาม Priority**:
   - เรียงตาม Platform + Order Time
   - วนลูปแต่ละ Order:
     - **ถ้า Packed/Cancelled**: ข้าม (ไม่ตัดสต็อก)
     - **ถ้า Accepted**: ตัดสต็อก (จองของไว้)
     - **ถ้า Issued**: ตัดสต็อก (จองของไว้)
     - **ถ้าใหม่**:
       - สต็อก <= 0 → SHORTAGE
       - สต็อก < Qty → NOT_ENOUGH
       - สต็อกพอ แต่เหลือน้อย (1-3) → LOW_STOCK
       - สต็อกพอ → READY_ACCEPT
       - ตัดสต็อกเฉพาะกรณีพอ (READY_ACCEPT/LOW_STOCK)

5. **คำนวณ KPI**:
   - Total Items, Total Orders
   - Ready, Accepted, Low, Shortage, Not Enough, Packed
   - Orders Ready, Orders Low

---

### 4.2 SLA Calculation (`utils.py`)

**วัตถุประสงค์**: คำนวณ SLA แบบวันทำการ

**Cutoff Time**:
- Lazada: 11:00
- Shopee/TikTok/อื่นๆ: 12:00

**วันทำการ**:
- ข้ามเสาร์/อาทิตย์
- ข้ามวันหยุดไทย (TH_HOLIDAYS)

**สูตร**:
```
ถ้า Order Time <= Cutoff:
  Due = Order Date (ถ้าวันทำการ) หรือวันทำการถัดไป
ถ้า Order Time > Cutoff:
  Due = วันทำการถัดไป
```

**SLA Text**:
- `diff > 0`: "เลยกำหนด (X วัน)"
- `diff == 0`: "วันนี้"
- `diff == -1`: "พรุ่งนี้"
- `diff < -1`: "อีก X วัน"

---

### 4.3 Price Calculation (`app.py`)

**Build Sell Prices**:
- Input: our_price, cost, step_pct, min_profit_pct, loss_aging3/6/12_pct, aging_bucket
- Process:
  1. คำนวณ Sell1..Sell5 โดยลดทีละ step_pct
  2. ตรวจสอบ Threshold:
     - **Non-aging**: threshold = cost * (1 + min_profit_pct)
     - **Aging**: threshold = cost * (1 - max_loss_pct)
  3. ถ้า tier < threshold → เลื่อนขึ้นเป็น floor_price
  4. **Special Case**: Sell1 เท่ากับ Sell2 (แบน) → Sell1 = floor_to_5(Sell2 * 1.03)

**Export Price Adjustment**:
- `adj_pct > 0`: คูณแล้วปัดขึ้นเป็น 0/5
- `adj_pct < 0`: คูณแล้วปัดลงเป็น 0/5

---

## 5. Import Logic (`importers.py`)

### 5.1 Common Functions

**`first_existing(df, candidates)`**: หาคอลัมน์ที่มีอยู่จากรายการ候选

**`clean_shop_name(s)`**: ทำความสะอาดชื่อร้าน (ตัด "•", "(Shopee)")

**`get_or_create_shop(platform, shop_name)`**: ดึง/สร้าง Shop

**`_to_float`, `_to_int`, `_to_bool`, `_is_blank`**: แปลง DataType

**`_set_attr(obj, attr, col, row, kind)`**: Patch semantics (col missing → no touch, blank → None)

---

### 5.2 Import Stock

**Full Sync Mode**:
1. Reset ทุก SKU เป็น 0
2. Update ตามไฟล์
3. SKU ที่ไม่อยู่ในไฟล์ → 0

**Normalization**:
- รองรับหัวคอลัมน์หลากหลาย (ไทย/อังกฤษ)
- Qty ว่าง/NaN → 0
- รวมยอด SKU ซ้ำ

---

### 5.3 Import Orders

**INSERT-ONLY Mode**:
1. Group by (Shop, Order ID)
2. เช็คว่า Order มีอยู่แล้วหรือไม่
   - มีแล้ว → Skip (Duplicate)
   - ไม่มี → Insert
3. รวม SKU ซ้ำใน Order เดียวกัน
4. บันทึก Import Log

**Statistics**:
- `added`: จำนวน Order ที่เพิ่ม
- `duplicates`: จำนวน Order ที่ซ้ำทั้งหมด
- `duplicates_old`: ซ้ำข้ามวัน
- `duplicates_today`: ซ้ำในวันเดียวกัน
- `failed`: จำนวนที่ล้มเหลว
- `errors`: รายการ Error (สูงสุด 10 รายการ)

---

### 5.4 Import Price Marketing

**Patch Semantics**:
- คอลัมน์ไม่มี → ไม่แก้ไข
- ค่าว่าง → NULL
- ค่ามี → Update ถ้าต่าง

**Undo System**:
1. สร้าง PriceImportBatch
2. บันทึก PriceImportOp ทุก operation (insert/update)
3. เก็บ before_json เพื่อ restore

---

## 6. Caching Strategy

### 6.1 Price Dashboard Rows Cache
- **Key**: `user_id + filter_hash`
- **TTL**: 15 นาที
- **GC**: Auto cleanup expired entries

### 6.2 Supplier Stock Dashboard Rows Cache
- **Key**: `user_id + filter_hash`
- **TTL**: 15 นาที
- **GC**: Auto cleanup + Max 30 items

### 6.3 Platform Import Cache
- **Purpose**: Store output workbook for download after apply
- **TTL**: 30 นาที
- **GC**: Auto cleanup + Delete file

---

## 7. Google Sheets Integration

**Authentication**:
1. ลอง Environment Variable: `GOOGLE_CREDENTIALS_JSON` (JSON string)
2. ลอง Environment Variables แยก: `GOOGLE_PRIVATE_KEY`, `GOOGLE_CLIENT_EMAIL`, ฯลฯ
3. ลองไฟล์: `credentials.json` (Local)

**Usage**:
- Price Dashboard: Import/Export SKU Pricing
- Supplier Stock: Import SKU + Stock
- Shop Config: Sync Google Sheet URL

---

## 8. Deployment

### 8.1 Environment Variables
- `SECRET_KEY`: Flask Secret Key
- `RAILWAY_VOLUME_MOUNT_PATH`: Volume Path (Production)
- `GOOGLE_CREDENTIALS_JSON`: Google Service Account Credentials
- `APP_NAME`: Application Name

### 8.2 Database Storage
- **Production**: Railway Volume
  - `data.db`: `/volume/data.db`
  - `price.db`: `/volume/price.db`
  - `supplier_stock.db`: `/volume/supplier_stock.db`
- **Local**: Project Directory

### 8.3 Auto-Migration
- สร้างตารางอัตโนมัติ (`db.create_all`)
- เพิ่มคอลัมน์ใหม่อัตโนมัติ (ALTER TABLE)
- ย้าย Unique Index (`shops`): name → (platform, name)

---

## 9. Security

### 9.1 Authentication
- Password Hashing (Werkzeug)
- Session Management
- Login Required Decorator

### 9.2 Authorization
- Role-based Access Control (admin/user)
- User Preferences

### 9.3 Data Validation
- Input Validation (Client + Server)
- SQL Injection Prevention (SQLAlchemy ORM)
- XSS Protection (Jinja2 Auto-escape)

### 9.4 Idempotency
- Action Dedupe Table: กัน request ซ้ำ
- Print Token: กันกดพิมพ์ซ้ำ

---

## 10. Performance Optimization

### 10.1 Database
- Indexing: สำคัญ columns (sku, order_id, ฯลฯ)
- Query Optimization: JOIN, Filter ที่ SQL level
- Connection Pooling: SQLAlchemy default

### 10.2 Caching
- In-memory cache (per-process)
- TTL-based expiration

### 10.3 Async Processing
- สำหรับ Future: Use Celery/Background Tasks

---

## 11. Error Handling

### 11.1 Validation Errors
- Flash Messages
- JSON Error Response

### 11.2 Database Errors
- IntegrityError: Handle duplicate keys
- Rollback on error

### 11.3 Import Errors
- Log errors (ImportLog.error_details)
- Continue on error (don't stop entire import)

---

## 12. Logging

### 12.1 Application Logs
- Flask app.logger
- Warning/Info/Error levels

### 12.2 Import Logs
- ImportLogs Table
- PriceImportBatch + PriceImportOp

---

## 13. Testing (ถ้ามี)

### 13.1 Unit Tests
- Test Allocation Logic
- Test Price Calculation
- Test Import Logic

### 13.2 Integration Tests
- Test API Endpoints
- Test Database Operations

---

## 14. 🚀 Scalability Roadmap (แผนขยายระบบฝั่ง Backend)

### Phase 1: Database Migration (3 เดือน)
**เป้าหมาย**: ย้ายจาก SQLite → PostgreSQL เพื่อรองรับ Concurrent Users

**Changes:**
- 🗄️ **PostgreSQL Migration**
  - ย้าย `data.db` → PostgreSQL (Orders, Products)
  - ย้าย `price.db` → PostgreSQL (Prices)
  - ย้าย `supplier_stock.db` → PostgreSQL (Suppliers)
- 🔧 **Connection Pooling**
  - ใช้ SQLAlchemy Pool (size 10-20 connections)
  - รองรับ Concurrent Writes ได้จริง
- 📊 **Read Replicas** (Optional)
  - 1 Master (Write) + 2 Replicas (Read)
  - Load Balance การ Query ข้อมูล

**Benefits:**
- รองรับ Concurrent Users ได้ >50 คนพร้อมกัน
- ข้อมูลไม่สูญหายจาก Lock
- Query เร็วขึ้นจาก Indexing ที่ดีกว่า

**Migration Strategy:**
1. Backup SQLite → ย้ายข้อมูลไป PostgreSQL
2. ทดสอบระบบบน PostgreSQL (Staging)
3. Switch Production พร้อม Rollback Plan
4. Monitor 7 วัน ก่อนลบ SQLite

---

### Phase 2: Caching Layer (6 เดือน)
**เป้าหมาย**: ใช้ Redis เพื่อลด Load ของ Database

**Changes:**
- 🔴 **Redis Caching**
  - Cache Dashboard KPI (TTL: 1 นาที)
  - Cache Price Dashboard Rows (TTL: 15 นาที)
  - Cache Session Data
  - Cache User Preferences
- ⚡ **Query Optimization**
  - In-memory Cache สำหรับข้อมูลที่อ่านบ่อย (Platform, Shops)
  - Reduce Database Queries ลง 60-80%
- 🔄 **Cache Invalidation**
  - Auto-invalidate เมื่อมีการ Update
  - Manual Invalidate สำหรับ Critical Data

**Benefits:**
- Response Time ลดลง 50% (200ms → 100ms)
- Database Load ลดลง 60%
- รองรับ Users ได้ >100 คนพร้อมกัน

---

### Phase 3: Real-time & Background Jobs (12 เดือน)
**เป้าหมาย**: อัปเดตข้อมูล Real-time และจัดการ Background Jobs

**Changes:**
- 🔌 **WebSocket Integration**
  - Real-time SLA Updates (ทุก 1 นาที)
  - Real-time Stock Updates (เมื่อกดรับ)
  - Live Notifications (เมื่อมีออเดอร์ใหม่)
- ⚙️ **Celery Task Queue**
  - Background Import (ไม่ Block UI)
  - Background Price Calculation
  - Scheduled Jobs (Daily/Monthly Reports)
- 📊 **Message Queue** (RabbitMQ/Redis)
  - Queue สำหรับ Background Tasks
  - Retry Mechanism ถ้า Task ล้มเหลว

**Benefits:**
- User Experience ดีขึ้น (ไม่ต้อง Refresh)
- ประมวลผลเบื้องหลังได้โดยไม่ Block UI
- รองรับ Heavy Operations (Import ไฟล์ใหญ่)

---

### Phase 4: Microservices & Cloud Native (18 เดือน)
**เป้าหมาย**: แยก Service และย้ายไป Cloud Native Architecture

**Changes:**
- 🔧 **Service Decomposition**
  - Order Service (จัดการออเดอร์)
  - Price Service (จัดการราคา)
  - Supplier Service (จัดการ Supplier)
  - Notification Service (จัดการแจ้งเตือน)
- ☁️ **Cloud Deployment**
  - Kubernetes (K8s) Orchestration
  - Docker Containerization
  - Auto-scaling (Horizontal/Vertical)
- 📊 **Monitoring & Observability**
  - Prometheus + Grafana (Metrics)
  - ELK Stack (Logs)
  - Jaeger (Distributed Tracing)

**Benefits:**
- Scale แต่ละ Service ได้อิสระ
- High Availability (Zero Downtime)
- Deploy ได้รวดเร็ว (Rolling Update)
- Monitor และ Debug ได้ง่าย

---

### Phase 5: AI & Analytics Integration (24 เดือน)
**เป้าหมาย**: ใช้ AI ช่วยวิเคราะห์และแนะนำ

**Changes:**
- 🤖 **AI Price Recommendation**
  - Machine Learning Model (Recommend Price)
  - Train จาก Historical Data
  - Auto-update Price ทุกสัปดาห์
- 🔮 **Predictive Analytics**
  - Predict Demand (ทำนายยอดขาย)
  - Predict Stock Out (ทำนายสต็อกขาด)
  - Optimize Stock Level
- 📊 **Business Intelligence**
  - Advanced Dashboards (Power BI/Tableau)
  - Custom Reports (Drag & Drop)
  - Data Warehouse (Snowflake/BigQuery)

**Benefits:**
- ตั้งราคาได้ถูกต้อง เพิ่มกำไร
- ลด Stock Out และ Overstock
- ตัดสินใจเชิงกลยุทธ์ได้ดีขึ้น

---

## 15. Performance & Reliability Targets

| Metric | Current | Phase 1 (PG) | Phase 2 (Redis) | Phase 3 (WS) |
|--------|---------|--------------|-----------------|--------------|
| **Concurrent Users** | 10-20 | 50-100 | 100-200 | 200-500 |
| **API Response Time** | 200ms | 150ms | 100ms | 50ms |
| **Database Query Time** | 100ms | 50ms | 20ms | 10ms |
| **System Uptime** | 95% | 98% | 99% | 99.9% |
| **Data Loss Risk** | Low | Very Low | Minimal | None |

---

## 16. Monitoring & Maintenance Plan

### 16.1 Health Check Endpoints
```
GET /health          - สถานะระบบทั่วไป
GET /health/db       - สถานะ Database Connection
GET /health/cache     - สถานะ Redis Cache
GET /health/queue     - สถานะ Celery Queue
```

### 16.2 Key Metrics to Track
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Orders/Day** | จำนวนออเดอร์ต่อวัน | < 10 (Abnormal Low) |
| **Import Success Rate** | % การ Import สำเร็จ | < 95% |
| **API Response Time** | เวลาตอบ API | > 500ms |
| **Error Rate** | % ข้อผิดพลาด | > 1% |
| **Stock Zero Count** | จำนวน SKU ที่สต็อก = 0 | > 50 SKUs |

### 16.3 Backup Strategy
- **Daily Backup**: เวลา 02:00 น. (Auto)
- **Retention**: เก็บ 30 วัน
- **Off-site Backup**: เก็บที่ Cloud Storage (S3/GCS)
- **Restore Test**: ทดสอบ Restore ทุกเดือน

### 16.4 Incident Response
| Severity | Response Time | Example |
|----------|--------------|---------|
| **P1 - Critical** | < 15 min | System Down, Data Loss |
| **P2 - High** | < 1 hour | Slow Performance, Partial Outage |
| **P3 - Medium** | < 4 hours | Feature Not Working, Minor Bug |
| **P4 - Low** | < 1 day | UI Issue, Typo |

---

## 17. Cost Estimation (Infrastructure)

### Phase 0 (Current)
- Railway: ~$20-30/เดือน
- Total: **$20-30/เดือน**

### Phase 1 (PostgreSQL)
- Railway (PG): ~$50-80/เดือน
- Total: **$50-80/เดือน**

### Phase 2 (Redis)
- Railway (PG + Redis): ~$100-150/เดือน
- Total: **$100-150/เดือน**

### Phase 3 (Celery + WebSocket)
- Railway + Dedicated Worker: ~$200-300/เดือน
- Total: **$200-300/เดือน**

### Phase 4 (Kubernetes)
- Cloud (GCP/AWS): ~$500-1000/เดือน
- Total: **$500-1000/เดือน**

---

## 18. Glossary (Technical Terms)

| ศัพท์ | ความหมาย |
|-------|----------|
| **ORM** | Object-Relational Mapping - SQLAlchemy |
| **Multi-Database** | ใช้หลาย Database แยกกัน (data.db, price.db, supplier_stock.db) |
| **Bind Key** | กำหนดว่า Model ไปอยู่ Database ไหน (__bind_key__) |
| **TTL** | Time To Live - อายุของ Cache |
| **GC** | Garbage Collection - ลบข้อมูลเก่า |
| **INSERT-ONLY** | เพิ่มข้อมูลใหม่เท่านั้น ไม่ Update ของเดิม |
| **Patch Semantics** | อัปเดตเฉพาะคอลัมน์ที่มี ไม่แก้ทั้ง Row |
| **Undo System** | ย้อนการแก้ไขได้ (ใน Price Import) |
| **Connection Pooling** | ใช้ Connection ร่วมกันเพื่อ Performance |
| **Read Replicas** | Database สำหรับอ่านอย่างเดียว |
| **WebSocket** | Two-way Communication ระหว่าง Server-Client |
| **Celery** | Python Task Queue สำหรับ Background Jobs |
| **Kubernetes** | Container Orchestration System |
| **Distributed Tracing** | ติดตาม Request ข้าม Services |

---

## 19. Assumptions & Constraints

### 19.1 สมมติฐาน (Assumptions)
- ผู้ใช้ใช้ Browser ที่รองรับ Modern JavaScript
- อินเทอร์เน็ตเสถียร (ไม่ Disconnect บ่อย)
- ข้อมูลจากแพลตฟอร์มถูกต้อง
- Team มีความสามารถดูแลระบบ Basic Level

### 19.2 ข้อจำกัด (Constraints)
- SQLite: 1 Write ต่อ 1 เวลา (ปัจจุบัน)
- Single Server: ไม่มี Load Balancing (ปัจจุบัน)
- Python Dependencies: ต้องเวอร์ชันที่รองรับ
- Google Sheets API: มี Quota จำกัด

---

## 20. Success Metrics (Backend)

### 20.1 Technical Metrics
- **API Response Time**: < 200ms (p95)
- **Error Rate**: < 0.1%
- **System Uptime**: > 99%
- **Database Query Time**: < 100ms (p95)
- **Cache Hit Rate**: > 80%

### 20.2 Business Metrics
- **Import Success Rate**: > 99%
- **Order Processing Time**: < 30 วินาที/ออเดอร์
- **Allocation Accuracy**: 100%
- **SLA Achievement**: > 95%

---

*PRD ฉบับนี้ครอบคลุมทั้งฝั่ง Business และ Technical พร้อม Roadmap สำหรับการส่งมอบและวางแผนขยายระบบ*
