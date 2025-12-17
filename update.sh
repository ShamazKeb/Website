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

