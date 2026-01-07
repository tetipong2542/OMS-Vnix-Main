#!/usr/bin/env python3
"""
Migration Script: แปลง created_at ใน ImportLog จาก UTC เป็น Thai Timezone (GMT+7)

วิธีใช้:
    python migrate_import_log_timezone.py

หมายเหตุ:
    - Script นี้จะอัพเดตเฉพาะ records ที่มี created_at อยู่แล้ว
    - จะบวกเวลา +7 ชั่วโมงให้กับ created_at ทุกแถว
    - มี backup confirmation ก่อนทำงาน
"""

from datetime import timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# สร้าง database connection
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///oms.db')
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def migrate_import_log_timezone():
    """แปลง created_at จาก UTC เป็น Thai timezone (+7 ชั่วโมง)"""
    session = Session()

    try:
        # ตรวจสอบจำนวน records ทั้งหมด
        count_result = session.execute(text("SELECT COUNT(*) FROM import_logs WHERE created_at IS NOT NULL"))
        total_count = count_result.scalar()

        if total_count == 0:
            print("✅ ไม่มีข้อมูลที่ต้อง migrate")
            return

        print(f"📊 พบข้อมูลทั้งหมด: {total_count} records")
        print("⚠️  Script นี้จะบวกเวลา +7 ชั่วโมงให้กับคอลัมน์ created_at ทั้งหมด")

        # ขอยืนยันจากผู้ใช้
        confirm = input("\n❓ ต้องการดำเนินการต่อหรือไม่? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("❌ ยกเลิกการ migrate")
            return

        print("\n🚀 เริ่มทำการ migrate...")

        # อัพเดต created_at โดยบวก 7 ชั่วโมง
        # สำหรับ SQLite ใช้ datetime() function
        # สำหรับ PostgreSQL/MySQL ใช้ INTERVAL

        # ตรวจสอบว่าใช้ database อะไร
        db_type = DATABASE_URI.split(':')[0]

        if db_type == 'sqlite':
            # SQLite: ใช้ datetime() function
            update_query = text("""
                UPDATE import_logs
                SET created_at = datetime(created_at, '+7 hours')
                WHERE created_at IS NOT NULL
            """)
        elif db_type in ['postgresql', 'postgres']:
            # PostgreSQL: ใช้ INTERVAL
            update_query = text("""
                UPDATE import_logs
                SET created_at = created_at + INTERVAL '7 hours'
                WHERE created_at IS NOT NULL
            """)
        elif db_type == 'mysql':
            # MySQL: ใช้ DATE_ADD
            update_query = text("""
                UPDATE import_logs
                SET created_at = DATE_ADD(created_at, INTERVAL 7 HOUR)
                WHERE created_at IS NOT NULL
            """)
        else:
            print(f"❌ ไม่รองรับ database type: {db_type}")
            return

        # Execute update
        result = session.execute(update_query)
        session.commit()

        updated_count = result.rowcount

        print(f"✅ อัพเดตสำเร็จ: {updated_count} records")
        print("✅ Migration เสร็จสมบูรณ์!")

        # แสดงตัวอย่างข้อมูลหลัง migrate
        sample_result = session.execute(text("""
            SELECT id, filename, created_at
            FROM import_logs
            WHERE created_at IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 5
        """))

        print("\n📋 ตัวอย่างข้อมูลหลัง migrate (5 records ล่าสุด):")
        print("ID | Filename | Created At")
        print("-" * 80)
        for row in sample_result:
            print(f"{row[0]} | {row[1][:40] if row[1] else 'N/A'} | {row[2]}")

    except Exception as e:
        session.rollback()
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 Migration Script: ImportLog Timezone Conversion (UTC → GMT+7)")
    print("=" * 80)
    print()

    migrate_import_log_timezone()

    print()
    print("=" * 80)
    print("📝 หมายเหตุ: หลังจาก migrate แล้ว records ใหม่จะใช้ Thai timezone อัตโนมัติ")
    print("=" * 80)
