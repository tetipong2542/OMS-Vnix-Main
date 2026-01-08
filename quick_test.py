#!/usr/bin/env python3
"""
Quick test - ทดสอบว่าโค้ดที่แก้ไขทำงานถูกต้องหรือไม่
"""

import sqlite3
from datetime import date, datetime

print("=" * 70)
print("Quick Test: ทดสอบการนับ KPI บิลเปล่า")
print("=" * 70)

# จำลอง scope_rows จาก database
db_path = 'data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ดึงข้อมูลเหมือน compute_allocation
cursor.execute("""
    SELECT ol.id, ol.order_id, ol.sku, ol.allocation_status, ol.import_date,
           s.platform, s.name as shop_name,
           EXISTS(SELECT 1 FROM cancelled_orders co WHERE co.order_id = ol.order_id) as is_cancelled,
           CASE
               WHEN EXISTS(SELECT 1 FROM sales sa WHERE sa.order_id = ol.order_id
                          AND (LOWER(sa.status) LIKE '%ครบตามจำนวน%'
                               OR LOWER(sa.status) LIKE '%packed%'
                               OR LOWER(sa.status) LIKE '%แพ็ค%'
                               OR LOWER(sa.status) LIKE '%opened_full%'))
               THEN 1 ELSE 0
           END as is_packed
    FROM order_lines ol
    JOIN shops s ON ol.shop_id = s.id
    WHERE ol.allocation_status IS NOT NULL
    ORDER BY ol.order_id
""")

rows_db = cursor.fetchall()

# สร้าง scope_rows ในรูปแบบ dict
scope_rows = []
for row in rows_db:
    ol_id, order_id, sku, alloc_status, imp_date, platform, shop, is_cancelled, is_packed = row
    scope_rows.append({
        'id': ol_id,
        'order_id': order_id,
        'sku': sku,
        'allocation_status': alloc_status,
        'import_date': imp_date,
        'platform': platform,
        'shop': shop,
        'is_cancelled': bool(is_cancelled),
        'is_packed': bool(is_packed)
    })

print(f"\n1. จำนวน rows ทั้งหมด: {len(scope_rows)}")
print(f"   (จาก order_lines WHERE allocation_status IS NOT NULL)")

# จำลองโค้ดการนับ KPI ตามที่แก้ไข
print("\n2. กำลังนับ KPI บิลเปล่าตามโค้ดใหม่...")
print("-" * 70)

kpi_orders_bill_empty = set()
bill_empty_count_debug = 0

for r in scope_rows:
    status_alloc = (r.get("allocation_status") or "").strip().upper()
    if status_alloc == "BILL_EMPTY":
        bill_empty_count_debug += 1
        oid = (r.get("order_id") or "").strip()
        if oid:
            kpi_orders_bill_empty.add(oid)
            # แสดงรายละเอียด
            print(f"   ✓ พบ: {oid} (SKU: {r['sku']}, is_packed: {r['is_packed']}, is_cancelled: {r['is_cancelled']})")

print(f"\n3. ผลลัพธ์:")
print("-" * 70)
print(f"   จำนวนแถวที่มี allocation_status='BILL_EMPTY': {bill_empty_count_debug}")
print(f"   จำนวน Order ที่เป็น BILL_EMPTY (unique): {len(kpi_orders_bill_empty)}")
print(f"   Order IDs: {sorted(kpi_orders_bill_empty)}")

# นับแยกเก่า/ใหม่
today = date.today()

# จำลองฟังก์ชัน _count_split
def count_split(oid_set, source_rows):
    total = len(oid_set)
    old_c = 0
    today_c = 0

    # สร้าง map order_id -> import_date
    oid_date_map = {}
    for r in source_rows:
        if r.get("order_id"):
            d = r.get("import_date")
            oid_date_map[r["order_id"]] = d

    for oid in oid_set:
        d = oid_date_map.get(oid)
        is_old = True

        if d:
            if isinstance(d, datetime):
                d = d.date()
            elif isinstance(d, str):
                try:
                    d = datetime.strptime(d, "%Y-%m-%d").date()
                except:
                    d = today

            if d >= today:
                is_old = False

        if is_old:
            old_c += 1
        else:
            today_c += 1

    return total, old_c, today_c

c_bill_empty, c_bill_empty_old, c_bill_empty_new = count_split(kpi_orders_bill_empty, scope_rows)

print(f"\n4. แยกเก่า/ใหม่:")
print("-" * 70)
print(f"   รวม: {c_bill_empty}")
print(f"   ค้าง (เก่า): {c_bill_empty_old}")
print(f"   วันนี้ (ใหม่): {c_bill_empty_new}")

# แสดงรายละเอียดแต่ละ Order
print(f"\n5. รายละเอียดแต่ละ Order:")
print("-" * 70)

for oid in sorted(kpi_orders_bill_empty):
    # หา import_date
    for r in scope_rows:
        if r['order_id'] == oid:
            imp_date = r.get('import_date', 'N/A')
            is_today = str(imp_date) == str(today)
            today_marker = " ← วันนี้" if is_today else ""
            print(f"   {oid}: import_date={imp_date}{today_marker}")
            break

conn.close()

print("\n" + "=" * 70)
print("สรุป")
print("=" * 70)
print(f"""
ค่าที่ควรแสดงใน Dashboard:
  - บิลเปล่า รวม: {c_bill_empty}
  - ค้าง: {c_bill_empty_old}
  - วันนี้: {c_bill_empty_new}

ถ้า Dashboard ยังแสดง 0:
  1. Server ยังไม่ได้ restart จริง
  2. ใช้คนละ database (เช็คว่า path ถูกต้อง)
  3. มี cache ที่ browser (กด Ctrl+Shift+R)
  4. ใช้คนละ Python environment

ขั้นตอนแก้ไข:
  1. หยุด Server (Ctrl+C)
  2. ลบไฟล์ .pyc ทั้งหมด: find . -name "*.pyc" -delete
  3. รัน Server ใหม่: python3 app.py
  4. Hard Refresh Browser: Ctrl+Shift+R
""")
