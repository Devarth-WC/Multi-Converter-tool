#!/bin/bash

# Quick start script for Multi-Format Converter
echo "🚀 Starting Multi-Format Converter"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".dependencies_installed" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .dependencies_installed
    echo "✅ Dependencies installed"
fi

# Create directories if they don't exist
mkdir -p static/uploads downloads

# Set permissions
chmod 755 static/uploads downloads

echo "🌐 Starting Flask development server..."
echo "💡 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python3 app.py