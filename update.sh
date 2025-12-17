#!/bin/bash

# 1. Code aktualisieren
echo "📦 Hole neuesten Code..."
git pull

# 2. Infrastructure (Nginx Proxy Manager)
echo "🚀 Starte Infrastructure..."
cd infrastructure
docker compose up -d --build
cd ..

# 3. Landing Page
echo "🚀 Starte Landing Page..."
cd landing-page
docker compose up -d --build
cd ..

# 4. Keto Monitor
echo "🚀 Starte Keto Monitor..."
cd keto-monitor
docker compose up -d --build
cd ..

# 5. Handball Tracker
echo "🤾 Starte Handball Tracker..."
cd handball-tracker
docker compose up -d --build
cd ..

# 6. Audio Wake (formerly Sheep)
echo "🔉 Starte Audio Wake System..."
cd audio-wake
docker compose up -d --build
cd ..

echo "✅ Alle Dienste aktualisiert!"

# 7. Admin Display (Self-Update)
echo "🖥️  Aktualisiere Admin Display..."
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


