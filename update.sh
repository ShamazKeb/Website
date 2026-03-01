#!/bin/bash

# 1. Code aktualisieren
# Reset Status File Permissions
sudo rm -f /tmp/admin_update_status
echo "📦 Hole neuesten Code..."
echo "CODE" > /tmp/admin_update_status
# Force Pull (Discard local changes)
git fetch --all
git reset --hard origin/main
git pull

# 2. Infrastructure (Nginx Proxy Manager)
echo "🚀 Starte Infrastructure..."
echo "INFRA" > /tmp/admin_update_status
cd infrastructure
docker compose up -d --build
cd ..

# 3. Landing Page
echo "🚀 Starte Landing Page..."
echo "LANDING" > /tmp/admin_update_status
cd landing-page
docker compose up -d --build
cd ..

# 4. Keto Monitor
echo "🚀 Starte Keto Monitor..."
echo "KETO" > /tmp/admin_update_status
cd keto-monitor
docker compose up -d --build
cd ..

# 5. Handball Tracker
echo "🤾 Starte Handball Tracker..."
echo "HANDBALL" > /tmp/admin_update_status
cd handball-tracker
docker compose up -d --build
cd ..

# 6. Audio Wake (formerly Sheep)
echo "🔉 Starte Audio Wake System..."
echo "AUDIO" > /tmp/admin_update_status
cd audio-wake
docker compose up -d --build
cd ..

# 7. 50Liter Challenge
echo "🍺 Starte 50Liter Challenge..."
echo "50LITER" > /tmp/admin_update_status
cd 50Liter
docker compose up -d --build
cd ..

echo "✅ Alle Dienste aktualisiert!"

# 7. Admin Display (Self-Update)
echo "🖥️  Aktualisiere Admin Display..."
echo "ADMIN" > /tmp/admin_update_status
cd admin-display
if [ -x "$(command -v pip3)" ]; then
    pip3 install -r requirements.txt --break-system-packages
fi
# Restart Service if it exists (This restarts the GUI)
if systemctl list-units --full -all | grep -Fq "admin.service"; then
    echo "   Restarting Admin Interface..."
    sudo systemctl restart admin.service
fi
cd ..
echo "DONE" > /tmp/admin_update_status


