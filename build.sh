#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt

# Create uploads directory
mkdir -p static/uploads
chmod -R 777 static/uploads
