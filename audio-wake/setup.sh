#!/bin/bash
echo "🐑 Installing Sheep dependencies..."

# System dependencies for sounddevice (PortAudio)
if [ -x "$(command -v apt-get)" ]; then
    echo "📦 Installing system libraries (libportaudio2)..."
    sudo apt-get update
    sudo apt-get install -y libportaudio2
else
    echo "⚠️ Not on Debian/Ubuntu? Please ensure libportaudio2 is installed manually."
fi

# Python dependencies
echo "🐍 Installing Python packages..."
# Try pip3, fallback to pip
if [ -x "$(command -v pip3)" ]; then
    pip3 install -r requirements.txt --break-system-packages
else
    pip install -r requirements.txt --break-system-packages
fi

echo "✅ Setup complete! Try running: python3 shepherd.py"
