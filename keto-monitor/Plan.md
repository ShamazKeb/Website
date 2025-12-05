Projekt: Firmen-News Aggregator mit automatischer Klassifikation & Zusammenfassung

Ziel: Eine Website, die täglich neue Unternehmens-News sucht, diese automatisiert Themen zuordnet, zusammenfasst und historisch speichert.

1. Gesamtarchitektur

Architekturstil: Modularer Monolith
Sprache: Python
Framework: Flask (Web), Jinja2 (Templates)
DB: SQLite
LLM: Groq API
Scheduler: Cronjob (1× täglich)

Das System besteht aus einem Backend, das:

Artikel im Internet sucht

Themencluster erzeugt (LLM)

Zusammenfassungen schreibt (LLM)

Daten speichert

Eine Website rendert

2. Module & Dateien

Vorgesehene Projektstruktur:

config/
  companies.yaml
app/
  db.py
  models.py
  news_fetcher.py
  topic_grouper.py
  summary_generator.py
  pipeline.py
  web.py
templates/
  index.html
daily_job.py


Zweck aller Module:

config/companies.yaml

Liste der beobachteten Firmen + Suchbegriffe.

app/db.py

SQLite-Verbindung, Erstellung der Tabellen, Session-Handling.

app/models.py

ORM-Modelle: companies, articles, topics, topic_articles, summaries.

app/news_fetcher.py

Tägliche Artikelsuche je Firma, Duplicate-Filter, Speicherung neuer Artikel.

app/topic_grouper.py

Zuweisung neuer Artikel zu „Topics“ über Groq → verhindert doppelte Neuigkeiten.

app/sumary_generator.py

Erzeugt pro Topic eine textuelle Zusammenfassung (falls neue Artikel). Speichert sie historisch.

app/pipeline.py

Orchestriert den täglichen Ablauf:

Firmen laden

Artikel suchen

Topics erstellen/aktualisieren

Summaries erstellen

app/web.py

Flask-App mit Startseite, Filtern nach Firma/Zeitraum, Ausgabe der Topics/Summaries/Quellen.

templates/index.html

HTML-Seite für Listenansicht.

daily_job.py

Entrypoint für Cron → ruft pipeline.run_daily_pipeline() auf.

3. Datenmodell (tabellarisch beschrieben)
Table: companies
Feld	Zweck
id	Primärschlüssel
name	Firmenname
slug	Kurz-ID für URLs
search_query	Suchstring für Websuche
Table: articles
Feld	Zweck
id	Primärschlüssel
company_id	ref companies
url	Artikel-URL
title	Titel
source_name	Domain/Paper
published_at	Veröffentlichungsdatum
fetched_at	Wann gefunden
content	Artikeltext / Teaser
hash	Duplicate-Check
Table: topics
Feld	Zweck
id	Primärschlüssel
company_id	ref companies
topic_key	LLM-basierter stabiler Identifier
title	kurze Beschreibung des Themas
created_at	Anlagedatum
updated_at	wann letzter Artikel kam
Table: topic_articles
Feld	Zweck
id	Primärschlüssel
topic_id	ref topics
article_id	ref articles
Table: summaries
Feld	Zweck
id	Primärschlüssel
topic_id	ref topics
summary_text	generierte Kurzfassung
generated_at	Zeitstempel
4. Täglicher Datenfluss (Pipeline)

Dieser Ablauf wird 1× täglich ausgeführt:

Schritt 1 – Firmen laden

Lese alle Firmen aus companies.yaml oder DB.

Schritt 2 – Artikel suchen

Für jede Firma:

Web-Suche durchführen

Daten (URL, Titel, Date, Text) extrahieren

Nur neue Artikel speichern

Schritt 3 – Topic-Zuordnung

Für neue Artikel je Firma:

Groq aufrufen → topic_key + topic_title pro Artikel

If Topic existiert → anhängen

Else → neues Topic anlegen

Ziel: gleiche Neuigkeit = genau ein Topic.

Schritt 4 – Summaries generieren

Für alle Topics mit neuen Artikeln:

Alle Artikel des Topics holen

Groq kurz zusammenfassen lassen

Summary speichern

5. Website / UI

Eine einzige Seite (/):

Filter:

Firma (Dropdown: companies.slug)

Zeitraum (von/bis)

Anzeige pro Topic:

Topic-Titel

Neueste Summary

Datum letzter Aktualisierung

Liste aller Quellenartikel mit URL & Datum

UI ist server-rendered via HTML-Template.

6. Groq-LLM Nutzung (konzeptionell)
Topic-Grouper Prompt

Input: Liste neuer Artikel einer Firma (Titel + Textauszug)
Output: Für jeden Artikel → topic_key + kurzer thematischer Titel
Ziel: identische Themen bündeln.

Summary-Generator Prompt

Input: alle Artikel eines Topics
Output: 3–6 Sätze prägnante Zusammenfassung.

7. Hosting / Deployment

Entwicklung: lokal

Final: Raspberry Pi, täglicher Cronjob

Optional: Frontend auf Vercel hostbar (API + DB weiter auf Pi)

Keine besonderen Performance- oder Sicherheitsanforderungen.