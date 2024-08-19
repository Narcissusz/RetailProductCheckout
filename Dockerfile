FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

ENV PYTHONPATH="${PYTHONPATH}:/app/app/yolov7"

RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 8080

COPY . /app

CMD ["python", "app/app.py"]
