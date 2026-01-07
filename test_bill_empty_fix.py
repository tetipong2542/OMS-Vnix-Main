#!/usr/bin/env python3
"""
Script ทดสอบว่าการแก้ไข BILL_EMPTY ทำงานถูกต้อง
"""

import sys
import os

# เพิ่ม path เพื่อ import modules
sys.path.insert(0, os.path.dirname(__file__))

from allocation import compute_allocation
from models import db
from app import create_app
from datetime import date

print("=" * 60)
print("ทดสอบการแก้ไข BILL_EMPTY")
print("=" * 60)

# สร้าง app context
app = create_app() if hasattr(sys.modules['app'], 'create_app') else sys.modules['app'].app

with app.app_context():
    print("\n1. ทดสอบ compute_allocation...")
    print("-" * 60)

    # เรียก compute_allocation โดยไม่มี filter
    filters = {
        "platform": "Shopee",
        "active_only": False,
        "all_time": True
    }

    rows, kpis = compute_allocation(db.session, filters)

    print(f"จำนวน rows ทั้งหมด: {len(rows)}")

    # หา rows ที่มี allocation_status = 'BILL_EMPTY'
    bill_empty_rows = [r for r in rows if r.get("allocation_status") == "BILL_EMPTY"]

    print(f"จำนวน rows ที่มี allocation_status = 'BILL_EMPTY': {len(bill_empty_rows)}")

    if bill_empty_rows:
        print("\nตัวอย่าง BILL_EMPTY rows:")
        for i, r in enumerate(bill_empty_rows[:5], 1):
            print(f"\n  {i}. Order: {r.get('order_id')}")
            print(f"     SKU: {r.get('sku')}")
            print(f"     Status: {r.get('allocation_status')}")
            print(f"     is_packed: {r.get('is_packed')}")
            print(f"     is_cancelled: {r.get('is_cancelled')}")
            print(f"     import_date: {r.get('import_date')}")

    print("\n2. ทดสอบการนับ KPI...")
    print("-" * 60)

    # จำลองการนับ KPI แบบเดียวกับใน dashboard
    scope_rows = rows
    today_date = date.today()

    kpi_orders_bill_empty = set()
    for r in scope_rows:
        # ใช้ is_packed แทน packed
        if not r.get("is_packed") and not r.get("is_cancelled"):
            status_alloc = (r.get("allocation_status") or "").strip().upper()
            if status_alloc == "BILL_EMPTY":
                oid = (r.get("order_id") or "").strip()
                if oid:
                    kpi_orders_bill_empty.add(oid)

    print(f"จำนวน Order ที่เป็น BILL_EMPTY (set): {len(kpi_orders_bill_empty)}")
    print(f"Order IDs: {sorted(kpi_orders_bill_empty)}")

    # นับแยกเก่า/ใหม่
    def _count_split(oid_set, source_rows):
        """ฟังก์ชันช่วยนับ: คืนค่า (total, old_count, today_count)"""
        total = len(oid_set)
        old_c = 0
        today_c = 0

        # สร้าง Dict เพื่อ map order_id -> import_date จาก source_rows
        oid_date_map = {}
        for r in source_rows:
            if r.get("order_id"):
                d = r.get("import_date")
                oid_date_map[r["order_id"]] = d

        for oid in oid_set:
            d = oid_date_map.get(oid)
            # ตรวจสอบว่าเป็นเก่าหรือใหม่
            is_old = True
            if d:
                # แปลงเป็น date object ถ้าจำเป็น
                from datetime import datetime
                if isinstance(d, datetime):
                    d = d.date()
                elif isinstance(d, str):
                    try:
                        d = datetime.strptime(d, "%Y-%m-%d").date()
                    except:
                        d = today_date

                if d >= today_date:
                    is_old = False

            if is_old:
                old_c += 1
            else:
                today_c += 1

        return total, old_c, today_c

    c_bill_empty, c_bill_empty_old, c_bill_empty_new = _count_split(kpi_orders_bill_empty, scope_rows)

    print(f"\nผลลัพธ์:")
    print(f"  รวม: {c_bill_empty}")
    print(f"  ค้าง (เก่า): {c_bill_empty_old}")
    print(f"  วันนี้ (ใหม่): {c_bill_empty_new}")

    print("\n3. ตรวจสอบว่าตรงกับ Database หรือไม่...")
    print("-" * 60)

    # Query โดยตรงจาก DB
    from sqlalchemy import text
    result = db.session.execute(text("""
        SELECT import_date, COUNT(DISTINCT order_id) as count
        FROM order_lines
        WHERE allocation_status = 'BILL_EMPTY'
        GROUP BY import_date
        ORDER BY import_date DESC
    """)).fetchall()

    db_total = 0
    db_today = 0
    db_old = 0

    print("จำนวนบิลเปล่าจาก DB (แยกตามวันที่):")
    for imp_date, count in result:
        db_total += count
        if str(imp_date) == str(today_date):
            db_today += count
            print(f"  {imp_date}: {count} Order ← วันนี้")
        else:
            db_old += count
            print(f"  {imp_date}: {count} Order")

    print(f"\nสรุปจาก DB:")
    print(f"  รวม: {db_total}")
    print(f"  ค้าง (เก่า): {db_old}")
    print(f"  วันนี้ (ใหม่): {db_today}")

    print("\n" + "=" * 60)
    print("สรุปผลการทดสอบ")
    print("=" * 60)

    if c_bill_empty == db_total and c_bill_empty_new == db_today and c_bill_empty_old == db_old:
        print("✅ ผ่าน! ตัวเลขตรงกับ Database ทุกอย่าง")
    else:
        print("❌ ไม่ผ่าน! ตัวเลขไม่ตรงกับ Database")
        print(f"\nความแตกต่าง:")
        print(f"  รวม: KPI={c_bill_empty}, DB={db_total} (ต่าง {c_bill_empty - db_total})")
        print(f"  วันนี้: KPI={c_bill_empty_new}, DB={db_today} (ต่าง {c_bill_empty_new - db_today})")
        print(f"  ค้าง: KPI={c_bill_empty_old}, DB={db_old} (ต่าง {c_bill_empty_old - db_old})")

    print("\n" + "=" * 60)
    print("การดำเนินการต่อไป")
    print("=" * 60)
    print("""
1. ถ้าผ่านการทดสอบ → Restart server แล้วเข้า Dashboard
2. ไปที่ Dashboard แล้วเลือก Platform = Shopee (หรือทั้งหมด)
3. ตรวจสอบ Card KPI "บิลเปล่า" ว่าแสดงตัวเลขถูกต้องหรือไม่
4. ถ้ายังไม่แสดง → อาจต้องล้าง cache หรือ hard refresh (Ctrl+Shift+R)
    """)
