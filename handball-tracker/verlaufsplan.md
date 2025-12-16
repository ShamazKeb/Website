# Verlaufsplan – Handball-Tracker (inkrementelle Entwicklung)

Ziel:
- Projekt in kleine, logisch aufeinander aufbauende Schritte zerlegen
- Jeder Schritt ist einzeln testbar
- Nach jedem Schritt Integrität prüfen, bevor der nächste beginnt
- Security (Auth/RBAC/Secrets) früh einbauen

---

## Phase 0 – Projektgrundlage & Infrastruktur

### Schritt 0.1 – Basis-Projektstruktur

- Ziel:
  - Backend-Grundgerüst (z. B. FastAPI)
  - Ordnerstruktur einrichten: `app/`, `models/`, `schemas/`, `routes/`, `core/`
- Test:
  - Health-Endpoint `/health` gibt `{"status": "ok"}` zurück

### Schritt 0.2 – Config & Secrets

- Ziel:
  - `.env`-Handling (z. B. `pydantic` Settings)
  - `SECRET_KEY`, `ALGORITHM`, `DATABASE_URL` aus Umgebungsvariablen
- Test:
  - App startet korrekt mit und ohne `.env`
  - Fehlt eine kritische Variable → sauberer Fehler

### Schritt 0.3 – DB-Anbindung

- Ziel:
  - SQLAlchemy-Engine & Session einrichten
  - Leere DB initialisieren (z. B. `users`-Tabelle als Platzhalter)
- Test:
  - Migration/Start legt Tabelle an
  - Einfache Insert/Select-Operation via Script oder Test-Route

---

## Phase 1 – Authentifizierung & User-Modell

### Schritt 1.1 – User-Model & Role-Feld

- Ziel:
  - `User`-Modell mit:
    - id, email, password_hash, role, created_at
  - Rollen: `admin`, `coach`, `player`
- Test:
  - User-Objekt kann in DB gespeichert und ausgelesen werden

### Schritt 1.2 – Passwort-Hashing (Argon2)

- Ziel:
  - `get_password_hash`, `verify_password` mit Argon2
- Test:
  - Unit-Tests:
    - Klartext → Hash ≠ Klartext
    - `verify_password(plain, hash)` → True/False wie erwartet

### Schritt 1.3 – JWT-Login-Flow

- Ziel:
  - `/auth/login`:
    - Prüft E-Mail + Passwort
    - Gibt JWT mit `sub` und `exp` zurück
  - `OAuth2PasswordBearer` integrieren
- Test:
  - Falsches Passwort → 401
  - Richtiges Passwort → Token
  - Token kann mit Test-Route (`/auth/me`) geprüft werden

### Schritt 1.4 – get_current_user Dependency

- Ziel:
  - `get_current_user` dekodiert Token, lädt User aus DB
- Test:
  - Route `/auth/me` gibt korrekten User zurück
  - Abgelaufener/invalid Token → 401

---

## Phase 2 – RBAC & Basis-Routen

### Schritt 2.1 – Rollen-Dependencies

- Ziel:
  - `get_current_admin`
  - `get_current_coach_or_admin`
  - `get_current_player`
- Test:
  - Test-Routen:
    - `/admin/test` → nur admin
    - `/coach/test` → coach + admin
    - `/player/test` → nur player

### Schritt 2.2 – Admin-Benutzer anlegen (Setup)

- Ziel:
  - Script oder temporäre `/auth/register`-Route für ersten Admin
- Test:
  - Admin anlegen und via `/auth/login` einloggen

---

## Phase 3 – Kern-Datenmodell: Teams, Coaches, Spieler

### Schritt 3.1 – Tabellen: Teams, Players, Coaches

- Ziel:
  - Tabellen:
    - `players` (1–1 zu `users`)
    - `coaches` (1–1 zu `users`)
    - `teams`
- Test:
  - Anlegen von Player/Coach/Team in der DB per Script

### Schritt 3.2 – Many-to-Many Beziehungen

- Ziel:
  - `team_players`
  - `team_coaches`
- Test:
  - Spieler mehreren Teams und Coach mehreren Teams zuordnen
  - Queries: Alle Spieler eines Teams, alle Teams eines Trainers

### Schritt 3.3 – Admin-APIs für Team-Verwaltung

- Ziel:
  Admins können Teams erstellen und Spieler/Trainer Teams zuordnen.

- Routen:
  - `POST /admin/teams`  
    - Admin-only
    - Legt ein neues Team an (Name, Saison, optional age_group, notes)
  - `POST /admin/teams/{team_id}/players`
    - Admin-only
    - Body: `{ "player_ids": [1,2,3] }`
    - Fügt mehrere Spieler einem Team hinzu (ohne Duplikate)
  - `POST /admin/teams/{team_id}/coaches`
    - Admin-only
    - Body: `{ "coach_ids": [1,2] }`
    - Fügt mehrere Trainer einem Team hinzu (ohne Duplikate)

- Test:
  - Nur Admin kann diese Endpunkte verwenden → Coach/Player → 403
  - Nach Zuordnung:
    - `team.players` enthält die Spieler
    - `team.coaches` enthält die Trainer
    - `player.teams` / `coach.teams` enthalten das Team

### Schritt 3.4 – Admin-APIs zur Spieler- und Trainer-Erstellung

- Ziel:
  - Admin kann über die API User + Player-/Coach-Profil in einem Schritt anlegen.
- Routen:
  - POST /admin/players
  - POST /admin/coaches
- Test:
  - Admin → 200
  - Duplicate email → 400

## Phase 4 – Übungen & Kategorien

### Schritt 4.1 – Kategorienmodell

- Ziel:
  - Tabelle `categories` mit fester Liste
  - Many-to-Many `exercise_categories`
- Test:
  - Abfrage: Alle Übungen pro Kategorie

### Schritt 4.2 – Exercises & Messgrößen

- Ziel:
  - `exercises` (Owner-Coach, Name, Beschreibung)
  - `exercise_measurements` (mind. 1, optional mehr; ENUM-Typ)
- Test:
  - Coach erstellt Übung mit Messgrößen
  - Ungültige Messgröße (nicht im ENUM) → 422

### Schritt 4.3 – Coach-APIs für Übungen

- Ziel:
  - Routen:
    - `POST /coach/exercises`
    - `GET /coach/exercises`
    - `PUT /coach/exercises/{id}`
- Test:
  - Coach sieht nur eigene Übungen
  - Admin sieht alle (optional)
  - Player → kein Zugriff

---

## Phase 5 – Leistungsdaten (Measurements)

### Schritt 5.1 – Datenmodell player_measurements

- Ziel:
  - Tabelle `player_measurements` mit:
    - player_id, exercise_id, timestamp
    - Werte für alle Messgrößen der Übung
- Test:
  - Insert für verschiedene Übungen mit unterschiedlichen Messgrößen

### Schritt 5.2 – Player-APIs für Dateneingabe

- Ziel:
  - `POST /player/measurements`
  - `GET /player/measurements` (eigene Daten)
- Test:
  - Player kann nur eigene Messungen anlegen
  - Coach/Admin versuchen für Player einzutragen → Verhalten definieren (z. B. verboten)

### Schritt 5.3 – Coach-APIs für Datenansicht & Bearbeitung

- Ziel:
  - `GET /coach/measurements` mit Filtern (Team, Spieler, Übung, Zeitraum)
  - `PUT /coach/measurements/{id}` zum Bearbeiten
- Test:
  - Coach sieht nur Daten von Spielern seiner Teams
  - Berechtigungsprüfung anhand Team-Zuordnung

---

## Phase 6 – Activity Log

### Schritt 6.1 – Log-Modell

- Ziel:
  - `activity_logs`-Tabelle
- Test:
  - Einfacher Insert bei manueller Aktion

### Schritt 6.2 – Automatisches Logging

- Ziel:
  - Hooks/Service-Layer:
    - Beim Anlegen von Messungen durch Spieler
    - Beim Bearbeiten von Messungen durch Trainer
    - Beim Anlegen/Deaktivieren von Spielern
    - Beim Ändern von Übungen
- Test:
  - Jede dieser Aktionen erzeugt einen Log-Eintrag

### Schritt 6.3 – Log-API für Trainer

- Ziel:
  - `GET /coach/logs` mit Filtern (Team, Spieler, Zeitraum, Typ)
- Test:
  - Coach sieht nur Logs zu seinen Teams
  - Admin kann alles sehen

---

## Phase 7 – Analyse & Visualisierungen

### Schritt 7.1 – Aggregations-Endpoints

- Ziel:
  - Endpoints, die:
    - Durchschnittswerte
    - Bestwerte
    - Zeitreihen pro Spieler/Übung
    berechnen
- Test:
  - Korrekte Aggregation für Testdaten

### Schritt 7.2 – Rankings/Bestenlisten

- Ziel:
  - `GET /coach/rankings` (z. B. pro Übung, Team, Saison)
- Test:
  - Ranking stimmt mit erwarteten Werten überein

---

## Phase 8 – Frontend & Mobile-First UI

### Schritt 8.1 – Basis-Layout & Login-Flow

- Ziel:
  - Login-Seite
  - Rollenbasierte Navigationsbereiche
- Test:
  - Player, Coach, Admin sehen jeweils passende UI-Bereiche

### Schritt 8.2 – Player-Dashboard (Mobile First)

- Ziel:
  - Einfache Formulare für Dateneingabe
  - Übersichtsseite mit letzter Leistung + einfache Diagramme
- Test:
  - Auf Smartphone-Viewport nutzbar (Responsive Design)

### Schritt 8.3 – Coach-Dashboard

- Ziel:
  - Activity-Log, Filter, Links zu Übungen, Teamverwaltung und Auswertungen
- Test:
  - Szenarien: Coach mit mehreren Teams → Übersicht bleibt nachvollziehbar

---

## Phase 9 – Debug & Dev-Tools (nur Entwicklung)

### Schritt 9.1 – Swagger & Dev-Konfiguration

- Ziel:
  - `/docs` und `/redoc` aktiviert in Dev
- Test:
  - API vollständig über Swagger testbar

### Schritt 9.2 – DB-Reset-Endpoint

- Ziel:
  - `DELETE /debug/reset` nur in Dev
- Test:
  - In Dev: Endpoint resetet DB
  - In Prod: Endpoint gar nicht verfügbar oder strikt geblockt

### Schritt 9.3 – „Hacker Mode UI“

- Ziel:
  - Einfache Dev-HTML-Seite zum Anlegen von Demo-Usern
- Test:
  - Nur in Dev erreichbar (z. B. abhängig von ENV-Flag)

---

## Phase 10 – Production-Hardening

### Schritt 10.1 – HTTPS & Reverse Proxy

- Ziel:
  - App hinter Nginx/Traefik mit HTTPS
- Test:
  - Alle Requests laufen über HTTPS

### Schritt 10.2 – Security-Review

- Ziel:
  - Prüfen:
    - Keine Debug-Endpoints in Prod
    - ENV-Variablen gesetzt
    - RBAC-Tests (Coach/Player/Admin) laufen
- Test:
  - Manuelle Durchgänge + automatisierte Tests

