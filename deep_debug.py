#!/usr/bin/env python3
"""
Deep Debug - ตรวจสอบทุกขั้นตอนว่าทำไมบิลเปล่ายังเป็น 0
"""

import sqlite3
import sys
from datetime import date

print("=" * 80)
print("DEEP DEBUG - ตรวจสอบทุกขั้นตอน")
print("=" * 80)

db_path = 'data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ===== STEP 1: ตรวจสอบ Database =====
print("\n[STEP 1] ตรวจสอบฐานข้อมูล")
print("-" * 80)

cursor.execute("SELECT COUNT(*) FROM order_lines WHERE allocation_status = 'BILL_EMPTY'")
bill_empty_count = cursor.fetchone()[0]
print(f"✓ จำนวน OrderLine ที่มี allocation_status='BILL_EMPTY': {bill_empty_count}")

if bill_empty_count == 0:
    print("\n❌ ปัญหา: ไม่มี OrderLine ใดๆ ที่มี allocation_status='BILL_EMPTY' ใน Database!")
    print("   → ต้อง Import บิลเปล่าก่อน ที่หน้า /import/bill_empty")
    sys.exit(1)

# ดึงข้อมูล Order ที่เป็น BILL_EMPTY
cursor.execute("""
    SELECT DISTINCT ol.order_id, ol.import_date, s.platform, s.name
    FROM order_lines ol
    JOIN shops s ON ol.shop_id = s.id
    WHERE ol.allocation_status = 'BILL_EMPTY'
    ORDER BY ol.import_date DESC
""")
bill_empty_orders = cursor.fetchall()

print(f"✓ จำนวน Order (unique) ที่เป็น BILL_EMPTY: {len(bill_empty_orders)}")
print("\nรายละเอียด Order:")
for order_id, imp_date, platform, shop in bill_empty_orders:
    print(f"  - {order_id} | {platform}/{shop} | import_date: {imp_date}")

# ===== STEP 2: ตรวจสอบว่า allocation.py อ่านค่าจาก DB หรือไม่ =====
print("\n[STEP 2] ตรวจสอบ allocation.py")
print("-" * 80)

with open('allocation.py', 'r', encoding='utf-8') as f:
    allocation_code = f.read()

if 'db_allocation_status' in allocation_code:
    print("✓ allocation.py มีการอ่าน db_allocation_status จาก DB")
else:
    print("❌ allocation.py ไม่มีการอ่าน db_allocation_status!")
    print("   → ต้องแก้ไข allocation.py")

if 'if r["allocation_status"] == "BILL_EMPTY":' in allocation_code:
    print("✓ allocation.py มีการเช็คว่า allocation_status == 'BILL_EMPTY'")
else:
    print("❌ allocation.py ไม่มีการป้องกันการ override BILL_EMPTY!")

# ===== STEP 3: ตรวจสอบ app.py =====
print("\n[STEP 3] ตรวจสอบ app.py")
print("-" * 80)

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

if 'BILL_EMPTY DEBUG' in app_code:
    print("✓ app.py มี debug logging")
else:
    print("❌ app.py ไม่มี debug logging!")

# เช็คว่าไม่กรอง is_packed สำหรับบิลเปล่า
if 'status_alloc == "BILL_EMPTY":' in app_code:
    # หาบรรทัดที่มี status_alloc == "BILL_EMPTY"
    lines = app_code.split('\n')
    for i, line in enumerate(lines):
        if 'status_alloc == "BILL_EMPTY"' in line:
            # เช็ค 5 บรรทัดก่อนหน้า
            prev_lines = '\n'.join(lines[max(0, i-5):i])
            if 'if not r.get("is_packed")' in prev_lines:
                print("❌ app.py ยังมีการกรอง is_packed สำหรับบิลเปล่า!")
                print(f"   → บรรทัด {i}: มีการเช็ค is_packed ก่อนเช็ค BILL_EMPTY")
            else:
                print("✓ app.py ไม่กรอง is_packed สำหรับบิลเปล่า")
            break

# ===== STEP 4: จำลองการทำงานของ compute_allocation =====
print("\n[STEP 4] จำลอง compute_allocation")
print("-" * 80)

# ดึงข้อมูลแบบที่ compute_allocation ทำ (ไม่กรอง platform/shop)
cursor.execute("""
    SELECT ol.id, ol.order_id, ol.sku, ol.allocation_status, ol.import_date,
           s.platform, s.name as shop_name
    FROM order_lines ol
    JOIN shops s ON ol.shop_id = s.id
    WHERE ol.allocation_status = 'BILL_EMPTY'
""")
rows_from_db = cursor.fetchall()

print(f"✓ compute_allocation จะได้ {len(rows_from_db)} แถวที่มี allocation_status='BILL_EMPTY'")

# ===== STEP 5: ตรวจสอบ Filter ที่ Dashboard =====
print("\n[STEP 5] ตรวจสอบ Filter")
print("-" * 80)

print("Order ที่เป็น BILL_EMPTY อยู่ที่:")
platforms = set()
shops = set()
for row in rows_from_db:
    platforms.add(row[5])  # platform
    shops.add(row[6])      # shop_name

print(f"  Platform: {', '.join(sorted(platforms))}")
print(f"  Shop: {', '.join(sorted(shops))}")

print("\n⚠️  สำคัญ! ต้องเลือก Filter ใน Dashboard:")
print(f"  - Platform = {', '.join(sorted(platforms))} (หรือ 'ทั้งหมด')")
print(f"  - Shop = {', '.join(sorted(shops))} (หรือ 'ทั้งหมด')")

# ===== STEP 6: ตรวจสอบว่า Server รันอยู่หรือไม่ =====
print("\n[STEP 6] ตรวจสอบ Server")
print("-" * 80)

import subprocess

try:
    result = subprocess.run(['pgrep', '-f', 'python.*app.py'],
                          capture_output=True, text=True)
    if result.returncode == 0:
        pids = result.stdout.strip().split('\n')
        print(f"✓ Server กำลังรัน (PID: {', '.join(pids)})")
        print("  ⚠️  ต้อง RESTART Server เพื่อ reload โค้ด!")
    else:
        print("❌ Server ไม่ได้รัน!")
        print("   → ต้องรัน Server: python3 app.py")
except:
    print("⚠️  ไม่สามารถตรวจสอบ Server ได้")

# ===== STEP 7: ตรวจสอบ .pyc cache =====
print("\n[STEP 7] ตรวจสอบ Cache")
print("-" * 80)

import os
pyc_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_files.append(os.path.join(root, file))

if pyc_files:
    print(f"⚠️  พบ {len(pyc_files)} ไฟล์ .pyc (cache)")
    print("   → ควรลบด้วย: find . -name '*.pyc' -delete")
else:
    print("✓ ไม่มีไฟล์ .pyc")

# ===== STEP 8: สรุปและแนะนำ =====
print("\n" + "=" * 80)
print("สรุปและแนะนำ")
print("=" * 80)

print(f"""
✅ สิ่งที่ถูกต้อง:
  - มี {bill_empty_count} OrderLine ที่เป็น BILL_EMPTY ใน Database
  - มี {len(bill_empty_orders)} Order (unique) ที่เป็น BILL_EMPTY

⚠️  สิ่งที่ต้องทำ:
  1. หยุด Server: pkill -9 -f "python.*app.py"
  2. ลบ cache: find . -name "*.pyc" -delete
  3. รัน Server: python3 app.py
  4. เปิด Dashboard: http://localhost:5000/dashboard
  5. เลือก Platform = {', '.join(sorted(platforms))} (หรือทั้งหมด)
  6. เลือก Shop = {', '.join(sorted(shops))} (หรือทั้งหมด)
  7. กด Ctrl+Shift+R (Hard Refresh)

📊 ค่าที่ควรเห็น:
  - บิลเปล่า รวม: {len(bill_empty_orders)}
  - ค้าง: {len([o for o in bill_empty_orders if str(o[1]) != str(date.today())])}
  - วันนี้: {len([o for o in bill_empty_orders if str(o[1]) == str(date.today())])}

🔍 ถ้ายังเป็น 0:
  รัน: tail -f app.log | grep "BILL_EMPTY DEBUG"
  แล้ว refresh Dashboard เพื่อดู log
""")

conn.close()
