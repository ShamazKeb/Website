#!/bin/bash
echo "🐑 Installing Sheep Service..."

SERVICE_FILE="sheep.service"
SYSTEMD_DIR="/etc/systemd/system"

# 1. Copy Service File
sudo cp $SERVICE_FILE $SYSTEMD_DIR/

# 2. Reload Daemon
sudo systemctl daemon-reload

# 3. Enable and Start
sudo systemctl enable sheep.service
sudo systemctl restart sheep.service

echo "✅ Sheep Service installed and started!"
echo "Check status with: sudo systemctl status sheep.service"
