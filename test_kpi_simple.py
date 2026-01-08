#!/usr/bin/env python3
"""
Script ทดสอบแบบง่ายว่า KPI จะนับได้ถูกต้องหรือไม่
"""

import sqlite3
from datetime import date

db_path = 'data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("ทดสอบการนับ KPI บิลเปล่า")
print("=" * 60)

today = date.today()
print(f"วันนี้: {today}\n")

# 1. ดึงข้อมูล Order ที่มี allocation_status = 'BILL_EMPTY'
cursor.execute("""
    SELECT ol.id, ol.order_id, ol.sku, ol.allocation_status, ol.import_date,
           s.platform, s.name as shop_name,
           EXISTS(SELECT 1 FROM cancelled_orders co WHERE co.order_id = ol.order_id) as is_cancelled
    FROM order_lines ol
    JOIN shops s ON ol.shop_id = s.id
    WHERE ol.allocation_status = 'BILL_EMPTY'
    ORDER BY ol.import_date DESC, ol.order_id
""")

bill_empty_rows = cursor.fetchall()

print(f"1. จำนวน OrderLine ที่มี allocation_status = 'BILL_EMPTY': {len(bill_empty_rows)}")
print("-" * 60)

# จัดกลุ่มตาม order_id
orders_by_date = {}
for row in bill_empty_rows:
    ol_id, order_id, sku, status, imp_date, platform, shop, is_cancelled = row

    # เช็คว่า is_packed หรือไม่ (จากตาราง sales)
    cursor.execute("""
        SELECT status FROM sales WHERE order_id = ? LIMIT 1
    """, (order_id,))
    sales_row = cursor.fetchone()

    is_packed = False
    if sales_row and sales_row[0]:
        s_label = sales_row[0].lower()
        if any(kw in s_label for kw in ["ครบตามจำนวน", "packed", "แพ็คแล้ว", "opened_full"]):
            is_packed = True

    # เก็บข้อมูล
    if imp_date not in orders_by_date:
        orders_by_date[imp_date] = {}

    if order_id not in orders_by_date[imp_date]:
        orders_by_date[imp_date][order_id] = {
            'platform': platform,
            'shop': shop,
            'is_cancelled': bool(is_cancelled),
            'is_packed': is_packed,
            'lines': []
        }

    orders_by_date[imp_date][order_id]['lines'].append({
        'ol_id': ol_id,
        'sku': sku
    })

print("\n2. แยกตามวันที่ Import:")
print("-" * 60)

total_orders = 0
today_orders = 0
old_orders = 0

for imp_date in sorted(orders_by_date.keys(), reverse=True):
    orders = orders_by_date[imp_date]

    # [แก้ไข] บิลเปล่านับทั้งหมด ไม่กรอง packed/cancelled
    valid_orders = orders

    count = len(valid_orders)
    total_orders += count

    is_today = str(imp_date) == str(today)
    if is_today:
        today_orders += count
        print(f"  {imp_date}: {count} Order ← วันนี้")
    else:
        old_orders += count
        print(f"  {imp_date}: {count} Order")

    # แสดงรายละเอียด Order
    for oid, data in list(valid_orders.items())[:3]:  # แสดงแค่ 3 orders แรก
        print(f"    - {oid} ({data['platform']}/{data['shop']}) - {len(data['lines'])} items")

print(f"\n3. สรุปผลลัพธ์:")
print("-" * 60)
print(f"รวมทั้งหมด (ไม่นับ packed/cancelled): {total_orders} Orders")
print(f"  - ค้าง (เก่า): {old_orders} Orders")
print(f"  - วันนี้ (ใหม่): {today_orders} Orders")

print("\n4. ตรวจสอบ Order ที่ถูก Packed/Cancelled:")
print("-" * 60)

packed_count = 0
cancelled_count = 0

for imp_date, orders in orders_by_date.items():
    for oid, data in orders.items():
        if data['is_packed']:
            packed_count += 1
        if data['is_cancelled']:
            cancelled_count += 1

print(f"Order ที่ถูก Packed (ไม่นับใน KPI): {packed_count}")
print(f"Order ที่ถูก Cancelled (ไม่นับใน KPI): {cancelled_count}")

conn.close()

print("\n" + "=" * 60)
print("สรุป")
print("=" * 60)
print(f"""
ค่าที่ควรแสดงใน Dashboard:
  - บิลเปล่า รวม: {total_orders}
  - ค้าง: {old_orders}
  - วันนี้: {today_orders}

ถ้า Dashboard ยังแสดง 0:
1. ✅ แก้โค้ดแล้ว (is_packed แทน packed)
2. ⚠️  ต้อง Restart Server!
3. ⚠️  ตรวจสอบว่าเลือก Platform/Shop ถูกต้อง
4. ⚠️  Hard Refresh (Ctrl+Shift+R) ใน Browser
""")
