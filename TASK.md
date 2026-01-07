# 📋 Task List - VNIX Order Management System
**วันที่สร้าง:** 2026-01-07  
**สถานะ:** รอแก้ไข

---

## 🚨 ปัญหาเร่งด่วน (High Priority)

### 1. ไอคอน Bootstrap Icons ที่ยังไม่ได้ Migrate ไป Lucide Icons
**หน้าที่มีปัญหา:** 3 Template Files (users.html, import_stock.html, picking.html)

**Context:**  
ระบบกำลังอยู่ในช่วง Icon Migration จาก Bootstrap Icons เป็น Lucide Icons แต่ยังเหลือ 3 template files ที่ยังใช้ Bootstrap Icons อยู่ รวม 27 instances ทำให้ไม่สามารถ remove Bootstrap Icons CDN dependency ได้

#### 1.1 หน้าจัดการผู้ใช้ (users.html)
**Bootstrap Icons ที่ยังค้างอยู่:**
- `bi-person-plus-fill` - ไอคอนเพิ่มผู้ใช้ใน header section
- `bi-person` - ไอคอน username input field
- `bi-key` - ไอคอน password input field  
- `bi-eye-slash` / `bi-eye` - Toggle password visibility
- `bi-plus-lg` - ปุ่ม Add User
- `bi-list-ul` - User list section header
- `bi-person-fill` - User avatar icon in table
- `bi-shield-lock-fill` - Admin role badge
- `bi-person-badge-fill` - User role badge
- `bi-trash` - Delete user action button

**จำนวนรวม:** 15 icon instances ที่ต้อง migrate

**Suggested Lucide Icons Mapping:**
- `bi-person-plus-fill` → `user-plus`
- `bi-person` → `user`
- `bi-key` → `key-round`
- `bi-eye-slash` / `bi-eye` → `eye-off` / `eye`
- `bi-plus-lg` → `plus`
- `bi-list-ul` → `list`
- `bi-person-fill` → `user-circle`
- `bi-shield-lock-fill` → `shield-check`
- `bi-person-badge-fill` → `user-check`
- `bi-trash` → `trash-2`

#### 1.2 หน้านำเข้าสต็อก (import_stock.html)
**Bootstrap Icons ที่ยังค้างอยู่:**
- `bi-file-earmark-excel` - Tab นำเข้าจากไฟล์ Excel
- `bi-google` - Tab นำเข้าจาก Google Sheet
- `bi-cloud-upload` - ปุ่ม Upload file
- `bi-save` - ปุ่ม Save data
- `bi-trash` - ปุ่ม Clear data
- `bi-cloud-download-fill` - ไอคอน Download template
- `bi-check-circle-fill` / `bi-check-circle` - Success indicators

**จำนวนรวม:** 8 icon instances ที่ต้อง migrate

**Suggested Lucide Icons Mapping:**
- `bi-file-earmark-excel` → `file-spreadsheet`
- `bi-google` → `chrome` (closest alternative)
- `bi-cloud-upload` → `cloud-upload`
- `bi-save` → `save`
- `bi-trash` → `trash-2`
- `bi-cloud-download-fill` → `cloud-download`
- `bi-check-circle-fill` / `bi-check-circle` → `check-circle-2`

#### 1.3 หน้ารายการหยิบสินค้า (picking.html)
**Bootstrap Icons ที่ยังค้างอยู่:**
- `bi-search` - Search box icon
- `bi-x-circle` - Clear search button
- `bi-truck` - Delivery/logistics icon

**Emoji ที่ยังค้างอยู่:**
- 📋 - Page header icon

**จำนวนรวม:** 4 instances ที่ต้อง migrate (3 icons + 1 emoji)

**Suggested Lucide Icons Mapping:**
- `bi-search` → `search`
- `bi-x-circle` → `x-circle`
- `bi-truck` → `truck`
- 📋 → `clipboard-list`

**ผลกระทบ:**
- **UI Inconsistency:** หน้าต่างๆ ใช้ icon library ต่างกัน (Bootstrap Icons vs Lucide Icons)
- **Bundle Size:** ต้อง load 2 icon libraries พร้อมกัน (~150KB overhead)
- **Maintenance Burden:** ยาก maintain เพราะมี 2 systems
- **User Experience:** ไอคอนดูไม่เหมือนกันทั้งระบบ อาจทำให้ user สับสน

**วิธีแก้:**
1. **Replace Icons:** แทนที่ `<i class="bi bi-*">` ด้วย `<i data-lucide="*"></i>`
2. **Update JavaScript:** ตรวจสอบว่า icon initialization (`lucide.createIcons()`) ถูก call หลัง DOM ready
3. **Browser Testing:** ทดสอบการ render ใน Chrome, Firefox, Safari
4. **Remove Dependency:** ลบ Bootstrap Icons CDN link จาก `base.html` หลัง migration เสร็จ
5. **Documentation:** อัปเดต `docs/ICONS.md` ให้ dev คนอื่นใช้ Lucide Icons เท่านั้น

**Acceptance Criteria:**
- ✅ ไม่มี `bi-*` class เหลืออยู่ใน 3 templates
- ✅ ไม่มี emoji ในส่วน UI (ยกเว้น comments)
- ✅ ทุก icon render ถูกต้องใน responsive mode
- ✅ ผ่าน validation test: `test_all_pages_checkpoint.py`

---

### 2. BILL_EMPTY Status Tracking & KPI Calculation Issue
**สถานะ:** แก้ไขแล้ว แต่ต้อง Monitor Production Environment

**Context:**  
ระบบมีฟีเจอร์นำเข้า "บิลเปล่า" (Empty Bill Orders) ซึ่งเป็น order ที่ต้องทำเอกสารแต่ไม่มีสินค้าจริง โดยบันทึกเป็น `allocation_status = 'BILL_EMPTY'` แต่พบว่า Dashboard KPI cards แสดงจำนวนบิลเปล่าเป็น 0 แม้จะมีข้อมูลใน database

**อาการที่พบ:**
- Dashboard KPI card "บิลเปล่า" แสดง **0** แม้มี `OrderLine` records ที่ `allocation_status = 'BILL_EMPTY'`
- บิลเปล่าที่ scan barcode แล้วจะหายจากรายงาน (ถูกกรองออก)
- Filter by Platform/Shop ไม่แสดงบิลเปล่า
- Log file แสดง `[BILL_EMPTY DEBUG] พบ 0 แถว` แม้ query database ได้ผลลัพธ์

**Root Causes (พบ 3 จุด):**

1. **allocation.py ไม่ Preserve DB Status**
   - `allocation.py` line 137-139: กำหนด `allocation_status = ""` เสมอ
   - จากนั้นคำนวณ allocation_status ใหม่ตาม stock logic
   - ผลลัพธ์: ค่า `BILL_EMPTY` จาก DB ถูก overwrite

2. **Field Name Mismatch**
   - `allocation.py` return field: `is_packed`
   - `app.py` dashboard check field: `packed`
   - ผลลัพธ์: Filter logic ทำงานผิดพลาด

3. **Incorrect Filtering Logic**
   - `app.py` กรองบิลเปล่าออกเมื่อ `is_packed = True`
   - แต่บิลเปล่าที่ scan barcode จะมี `sales.status = 'เปิดใบขายครบตามจำนวนแล้ว'`
   - ผลลัพธ์: บิลเปล่าที่ยัง active ถูกกรองออก

**การแก้ไขที่ทำไปแล้ว:**

1. **app.py (3 locations):**
   - Line 9977-9982: เพิ่ม `import_date` update เมื่อ Import บิลเปล่า
   - Line 8336-8348: ลบการกรอง `is_packed/is_cancelled` จาก BILL_EMPTY KPI
   - Line 8627-8633: Recalculate BILL_EMPTY set โดยไม่กรอง packed orders

2. **allocation.py (2 locations):**
   - Line 137-139: อ่าน `allocation_status` จาก DB แทนการ reset เป็น `""`
   - Line 202-205: Skip allocation logic ถ้า status เป็น `BILL_EMPTY` (preserve DB value)

3. **Created Helper Scripts:**
   - `check_bill_empty.py` - Validate DB records
   - `diagnose_bill_empty.py` - Debug allocation logic
   - `fix_bill_empty_status.py` - Backfill historical orders
   - `quick_test.py` - Fast validation

**ต้องทำ (Ongoing Monitoring):**
- Monitor production logs หา `[BILL_EMPTY DEBUG]` messages
- Validate KPI counts หลัง Import บิลเปล่าใหม่
- ตรวจสอบว่า Server restart ไม่ทำให้ค่า reset
- Run `quick_test.py` ทุกครั้งก่อน deploy code changes
- Track false positives/negatives จาก user feedback

**Test Cases:**
```python
# Expected behavior:
# 1. Import BILL_EMPTY orders → KPI count should increase
# 2. Scan barcode on BILL_EMPTY → should still show in KPI
# 3. Filter by platform → should include BILL_EMPTY orders
# 4. Server restart → KPI count should persist
```

---

### 3. Development Workflow - Frequent Manual Restarts Required
**Priority:** High (Developer Experience Issue)

**Context:**  
Development workflow มีความยุ่งยากเพราะทุกครั้งที่แก้ไข code ต้อง manual restart server และลบ Python bytecode cache (`.pyc` files) ทำให้ development cycle ช้า และเสี่ยงต่อการใช้ cached code เก่า

**อาการที่พบ:**
- แก้ไข `app.py` หรือ `models.py` แล้วไม่เห็นผล (ยังใช้ cached code)
- ต้อง manual restart: `pkill -9 -f "python.*app.py" && python3 app.py`
- ต้อง manual clear cache: `find . -name "*.pyc" -delete`
- Browser cache ทำให้ static files (JS/CSS) ไม่ update
- Hot reload ไม่ทำงานแม้ตั้งค่า `debug=True`

**Root Causes:**

1. **Flask Debug Mode ไม่ทำงาน**
   - `app.py` อาจมี `debug=False` หรือไม่มี debug setting
   - Flask reloader ไม่ detect file changes
   - Production mode ทำให้ไม่มี auto-reload

2. **Python Bytecode Cache**
   - Python สร้าง `.pyc` files ใน `__pycache__/` directories
   - แม้แก้ไข `.py` source แล้ว interpreter ยังใช้ `.pyc` เก่า
   - SQLAlchemy models cache schema definitions

3. **Browser Caching**
   - Static files (CSS/JS) ถูก cache ตาม HTTP headers
   - ไม่มี cache-busting strategy (query string versioning)
   - Hard refresh (`Ctrl+Shift+R`) ต้องทำทุกครั้ง

4. **Process Management**
   - Background process ยังทำงานอยู่หลัง `Ctrl+C`
   - Multiple Python processes conflict กัน
   - Port 5000 ถูก bind โดย process เก่า

**วิธีแก้:**

1. **Enable Development Mode:**
```python
# app.py - Development configuration
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,              # Enable debug mode
        use_reloader=True,       # Enable auto-reload
        use_debugger=True        # Enable debugger
    )
```

2. **Environment-based Configuration:**
```python
# Use environment variable
import os
DEBUG = os.getenv('FLASK_ENV') == 'development'
app.config['DEBUG'] = DEBUG
```

3. **Improve FORCE_RESTART.sh Script:**
   - ✅ Kill all Python processes
   - ✅ Clear `.pyc` and `__pycache__`
   - ✅ Validate code syntax
   - ⚠️ Add: Watch mode สำหรับ development

4. **Development Watch Script:**
```bash
# dev_watch.sh
while true; do
    python3 app.py &
    PID=$!
    inotifywait -r -e modify,create,delete ./
    kill $PID
    find . -name "*.pyc" -delete
done
```

5. **Cache Busting for Static Files:**
```html
<!-- Add version query string -->
<link rel="stylesheet" href="/static/css/style.css?v={{ cache_version }}">
```

**Acceptance Criteria:**
- Code changes ใน `app.py` reflect โดยอัตโนมัติภายใน 5 วินาที
- ไม่ต้อง manual clear cache
- Browser cache ไม่ block development
- Error messages แสดงชัดเจน (debug mode)

---

## 🔧 ปัญหาระยะยาว (Medium Priority)

### 4. Database Architecture - SQLite Scalability & Multi-DB Complexity
**Priority:** Medium (Technical Debt)

**Context:**  
ระบบปัจจุบันใช้ 3 SQLite databases แยกกัน (`data.db`, `price.db`, `supplier_stock.db`) ซึ่งมีข้อจำกัดด้าน scalability, performance, และความซับซ้อนใน data relationships

**ปัญหาที่พบ:**

1. **SQLite Limitations**
   - **Concurrent Writes:** SQLite lock ทั้ง database เมื่อ write → bottleneck เมื่อมี concurrent users
   - **Database Size:** SQLite performance ลดลงเมื่อ DB > 2GB (ปัจจุบัน ~3.2MB แต่จะโต)
   - **No User Management:** ไม่มี user/role management แบบ built-in
   - **Limited Data Types:** ไม่มี native JSON, Array types
   - **Write Performance:** ~1,000 writes/sec max (PostgreSQL ทำได้ ~10,000+)

2. **Multi-Database Complexity**
   - **Cross-DB Queries:** ไม่สามารถ JOIN ข้าม database ได้ → ต้อง query 2 ครั้งแล้ว merge ใน Python
   - **Transaction Consistency:** ยาก maintain ACID properties ข้าม 3 databases
   - **Foreign Key Constraints:** ไม่ enforce ข้าม DB boundaries
   - **Migration Complexity:** ต้อง migrate 3 DBs แยกกัน

3. **Backup & Recovery**
   - **Manual Backup:** ต้อง copy files เอง (`cp data.db data.db.backup`)
   - **No Point-in-Time Recovery:** ไม่มี WAL replay หรือ transaction logs
   - **No Incremental Backup:** ต้อง copy ทั้ง DB ทุกครั้ง
   - **Corruption Risk:** SQLite มีโอกาส corrupt หาก process crash ตอน write

4. **Monitoring & Observability**
   - ไม่มี query performance metrics
   - ไม่มี slow query logs
   - ยากต่อการ debug query performance issues
   - ไม่มี connection pooling

**แนวทางแก้ไข (3 Options):**

**Option 1: Migrate to PostgreSQL (Recommended)**
```
Pros:
- Better concurrent write performance
- Built-in backup/restore (pg_dump/pg_restore)
- Point-in-time recovery (PITR)
- Advanced data types (JSON, Array)
- Query optimization tools
- Connection pooling

Cons:
- Infrastructure change (need PostgreSQL server)
- Migration effort (~2-3 weeks)
- Hosting cost increase
```

**Option 2: Consolidate to Single SQLite DB**
```
Pros:
- Single source of truth
- Easier cross-table queries
- Single migration path
- Lower complexity

Cons:
- Still has SQLite limitations
- Larger single file (~10-20MB)
- Migration effort (~1 week)
```

**Option 3: Keep Multi-DB but Improve Backup**
```
Pros:
- No architecture change
- Quick implementation
- Lower risk

Cons:
- Doesn't solve scalability
- Doesn't solve concurrent writes
- Band-aid solution
```

**Recommended Approach (Phased Migration):**

**Phase 1 (Immediate):**
1. Automated SQLite Backup Script
   - Cron job: backup ทุก 6 ชั่วโมง
   - Retention: 7 days daily + 4 weeks weekly
2. Add SQLAlchemy Connection Pooling
3. Monitor DB file sizes

**Phase 2 (3 months):**
1. Consolidate to Single SQLite DB
2. Add database migration tool (Alembic)
3. Improve error handling & retry logic

**Phase 3 (6 months):**
1. Migrate to PostgreSQL
2. Setup read replicas
3. Implement proper monitoring

**Acceptance Criteria:**
- Zero data loss during migrations
- < 1 hour downtime for DB migration
- Automated daily backups with verification
- Query performance ≤ 500ms (p95)

---

### 5. Notification System - No Proactive Alerts
**Priority:** Medium (User Experience)

**Context:**  
ระบบปัจจุบันไม่มี proactive notification mechanism ทำให้ผู้ใช้ต้อง manually check dashboard เพื่อดูสถานะออเดอร์, สต็อก, และ SLA deadlines

**ปัญหาที่พบ:**
- **No Low Stock Alerts:** ไม่แจ้งเตือนเมื่อสต็อก SKU ใดๆ เหลือน้อย (< threshold)
- **No SLA Breach Warnings:** ไม่แจ้งเตือนเมื่อออเดอร์ใกล้เกิน due date
- **No New Order Notifications:** ไม่แจ้งเตือนเมื่อมีการ import orders ใหม่
- **Manual Monitoring Required:** ต้องเปิด dashboard refresh เพื่อดูข้อมูล real-time

**Business Impact:**
- พลาด SLA deadlines → customer complaints
- สต็อกหมดกะทันหัน → orders ค้าง
- ล่าช้าในการรับ orders → workflow delays

**แนวทางแก้ไข:**

**Notification Channels (Priority Order):**

1. **Web Push Notifications (Quick Win)**
   ```javascript
   // Browser notification API
   if (Notification.permission === "granted") {
       new Notification("Low Stock Alert", {
           body: "SKU ABC123 stock: 2 units",
           icon: "/static/icon.png"
       });
   }
   ```
   - **Pros:** Real-time, no email spam, cross-device
   - **Cons:** Requires user permission, browser-dependent

2. **Email Notifications (Must-have)**
   ```python
   # Using Flask-Mail
   from flask_mail import Mail, Message
   
   def send_sla_alert(order_id, due_date):
       msg = Message(
           f"SLA Alert: Order {order_id}",
           recipients=["warehouse@company.com"],
           body=f"Order {order_id} due: {due_date}"
       )
       mail.send(msg)
   ```
   - **Pros:** Reliable, supports attachments, formal
   - **Cons:** Email overload, spam filters

3. **LINE Notify (Thailand-specific)**
   ```python
   import requests
   
   def send_line_notify(message):
       headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
       data = {"message": message}
       requests.post(
           "https://notify-api.line.me/api/notify",
           headers=headers,
           data=data
       )
   ```
   - **Pros:** Popular in Thailand, instant, free
   - **Cons:** Requires LINE account, API token management

4. **In-App Notifications (Future)**
   - Bell icon badge count
   - Notification center panel
   - Persistent notification history

**Alert Types & Triggers:**

| Alert Type | Trigger Condition | Urgency | Channel |
|-----------|------------------|---------|---------|
| Low Stock | stock_qty < 5 | High | Email + LINE |
| Stock Out | stock_qty = 0 | Critical | All channels |
| SLA Warning | due_date - today ≤ 1 day | High | Email + Web Push |
| SLA Breach | today > due_date | Critical | All channels |
| New Orders | import_count > 0 | Medium | LINE |
| Large Order | order_qty > 100 | Medium | Email |

**Implementation Plan:**

**Phase 1 (1 week):**
- Email notifications สำหรับ Low Stock & SLA
- Configurable thresholds ในหน้า Settings

**Phase 2 (2 weeks):**
- LINE Notify integration
- Notification preferences per user

**Phase 3 (1 month):**
- Web Push notifications
- In-app notification center

**Acceptance Criteria:**
- ✅ Email delivered within 5 minutes of trigger event
- ✅ User can configure notification preferences
- ✅ No duplicate notifications (deduplication logic)
- ✅ Notification history stored for audit

---

### 6. Performance Optimization - Slow Dashboard with Large Datasets
**Priority:** Medium (Scalability)

**Context:**  
Dashboard performance degradation เมื่อมีออเดอร์หลายพัน records โดยเฉพาะการ load initial page และ export Excel

**Performance Bottlenecks:**

1. **N+1 Query Problem**
   ```python
   # Current: O(n) queries
   for order in orders:
       order.shop_name  # SELECT from shops table
       order.sales_status  # SELECT from sales table
   
   # Should be: O(1) with JOIN
   orders = db.session.query(OrderLine)\
       .join(Shop).join(Sales)\
       .all()
   ```

2. **Full Table Scan in Dashboard**
   - `compute_allocation()` load ทุก OrderLine records
   - ไม่มี pagination → render 5,000+ rows ในครั้งเดียว
   - DataTables client-side processing ช้า

3. **Missing Database Indexes**
   ```sql
   -- Missing indexes:
   CREATE INDEX idx_order_platform ON order_lines(platform);
   CREATE INDEX idx_order_shop ON order_lines(shop_id);
   CREATE INDEX idx_order_date ON order_lines(import_date);
   CREATE INDEX idx_order_accepted ON order_lines(accepted);
   ```

4. **No Caching Layer**
   - KPI cards recalculate ทุก page load
   - Stock quantities ถูก query ทุกครั้ง
   - Platform/Shop dropdowns query DB ทุก request

**Performance Metrics (Current vs Target):**

| Metric | Current | Target | Improvement |
|--------|---------|--------|------------|
| Dashboard Load | ~8s | < 2s | 75% faster |
| Export Excel (1000 rows) | ~15s | < 5s | 67% faster |
| Search/Filter | ~3s | < 1s | 67% faster |
| KPI Calculation | ~2s | < 500ms | 75% faster |

**Optimization Strategy:**

**Quick Wins (1 week):**
1. **Add Database Indexes**
   ```python
   # models.py
   class OrderLine(db.Model):
       __tablename__ = 'order_lines'
       __table_args__ = (
           db.Index('idx_platform_shop', 'platform', 'shop_id'),
           db.Index('idx_import_date', 'import_date'),
           db.Index('idx_accepted', 'accepted'),
       )
   ```

2. **Enable SQLAlchemy Query Caching**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   
   @cache.memoize(timeout=300)  # 5 minutes
   def get_kpi_stats():
       return compute_allocation(db.session, {})
   ```

3. **Server-side Pagination**
   ```javascript
   // DataTables server-side processing
   $('#orders-table').DataTable({
       serverSide: true,
       ajax: '/api/orders',
       pageLength: 100
   });
   ```

**Medium-term (1 month):**
1. **Eager Loading (JOIN queries)**
2. **Background Jobs for Heavy Operations**
   ```python
   # Using Celery
   @celery.task
   def export_excel_async(filters):
       # Generate Excel in background
       # Send download link via email
   ```

3. **Response Compression**
   ```python
   from flask_compress import Compress
   Compress(app)  # Gzip responses
   ```

**Long-term (3 months):**
1. **Redis Caching Layer**
2. **Database Query Optimization**
3. **CDN for Static Assets**

**Acceptance Criteria:**
- Dashboard load < 2 seconds (p95)
- Support 10,000+ active orders
- Export Excel < 5 seconds for 1,000 rows
- Lighthouse Performance Score > 80

---

### 7. Error Handling & Logging - Poor Observability
**Priority:** Medium (Operations & Debugging)

**Context:**  
ระบบขาดการจัดการ errors และ logging ที่เป็นระบบ ทำให้ยากต่อการ debug production issues และ track down root causes

**ปัญหาที่พบ:**
- **Generic Error Messages:** แสดง "An error occurred" โดยไม่ระบุรายละเอียด
- **No Structured Logging:** log เป็น plain text ไม่มี timestamp, severity, context
- **Missing Error Context:** ไม่บันทึก user action, request parameters เมื่อ error เกิด
- **No Error Tracking:** ไม่รู้ว่า error ใดเกิดบ่อย, กระทบ user กี่คน
- **Silent Failures:** บาง operations fail แต่ไม่แสดง error (e.g., email send failure)

**Current Error Handling:**
```python
# ❌ Bad: Generic error handling
try:
    process_order(order_id)
except Exception as e:
    print(f"Error: {e}")  # Lost in logs
    return "Error occurred"  # No details for user
```

**Improved Error Handling:**

**1. Structured Logging with Python `logging` module**
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10MB, backupCount=5)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Usage:
app.logger.info(f"Order {order_id} processed successfully")
app.logger.error(f"Failed to process order {order_id}", exc_info=True)
```

**2. User-Friendly Error Messages**
```python
ERROR_MESSAGES = {
    'STOCK_NOT_ENOUGH': 'สต็อกไม่พอสำหรับ SKU: {sku} (มี {available}, ต้องการ {required})',
    'ORDER_NOT_FOUND': 'ไม่พบออเดอร์หมายเลข: {order_id}',
    'IMPORT_FAILED': 'นำเข้าข้อมูลล้มเหลว: {reason}'
}

def format_error(error_code, **kwargs):
    return ERROR_MESSAGES[error_code].format(**kwargs)
```

**3. Error Tracking with Sentry (Optional)**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)

# Automatic error reporting to Sentry dashboard
```

**4. Custom Error Pages**
```html
<!-- templates/errors/500.html -->
<h1>เกิดข้อผิดพลาด</h1>
<p>ระบบกำลังประสบปัญหา กรุณาลองใหม่ภายหลัง</p>
<p>รหัสอ้างอิง: {{ error_id }}</p>
```

**5. Error Monitoring Dashboard**
- Top 10 errors (by frequency)
- Error rate trend (last 7 days)
- Affected users count
- Error resolution status

**Implementation Plan:**

**Phase 1 (Quick Win):**
- Add structured logging
- Implement RotatingFileHandler
- User-friendly error messages

**Phase 2:**
- Error tracking integration (Sentry or custom)
- Custom error pages
- Error notification via email

**Phase 3:**
- Error monitoring dashboard
- Automated error categorization
- Error resolution workflow

**Acceptance Criteria:**
- All exceptions logged with full stack trace
- User sees helpful error message (not technical details)
- Critical errors trigger notifications
- 90% of production errors diagnosed within 1 hour

---

### 8. RBAC (Role-Based Access Control) - Limited Granularity
**Priority:** Low (Security & Compliance)

**Context:**  
ระบบมี 2 roles เท่านั้น (`admin` และ `user`) ทำให้ไม่สามารถแยกสิทธิ์ตาม job function ได้ละเอียด

**ปัญหาที่พบ:**
- **Only 2 Roles:** Admin (full access) กับ User (limited access)
- **No Granular Permissions:** ไม่สามารถกำหนดว่า user A ดูราคาได้ แต่ user B ไม่ได้
- **Data Exposure:** ทุกคนเห็นข้อมูลเหมือนกัน (ราคา, กำไร, supplier info)
- **No Audit Trail:** ไม่ track ว่า user ทำอะไรบ้าง

**Proposed RBAC Model:**

| Role | Permissions | Use Cases |
|------|-----------|-----------|
| **Admin** | Full access | ผู้ดูแลระบบ, Owner |
| **Warehouse Manager** | Orders, Stock, Reports | จัดการคลัง, จ่ายงาน |
| **Price Analyst** | View pricing, Edit pricing | วิเคราะห์ราคา |
| **Viewer** | Read-only | ดูข้อมูลอย่างเดียว |

**Implementation:**
```python
# models.py
class Permission:
    VIEW_ORDERS = 0x01
    ACCEPT_ORDERS = 0x02
    VIEW_PRICING = 0x04
    EDIT_PRICING = 0x08
    MANAGE_USERS = 0x10

# Decorator for route protection
@require_permission(Permission.ACCEPT_ORDERS)
def accept_order():
    # Only users with ACCEPT_ORDERS permission can access
    pass
```

**Acceptance Criteria:**
- 4+ roles defined
- Page-level access control
- Data masking for sensitive fields
- Audit log for critical actions

---

### 9. Analytics & Reporting - Limited Business Intelligence
**Priority:** Low (Business Insights)

**Context:**  
ระบบมีรายงานพื้นฐาน (Picking List, Warehouse Report) แต่ขาด business analytics และ trend analysis

**Missing Reports:**
- **Sales Summary:** ยอดขายรายวัน/รายสัปดาห์/รายเดือน
- **Platform Performance:** เปรียบเทียบ Shopee vs Lazada vs TikTok
- **SKU Analysis:** Top selling SKUs, slow-moving items
- **SLA Compliance:** เปอร์เซ็นต์การส่งของตรงเวลา
- **Trend Charts:** กราฟแสดงแนวโน้มออเดอร์, สต็อก

**Proposed Reports:**

1. **Daily Sales Dashboard**
   - Total orders by platform
   - Revenue trends
   - SLA compliance rate

2. **Inventory Turnover Report**
   - Fast-moving vs slow-moving SKUs
   - Stock aging analysis
   - Reorder recommendations

3. **Platform Comparison**
   - Orders per platform
   - Average order value
   - Processing time

**Implementation:**
```python
# Use Chart.js for visualization
<canvas id="ordersChart"></canvas>
<script>
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed'],
        datasets: [{
            label: 'Orders',
            data: [12, 19, 15]
        }]
    }
});
</script>
```

**Acceptance Criteria:**
- 5+ new reports
- Export to Excel/PDF
- Scheduled email delivery (daily/weekly)
- Chart visualization

---

### 10. Data Import - Rigid Format Requirements
**Priority:** Low (User Experience)

**Context:**  
Import function ต้องการ Excel format ที่แน่นอน ไม่ flexible และไม่มี validation ก่อน import

**ปัญหาที่พบ:**
- **Strict Format:** Column headers ต้องตรงทุกตัวอักษร
- **No CSV Support:** รองรับแค่ `.xlsx` เท่านั้น
- **No Validation Preview:** Import เลยโดยไม่มีการแสดง preview
- **No Template:** ไม่มี template Excel ให้ download
- **Poor Error Messages:** บอกแค่ "Import failed" ไม่บอกว่าผิดตรงไหน

**Proposed Improvements:**

1. **Flexible Column Mapping**
   ```python
   # Auto-detect column names (fuzzy matching)
   column_map = {
       'order id': ['order_id', 'Order ID', 'order-id'],
       'sku': ['SKU', 'sku', 'product_code']
   }
   ```

2. **Multiple Format Support**
   - Excel (.xlsx, .xls)
   - CSV (.csv)
   - Google Sheets (direct API)

3. **Import Preview**
   - Show first 10 rows
   - Highlight validation errors
   - Confirm before import

4. **Downloadable Templates**
   ```python
   @app.route('/download/template/<import_type>')
   def download_template(import_type):
       # Generate template Excel
       return send_file('templates/order_import.xlsx')
   ```

5. **Validation Rules**
   - Required fields check
   - Data type validation
   - Duplicate detection
   - Business rule validation

**Acceptance Criteria:**
- Support 3+ file formats
- Download templates available
- Import preview with validation
- Detailed error messages with row numbers

---

## 📊 สรุปลำดับความสำคัญ

### ✅ แก้ก่อน (ภายใน 1-2 สัปดาห์)
1. แทนที่ไอคอนทั้งหมดให้เหมือนกัน (Task 1)
2. ติดตามปัญหาบิลเปล่า (Task 2)
3. ปรับปรุงการ Restart Server (Task 3)

### 🔄 แก้ภายหลัง (ภายใน 1-3 เดือน)
4. ปรับปรุงฐานข้อมูล (Task 4)
5. เพิ่มระบบแจ้งเตือน (Task 5)
6. เพิ่มความเร็ว (Task 6)

### 💡 ปรับปรุงต่อเนื่อง
7. จัดการข้อผิดพลาด (Task 7)
8. ระบบสิทธิ์ละเอียด (Task 8)
9. รายงานครบถ้วน (Task 9)
10. นำเข้าข้อมูลยืดหยุ่น (Task 10)

---

## 📝 หมายเหตุสำหรับ Dev
- ไม่ต้องแก้ทุก Task พร้อมกัน
- เริ่มจาก Task เร่งด่วนก่อน
- Task ระยะยาวค่อยทำทีละอย่าง
- ทดสอบทุกครั้งหลังแก้ไข
- บันทึก Log การแก้ไขทุกครั้ง

---

**อัปเดตล่าสุด:** 2026-01-07  
**ผู้สร้าง:** Droid AI
