#!/usr/bin/env python3
"""
Diagnose Script - ตรวจสอบว่า Backend คำนวณ KPI บิลเปล่าถูกต้องหรือไม่
"""

import sys
from datetime import date, datetime
from app import app, db
from allocation import compute_allocation

def main():
    print("=" * 80)
    print("DIAGNOSE: ตรวจสอบการคำนวณ KPI บิลเปล่า")
    print("=" * 80)

    # จำลองการเรียก compute_allocation เหมือนที่ app.py ทำ
    print("\n[STEP 1] เรียก compute_allocation() เหมือน app.py")
    print("-" * 80)

    try:
        # เรียก compute_allocation โดยไม่กรอง (เหมือน default view)
        # [สำคัญ] ต้องใช้ active_only=True เพื่อจำลอง Default View ของ Dashboard
        filters = {"active_only": True}
        scope_rows, kpis_from_allocation = compute_allocation(db.session, filters)

        print(f"✓ compute_allocation คืนค่า {len(scope_rows)} แถว")
        print(f"✓ KPIs จาก compute_allocation: {kpis_from_allocation}")

    except Exception as e:
        print(f"❌ Error เรียก compute_allocation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ตรวจสอบว่ามีแถวที่เป็น BILL_EMPTY หรือไม่
    print("\n[STEP 2] ตรวจสอบ allocation_status ใน scope_rows")
    print("-" * 80)

    bill_empty_rows = []
    allocation_status_count = {}

    for r in scope_rows:
        status = (r.get("allocation_status") or "").strip().upper()

        # นับจำนวนแต่ละสถานะ
        allocation_status_count[status] = allocation_status_count.get(status, 0) + 1

        # เก็บแถวที่เป็น BILL_EMPTY
        if status == "BILL_EMPTY":
            bill_empty_rows.append(r)

    print(f"จำนวนแถวแต่ละ allocation_status:")
    for status, count in sorted(allocation_status_count.items()):
        print(f"  - {status}: {count}")

    print(f"\n✓ พบแถวที่มี allocation_status='BILL_EMPTY': {len(bill_empty_rows)}")

    if len(bill_empty_rows) == 0:
        print("\n❌ ปัญหา: ไม่มีแถวใดที่มี allocation_status='BILL_EMPTY'")
        print("   → allocation.py ไม่ได้ส่งค่า BILL_EMPTY มา!")
        sys.exit(1)

    # แสดงรายละเอียดแถวที่เป็น BILL_EMPTY
    print("\nรายละเอียดแถว BILL_EMPTY:")
    for r in bill_empty_rows:
        print(f"  - Order: {r.get('order_id')}, SKU: {r.get('sku')}, Platform: {r.get('platform')}/{r.get('shop')}")

    # จำลองการคำนวณ KPI เหมือน app.py
    print("\n[STEP 3] จำลองการคำนวณ KPI เหมือน app.py")
    print("-" * 80)

    # นับ unique order IDs
    kpi_orders_bill_empty = set()
    bill_empty_count_debug = 0

    for r in scope_rows:
        status_alloc = (r.get("allocation_status") or "").strip().upper()
        if status_alloc == "BILL_EMPTY":
            bill_empty_count_debug += 1
            oid = (r.get("order_id") or "").strip()
            if oid:
                kpi_orders_bill_empty.add(oid)

    print(f"✓ จำนวนแถวที่มี allocation_status='BILL_EMPTY': {bill_empty_count_debug}")
    print(f"✓ จำนวน Order (unique) ที่เป็น BILL_EMPTY: {len(kpi_orders_bill_empty)}")
    print(f"✓ Order IDs: {sorted(kpi_orders_bill_empty)}")

    # จำลอง _count_split function
    def count_split(oid_set, source_rows):
        today = date.today()
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

    print(f"\n[STEP 4] แยกเก่า/ใหม่:")
    print("-" * 80)
    print(f"  รวม: {c_bill_empty}")
    print(f"  ค้าง (เก่า): {c_bill_empty_old}")
    print(f"  วันนี้ (ใหม่): {c_bill_empty_new}")

    # ทดสอบกรองด้วย platform/shop
    print("\n[STEP 5] ทดสอบกรอง Platform/Shop")
    print("-" * 80)

    # หา platform/shop ที่มี BILL_EMPTY
    platforms = set()
    shops = set()
    for r in bill_empty_rows:
        platforms.add(r.get("platform"))
        shops.add(r.get("shop"))

    print(f"Platform ที่มี BILL_EMPTY: {', '.join(sorted(platforms))}")
    print(f"Shop ที่มี BILL_EMPTY: {', '.join(sorted(shops))}")

    # ทดสอบกรอง Platform
    if platforms:
        test_platform = list(platforms)[0]
        print(f"\nทดสอบกรอง Platform = '{test_platform}':")

        try:
            filters_with_platform = {"platform": test_platform}
            filtered_rows, _ = compute_allocation(db.session, filters_with_platform)

            # นับ BILL_EMPTY ในผลลัพธ์
            bill_empty_filtered = set()
            for r in filtered_rows:
                status = (r.get("allocation_status") or "").strip().upper()
                if status == "BILL_EMPTY":
                    oid = (r.get("order_id") or "").strip()
                    if oid:
                        bill_empty_filtered.add(oid)

            print(f"  ✓ พบ BILL_EMPTY: {len(bill_empty_filtered)} orders")
            print(f"  ✓ Order IDs: {sorted(bill_empty_filtered)}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # สรุป
    print("\n" + "=" * 80)
    print("สรุปผลการวินิจฉัย")
    print("=" * 80)

    if c_bill_empty > 0:
        print(f"""
✅ Backend (allocation.py + app.py) คำนวณถูกต้อง:
  - compute_allocation ส่งค่า BILL_EMPTY มา {len(bill_empty_rows)} แถว
  - KPI นับได้ {c_bill_empty} orders (ค้าง {c_bill_empty_old}, วันนี้ {c_bill_empty_new})

⚠️  ปัญหาน่าจะอยู่ที่:
  1. Server ยังไม่ได้ reload โค้ด (ต้อง restart)
  2. Filter ไม่ตรง (ต้องเลือก Platform/Shop ที่มี BILL_EMPTY)
  3. Browser cache (ต้อง Hard Refresh)

🔧 แนะนำ:
  1. Restart Server: pkill -9 -f "python.*app.py" && python3 app.py
  2. เปิด Dashboard: http://localhost:5000/dashboard
  3. เลือก Platform = {', '.join(sorted(platforms))} (หรือ "ทั้งหมด")
  4. Hard Refresh: Ctrl+Shift+R
""")
    else:
        print(f"""
❌ ปัญหา: Backend ไม่ได้คำนวณ BILL_EMPTY!
  - allocation.py ไม่ส่งค่า BILL_EMPTY มา
  - ต้องตรวจสอบว่า allocation_status ใน DB เป็น BILL_EMPTY จริงหรือไม่

🔧 แนะนำ:
  1. รัน check_bill_empty.py เพื่อเช็ค DB
  2. ตรวจสอบ allocation.py บรรทัด 137-139, 172, 203-205
""")

if __name__ == "__main__":
    with app.app_context():
        main()
