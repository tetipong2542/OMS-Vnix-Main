#!/usr/bin/env python3
"""
Migration: เพิ่มคอลัมน์ is_system_config ในตาราง shops
และอัปเดต shop config ทั้ง 4 รายการให้เป็น system config
"""
import sys
from app import app, db
from models import Shop

def migrate():
    """เพิ่มคอลัมน์ is_system_config และอัปเดตข้อมูล"""
    with app.app_context():
        # 1. เพิ่มคอลัมน์ is_system_config (ถ้ายังไม่มี)
        from sqlalchemy import text
        with db.engine.connect() as con:
            cols = {row[1] for row in con.execute(text("PRAGMA table_info(shops)")).fetchall()}
            if "is_system_config" not in cols:
                print("✅ เพิ่มคอลัมน์ is_system_config ในตาราง shops")
                con.execute(text("ALTER TABLE shops ADD COLUMN is_system_config INTEGER DEFAULT 0"))
                con.commit()
            else:
                print("⚠️  คอลัมน์ is_system_config มีอยู่แล้ว")

        # 2. อัปเดต shop config ทั้ง 4 รายการให้เป็น system config
        system_configs = [
            ('CANCEL_SYSTEM', 'GoogleSheet'),
            ('EMPTY_BILL_SYSTEM', 'GoogleSheet'),
            ('SALES_SYSTEM', 'GoogleSheet_Sales'),
            ('STOCK_SYSTEM', 'SabuySoft'),
        ]

        updated = 0
        for platform, name in system_configs:
            shop = Shop.query.filter_by(platform=platform, name=name).first()
            if shop:
                shop.is_system_config = True
                updated += 1
                print(f"✅ อัปเดต {platform} / {name} -> is_system_config=True")
            else:
                print(f"⚠️  ไม่พบ {platform} / {name}")

        if updated > 0:
            db.session.commit()
            print(f"\n✅ Migration สำเร็จ: อัปเดต {updated} shops")
        else:
            print("\n⚠️  ไม่มีการอัปเดตข้อมูล")

if __name__ == "__main__":
    migrate()
