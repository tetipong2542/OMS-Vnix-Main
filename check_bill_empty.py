#!/usr/bin/env python3
"""
Script ตรวจสอบปัญหา BILL_EMPTY ไม่แสดงใน Dashboard
"""

import sqlite3
import os
from datetime import datetime, date

# หา path ของ database
db_path = os.path.join(os.path.dirname(__file__), 'data.db')

if not os.path.exists(db_path):
    # ลองหาใน instance/database.db
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ database")
        print("ลองหาที่: data.db หรือ instance/database.db")
        exit(1)

print(f"✅ พบไฟล์ database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ===== 1. ตรวจสอบว่ามี column allocation_status หรือไม่ =====
print("=" * 60)
print("1. ตรวจสอบ Schema ตาราง order_lines")
print("=" * 60)

cursor.execute("PRAGMA table_info(order_lines)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print(f"จำนวน columns: {len(columns)}")
if 'allocation_status' in column_names:
    print("✅ มี column 'allocation_status' ในตาราง order_lines")
else:
    print("❌ ไม่มี column 'allocation_status' ในตาราง order_lines")
    print("   → ต้องเพิ่ม column นี้ก่อน!")

print(f"\nColumns ทั้งหมด: {', '.join(column_names)}\n")

# ===== 2. ตรวจสอบ ImportLog ของ BILL_EMPTY =====
print("=" * 60)
print("2. ตรวจสอบ Import Log ของบิลเปล่า")
print("=" * 60)

try:
    cursor.execute("""
        SELECT id, import_date, filename, added_count, duplicates_count, failed_count, created_at
        FROM import_logs
        WHERE platform = 'EMPTY_BILL_SYSTEM'
        ORDER BY created_at DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()

    if logs:
        print(f"พบ {len(logs)} รายการ Import บิลเปล่า:\n")
        for log in logs:
            log_id, imp_date, filename, added, dupes, failed, created = log
            print(f"  ID: {log_id}")
            print(f"  วันที่ Import: {imp_date}")
            print(f"  ไฟล์: {filename}")
            print(f"  สำเร็จ (ใหม่): {added}")
            print(f"  ซ้ำ: {dupes}")
            print(f"  ล้มเหลว: {failed}")
            print(f"  เวลา: {created}")
            print()
    else:
        print("❌ ไม่พบประวัติการ Import บิลเปล่า")
        print("   → ยังไม่เคย Import บิลเปล่าเลย หรือ Import ไม่สำเร็จ\n")
except Exception as e:
    print(f"❌ Error: {e}")
    print("   → อาจไม่มีตาราง import_logs หรือ column ไม่ครบ\n")

# ===== 3. ตรวจสอบว่ามี Order ที่มี allocation_status = 'BILL_EMPTY' หรือไม่ =====
print("=" * 60)
print("3. ตรวจสอบ Order ที่มี allocation_status = 'BILL_EMPTY'")
print("=" * 60)

if 'allocation_status' in column_names:
    cursor.execute("""
        SELECT id, order_id, sku, allocation_status, import_date, accepted,
               scanned_at IS NOT NULL as scanned
        FROM order_lines
        WHERE allocation_status = 'BILL_EMPTY'
        LIMIT 20
    """)
    bill_empty_orders = cursor.fetchall()

    if bill_empty_orders:
        print(f"✅ พบ {len(bill_empty_orders)} รายการที่มี allocation_status = 'BILL_EMPTY':\n")
        for order in bill_empty_orders:
            ol_id, order_id, sku, status, imp_date, accepted, scanned = order
            print(f"  ID: {ol_id}")
            print(f"  Order ID: {order_id}")
            print(f"  SKU: {sku}")
            print(f"  Status: {status}")
            print(f"  Import Date: {imp_date}")
            print(f"  Accepted: {accepted}")
            print(f"  Scanned: {scanned}")
            print()
    else:
        print("❌ ไม่พบ Order ใดๆ ที่มี allocation_status = 'BILL_EMPTY'")
        print("   → ต้อง Import บิลเปล่าก่อน หรือ Import ไม่สำเร็จ\n")

    # นับแยกตามวันที่
    today = date.today()
    cursor.execute("""
        SELECT import_date, COUNT(DISTINCT order_id) as count
        FROM order_lines
        WHERE allocation_status = 'BILL_EMPTY'
        GROUP BY import_date
        ORDER BY import_date DESC
    """)
    date_counts = cursor.fetchall()

    if date_counts:
        print("จำนวนบิลเปล่าแยกตามวันที่ Import:")
        for imp_date, count in date_counts:
            is_today = " ← วันนี้" if str(imp_date) == str(today) else ""
            print(f"  {imp_date}: {count} Order{is_today}")
        print()
else:
    print("❌ ข้าม - ไม่มี column allocation_status\n")

# ===== 4. ตรวจสอบ Order ทั้งหมดที่มีใน order_lines =====
print("=" * 60)
print("4. สถิติ Order ทั้งหมด")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM order_lines")
total = cursor.fetchone()[0]
print(f"จำนวน Order Lines ทั้งหมด: {total}")

cursor.execute("SELECT COUNT(DISTINCT order_id) FROM order_lines")
unique_orders = cursor.fetchone()[0]
print(f"จำนวน Order ID ไม่ซ้ำ: {unique_orders}")

# ===== 5. ตรวจสอบ Order ที่ถูก Packed/Cancelled =====
print("\n" + "=" * 60)
print("5. ตรวจสอบสถานะ Packed/Cancelled ของบิลเปล่า")
print("=" * 60)

if 'allocation_status' in column_names:
    # ตรวจสอบว่า Order ที่เป็น BILL_EMPTY มี is_cancelled หรือ packed หรือไม่
    cursor.execute("""
        SELECT ol.order_id, ol.allocation_status,
               EXISTS(SELECT 1 FROM cancelled_orders co WHERE co.order_id = ol.order_id) as is_cancelled,
               ol.sku, ol.import_date
        FROM order_lines ol
        WHERE ol.allocation_status = 'BILL_EMPTY'
        LIMIT 10
    """)
    bill_empty_status = cursor.fetchall()

    if bill_empty_status:
        print(f"ตรวจสอบสถานะของบิลเปล่า {len(bill_empty_status)} รายการแรก:\n")
        for order_id, status, is_cancelled, sku, imp_date in bill_empty_status:
            print(f"  Order: {order_id}")
            print(f"    Status: {status}")
            print(f"    Cancelled: {'ใช่ ❌' if is_cancelled else 'ไม่'}")
            print(f"    SKU: {sku}")
            print(f"    Import Date: {imp_date}")
            print()

        # นับว่ามี bill_empty ที่ถูก cancel กี่ตัว
        cursor.execute("""
            SELECT COUNT(DISTINCT ol.order_id)
            FROM order_lines ol
            WHERE ol.allocation_status = 'BILL_EMPTY'
              AND EXISTS(SELECT 1 FROM cancelled_orders co WHERE co.order_id = ol.order_id)
        """)
        cancelled_count = cursor.fetchone()[0]

        if cancelled_count > 0:
            print(f"⚠️ พบ {cancelled_count} Order ที่เป็น BILL_EMPTY แต่ถูกยกเลิก")
            print("   → Order เหล่านี้จะไม่แสดงใน Dashboard (ถูกกรองออก)\n")
    else:
        print("ไม่มีข้อมูลให้ตรวจสอบ\n")

conn.close()

print("=" * 60)
print("สรุป")
print("=" * 60)
print("""
ถ้าตัวเลขยังเป็น 0:
1. ✅ ต้องมี column 'allocation_status' ในตาราง order_lines
2. ✅ ต้องมีการ Import บิลเปล่าสำเร็จ (added_count > 0)
3. ✅ Order ที่ Import ต้องไม่ถูก Cancel/Packed
4. ✅ Restart server หลังแก้ไขโค้ด

วิธีแก้:
- ถ้าไม่มี column → รัน migration หรือเพิ่ม column ด้วยมือ
- ถ้ายังไม่เคย Import → Import บิลเปล่าที่หน้า /import/bill_empty
- ถ้า Import แล้วแต่ Order ID ไม่ตรง → ตรวจสอบ Excel/Google Sheet
""")
