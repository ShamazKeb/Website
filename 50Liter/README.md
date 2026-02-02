# 50 Liter Challenge - Liegestütz Tracker

Eine Web-App zum Tracken der 500 Liegestütz-Challenge der Handball-Mannschaft.

## Quick Start (Lokal testen)

### Backend starten
```bash
cd backend
pip install -r requirements.txt
python seed.py  # Spieler anlegen
python main.py  # Server starten auf Port 8000
```

### Frontend öffnen
Einfach `frontend/index.html` im Browser öffnen.

## Deployment mit Docker

```bash
# Im 50Liter Ordner:
docker-compose up -d --build
```

Die App ist dann erreichbar unter `http://<deine-ip>:8085`

## Spieler anpassen

Bearbeite die `PLAYERS` Liste in `backend/seed.py` und führe dann aus:
```bash
# Datenbank löschen und neu erstellen
rm backend/pushups.db  # oder data/pushups.db bei Docker
cd backend
python seed.py
```

## API Endpoints

- `GET /api/players` - Alle Spieler abrufen
- `POST /api/players/{id}/pushups` - Liegestütze hinzufügen
- `GET /api/stats` - Gesamtstatistik
