#!/bin/bash

echo "================================================================"
echo "FORCE RESTART - บังคับ Restart Server และล้าง Cache"
echo "================================================================"

# 1. หยุด Server ทั้งหมด
echo -e "\n[1/6] หยุด Server ที่กำลังรัน..."
pkill -9 -f "python.*app.py" 2>/dev/null
pkill -9 -f "flask.*run" 2>/dev/null
sleep 2
echo "      ✅ หยุด Server แล้ว"

# 2. ลบไฟล์ .pyc และ __pycache__ ทั้งหมด
echo -e "\n[2/6] ลบ Python bytecode cache..."
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "      ✅ ลบ cache แล้ว"

# 3. ตรวจสอบการแก้ไขโค้ด
echo -e "\n[3/6] ตรวจสอบการแก้ไขโค้ด..."

# เช็คว่ามี debug logging
if grep -q "BILL_EMPTY DEBUG" app.py; then
    echo "      ✅ พบ debug logging ใน app.py"
else
    echo "      ❌ ไม่พบ debug logging - โค้ดอาจไม่ได้แก้ไข!"
fi

# เช็คว่า allocation.py อ่าน allocation_status จาก DB
if grep -q "db_allocation_status" allocation.py; then
    echo "      ✅ allocation.py อ่าน allocation_status จาก DB"
else
    echo "      ❌ allocation.py ยังไม่อ่าน allocation_status!"
fi

# เช็คว่าไม่กรอง is_packed ใน dashboard
if grep -q 'if status_alloc == "BILL_EMPTY":' app.py; then
    # เช็คว่าบรรทัดก่อนหน้าไม่มีการเช็ค is_packed
    if ! grep -B1 'if status_alloc == "BILL_EMPTY":' app.py | grep -q 'if not r.get("is_packed")'; then
        echo "      ✅ ไม่กรอง is_packed/is_cancelled สำหรับบิลเปล่า"
    else
        echo "      ⚠️  ยังมีการกรอง is_packed อยู่!"
    fi
fi

# 4. ทดสอบโค้ด
echo -e "\n[4/6] ทดสอบโค้ดด้วย quick_test.py..."
python3 quick_test.py | tail -20

# 5. เตรียม environment variables
echo -e "\n[5/6] ตั้งค่า environment..."
export FLASK_ENV=development
export FLASK_DEBUG=1
echo "      ✅ ตั้งค่า FLASK_ENV=development"

# 6. รัน Server
echo -e "\n[6/6] กำลังรัน Server..."
echo "================================================================"
echo ""
echo "  🚀 Server กำลังเริ่มทำงาน..."
echo ""
echo "  📌 URL: http://localhost:5000/dashboard"
echo "  📌 กด Ctrl+C เพื่อหยุด Server"
echo ""
echo "================================================================"
echo ""
echo "วิธีทดสอบ:"
echo "  1. เปิดเบราว์เซอร์ไปที่: http://localhost:5000/dashboard"
echo "  2. กด Ctrl+Shift+R (Hard Refresh)"
echo "  3. เลือก Platform = Shopee, Shop = sh mall"
echo "  4. ดูที่ Card 'บิลเปล่า' ควรเห็น: 3 (ค้าง 2 | วันนี้ 1)"
echo ""
echo "================================================================"
echo ""

# รัน server โดยแสดง log ที่เกี่ยวข้อง
python3 app.py 2>&1 | grep --line-buffered -E "(Running on|BILL_EMPTY DEBUG|WARNING|ERROR|KeyError)"
