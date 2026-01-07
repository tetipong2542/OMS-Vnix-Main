#!/usr/bin/env python3
"""
Script: อัพเดตสถานะบิลเปล่าย้อนหลัง
จุดประสงค์: อัพเดต allocation_status = 'BILL_EMPTY' สำหรับ Order ที่นำเข้าผ่าน Import Bill Empty แล้ว
"""

import sys
import json
from app import app, db
from models import OrderLine
from sqlalchemy import text

def main():
    print("=" * 80)
    print("Script: อัพเดตสถานะบิลเปล่าย้อนหลัง")
    print("=" * 80)
    print()

    with app.app_context():
        # 1. ดึง Import Log ทั้งหมดจากระบบบิลเปล่า
        print("[STEP 1] ดึง Import Log จากระบบบิลเปล่า...")
        logs_query = text("""
            SELECT id, batch_data, created_at
            FROM import_logs
            WHERE platform = 'EMPTY_BILL_SYSTEM'
            ORDER BY created_at DESC
        """)
        logs = db.session.execute(logs_query).fetchall()

        print(f"   พบ Import Log: {len(logs)} รายการ")
        print()

        if not logs:
            print("❌ ไม่พบ Import Log ของบิลเปล่า")
            return

        # 2. รวม Order IDs ทั้งหมดจาก batch_data
        print("[STEP 2] รวม Order IDs จาก Log...")
        all_order_ids = set()

        for log in logs:
            batch_data_str = log[1]  # batch_data column
            if batch_data_str:
                try:
                    batch_data = json.loads(batch_data_str)
                    new_ids = batch_data.get('new_ids', [])
                    duplicate_ids = batch_data.get('duplicate_ids', [])

                    for oid in new_ids + duplicate_ids:
                        if oid:
                            all_order_ids.add(oid)
                except:
                    pass

        print(f"   พบ Order IDs ทั้งหมด: {len(all_order_ids)} orders")
        print(f"   Order IDs: {sorted(list(all_order_ids)[:10])}{'...' if len(all_order_ids) > 10 else ''}")
        print()

        if not all_order_ids:
            print("❌ ไม่พบ Order IDs ใน Import Log")
            return

        # 3. อัพเดตสถานะบิลเปล่าสำหรับ Order ทั้งหมด
        print("[STEP 3] อัพเดตสถานะบิลเปล่า...")
        updated_count = 0
        already_updated_count = 0
        not_found_count = 0

        for order_id in sorted(all_order_ids):
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
            sys.exit(1)

        # 4. สรุปผล
        print()
        print("=" * 80)
        print("สรุปผลการอัพเดต")
        print("=" * 80)
        print(f"  Order ที่อัพเดต:           {updated_count}")
        print(f"  Order ที่เป็น BILL_EMPTY อยู่แล้ว: {already_updated_count}")
        print(f"  Order ที่ไม่พบในระบบ:      {not_found_count}")
        print(f"  รวมทั้งหมด:                {len(all_order_ids)}")
        print()

        if updated_count > 0:
            print("🎉 อัพเดตสถานะบิลเปล่าย้อนหลังเรียบร้อย!")
            print()
            print("ขั้นตอนถัดไป:")
            print("  1. Restart Server: pkill -9 -f 'python.*app.py' && PORT=8001 python3 app.py > server.log 2>&1 &")
            print("  2. Hard Refresh Browser: Ctrl+Shift+R")
            print("  3. ทดสอบ Search Order ที่มีปัญหา")
        else:
            print("ℹ️  ไม่มี Order ใดที่ต้องอัพเดต (อัพเดตไปแล้วทั้งหมด)")

if __name__ == "__main__":
    main()
