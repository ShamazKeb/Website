#!/bin/bash
echo "🖥️  Installing Admin Display Service..."

SERVICE_FILE="admin.service"
SYSTEMD_DIR="/etc/systemd/system"

# 1. Copy Service File
sudo cp $SERVICE_FILE $SYSTEMD_DIR/

# 2. Reload Daemon
sudo systemctl daemon-reload

# 3. Enable and Start
sudo systemctl enable admin.service
sudo systemctl restart admin.service

echo "✅ Admin Display Service installed and started!"
echo "Check status with: sudo systemctl status admin.service"
