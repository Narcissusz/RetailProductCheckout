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

# Get the current directory where app.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the yolov7 directory to sys.path
yolov7_path = os.path.join(current_dir, 'yolov7')
# sys.path.append(yolov7_path)
sys.path.append(os.path.join(os.path.dirname(__file__), 'yolov7'))


import torch

app = Flask(__name__)
detect_script = os.path.join(yolov7_path, 'detect.py')
model_path = os.path.join(current_dir, 'best.pt')
model = attempt_load(model_path, map_location=torch.device('cpu'))
model.eval()
num_classes = model.nc
class_names = model.names

def calculate_total_price(detected_items):
    price_data = {
        "Coke": 2.59,
        "Cokes": 2.59,
        "Shampoo": 15.49,
        "Shampoos": 15.49,
        "SunScreen": 27.89,
        "SunScreens": 27.89,
        "VitaminC": 45.29,
        "VitaminCs": 45.29
    }

    total_price = 0
    for item, quantity in detected_items.items():
        price = price_data.get(item, 0)
        total_price += price * quantity

    return total_price

def parse_detect_output(output):
 
    lines = output.split('\n')
    for line in lines:
        if 'Done.' in line:
            detection_line = line
            break
    else:
        raise ValueError("Detection results not found in output")

    detection_line = detection_line.replace('Done.', '').strip()
    items = detection_line.split(', ')

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
        # Run the subprocess with relative paths
        result = subprocess.run(['python', detect_script, '--weights', model_path, '--conf', '0.3', '--source', filepath],
                         capture_output=True, text=True)
        
        output = result.stdout
        detected_items = parse_detect_output(output)

        # Define price data
        price_data = {
            "Coke": 2.59,
            "Cokes": 2.59,
            "Shampoo": 15.49,
            "Shampoos": 15.49,
            "SunScreen": 27.89,
            "SunScreens": 27.89,
            "VitaminC": 45.29,
            "VitaminCs": 45.29
        }
        total_price = calculate_total_price(detected_items)
        tax = total_price * 0.13
        total_price_with_tax = total_price + tax
        return render_template('receipt.html', detected_items=detected_items, total_price=total_price, tax=tax, total_price_with_tax=total_price_with_tax, price_data=price_data)

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
    app.run(host='0.0.0.0', port=8080, debug=False)