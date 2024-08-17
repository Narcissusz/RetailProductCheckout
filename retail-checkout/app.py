from flask import Flask, request, jsonify, render_template
import cv2
import torch
import numpy as np
import json
import sys
import os
sys.path.append(os.path.abspath('yolov7'))
from yolov7.models.experimental import attempt_load 
import torchvision.transforms as transforms
from PIL import Image
import uuid
import subprocess
import re

# เพิ่มเส้นทางของ YOLOv7 ลงใน PYTHONPATH
sys.path.append('/Users/edward/Downloads/RetailProductCheckout/retail-checkout/yolov7')

import torch


app = Flask(__name__)


model_path = '/Users/edward/Downloads/RetailProductCheckout/retail-checkout/best.pt'
model = attempt_load(model_path, map_location=torch.device('cpu'))
model.eval()
num_classes = model.nc
class_names = model.names

def parse_detect_output(output):
    """
    Parse the output of detect.py to extract item names and quantities.
    """
    lines = output.split('\n')
    # Find the line containing the detection results
    for line in lines:
        if 'Done.' in line:
            detection_line = line
            break
    else:
        raise ValueError("Detection results not found in output")

    # Example of detected items line: "2 Cokes, 1 Shampoo, 1 SunScreen, 1 VitaminC, Done."
    detection_line = detection_line.replace('Done.', '').strip()
    items = detection_line.split(', ')

    # Parse item quantities
    item_counts = {}
    for item in items:
        parts = item.split(' ', 1)
        if len(parts) == 2:
            count_str, name = parts
            try:
                count = int(count_str)
                item_counts[name] = count
            except ValueError:
                print(f"Skipping invalid count value: {count_str}")
    
    return item_counts

def calculate_total_price(detected_items, price_file):
    """
    Calculate the total price of detected items using the price JSON file.
    """
    with open(price_file) as f:
        price_data = json.load(f)


    return sum(price_data.get(item, 0) for item in detected_items)
    # total_price = sum(price_data.get(item, 0) * quantity for item, quantity in detected_items.items())
    # return total_price


@app.route('/')
def index():
    
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file found"}), 400

    file = request.files['image']
    filename = str(uuid.uuid4()) + '.jpg'
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    try:
        result = subprocess.run(['python', '/Users/edward/Downloads/RetailProductCheckout/retail-checkout/yolov7/detect.py', '--weights', '/Users/edward/Downloads/RetailProductCheckout/retail-checkout/best.pt', '--conf', '0.1', '--source', filepath],
                                capture_output=True, text=True)
        
        output = result.stdout

        detected_items = parse_detect_output(output)
        price_file = 'prices.json'
        total_price = calculate_total_price(detected_items, price_file)
        return jsonify({"detected_items": detected_items, "total_price": total_price}), 200
        # return render_template('receipt.html', detected_items=detected_items, total_price=total_price), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/receipt')
def receipt():
    detected_items = {
        'Coke': 2,
        'Shampoo': 1,
        'SunScreen': 1,
        'VitaminC': 1
    }
    
    total_price = 10
    
    tax = total_price * 0.13
    total_with_tax = total_price + tax

    return render_template('receipt.html', detected_items=detected_items, total_price=total_price, tax=tax, total_with_tax=total_with_tax)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)