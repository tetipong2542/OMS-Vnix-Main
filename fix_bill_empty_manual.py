#!/usr/bin/env python3
"""
Script: อัพเดตสถานะบิลเปล่าโดยระบุ Order ID โดยตรง
จุดประสงค์: อัพเดต allocation_status = 'BILL_EMPTY' สำหรับ Order ที่ระบุ
"""

import sys
from app import app, db
from models import OrderLine

# รายการ Order IDs ที่ต้องการอัพเดตเป็นบิลเปล่า
ORDER_IDS = [
    '25122462V4JKC4',
    '251224724S3NA1',
    '2512259PJ7WFCC',
    '2512259PEPEMRJ',
    '2512258KYDCKMB',
    '2512247P9JTCXP',
    '2512247MKFWYYQ',
    '2512247QUTR36S',
    '2512247SMS5Q3N',
    '2601046M4Y71Q9',
]

def main():
    print("=" * 80)
    print("Script: อัพเดตสถานะบิลเปล่าโดยระบุ Order ID")
    print("=" * 80)
    print()

    with app.app_context():
        print(f"[STEP 1] อัพเดตสถานะบิลเปล่าสำหรับ {len(ORDER_IDS)} orders...")
        print()

        updated_count = 0
        already_updated_count = 0
        not_found_count = 0

        for order_id in ORDER_IDS:
            # หา OrderLine ทั้งหมดที่มี order_id นี้
            lines = OrderLine.query.filter_by(order_id=order_id).all()

            if lines:
                # เช็คว่าเป็น BILL_EMPTY อยู่แล้วหรือไม่
                is_already_bill_empty = any(
                    hasattr(line, 'allocation_status') and line.allocation_status == 'BILL_EMPTY'
                    for line in lines
                )

                if is_already_bill_empty:
                    already_updated_count += 1
                    print(f"   ℹ️  {order_id}: เป็น BILL_EMPTY อยู่แล้ว")
                else:
                    # อัพเดตสถานะเป็น BILL_EMPTY
                    for line in lines:
                        line.allocation_status = 'BILL_EMPTY'
                    updated_count += 1
                    print(f"   ✓ อัพเดต: {order_id} ({len(lines)} แถว)")
            else:
                not_found_count += 1
                print(f"   ⚠ ไม่พบ: {order_id}")

        # Commit การเปลี่ยนแปลง
        try:
            db.session.commit()
            print()
            print("✅ บันทึกการเปลี่ยนแปลงสำเร็จ!")
        except Exception as e:
            db.session.rollback()
            print()
            print(f"❌ เกิดข้อผิดพลาดในการบันทึก: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # สรุปผล
        print()
        print("=" * 80)
        print("สรุปผลการอัพเดต")
        print("=" * 80)
        print(f"  Order ที่อัพเดต:           {updated_count}")
        print(f"  Order ที่เป็น BILL_EMPTY อยู่แล้ว: {already_updated_count}")
        print(f"  Order ที่ไม่พบในระบบ:      {not_found_count}")
        print(f"  รวมทั้งหมด:                {len(ORDER_IDS)}")
        print()

        if updated_count > 0:
            print("🎉 อัพเดตสถานะบิลเปล่าเรียบร้อย!")
            print()
            print("ทดสอบผลลัพธ์:")
            print("  1. Hard Refresh Browser: Ctrl+Shift+R")
            print("  2. ทดสอบ Search Order: 2512247QUTR36S")
            print("  3. ทดสอบ Search Order: 2512247SMS5Q3N")
            print("  4. ตรวจสอบ Dashboard KPI บิลเปล่า")
        else:
            print("ℹ️  ไม่มี Order ใดที่ต้องอัพเดต")

if __name__ == "__main__":
    main()
