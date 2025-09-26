#!/bin/bash

# Installation script for Multi-Format Converter
# This script installs all required dependencies

echo "Multi-Format Converter Setup Script"
echo "=================================="

# Check if running as root for system packages
if [[ $EUID -eq 0 ]]; then
   echo "Please don't run this script as root. Run as regular user."
   exit 1
fi

echo "Step 1: Installing system dependencies..."

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux system"
    sudo apt update
    sudo apt install -y tesseract-ocr tesseract-ocr-eng ffmpeg libsm6 libxext6 libxrender-dev libglib2.0-0 python3-pip python3-venv
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
    brew install tesseract ffmpeg
else
    echo "Unsupported operating system. Please install tesseract and ffmpeg manually."
fi

echo "Step 2: Creating Python virtual environment..."
python3 -m venv venv

echo "Step 3: Activating virtual environment and installing Python packages..."
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "Step 4: Creating necessary directories..."
mkdir -p static/uploads downloads

echo "Step 5: Setting permissions..."
chmod 755 static/uploads downloads

echo ""
echo "Installation complete!"
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python3 app.py"
echo "3. Open your browser to: http://localhost:5000"
echo ""
echo "To test the installation:"
echo "python3 test_converters.py"