Phase 0 – Projektgrundlage

Repo & Umgebung

Git-Repo anlegen, Python venv erstellen.

Basis-Ordnerstruktur anlegen:

app/, config/, templates/, daily_job.py

Test: python -m app (oder irgendein Mini-Script) läuft ohne Fehler.

Phase 1 – Minimaler Webserver (Grundgerüst)

Flask-Minimalversion (app/web.py)

Eine simple Flask-App mit Route /, die nur „OK“ zurückgibt.

templates/index.html mit einfachem Text.

Test: flask run → Seite im Browser erreichbar.

Config laden (config/companies.yaml)

Hilfsfunktion schreiben: load_companies_from_yaml().

Test: Kleines Script, das Firmen ausgibt: python -m app.debug_companies o. Ä.

Phase 2 – Datenbank-Basis

DB-Setup (app/db.py)

SQLite-Engine + Session-Fabrik + init_db().

Test: kleines Script, das init_db() aufruft, ohne Fehler.

Modelle (app/models.py)

Nur Company-Modell zuerst implementieren.

Später Article, Topic, TopicArticle, Summary.

Test: Script, das 1 Company in die DB schreibt und wieder ausliest.

Companies aus YAML in DB synchronisieren

z. B. sync_companies_from_yaml(): legt Companies aus YAML an/aktualisiert.

Test: Script, das nach Sync Companies aus DB ausgibt.

Phase 3 – Artikelmodell & Fake-News-Fetcher (ohne Internet/LLM)

Article-/Topic-/Summary-Modelle hinzufügen

Article, Topic, TopicArticle, Summary in models.py ergänzen.

Test: Tables neu erstellen (oder Migration) → Probe-Datensätze einfügen.

Fake-news_fetcher.py

Funktion fetch_dummy_articles_for_company(company) mit statischen Beispielartikeln.

Funktion store_new_articles(session, company, articles).

Test: Script, das:

Firmen lädt

Dummy-Artikel speichert

Artikel aus DB ausgibt.

Phase 4 – Topics & Summaries (erstmal ohne Groq, lokal)

Topic-Grouper (stub, ohne LLM)

assign_topics_to_new_articles(session):

z. B. einfach nach title-Ähnlichkeit gruppieren (oder 1 Topic pro Artikel) – egal, Hauptsache Logik steht.

Test: Script:

DB leeren, Dummy-Artikel anlegen

Topic-Grouper laufen lassen

Topics + TopicArticles ausgeben.

Summary-Generator (stub, ohne LLM)

update_summaries_for_recent_topics(session):

Erzeugt Summary, indem er z. B. die Titel der Artikel zusammenklebt.

Test: Script, das:

Topics lädt

Summaries erzeugt

Summaries ausgibt.

Pipeline (app/pipeline.py) – lokale Dummy-Version

run_daily_pipeline():

Firmen → Dummy-Artikel → Topic-Grouper (stub) → Summary-Generator (stub)

Test: python daily_job.py:

Prüfen: Artikel, Topics, Summaries in DB vorhanden.

Phase 5 – Weboberfläche an DB anbinden

Webseite mit echten DB-Daten

Route /:

Firmen aus DB laden

Topics + letzte Summary + Artikel anzeigen (ohne Filter)

index.html: einfache Liste.

Test: Browser öffnen, siehst Dummy-News.

Filter einbauen

Query-Parameter company, from, to.

SQL-Queries anpassen.

Test:

verschiedene URLs ausprobieren, z. B. /?company=keto, /?from=2025-01-01.

Phase 6 – Groq & echte Daten

Groq-Client integrieren

Hilfsmodul/Funktion z. B. llm_client.py:

Grundfunktion call_groq(prompt, system_prompt=None).

Test: Ein kleines Script, das einen einfachen Prompt absetzt und Response ausgibt.

Topic-Grouper von Stub → Groq

Stub-Logik ersetzen:

Artikel an Groq übergeben

JSON mit topic_key, topic_title parsen

Test: Pipeline mit sehr wenigen Dummy-Artikeln, schauen, ob Topics sinnvoll gruppiert werden.

Summary-Generator von Stub → Groq

Prompt wie im Plan.md.

Test: Summaries neu erzeugen, Ausgabe prüfen.

News-Fetcher von Dummy → echte Suche

Schrittweise:

zuerst simple API oder fest definierte URLs scrapen

später evtl. Such-API nachrüsten.

Test: Pipeline laufen lassen, echte Artikel in DB sehen.

Phase 7 – Productizing & Betrieb

Cron-Jobs auf Pi

daily_job.py per Cron 1x täglich ausführen.

Test: Cron-Log + DB-Inhalt nach einem Tag.

Fehlerhandling & Logs

Logging in Pipeline und Webserver:

Anzahl neuer Artikel/Topics/Summaries

LLM-Fehler wiederholen/brechen

Test: absichtlich Fehler provozieren (z. B. falscher API-Key), Verhalten beobachten.

Empfehlung zur Vorgehensweise

Ich würde konkret so starten:

Heute: Phase 0–2 (Struktur, Flask-„Hello World“, DB + Companies).

Dann: Phase 3–4 (Dummy-Artikel, Dummy-Topics, Dummy-Summaries).

Dann: Phase 5 (Website an DB).

Danach: Phase 6 (Groq + echte Artikel).

Zum Schluss: Phase 7 (Cron, Feinheiten).