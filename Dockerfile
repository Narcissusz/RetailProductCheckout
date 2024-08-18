# ใช้ Python image ที่เป็น slim version เพื่อลดขนาด image
FROM python:3.12-slim

# ตั้งค่า working directory ภายใน container
WORKDIR /app

# คัดลอก requirements.txt ไปยัง container
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดแอปพลิเคชันไปยัง container
COPY app/ ./app/

# กำหนดคำสั่งให้ container รันเมื่อเริ่มทำงาน
CMD ["python", "app/app.py"]
