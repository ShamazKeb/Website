Projekt: Automatischer Firmen-News-Aggregator mit Topic-Clustering & Summaries

Ziel:

Täglich neue News für definierte Firmen automatisch suchen

Artikel deduplizieren

Artikel zu „Topics“ bündeln (selbe Neuigkeit → ein Topic)

Für jedes Topic eine kurze Zusammenfassung generieren

Historisch speichern

Auf einer Website anzeigen (Filter: Firma, Zeitraum)

1. Architekturüberblick

Architekturstil: Modularer Monolith
Backend: Python 3
Framework: Flask
DB: SQLite
LLM: Groq API
Scheduler: Cronjob
Front-End: Minimal, server-rendered HTML Templates (Jinja2)

System besteht aus einer einzigen Anwendung mit 7 Kernmodulen, plus einer täglichen Pipeline und einer Weboberfläche.

2. Gesamtverzeichnisstruktur
config/
  companies.yaml          # Firmenliste + Such-Keywords
app/
  db.py                   # DB-Setup + Sessions
  models.py               # ORM-Models (SQLAlchemy)
  news_fetcher.py         # Artikelsuche
  topic_grouper.py        # Artikel -> Topics mittels Groq
  summary_generator.py     # LLM-Summaries
  pipeline.py             # orchestriert Tagesablauf
  web.py                  # Flask-App
templates/
  index.html              # Website-Template
daily_job.py              # Cron Entrypoint


Jede Datei wird weiter unten spezifiziert.

3. Datenmodell (detailliert)

Nutze SQLAlchemy.

3.1 Tabelle: companies

Speichert Firmen, für die News gesucht werden.

Feld	Typ	Beschreibung
id	Integer, PK	interne ID
name	String	Firmenname
slug	String	URL-ID, lowercase, unique
search_query	String	Query für Such-API oder Scraper

Hinweise:

slug wird für Filter verwendet.

search_query bildet die Grundlage für die Artikelsuche.

3.2 Tabelle: articles

Speichert alle Artikel (inkl. Historie).

Feld	Typ	Beschreibung
id	Integer, PK	
company_id	Integer, FK → companies.id	
url	String	Artikel-URL
title	String	
source_name	String	Domain/Publisher
published_at	DateTime	vom Publisher extrahiert
fetched_at	DateTime	Zeit des Auffindens
content	Text	extrahierter Volltext oder Teaser
hash	String	Hash aus URL + Titel; dient der Duplikatserkennung

Regeln:

Artikel gilt als Duplikat, wenn url oder hash existiert.

Volltext ist optional, aber empfohlen.

3.3 Tabelle: topics

Ein Topic = eine unabhängige Neuigkeit.

Feld	Typ	Beschreibung
id	Integer, PK	
company_id	FK	
topic_key	String	stabiler Identifier vom LLM
title	String	kurzer Themenname
created_at	DateTime	
updated_at	DateTime	aktualisiert, wenn neue Artikel angehängt werden

Wichtig:

topic_key entsteht aus LLM-Analyse (z. B. Unique-Summary oder semantischer Tag).

topic_key + company_id ist unique: selbe Neuigkeit → selbes Topic.

3.4 Tabelle: topic_articles

Relation zwischen Artikeln und Topics (m:n möglich).

Feld	Typ
id	Integer, PK
topic_id	FK
article_id	FK
3.5 Tabelle: summaries

Speichert historische Zusammenfassungen.

Feld	Typ	Beschreibung
id	Integer, PK	
topic_id	FK	
summary_text	Text	
generated_at	DateTime	Zeitpunkt der Erzeugung

Regeln:

Immer nur letzte Summary wird auf Website gezeigt

Historie bleibt vollständig bestehen

4. Modul-Spezifikation (sehr präzise)
4.1 config/companies.yaml

Format:

companies:
  - name: "Keto Software"
    slug: "keto"
    search_query: "Keto Software portfolio management"
  - name: "Valmet"
    slug: "valmet"
    search_query: "Valmet oxygen technology industrial news"

4.2 app/db.py

Zweck:

SQLite verbinden

Tabellen erstellen

Session bereitstellen

Singleton-Pattern für Engine

Funktionen:

get_engine()

create_session()

init_db()

4.3 app/models.py

Definiert ORM-Modelle gemäß Datenmodell.

Regeln:

Nutze ForeignKey-Constraints

Nutze Indexe für:

topic_key

company_id

fetched_at

4.4 app/news_fetcher.py

Zweck: Artikel im Netz suchen.

Input:

Firmenliste (aus YAML oder DB)

Output:

Liste neuer Artikel, die gespeichert werden müssen

Funktionen:

search_articles_for_company(company)

Muss:

Anhand company.search_query einen Web-Suchdienst benutzen
(API oder einfache Google-Suchergebnisse per Scraping – Implementierung frei)

Response normalisieren zu Objekten:

{
  "url": "...",
  "title": "...",
  "source": "domain.com",
  "published_at": "...",
  "content": "Text oder kurzer Auszug"
}

store_new_articles(session, company, articles)

Prüft Duplikate (URL oder Hash)

Speichert nur neue Artikel

Liefert Liste gespeicherter neuer Artikel zurück

4.5 app/topic_grouper.py

Zweck: Artikel zu Topics clustern.

Input:

Liste neuer Artikel aus der DB

Output:

Neue Topics oder Zuordnung neuer Artikel zu bestehenden Topics

LLM-PROMPT (empfohlen für Groq)

System Prompt:

Du bist ein präzises Clustering-Modell.
Aufgabe: Gruppiere Artikel derselben Neuigkeit.
Gib pro Artikel zwei Felder aus:

topic_key: ein kurzer, stabiler, textbasierter Identifier (max 10 Wörter).

topic_title: ein kurzer Thema-Name für Nutzer (max 12 Wörter).
Wenn zwei Artikel dieselbe Neuigkeit beschreiben, müssen sie denselben topic_key besitzen.

User Prompt (Beispiel-Struktur):

Hier ist eine Liste neuer Artikel zu der Firma: {{company_name}}.

Gib für jeden Artikel folgendes JSON zurück:
[
  {
    "original_id": <ID des Artikels>,
    "topic_key": "...",
    "topic_title": "..."
  },
  ...
]

Artikel:
1. ID: {{id}}, Titel: "{{title}}", Inhalt: "{{content}}"
2. ...

Funktion: assign_topics_to_new_articles(session)

Ablauf:

Lade alle Artikel der letzten 24h → new_articles

Rufe LLM auf → Liste mapping article-id → topic_key

Für jeden Artikel:

Suche Topic: gleiche topic_key + gleiche Firma

Falls gefunden → updated_at anpassen & topic_articles anlegen

Falls nicht → neues Topic + erste Summary später

4.6 app/summary_generator.py

Zweck: Zusammenfassung pro Topic erzeugen.

Input:

Topics, die neue Artikel bekommen haben

Output:

Neue Einträge in summaries

LLM-PROMPT für Summaries

System Prompt:

Du erzeugst prägnante Zusammenfassungen von Nachrichtenartikeln.
Die Summary soll:

kurz und faktisch sein

keine Redundanz enthalten

max. 6 Sätze

verständlich für Nicht-Experten

User Prompt-Struktur:

Fasse die Neuigkeit basierend auf diesen Artikeln zusammen:

Artikel:
1. "{{title}}" – Quelle: {{source}}, Datum: {{published_at}}
   Inhalt: "{{content}}"

2. ...

Gib nur die fertige Summary zurück, ohne zusätzliche Erklärungen.

Funktion: update_summaries_for_recent_topics(session)

Lade alle Topics, deren updated_at innerhalb der letzten Pipeline liegt

Lade alle Artikel dieses Topics

Rufe LLM auf

Speichere neue Summary

4.7 app/pipeline.py

Zweck: Tagesablauf orchestrieren.

Funktion: run_daily_pipeline()

Ablauf:

Lade Firmen aus YAML (companies.yaml)

Für jede Firma:

search_articles_for_company

store_new_articles

Rufe assign_topics_to_new_articles

Rufe update_summaries_for_recent_topics

Schreibe Logs:

Anzahl neuer Artikel

Anzahl neuer Topics

Anzahl aktualisierter Summaries

4.8 app/web.py

Zweck: Flask-Webserver.

Routen:

/ (GET)

Filter:

company=<slug>

from=<YYYY-MM-DD>

to=<YYYY-MM-DD>

Ablauf:

Firma = optional Filter

Zeitraum = optional

Lade passende Topics

Für jedes Topic:

Neueste Summary

Alle Artikel

Rendere index.html mit:

Firmenliste

Topics + Summaries + Artikel

5. Template: templates/index.html

Struktur:

Dropdown „Firma“

Datum-von, Datum-bis

Pro Topic ein Block:

Titel

Summary

"Zuletzt aktualisiert"

Liste der Quellenartikel

6. daily_job.py

Zweck: Cron-Einstiegspunkt.

Startet:

from app.pipeline import run_daily_pipeline

if __name__ == "__main__":
    run_daily_pipeline()

7. Logging & Fehlerverhalten

Jede Pipeline-Phase loggt:

Anzahl neuer Artikel

Anzahl neuer Topics

Fehler beim LLM-Aufruf

Falls ein LLM-Aufruf fehlschlägt:

Wiederhole 3× mit 30s Pause

Wenn weiterhin Fehler → Pipeline fährt weiter, Topic bleibt unzusammengefasst

Website muss Fehler robust überstehen (kein Absturz durch fehlende Summary)

8. Deployment Hinweise
Raspberry Pi

cron Eintrag zum täglichen Start:

0 6 * * * /usr/bin/python3 /home/pi/project/daily_job.py >> /home/pi/logs/pipeline.log 2>&1

Vercel

Optional: Nur das Frontend nach Vercel schieben (falls du ein separates UI willst).

9. Erweiterbarkeit

Wechsel auf Postgres → nur db.py austauschen

Frontend trennen (z. B. React/Next) → API-Schicht hinzufügen

Mehr Firmen → einfach YAML erweitern

Realtime statt daily → Pipeline alle 10 min laufen lassen