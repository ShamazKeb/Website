# Projektplan – Handball-Tracker

## 1. Ziel des Projekts

Webanwendung für einen Handballverein, um:
- Trainingsleistungen von Spielern zu erfassen und zu tracken
- Fortschritte, Schwächen und Potenziale sichtbar zu machen
- Trainer und Admins bei Organisation und Analyse zu unterstützen

System muss:
- Rollenbasiert funktionieren (admin, coach, player)
- Mobil nutzbar sein (Smartphone-optimiert)
- Sicher mit Logins & Daten umgehen (Auth, RBAC, keine Klartext-Passwörter)

---

## 2. Rollen & Berechtigungen (RBAC)

### 2.1 Rollen

- **admin**
  - Vollzugriff auf alle Teams, Spieler, Trainer, Übungen und Daten
  - Admin-spezifische Funktionen: Zuweisung von Teams zu Trainern und Spielern

- **coach**
  - Kann mehrere Teams coachen
  - Sieht alle Daten aller Spieler seiner Teams (auch wenn Spieler in mehreren Teams spielen)
  - Kann:
    - Übungen erstellen und bearbeiten (nur eigene Übungen)
    - Spielerleistungsdaten einsehen und bearbeiten
    - Spieler anlegen, bearbeiten, deaktivieren (aber nicht Accountdaten ändern)
    - Teamzusammensetzung verwalten

- **player**
  - Kann sich einloggen und nur **eigene** Daten sehen
  - Kann **eigene Leistungsdaten** zu Übungen eintragen
  - Sieht eigene Trainingshistorie, Auswertungen und Diagramme

Jeder User hat **genau eine Rolle** (entweder admin, coach oder player).

---

## 3. Datenmodell – Fachliche Anforderungen

### 3.1 Benutzer & Profile

- Gemeinsame Tabelle `users` mit:
  - E-Mail / Username
  - Passwort-Hash (Argon2, kein Klartext)
  - Rolle (`admin`, `coach`, `player`)
- Je Rolle eigenes Profil:
  - `players` (1–1 zu `users`)
    - Vorname, Nachname
    - Jahrgang
    - Aktiv/Deaktiviert-Flag
  - `coaches` (1–1 zu `users`)
  - Admin braucht ggf. kein extra Profil

### 3.2 Teams & Zuweisungen

- `teams`
  - Name (z. B. "C-Jugend", "B-Jugend")
  - Saison (z. B. "2024/2025")
- Beziehungen:
  - `team_players` (Many-to-Many Spieler ↔ Team)
  - `team_coaches` (Many-to-Many Coach ↔ Team)
- Anforderungen:
  - Spieler können mehreren Teams zugeordnet werden
  - Trainer können mehrere Teams coachen
  - Teams können mehrere Trainer haben

### 3.3 Übungen & Kategorien

- `exercises`
  - Owner-Coach (FK)
  - Name
  - Beschreibung (optional)
  - Aktiv/Archiviert-Status
- Kategorien:
  - feste Liste (`category`): z. B. `schnelligkeit`, `maximalkraft`, `ausdauer`, `koordination`
  - Many-to-Many: `exercise_categories`
- Messgrößen:
  - Eine Übung **muss** mindestens eine Messgröße haben
  - Weitere Messgrößen können hinzugefügt werden
  - Messgrößen sind vordefiniert (ENUM), z. B.:
    - `seconds`, `repetitions`, `kilograms`, `meters`, `centimeters`
  - Tabelle `exercise_measurements`:
    - z. B. `time_in_seconds`, `reps`, etc. als definierte Felder pro Übung

### 3.4 Messdaten (Leistungsdaten)

- `player_measurements`
  - Spieler (FK), Übung (FK), Datum/Uhrzeit
  - Werte zu allen definierten Messgrößen der Übung
  - Optional: Notizen
- Anforderungen:
  - Mehrere Eintragungen pro Tag erlaubt
  - Trainer können Werte korrigieren
  - Historische Daten bleiben erhalten (kein Löschen bei Deaktivierung)
  - Auswertungen (Durchschnitt, Bestwert, Trend) werden **on-the-fly berechnet**

### 3.5 Activity Log

- `activity_logs`
  - Typ der Aktion: `player_entry`, `coach_edit_measurement`, `coach_create_player`, `coach_deactivate_player`, `coach_edit_exercise` etc.
  - Wer (User-ID)
  - Zeitstempel
  - Betroffener Spieler/Übung/Team (optional)
  - Kurze Beschreibung
- Wird erzeugt bei:
  - Spieler trägt Messdaten ein
  - Trainer bearbeitet Messwerte
  - Trainer legt Spieler an / deaktiviert Spieler
  - Trainer ändert Übungen

Filtermöglichkeiten:
- nach User, Spieler, Team, Zeitraum, Aktionstyp

---

## 4. Auswertungen & Visualisierungen

### 4.1 Spieler-Ansicht

- Dashboard:
  - Übersicht über letzte Eintragungen
  - Diagramm: Leistungsentwicklung pro Übung
- Filter:
  - Übung
  - Zeitraum
  - Saison

### 4.2 Trainer-Ansicht

- Coaching-Bereich:
  - Activity-Log der eigenen Teams
  - Verlinkungen zu:
    - Übungen
    - Spielerdaten
    - Teamverwaltung
- Auswertungen:
  - Diagramme für mehrere Spieler gleichzeitig
  - Filter: Team, Spieler, Übung, Kategorie, Jahrgang, Saison
  - Bestenlisten (z. B. Top 10 pro Übung in einer Saison)

---

## 5. Security-Anforderungen

### 5.1 Authentifizierung

- Passwort-Hashing via Argon2 (`passlib[argon2]`)
- Kein Klartext-Passwort in der DB
- JWT-Auth via `python-jose`:
  - `sub` (E-Mail oder User-ID) und `exp` enthalten
  - Tokens in `Authorization: Bearer <token>`

### 5.2 Autorisierung (RBAC)

- Rollenfeld in `User`
- FastAPI-Dependencies:
  - `get_current_user`
  - `get_current_admin`
  - `get_current_coach_or_admin`
  - ggf. `get_current_player`
- Jede geschützte Route nutzt passende Dependency

### 5.3 DB-Sicherheit

- Nutzung von SQLAlchemy (ORM) zur Vermeidung von SQL-Injection
- Strikte Nutzung von Models und Schemas (Pydantic) für Eingaben
- FK-Beziehungen erzwingen, dass:
  - Coach nur auf eigene Teams zugreift
  - Spieler nur eigene Daten sieht

### 5.4 Config & Secrets
s
- `SECRET_KEY`, `ALGORITHM`, DB-URL aus Umgebungsvariablen (.env)
- Keine Secrets im Code-Repository

---

## 6. Debug- & Entwicklungstools

Nur in **Development-Umgebung**:

- Swagger / ReDoc unter `/docs` und `/redoc`
- `DELETE /debug/reset`:
  - Dropt und erstellt alle Tabellen neu
  - Muss in Produktion deaktiviert oder stark geschützt werden
- „Hacker Mode UI“:
  - Dev-Page, um schnell Test-User (Admin, Coach, Player) anzulegen
  - Zum manuellen Testen von RBAC
  - Nicht in Produktion ausliefern

---

## 7. Nicht-funktionale Anforderungen

- Mobile First UI (gut nutzbar auf Smartphone)
- Performant genug, um tägliche Einträge aller Spieler zu verarbeiten
- Guter Logging-Standard (mindestens Fehler- und Audit-Logs)
- HTTPS in Produktion (z. B. via Reverse Proxy)
