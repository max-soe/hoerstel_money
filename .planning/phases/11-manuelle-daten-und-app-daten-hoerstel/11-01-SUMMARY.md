---
phase: 11-manuelle-daten-und-app-daten-hoerstel
plan: 01
subsystem: pipeline
tags: [referenz, ostbevern, ci, konfiguration]
documented: "von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 08-hoerstel-grundlage
    provides: "Ostbevern-Jahrgang unter jahrgaenge/archiv/ostbevern, PIPELINE_JAHRGAENGE"
provides:
  - "pipeline/referenz/ostbevern/: Jahrgang (jahrgaenge/), daten/, app/src/data/*.json und app/public/quellen/ des Ostbevern-Stands v1.0"
  - "ostbevern/konfiguration.py: PIPELINE_REFERENZ lenkt Jahrgänge, DATEN_WURZEL und APP_WURZEL gemeinsam um (ersetzt PIPELINE_JAHRGAENGE)"
  - "schema.py, app_daten.py, quellen.py: Pfade über DATEN_WURZEL/APP_WURZEL statt PROJEKT_WURZEL"
  - "tests/conftest.py und CI-Reproduzierbarkeitsschritt auf PIPELINE_REFERENZ=referenz/ostbevern"
affects: [11-02, 11-03, 11-04, 11-05, 12-app-auf-hoerstel-umstellen]

key-files:
  created:
    - pipeline/referenz/ostbevern/
  modified:
    - pipeline/ostbevern/konfiguration.py
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/ostbevern/quellen.py
    - pipeline/tests/conftest.py
    - .github/workflows/ci.yml
---

# 11-01: Ostbevern-Referenzstand auslagern

## Ergebnis

- Der komplette Ostbevern-Stand (Jahrgangsdateien, `daten/`, App-JSON, Belegbilder) liegt unter `pipeline/referenz/ostbevern/`. Das Projekt-`daten/` und `app/src/data/` werden damit frei für Hörstel; die eingecheckten Ostbevern-Dateien dort werden in 11-03 bis 11-05 Datei für Datei ersetzt.
- `PIPELINE_REFERENZ=referenz/ostbevern` (relativ zu `pipeline/`) lenkt beim Import von `ostbevern.konfiguration` Jahrgänge, `DATEN_WURZEL` und `APP_WURZEL` gemeinsam um. Ohne Variable gilt der aktive Hörsteler Jahrgang mit Projekt-`daten/` und `app/`.
- Die volle Testsuite läuft gegen den Referenzstand; der lokal nachgestellte CI-Reproduzierbarkeitslauf (`alle.py` mit `PIPELINE_REFERENZ`) erzeugt den Referenzstand ohne Diff.

## Entscheidungen

- **Eine Variable statt zwei:** `PIPELINE_JAHRGAENGE` lenkte nur die Jahrgänge um; Schritte, die `daten/` lesen, hätten dann Hörsteler Handdaten mit Ostbevern-Jahrgang gemischt. `PIPELINE_REFERENZ` hält Jahrgang und Daten zusammen.
- **Kopie im Repository:** Der Referenzstand ist eingecheckt (wie `daten/`), damit die CI ihn reproduzieren und vergleichen kann.
