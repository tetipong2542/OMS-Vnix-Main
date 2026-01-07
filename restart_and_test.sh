#!/bin/bash

echo "=========================================="
echo "Restart Server และทดสอบ Dashboard"
echo "=========================================="

# ตรวจสอบว่ามี process ของ app.py รันอยู่หรือไม่
echo -e "\n1. ตรวจสอบ Server ที่กำลังรัน..."
pgrep -f "python.*app.py" > /dev/null
if [ $? -eq 0 ]; then
    echo "   ⚠️  พบ Server กำลังรันอยู่"
    echo "   กำลังหยุด Server..."
    pkill -f "python.*app.py"
    sleep 2
    echo "   ✅ หยุด Server แล้ว"
else
    echo "   ไม่มี Server รันอยู่"
fi

echo -e "\n2. ตรวจสอบการแก้ไขโค้ด..."
echo "   กำลังเช็คว่าโค้ดมี debug logging หรือไม่..."

if grep -q "BILL_EMPTY DEBUG" app.py; then
    echo "   ✅ พบ debug logging ในโค้ด"
else
    echo "   ❌ ไม่พบ debug logging - ต้องแก้ไขโค้ดก่อน!"
    exit 1
fi

echo -e "\n3. กำลังรัน Server ใหม่..."
echo "   (กด Ctrl+C เพื่อหยุด Server)"
echo "=========================================="
echo ""

# รัน server และแสดง log
python3 app.py 2>&1 | grep --line-buffered -E "(BILL_EMPTY DEBUG|Running on|WARNING|ERROR)" &

SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo ""
echo "=========================================="
echo "วิธีทดสอบ:"
echo "=========================================="
echo "1. เปิดเบราว์เซอร์ไปที่: http://localhost:5000/dashboard"
echo "2. เลือก Platform = Shopee (หรือทั้งหมด)"
echo "3. เลือก Shop = sh mall (หรือทั้งหมด)"
echo "4. ดูที่ Card 'บิลเปล่า'"
echo "5. ตรวจสอบ log ที่แสดงด้านล่าง"
echo "=========================================="
echo ""
echo "กำลังรอ log จาก Dashboard..."
echo "(กรุณารีเฟรชหน้า Dashboard เพื่อดู log)"
echo ""

# รอให้ผู้ใช้กด Ctrl+C
wait $SERVER_PID
