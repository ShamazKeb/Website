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

# 6. Project Sheep (Audio Wake)
echo "🐑 Aktualisiere Sheep..."
cd sheep
# Dependencies check (fast if already satisfied)
if [ -x "$(command -v pip3)" ]; then
    pip3 install -r requirements.txt --break-system-packages
fi
# Restart Service if it exists
if systemctl list-units --full -all | grep -Fq "sheep.service"; then
    sudo systemctl restart sheep.service
    echo "   Service restarted."
else
    echo "   Service not found (install via install_service.sh if desired)."
fi
cd ..

echo "✅ Alle Dienste aktualisiert!"

