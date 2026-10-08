---
phase: 08-hoerstel-grundlage
plan: 02
subsystem: pipeline, ci
tags: [tests, regression, profis, ostbevern, ci]
documented: "nachträglich von Hand, ohne GSD-Befehle (kein PLAN.md)"

requires:
  - phase: 08-hoerstel-grundlage
    plan: 01
    provides: "Jahrgang 2026 = Hörstel, Ostbevern-Jahrgang archiviert"
provides:
  - "pipeline/jahrgaenge/archiv/ostbevern/2026.toml und 2026_sollwerte.toml: Ostbevern-Referenzjahrgang (software = \"profis\")"
  - "raw_data/ostbevern/haushalt-2026.pdf: Ostbevern-PDF aus der Historie (gleicher Git-Blob, kein Repo-Wachstum)"
  - "ostbevern/konfiguration.py: STANDARD_JAHRGAENGE_VERZEICHNIS, Umlenkung über PIPELINE_JAHRGAENGE"
  - "tests/conftest.py: alle Tests außer test_ikvs.py laufen gegen den Ostbevern-Referenzjahrgang"
  - ".github/workflows/ci.yml: Reproduzierbarkeitsschritt mit PIPELINE_JAHRGAENGE=jahrgaenge/archiv/ostbevern"
affects: [09-ikvs-seiten-und-teilplaene, 11-manuelle-daten-und-app-daten-hoerstel]

commits:
  - 094db88

key-files:
  modified:
    - pipeline/ostbevern/konfiguration.py
    - pipeline/tests/conftest.py
    - pipeline/tests/test_ikvs.py
    - .github/workflows/ci.yml
    - .claude/CLAUDE.md
---

# 08-02: Ostbevern als ProFIS+-Referenz für Tests und CI

## Ergebnis

- Pipeline-Tests: **673 bestanden, 1 übersprungen** (fehlende `app/node_modules` im Container). Vor Phase 8 liefen mit dem ausgetauschten PDF nur 509 Tests durch; nach 08-01 allein waren 281 rot.
- `alle.py` mit `PIPELINE_JAHRGAENGE=jahrgaenge/archiv/ostbevern` (lokal nachgestellter CI-Schritt): alle Prüfregeln grün, `daten/` und `app/src/data/` ohne Diff, 0 Belegbilder neu gerendert.

## Entscheidungen

- **Referenz statt Löschen:** Die bestehenden Tests sichern die ProFIS+-Leser und die gemeinsame Logik (Prüfregeln, App-Daten, Quellen) ab. Sie laufen gegen den archivierten Ostbevern-Jahrgang und die eingecheckten Ostbevern-Daten unter `daten/`.
- **Umlenkung beim Import:** `PIPELINE_JAHRGAENGE` wird beim Import von `ostbevern.konfiguration` ausgewertet, damit Standardargumente und importierte Konstanten übereinstimmen. `conftest.py` setzt die Variable vor dem ersten Import; `test_ikvs.py` lädt den aktiven Jahrgang ausdrücklich über `STANDARD_JAHRGAENGE_VERZEICHNIS`.
- **CI:** Der Reproduzierbarkeitsschritt prüft bis Phase 11 den Ostbevern-Referenzjahrgang, weil `daten/` und `app/src/data/` noch von dort stammen.

## Offene Punkte

- Sobald Hörstel durchläuft (Phase 11), wechseln `daten/`, `app/src/data/` und der CI-Schritt auf Hörstel. Dann muss entschieden werden, ob die Ostbevern-Referenztests eigene Testdaten (statt `daten/`) bekommen.
