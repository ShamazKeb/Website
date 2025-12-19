# 📋 Projektplan: Pi-hole auf Raspberry Pi (WG-sicher)

## Ausgangslage

* Raspberry Pi mit **Raspberry Pi OS Lite**
* Pi-hole **noch nicht installiert**
* Kein globaler Router-Zugriff geplant
* Bestehender:

  * Webserver
  * Python-Programme (Touchscreen-UI)
* Ziel: **Netzwerkweiter Ad-Blocker nur für eigene Geräte**, lokal steuerbar

---

## Phase 1 – Basis & Vorbereitung (ca. 10–15 min)

### 1. System aktualisieren

**Ziel:** Sauberes, aktuelles Basissystem

* Systempakete aktualisieren
* Neustart durchführen

**Ergebnis:**

* Stabiles Raspberry Pi OS Lite ohne Altlasten

---

### 2. Netzwerkstatus prüfen

**Ziel:** WG-Sicherheit garantieren

* Aktuelle IP-Adresse prüfen
* Sicherstellen:

  * Keine Portweiterleitungen
  * Kein externer Zugriff von außen
* Entscheidung:

  * Betrieb über **LAN** (empfohlen)

**Ergebnis:**

* Raspberry Pi ist ausschließlich im lokalen Netzwerk erreichbar

---

## Phase 2 – Pi-hole Installation (ca. 15 min)

### 3. Pi-hole installieren

**Ziel:** Funktionierender DNS-basierter Ad-Blocker

* Offiziellen Pi-hole Installer verwenden
* Wichtige Installationsentscheidungen:

  * **Statische IP-Adresse: Ja**
  * Upstream DNS: z. B. Quad9 oder Cloudflare
  * Webinterface: Aktivieren
  * Logging: Standard

**Ergebnis:**

* Pi-hole läuft lokal, blockiert aber noch keine Geräte aktiv

---

### 4. Webinterface absichern

**Ziel:** Kein Zugriff durch Mitbewohner

* Admin-Passwort für Pi-hole setzen
* Zugriff nur aus dem lokalen Netzwerk zulassen

**Ergebnis:**

* Pi-hole-Weboberfläche ist geschützt

---

## Phase 3 – WG-sichere Nutzung (ca. 10 min)

### 5. Nutzung nur für eigene Geräte

**Ziel:** Keine Beeinflussung anderer WG-Mitglieder

* Router **nicht** verändern
* DNS-Server **nur auf eigenen Geräten** setzen:

  * Laptop
  * Smartphone
  * Tablet
  * Optional: Smart-TV

**Ergebnis:**

* Ausschließlich eigene Geräte nutzen Pi-hole

---

### 6. Funktionstest

**Ziel:** Korrekte Funktion sicherstellen

* Test-Webseiten mit Werbung aufrufen
* Pi-hole Dashboard prüfen:

  * Anzahl der DNS-Anfragen
  * Blockrate

**Ergebnis:**

* Pi-hole blockiert Werbung wie erwartet

---

## Phase 4 – Integration & Steuerung (ca. 20–40 min)

### 7. Pi-hole lokal steuerbar machen

**Ziel:** Steuerung ohne Browser

* Nutzung der Pi-hole CLI
* Steuerfunktionen definieren:

  * Status anzeigen
  * Aktivieren
  * Deaktivieren (temporär / dauerhaft)

**Ergebnis:**

* Pi-hole kann per Skript kontrolliert werden

---

### 8. Touchscreen-Integration

**Ziel:** Bedienung über bestehendes Touchscreen-UI

* Erweiterung des vorhandenen Python-UIs:

  * Statusanzeige (aktiv / inaktiv)
  * Ein-/Aus-Schaltfläche
* Alternativ:

  * Lokale HTTP-API (nur localhost)

**Ergebnis:**

* Zentrale Bedienung von Pi-hole über den Touchscreen

---

## Phase 5 – Komfort & Sicherheit (optional, ca. 30 min)

### 9. Schnelles Deaktivieren

**Ziel:** Frustfreie Nutzung

* Schnellzugriff im UI:

  * „5 Minuten deaktivieren“
  * „Jetzt deaktivieren“
* Optional:

  * Hardware-Button über GPIO

**Ergebnis:**

* Pi-hole kann jederzeit sofort abgeschaltet werden

---

### 10. Wartung & Absicherung

**Ziel:** Langfristige Stabilität

* Regelmäßige Updates (z. B. monatlich)
* Backup der SD-Karte nach Einrichtung
* Logdateien gelegentlich prüfen

**Ergebnis:**

* Wartbares, stabiles System

---

## Phase 6 – Erweiterungen (optional)

* Eigener DNS-Resolver (Unbound)
* Anzeige von Statistiken im Touchscreen-UI
* Nutzungsprofile (z. B. Gaming / Normal / Aus)
* Zeitgesteuertes Blockieren

---

## ⏱️ Gesamtaufwand (realistisch)

| Phase                   | Zeit                  |
| ----------------------- | --------------------- |
| Basis & Installation    | 25–30 min             |
| WG-Setup & Tests        | 10–15 min             |
| Touchscreen-Integration | 20–40 min             |
| **Gesamt**              | **ca. 1–1,5 Stunden** |

---

## ✅ Fazit

* WG-sicher
* Jederzeit rückgängig machbar
* Kein Router-Eingriff notwendig
* Touchscreen-tauglich
* Kein Einfluss auf Gaming-Ping
