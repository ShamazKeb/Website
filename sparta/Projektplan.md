# Handball Tormusik PWA – Projekt-Referenz v1.1

## Ziel
Eine PWA zur Steuerung von Tormusik und Spielsounds über Team-iPads.
Extrem niedrige Latenz, offline-fähig, robust im Spielbetrieb.

## Kern-Setup
- Pro Team mindestens 1 iPad (Bluetooth Box)
- Vor Spieltag: Sync/Download aller Teamdaten + Audios aufs iPad
- Im Spiel: vollständiger Offline-Betrieb (kein Netz erforderlich)

## Sound-Kategorien (pro Team)
- Spieler-Tormusiken (16 Spieler)
- Zusätzlich: Einlauf, Timeout, 7m, Strafe (erweiterbar)
- Tracks pro Team: ca. 30
- Aufwärmmusik: nicht im MVP

## Audio-Anforderungen
### Upload
- Team-Verwalter lädt MP3 hoch (Upload-Länge nicht limitiert)

### Clips (Trim)
- Jeder Sound spielt einen "Clip" aus einem Track: start_ms + duration_ms
- Trim UI: Slider + Preview (für nicht-technische Nutzer)
- Default duration: 15s (änderbar je nach Kategorie)
- **Tech-Note:** Im MVP lädt das iPad die gesamten MP3s herunter und wendet die Trim-Punkte via WebAudio API an. Perspektivisch (V2) sollte das Trimmen serverseitig erfolgen, um Sync-Zeiten und Offline-Speicherplatz (IndexedDB Browser-Limits) massiv zu schonen.

### Clip-Dauer Regeln (MVP)
- player_goal (Tormusik): 5–15s
- timeout / intro / seven_meter / penalty: keine harte Obergrenze (praktisch warnen ab z.B. >10min)

### Playback
- Preload für minimale Latenz
- Global: Notfall-Stop (stoppt alles) + Fade-Out

## Rollen & Zugriff
### Vereins-Admin
- Teams verwalten
- Team-Verwalter zuweisen
- globale Einstellungen

### Team-Verwalter (Admin)
- MP3 hochladen
- Clips trimmen
- Zuordnungen ändern (auch während Spiel)
- Sync/Publish auslösen
- Operator-Code pro Spiel generieren

### Operator (Player)
- Darf nur abspielen
- Zugriff via spielbezogenen Operator-Code (48h gültig)
- Keine Uploads/Edits

## Auth
- Team-Verwalter: Login-Name/E-Mail + Passwort
- "Eingeloggt bleiben" via Session/Refresh-Token (kein Passwort speichern)
- Operator: Code-Eingabe -> Player-Session

## Operator-Flow am Spieltag & Code-Regeln
1. **Code-Generierung:** Der Team-Verwalter (Musikverantwortliche) generiert in seinem eingeloggten Admin-Bereich einen Operator-Code für das Spiel.
2. **Übergabe:** Der Code wird an das Kampfgericht (mögliche wechselnde Personen) weitergegeben.
3. **Einfacher Login:** Der Operator öffnet die Web-App, gibt den Code ein und wird **direkt** zum fertig konfigurierten Soundboard der Mannschaft weitergeleitet.
4. **Auto-Sync & Offline:** Sofort nach Code-Eingabe lädt das iPad alle Audiodaten/Zuordnungen in den lokalen Cache. Ab hier ist das System zu 100% offline-fähig (Session 48h gültig).
- **Sicherheit:** Code kann vom Admin jederzeit regeneriert werden (alter Code verfällt sofort).

## Sync & Offline
- iPad hält lokale Offline-Kopie:
  - Zuordnungen (Buttons -> Clip)
  - Audiodateien
  - aktueller Kader (MVP: manuell gepflegt)
- Sync-Flow:
  1) Team wählen
  2) "Sync" lädt neue Version + Dateien
  3) Anzeige: letzte Sync-Zeit + Datenversion
- Änderungen kurz vor Spiel: erneuter Sync / Delta-Download

## Kader
- MVP: Team-Verwalter pflegt Kader vor jedem Spiel manuell (Rückennummern)
- später optional: Kader online importieren

## Audit/Logging
- Nur Änderungen loggen:
  - wer, wann, was (Track/Clip/Zuordnung/Kader), Team
- Keine Playback-Logs im MVP

## UX Must-haves (Player)
- Große Buttons: 1–16 Trikotnummern + Kategorien (Timeout etc.)
- Sofort Play (Operator drückt manuell auf den Button -> löst Wiedergabe aus. **Tech-Note iOS**: Diese Interaktion entsperrt den WebAudio-Context. Wichtig ist, die App so zu bauen, dass schon dieser *allererste* Klick ohne Latenz funktioniert).
- Verhindern von Standby: Screen Wake Lock API einbauen, da iOS Safari PWAs im Hintergrund bei der Audio-Wiedergabe sonst stark drosselt oder stoppt.
- Notfall-Stop + Fade-Out
- Anzeige "letzte Aktion"
- Schutz gegen Fehlbedienung (Lock/Player-Mode)

## UX Must-haves (Admin)
- Upload MP3
- Trim UI (Slider + Preview)
- Zuordnungen speichern
- Operator-Code generieren/anzeigen
- Sync/Publish

## Nicht-Ziele (MVP)
- Kein YouTube-to-MP3 / keine Download-Umgehungsflows
- Kein Streaming als Kernfeature
- Kein komplexer Spielplan
- Keine Aufwärmmusik

## Tech Default (Vorschlag)
- PWA: React/Next.js + TypeScript
- Backend: Supabase (Postgres + RLS) + Storage
- Offline: Service Worker + IndexedDB/Cache
- Audio: WebAudio API (Preload + Fade)
- Hardware-Controls: Screen Wake Lock API (verhindert Standby während des Operator-Betriebs)